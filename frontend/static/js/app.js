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
    console.log("[SSE RAW DATA]:", event.data);
    try {
      const message_from_server = JSON.parse(event.data);
      console.log("[AGENT TO CLIENT] ", message_from_server);
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
});

function audioRecorderHandler(pcmData) {
  sendMessage({
    mime_type: "audio/pcm",
    data: arrayBufferToBase64(pcmData),
  });
  console.log("[CLIENT TO AGENT] sent %s bytes", pcmData.byteLength);
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
});
