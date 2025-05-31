/**
 * app.js: JS code for the adk-streaming sample app.
 */

import { startAudioPlayerWorklet } from "./audio-player.js";
import { startAudioRecorderWorklet } from "./audio-recorder.js";

document.addEventListener("DOMContentLoaded", () => {
/**
 * SSE (Server-Sent Events) handling
 */

// Connect the server with SSE
const sessionId = Math.random().toString().substring(10);
const sse_url =
  window.location.protocol + "//" + window.location.host + "/events/" + sessionId;
const send_url =
  window.location.protocol + "//" + window.location.host + "/send/" + sessionId;
let eventSource = null;
let is_audio = false;

// Get DOM elements
const conversationDiv = document.getElementById("conversation");
let currentMessageId = null;

// SSE handlers
function connectSSE() {
  // Connect to SSE endpoint
  eventSource = new EventSource(sse_url + "?is_audio=" + is_audio);

  // Handle connection open
  eventSource.onopen = function () {
    // Connection opened messages
    console.log("SSE connection opened.");
    if (conversationDiv) conversationDiv.textContent = "Connection opened";
  };

  // Handle incoming messages
  eventSource.onmessage = function (event) {
    // Log raw event data before parsing
    console.log("[SSE RAW DATA]:", event.data);

    // Parse the incoming message
    try {
      const message_from_server = JSON.parse(event.data);
      console.log("[AGENT TO CLIENT] ", message_from_server);

      // Check if the turn is complete
      if (
        message_from_server.turn_complete &&
        message_from_server.turn_complete == true
      ) {
        currentMessageId = null;
        return;
      }

      // If it's audio, play it
      if (message_from_server.mime_type == "audio/pcm" && audioPlayerNode) {
        audioPlayerNode.port.postMessage(base64ToArray(message_from_server.data));
      }

      // If it's a text, print it
      if (message_from_server.mime_type == "text/plain") {
        // add a new message for a new turn
        if (currentMessageId == null) {
          currentMessageId = Math.random().toString(36).substring(7);
          const message = document.createElement("p");
          message.id = currentMessageId;
          if (conversationDiv) conversationDiv.appendChild(message);
        }

        // Add message text to the existing message element
        const message = document.getElementById(currentMessageId);
        message.textContent += message_from_server.data;

        // Scroll down to the bottom of the conversationDiv
        if (conversationDiv) conversationDiv.scrollTop = conversationDiv.scrollHeight;
      }
    } catch (e) {
      console.error("Error parsing JSON from SSE:", e);
      console.error("Offending SSE data string:", event.data);
      return; // Stop processing this malformed message
    }
  };

  // Handle connection close
  eventSource.onerror = function (event) {
    console.log("SSE connection error or closed.");
    if (conversationDiv) conversationDiv.textContent = "Connection closed";
    eventSource.close();
    setTimeout(function () {
      console.log("Reconnecting...");
      connectSSE();
    }, 5000);
  };
}
connectSSE();

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

// Decode Base64 data to Array
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

// Start audio
function startAudio() {
  // Start audio output
  startAudioPlayerWorklet().then(([node, ctx]) => {
    audioPlayerNode = node;
    audioPlayerContext = ctx;
  });
  // Start audio input
  startAudioRecorderWorklet(audioRecorderHandler).then(
    ([node, ctx, stream]) => {
      audioRecorderNode = node;
      audioRecorderContext = ctx;
      micStream = stream;
    }
  );
}

// Start the audio only when the user clicked the button
const startAudioButton = document.getElementById("startAudioButton");
const micBtn = document.getElementById("micBtn");
const stopBtn = document.getElementById("stopBtn");

micBtn.addEventListener("click", function() {
  startAudioButton.click();
});

// Show/hide stop button and mic button
window.showStopButton = function() {
  stopBtn.style.display = '';
  micBtn.style.display = 'none';
};
window.hideStopButton = function() {
  stopBtn.style.display = 'none';
  micBtn.style.display = '';
};

// When audio starts, show stop button
startAudioButton.addEventListener("click", () => {
  startAudioButton.disabled = true;
  startAudio();
  is_audio = true;
  eventSource.close(); // close current connection
  connectSSE(); // reconnect with the audio mode
  window.showStopButton();
});

// Audio recorder handler
function audioRecorderHandler(pcmData) {
  // Send the pcm data as base64
  sendMessage({
    mime_type: "audio/pcm",
    data: arrayBufferToBase64(pcmData),
  });
  console.log("[CLIENT TO AGENT] sent %s bytes", pcmData.byteLength);
}

// Encode an array buffer with Base64
function arrayBufferToBase64(buffer) {
  let binary = "";
  const bytes = new Uint8Array(buffer);
  const len = bytes.byteLength;
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return window.btoa(binary);
}

// Stop session logic
stopBtn.addEventListener("click", () => {
  // Stop audio input/output if possible
  if (window.audioRecorderNode && window.audioRecorderNode.port) {
    try { window.audioRecorderNode.port.postMessage({ command: 'stop' }); } catch (e) {}
  }
  if (window.audioPlayerNode && window.audioPlayerNode.port) {
    try { window.audioPlayerNode.port.postMessage({ command: 'stop' }); } catch (e) {}
  }
  // Optionally, close/reconnect SSE or reset state here
  window.hideStopButton();
});
});
