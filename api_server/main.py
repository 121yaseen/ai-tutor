import os
import json
import base64
import asyncio

from pathlib import Path
from dotenv import load_dotenv

from google.genai.types import (
    Part,
    Content,
    Blob,
)

from google.adk.runners import InMemoryRunner
from google.adk.agents import LiveRequestQueue
from google.adk.agents.run_config import RunConfig

from fastapi import FastAPI, Request, APIRouter, Depends, HTTPException, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from passlib.context import CryptContext
import jwt
from google.cloud import firestore
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict

from agents.ai_tutor.agent import root_agent
from firestore_client import get_firestore_client

#
# Pistah - IELTS Tutor
#

# Load Gemini API Key
load_dotenv()

APP_NAME = "Pistah - IELTS Tutor"


async def start_agent_session(user_email: str, is_audio=False):
    """Starts an agent session using the authenticated user's email as the session's user_id"""

    # Create a Runner
    runner = InMemoryRunner(
        app_name=APP_NAME,
        agent=root_agent,
    )

    # Create a Session
    session = await runner.session_service.create_session(
        app_name=APP_NAME,
        user_id=user_email,  # Use authenticated user's email
    )

    # Set response modality
    modality = "AUDIO" if is_audio else "TEXT"
    run_config = RunConfig(response_modalities=[modality])

    # Create a LiveRequestQueue for this session
    live_request_queue = LiveRequestQueue()

    # Start agent session
    live_events = runner.run_live(
        session=session,
        live_request_queue=live_request_queue,
        run_config=run_config,
    )

    # Send an initial empty message to trigger agent greeting
    initial_content = Content(role="user", parts=[Part.from_text(text="Hi")])
    live_request_queue.send_content(content=initial_content)

    return live_events, live_request_queue


async def agent_to_client_sse(live_events):
    """Agent to client communication via SSE"""
    async for event in live_events:
        # If the turn complete or interrupted, send it
        if event.turn_complete or event.interrupted:
            message = {
                "turn_complete": event.turn_complete,
                "interrupted": event.interrupted,
            }
            yield f"data: {json.dumps(message)}\n\n"
            #print(f"[AGENT TO CLIENT]: {message}")
            continue

        # Read the Content and its first Part
        part: Part = (
            event.content and event.content.parts and event.content.parts[0]
        )
        if not part:
            continue

        # If it's audio, send Base64 encoded audio data
        is_audio = part.inline_data and part.inline_data.mime_type.startswith("audio/pcm")
        if is_audio:
            audio_data = part.inline_data and part.inline_data.data
            if audio_data:
                message = {
                    "mime_type": "audio/pcm",
                    "data": base64.b64encode(audio_data).decode("ascii")
                }
                yield f"data: {json.dumps(message)}\n\n"
                #print(f"[AGENT TO CLIENT]: audio/pcm: {len(audio_data)} bytes.")
                continue

        # If it's text and a parial text, send it
        if part.text and event.partial:
            message = {
                "mime_type": "text/plain",
                "data": part.text
            }
            yield f"data: {json.dumps(message)}\n\n"
            #print(f"[AGENT TO CLIENT]: text/plain: {message}")


#
# FastAPI web app
#

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Calculate the project root and static directory path
# main_py_file_path is the absolute path to this file (api_server/main.py)
main_py_file_path = Path(__file__).resolve()
# project_root is the absolute path to the 'app' directory
project_root = main_py_file_path.parent.parent
# STATIC_DIR is the absolute path to 'app/frontend/static'
STATIC_DIR = project_root / "frontend" / "static"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Store active sessions
active_sessions = {}

# JWT and password hashing setup
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Firestore client
firestore_client = get_firestore_client()
users_collection = firestore_client.collection("users")

auth_router = APIRouter()

class UserRegister(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    email: str

# Helper functions
def get_user_by_email(email: str):
    docs = users_collection.where("email", "==", email).stream()
    for doc in docs:
        return doc.to_dict()
    return None

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None

# Renamed and modified to be a dependency that provides the user's email
async def get_authenticated_user_email(request: Request) -> str:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated - No token")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Token does not contain user email")
    # Optional: Verify user still exists in DB if necessary, but for email retrieval this is enough
    return email

# Auth endpoints
@auth_router.post("/api/auth/register", response_model=UserOut)
def register(user: UserRegister):
    if get_user_by_email(user.email):
        raise HTTPException(status_code=400, detail="Email already exists")
    hashed_password = get_password_hash(user.password)
    user_data = {
        "email": user.email,
        "password_hash": hashed_password,
    }
    users_collection.add(user_data)
    return UserOut(email=user.email)

@auth_router.post("/api/auth/login")
def login(user: UserLogin, response: Response):
    db_user = get_user_by_email(user.email)
    if not db_user or not verify_password(user.password, db_user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": db_user["email"]})
    response.set_cookie(key="access_token", value=token, httponly=True, secure=True)
    return {"message": "Logged in"}

@auth_router.post("/api/auth/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out"}

@auth_router.get("/api/auth/me", response_model=Optional[dict])
def get_me(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload:
        return None
    email = payload.get("sub")
    db_user = get_user_by_email(email)
    if not db_user:
        return None
    return db_user

# Dependency for protected endpoints (original one, can be kept if used elsewhere, or removed if get_authenticated_user_email replaces its usage patterns)
# async def get_current_user(request: Request):
# token = request.cookies.get("access_token")
# if not token:
# raise HTTPException(status_code=401, detail="Not authenticated")
# payload = decode_access_token(token)
# if not payload:
# raise HTTPException(status_code=401, detail="Invalid token")
# email = payload.get("sub")
# db_user = get_user_by_email(email)
# if not db_user:
# raise HTTPException(status_code=401, detail="User not found")
# return db_user

# Register the auth router
app.include_router(auth_router)

@app.get("/")
async def root():
    """Serves the index.html"""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/events/{client_session_id}")
async def sse_endpoint(
    client_session_id: str,
    is_audio: str = "false",
    authenticated_user_email: str = Depends(get_authenticated_user_email)
):
    """SSE endpoint for agent to client communication"""
    print(f"[SSE /events/{client_session_id}]: Connection attempt received. is_audio={is_audio}")

    try:
        # Start agent session
        print(f"[SSE /events/{client_session_id}]: Starting agent session...")
        live_events, live_request_queue = await start_agent_session(
            user_email=authenticated_user_email,
            is_audio=is_audio.lower() == "true"
        )
        print(f"[SSE /events/{client_session_id}]: Agent session started. live_events and live_request_queue created.")

        # Store the request queue for this user
        active_sessions[client_session_id] = live_request_queue
        print(f"[SSE /events/{client_session_id}]: live_request_queue stored in active_sessions.")

        print(f"Client #{client_session_id} connected via SSE, audio mode: {is_audio}")

        def cleanup():
            print(f"[SSE /events/{client_session_id}]: Cleanup called.")
            live_request_queue.close()
            if client_session_id in active_sessions:
                del active_sessions[client_session_id]
            print(f"Client #{client_session_id} disconnected from SSE")

        async def event_generator():
            print(f"[SSE /events/{client_session_id}]: Event generator started.")
            try:
                # Send an initial connected message & session ready message
                yield f"data: {json.dumps({'message': 'SSE connection established', 'user_id': client_session_id})}\n\n"
                print(f"[SSE /events/{client_session_id}]: Sent initial 'connected' message.")
                
                # Explicitly signal that the server-side session is fully ready for data
                yield f"data: {json.dumps({'type': 'session_ready_for_data', 'user_id': client_session_id})}\n\n"
                print(f"[SSE /events/{client_session_id}]: Sent 'session_ready_for_data' message.")
                
                await asyncio.sleep(0)

                async for data in agent_to_client_sse(live_events):
                    print(f"[SSE /events/{client_session_id}]: Yielding data: {data[:100]}...")
                    yield data
                print(f"[SSE /events/{client_session_id}]: Finished iterating agent_to_client_sse.")
            except Exception as e:
                print(f"[SSE /events/{client_session_id}]: Error in SSE stream event_generator: {e}", repr(e))
            finally:
                print(f"[SSE /events/{client_session_id}]: Event generator finally block. Calling cleanup.")
                cleanup()
                print(f"[SSE /events/{client_session_id}]: Event generator finished.")

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control"
            }
        )
    except Exception as e:
        print(f"[SSE /events/{client_session_id}]: CRITICAL ERROR in sse_endpoint before returning StreamingResponse: {e}", repr(e))
        # Optionally, return an error response if appropriate before streaming starts
        # For now, just logging, as it might be hard to return HTTP error if headers already sent.
        # raise # or handle gracefully


@app.post("/send/{client_session_id}")
async def send_message_endpoint(
    client_session_id: str,
    request: Request,
    authenticated_user_email: str = Depends(get_authenticated_user_email)
):
    """HTTP endpoint for client to agent communication"""

    if client_session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found or expired")

    live_request_queue = active_sessions[client_session_id]

    # Parse the message
    message = await request.json()
    mime_type = message["mime_type"]
    data = message["data"]

    # Send the message to the agent
    if mime_type == "text/plain":
        content = Content(role="user", parts=[Part.from_text(text=data)])
        live_request_queue.send_content(content=content)
        #print(f"[CLIENT TO AGENT]: {data}")
    elif mime_type == "audio/pcm":
        decoded_data = base64.b64decode(data)
        live_request_queue.send_realtime(Blob(data=decoded_data, mime_type=mime_type))
        #print(f"[CLIENT TO AGENT]: audio/pcm: {len(decoded_data)} bytes")
    else:
        return {"error": f"Mime type not supported: {mime_type}"}

    return {"status": "sent"}
