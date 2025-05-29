from flask import Flask, render_template, request, jsonify, session
import requests
import logging
import os

app = Flask(__name__)

# It's crucial to set a secret key for session management.
# For production, use a strong, randomly generated key and store it securely.
app.secret_key = os.urandom(24)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# TODO: Get this from a config file or environment variable
# Changed to reflect ADK api_server endpoint structure when run from parent app dir
AGENT_API_URL = "http://localhost:8000/ai_tutor/run"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_audio', methods=['POST'])
def process_audio():
    data = request.get_json()
    user_text = data.get('text')

    if not user_text:
        logger.error("No text received from frontend.")
        return jsonify({"error": "No text provided"}), 400

    logger.info(f"Received text from user: {user_text}")

    try:
        # Retrieve session_id from Flask session
        current_ai_tutor_session_id = session.get('ai_tutor_session_id')
        logger.info(f"Current Flask session ai_tutor_session_id: {current_ai_tutor_session_id}")

        payload = {
            "input": user_text,
            "session_id": current_ai_tutor_session_id,
            "stream": False # UI not designed for streaming responses from agent
        }
        logger.info(f"Sending payload to agent: {payload}")
        
        agent_response = requests.post(AGENT_API_URL, json=payload)
        agent_response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        
        response_data = agent_response.json()
        
        # Extract agent's text response
        agent_text = response_data.get("output", "Sorry, I could not process that.")
        
        # Extract and store the session_id from the agent's response into Flask session
        new_ai_tutor_session_id = response_data.get("session_id")
        if new_ai_tutor_session_id:
            session['ai_tutor_session_id'] = new_ai_tutor_session_id
            logger.info(f"Stored new ai_tutor_session_id in Flask session: {new_ai_tutor_session_id}")
        else:
            logger.warning("Agent did not return a session_id.")

        logger.info(f"Received response from agent: {agent_text}")
        return jsonify({"response": agent_text})

    except requests.exceptions.RequestException as e:
        logger.error(f"Error communicating with agent: {e}")
        # Clear potentially stale session ID on agent connection error
        session.pop('ai_tutor_session_id', None)
        return jsonify({"error": "Could not connect to the agent."}), 500
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        # Clear potentially stale session ID on other errors
        session.pop('ai_tutor_session_id', None)
        return jsonify({"error": "An unexpected error occurred."}), 500

if __name__ == '__main__':
    # Ensure the port doesn't clash with the ADK agent's port (default 8000)
    app.run(debug=True, port=5001) 