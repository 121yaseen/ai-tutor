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

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from agents.ai_tutor.agent import root_agent

#
# ADK Streaming
#

# Load Gemini API Key
load_dotenv()

APP_NAME = "ADK Streaming example"


async def start_agent_session(user_id, is_audio=False):
    """Starts an agent session"""

    # Create a Runner
    runner = InMemoryRunner(
        app_name=APP_NAME,
        agent=root_agent,
    )

    # Create a Session
    session = await runner.session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,  # Replace with actual user ID
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
            print(f"[AGENT TO CLIENT]: {message}")
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
                print(f"[AGENT TO CLIENT]: audio/pcm: {len(audio_data)} bytes.")
                continue

        # If it's text and a parial text, send it
        if part.text and event.partial:
            message = {
                "mime_type": "text/plain",
                "data": part.text
            }
            yield f"data: {json.dumps(message)}\n\n"
            print(f"[AGENT TO CLIENT]: text/plain: {message}")


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


@app.get("/")
async def root():
    """Serves the index.html"""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/events/{user_id}")
async def sse_endpoint(user_id: int, is_audio: str = "false"):
    """SSE endpoint for agent to client communication"""
    print(f"[SSE /events/{user_id}]: Connection attempt received. is_audio={is_audio}")

    try:
        # Start agent session
        user_id_str = str(user_id)
        print(f"[SSE /events/{user_id_str}]: Starting agent session...")
        live_events, live_request_queue = await start_agent_session(user_id_str, is_audio == "true")
        print(f"[SSE /events/{user_id_str}]: Agent session started. live_events and live_request_queue created.")

        # Store the request queue for this user
        active_sessions[user_id_str] = live_request_queue
        print(f"[SSE /events/{user_id_str}]: live_request_queue stored in active_sessions.")

        print(f"Client #{user_id} connected via SSE, audio mode: {is_audio}")

        def cleanup():
            print(f"[SSE /events/{user_id_str}]: Cleanup called.")
            live_request_queue.close()
            if user_id_str in active_sessions:
                del active_sessions[user_id_str]
            print(f"Client #{user_id} disconnected from SSE")

        async def event_generator():
            print(f"[SSE /events/{user_id_str}]: Event generator started.")
            try:
                # Send an initial connected message
                yield f"data: {json.dumps({'message': 'SSE connection established', 'user_id': user_id_str})}\n\n"
                print(f"[SSE /events/{user_id_str}]: Sent initial 'connected' message.")
                await asyncio.sleep(0)

                async for data in agent_to_client_sse(live_events):
                    print(f"[SSE /events/{user_id_str}]: Yielding data: {data[:100]}...")
                    yield data
                print(f"[SSE /events/{user_id_str}]: Finished iterating agent_to_client_sse.")
            except Exception as e:
                print(f"[SSE /events/{user_id_str}]: Error in SSE stream event_generator: {e}", repr(e))
            finally:
                print(f"[SSE /events/{user_id_str}]: Event generator finally block. Calling cleanup.")
                cleanup()
                print(f"[SSE /events/{user_id_str}]: Event generator finished.")

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
        print(f"[SSE /events/{user_id}]: CRITICAL ERROR in sse_endpoint before returning StreamingResponse: {e}", repr(e))
        # Optionally, return an error response if appropriate before streaming starts
        # For now, just logging, as it might be hard to return HTTP error if headers already sent.
        # raise # or handle gracefully


@app.post("/send/{user_id}")
async def send_message_endpoint(user_id: int, request: Request):
    """HTTP endpoint for client to agent communication"""

    user_id_str = str(user_id)

    # Get the live request queue for this user
    live_request_queue = active_sessions.get(user_id_str)
    if not live_request_queue:
        return {"error": "Session not found"}

    # Parse the message
    message = await request.json()
    mime_type = message["mime_type"]
    data = message["data"]

    # Send the message to the agent
    if mime_type == "text/plain":
        content = Content(role="user", parts=[Part.from_text(text=data)])
        live_request_queue.send_content(content=content)
        print(f"[CLIENT TO AGENT]: {data}")
    elif mime_type == "audio/pcm":
        decoded_data = base64.b64decode(data)
        live_request_queue.send_realtime(Blob(data=decoded_data, mime_type=mime_type))
        print(f"[CLIENT TO AGENT]: audio/pcm: {len(decoded_data)} bytes")
    else:
        return {"error": f"Mime type not supported: {mime_type}"}

    return {"status": "sent"}
