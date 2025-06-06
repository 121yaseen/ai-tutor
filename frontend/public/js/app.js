/**
 * app.js: JS code for the adk-streaming sample app.
 */

import { startAudioPlayerWorklet } from "./audio-player.js";
import { startAudioRecorderWorklet, stopMicrophone } from "./audio-recorder.js";

document.addEventListener("DOMContentLoaded", () => {
  // Set greeting based on user's local time
  const greetingDiv = document.querySelector('.greeting');
  if (greetingDiv) {
    const hour = new Date().getHours();
    let greeting = '';
    if (hour < 5) greeting = 'Good Night';
    else if (hour < 12) greeting = 'Good Morning';
    else if (hour < 18) greeting = 'Good Afternoon';
    else greeting = 'Good Evening';
    greetingDiv.textContent = greeting;
  }

/**
 * SSE (Server-Sent Events) handling
 */

let eventSource = null;
let is_audio = false;
let sessionId = null;
let sse_url = null;
let send_url = null;
let isServerSessionReady = false; // Flag to track server readiness

// Get DOM elements
const conversationDiv = document.getElementById("conversation");
const micBtn = document.getElementById("micBtn");
const stopBtn = document.getElementById("stopBtn");
const startAudioButton = document.getElementById("startAudioButton");
let currentMessageId = null;

// SSE handlers
function connectSSE() {
  if (eventSource) {
    eventSource.close();
    eventSource = null;
  }
  eventSource = new EventSource(sse_url + "?is_audio=" + is_audio);

  eventSource.onopen = function () {
    console.log("SSE connection opened.");
    if (conversationDiv) conversationDiv.textContent = "Connection opened";
  };

  eventSource.onmessage = function (event) {
    //console.log("[SSE RAW DATA]:", event.data);
    try {
      const message_from_server = JSON.parse(event.data);
      //console.log("[AGENT TO CLIENT] ", message_from_server);

      // Check for session ready message
      if (message_from_server.type === "session_ready_for_data") {
        console.log("[SSE] Received session_ready_for_data from server.");
        isServerSessionReady = true;
        // Potentially send any buffered audio data here if implemented
        return; 
      }

      if (
        message_from_server.turn_complete &&
        message_from_server.turn_complete == true
      ) {
        currentMessageId = null;
        return;
      }
      if (message_from_server.mime_type == "audio/pcm" && audioPlayerNode) {
        audioPlayerNode.port.postMessage(base64ToArray(message_from_server.data));
      }
      if (message_from_server.mime_type == "text/plain") {
        if (currentMessageId == null) {
          currentMessageId = Math.random().toString(36).substring(7);
          const message = document.createElement("p");
          message.id = currentMessageId;
          if (conversationDiv) conversationDiv.appendChild(message);
        }
        const message = document.getElementById(currentMessageId);
        message.textContent += message_from_server.data;
        if (conversationDiv) conversationDiv.scrollTop = conversationDiv.scrollHeight;
      }
    } catch (e) {
      console.error("Error parsing JSON from SSE:", e);
      console.error("Offending SSE data string:", event.data);
      return;
    }
  };

  eventSource.onerror = function (event) {
    console.log("SSE connection error or closed.");
    if (conversationDiv) conversationDiv.textContent = "Connection closed";
    if (eventSource) eventSource.close();
    eventSource = null;
    isServerSessionReady = false; // Reset flag
  };
}

// Send a message to the server via HTTP POST
async function sendMessage(message) {
  try {
    const response = await fetch(send_url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(message)
    });
    if (!response.ok) {
      console.error('Failed to send message:', response.statusText);
    }
  } catch (error) {
    console.error('Error sending message:', error);
  }
}

function base64ToArray(base64) {
  const binaryString = window.atob(base64);
  const len = binaryString.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes.buffer;
}

/**
 * Audio handling
 */

let audioPlayerNode;
let audioPlayerContext;
let audioRecorderNode;
let audioRecorderContext;
let micStream;

function startAudio() {
  startAudioPlayerWorklet().then(([node, ctx]) => {
    audioPlayerNode = node;
    audioPlayerContext = ctx;
    window.audioPlayerNode = node;
  });
  startAudioRecorderWorklet(audioRecorderHandler).then(
    ([node, ctx, stream]) => {
      audioRecorderNode = node;
      audioRecorderContext = ctx;
      micStream = stream;
      window.audioRecorderNode = node;
    }
  );
}

// Show/hide stop button and mic button
window.showStopButton = function() {
  stopBtn.style.display = '';
  micBtn.style.display = 'none';
};
window.hideStopButton = function() {
  stopBtn.style.display = 'none';
  micBtn.style.display = '';
};

// Start session on mic button click
micBtn.addEventListener("click", function() {
  // Generate a new sessionId for each session
  sessionId = Math.floor(Math.random() * 1e9).toString();
  sse_url = window.location.protocol + "//" + window.location.host + "/events/" + sessionId;
  send_url = window.location.protocol + "//" + window.location.host + "/send/" + sessionId;
  is_audio = true;
  isServerSessionReady = false; // Reset flag for new session
  currentMessageId = null;
  if (conversationDiv) conversationDiv.textContent = '';
  startAudio();
  connectSSE();
  window.showStopButton();
  if (window.setVoiceWaveActive) window.setVoiceWaveActive(true);
});

// Stop session logic
stopBtn.addEventListener("click", () => {
  // Stop audio input/output if possible
  if (window.audioRecorderNode && window.audioRecorderNode.port) {
    try { window.audioRecorderNode.port.postMessage({ command: 'stop' }); } catch (e) {}
  }
  if (window.audioPlayerNode && window.audioPlayerNode.port) {
    try { window.audioPlayerNode.port.postMessage({ command: 'stop' }); } catch (e) {}
  }
  // Stop microphone stream
  if (micStream) {
    try { stopMicrophone(micStream); } catch (e) {}
    micStream = null;
  }
  // Close and null audio contexts and nodes
  if (audioRecorderContext) {
    try { audioRecorderContext.close(); } catch (e) {}
    audioRecorderContext = null;
  }
  if (audioPlayerContext) {
    try { audioPlayerContext.close(); } catch (e) {}
    audioPlayerContext = null;
  }
  audioRecorderNode = null;
  audioPlayerNode = null;
  window.audioRecorderNode = null;
  window.audioPlayerNode = null;
  // Close SSE connection
  if (eventSource) {
    eventSource.close();
    eventSource = null;
  }
  window.hideStopButton();
  is_audio = false;
  currentMessageId = null;
  if (conversationDiv) conversationDiv.textContent = '';
  if (window.setVoiceWaveActive) window.setVoiceWaveActive(false);
  isServerSessionReady = false; // Reset flag
});

function audioRecorderHandler(pcmData) {
  if (!isServerSessionReady) {
    console.log("[AUDIO RECORDER] Server session not ready. Audio data buffered/dropped.");
    // Optionally, buffer pcmData here if needed, then send when isServerSessionReady becomes true
    return; 
  }
  sendMessage({
    mime_type: "audio/pcm",
    data: arrayBufferToBase64(pcmData),
  });
  //console.log("[CLIENT TO AGENT] sent %s bytes", pcmData.byteLength);
}

function arrayBufferToBase64(buffer) {
  let binary = "";
  const bytes = new Uint8Array(buffer);
  const len = bytes.byteLength;
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return window.btoa(binary);
}

// === AUTH LOGIC ===
const authSection = document.getElementById('auth-section');
const userInfoDiv = document.getElementById('user-info');
const userNameSpan = document.getElementById('user-name');
const logoutBtn = document.getElementById('logoutBtn');
const appLogoutBtn = document.getElementById('appLogoutBtn');
const loginForm = document.getElementById('login-form');
const loginError = document.getElementById('login-error');
const registerForm = document.getElementById('register-form');
const registerError = document.getElementById('register-error');

// Updated selectors for the new links
const showLoginLink = document.getElementById('show-login-link');
const showRegisterLink = document.getElementById('show-register-link');

const appContainer = document.querySelector('.container');
const loginPageWrapper = document.querySelector('.login-page-wrapper');

function showLoginForm() {
  if(loginForm) loginForm.style.display = '';
  if(registerForm) registerForm.style.display = 'none';
  if(loginError) loginError.textContent = '';
  if(registerError) registerError.textContent = '';
}
function showRegisterForm() {
  if(loginForm) loginForm.style.display = 'none';
  if(registerForm) registerForm.style.display = '';
  if(loginError) loginError.textContent = '';
  if(registerError) registerError.textContent = '';
}

// This function shows the main application content PLUS user info in the auth column
function showAppContent(email) {
  console.log("[showAppContent] Called. Hiding login wrapper, showing app container.");
  if (loginPageWrapper) loginPageWrapper.style.display = 'none'; // Hide login page completely
  if (appContainer) appContainer.style.display = 'flex'; // Show main app content
}

// This function shows the authentication page (login/register forms)
function showAuthPageStructure() {
  if(loginPageWrapper) loginPageWrapper.style.display = 'flex';
  if(appContainer) appContainer.style.display = 'none'; // Hide main app content
  if(userInfoDiv) userInfoDiv.style.display = 'none'; // Hide user info block
  showLoginForm(); // Default to showing the login form
}

// Updated event listeners for the new links
if (showLoginLink) showLoginLink.addEventListener('click', (e) => {
    e.preventDefault(); // Prevent anchor link behavior if it was an <a> tag
    showLoginForm();
});
if (showRegisterLink) showRegisterLink.addEventListener('click', (e) => {
    e.preventDefault(); // Prevent anchor link behavior
    showRegisterForm();
});

loginForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  loginError.textContent = '';
  const email = document.getElementById('login-username').value;
  const password = document.getElementById('login-password').value;
  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    if (res.ok) {
      // Immediately show the AI assistant page after login
      showAppContent(email);
      await checkAuth();
    } else {
      const data = await res.json();
      loginError.textContent = data.detail || 'Login failed';
    }
  } catch (err) {
    loginError.textContent = 'Login error';
  }
});

registerForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  registerError.textContent = '';
  const email = document.getElementById('register-email').value;
  const password = document.getElementById('register-password').value;
  try {
    const res = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    if (res.ok) {
      // Auto-login after registration
      await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      await checkAuth();
    } else {
      const data = await res.json();
      registerError.textContent = data.detail || 'Registration failed';
    }
  } catch (err) {
    registerError.textContent = 'Registration error';
  }
});

if (appLogoutBtn) {
  appLogoutBtn.addEventListener('click', async () => {
    await fetch('/api/auth/logout', { method: 'POST' });
    showAuthPageStructure(); // Show login page and hide app content
  });
}

async function checkAuth() {
  console.log("[checkAuth] Called.");
  try {
    const res = await fetch('/api/auth/me');
    if (res.ok) {
      const data = await res.json();
      // Ensure backend returns email in the /me response for consistency
      if (data && data.email) { 
        console.log("[checkAuth] User authenticated, email:", data.email);
        console.log("[DEV LOG] Full user document from 'users' collection:", data);
        showAppContent(data.email); // User is logged in
        return;
      }
    }
  } catch (err) {
    console.error("Error during checkAuth:", err);
  }
  console.log("[checkAuth] User NOT authenticated or error occurred. Showing auth page.");
  showAuthPageStructure(); // User is not logged in, or error, show auth page
}

// On page load, check auth
checkAuth();

});
