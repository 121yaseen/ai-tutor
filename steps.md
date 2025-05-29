adk web
INFO:     Started server process [64526]
INFO:     Waiting for application startup.

+-----------------------------------------------------------------------------+
| ADK Web Server started                                                      |
|                                                                             |
| For local testing, access at http://localhost:8000.                         |
+-----------------------------------------------------------------------------+

INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:63691 - "GET / HTTP/1.1" 307 Temporary Redirect
INFO:     127.0.0.1:63691 - "GET /.well-known/appspecific/com.chrome.devtools.json HTTP/1.1" 404 Not Found
INFO:     127.0.0.1:63691 - "GET /list-apps?relative_path=./ HTTP/1.1" 200 OK
2025-05-29 11:58:01,729 - INFO - fast_api.py:457 - New session created
2025-05-29 11:58:01,729 - INFO - fast_api.py:457 - New session created
INFO:     127.0.0.1:63693 - "POST /apps/ai_tutor/users/user/sessions HTTP/1.1" 200 OK
INFO:     127.0.0.1:63693 - "GET /apps/ai_tutor/eval_sets HTTP/1.1" 200 OK
INFO:     127.0.0.1:63801 - "GET /apps/ai_tutor/eval_results HTTP/1.1" 200 OK
INFO:     127.0.0.1:63801 - "GET /apps/ai_tutor/users/user/sessions HTTP/1.1" 200 OK
INFO:     127.0.0.1:63801 - "GET /apps/ai_tutor/users/user/sessions HTTP/1.1" 200 OK
INFO:     ('127.0.0.1', 63982) - "WebSocket /run_live?app_name=ai_tutor&user_id=user&session_id=184f6a01-777a-4974-b575-e79a216574b0" [accepted]
INFO:     connection open
2025-05-29 11:58:26,458 - INFO - envs.py:47 - Loaded .env file for ai_tutor at /Users/muhammedyaseen/Development/ai-tutor/adk-streaming/app/.env
2025-05-29 11:58:28,691 - INFO - live.py:1029 - b'{\n  "setupComplete": {}\n}\n'



1. fetch("http://localhost:8000/apps/ai_tutor/users/user/sessions", {
  "headers": {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
    "sec-ch-ua": "\"Chromium\";v=\"136\", \"Google Chrome\";v=\"136\", \"Not.A/Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin"
  },
  "referrer": "http://localhost:8000/dev-ui",
  "referrerPolicy": "strict-origin-when-cross-origin",
  "body": null,
  "method": "POST",
  "mode": "cors",
  "credentials": "include"
});
Response: {
    "id": "184f6a01-777a-4974-b575-e79a216574b0",
    "appName": "ai_tutor",
    "userId": "user",
    "state": {},
    "events": [],
    "lastUpdateTime": 1748500081.732051
}

2. fetch("http://localhost:8000/apps/ai_tutor/users/user/sessions", {
  "headers": {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
    "sec-ch-ua": "\"Chromium\";v=\"136\", \"Google Chrome\";v=\"136\", \"Not.A/Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin"
  },
  "referrer": "http://localhost:8000/dev-ui?app=ai_tutor",
  "referrerPolicy": "strict-origin-when-cross-origin",
  "body": null,
  "method": "GET",
  "mode": "cors",
  "credentials": "include"
});
[
    {
        "id": "184f6a01-777a-4974-b575-e79a216574b0",
        "appName": "ai_tutor",
        "userId": "user",
        "state": {},
        "events": [],
        "lastUpdateTime": 1748500081.732051
    }
]

3. fetch("ws://localhost:8000/run_live?app_name=ai_tutor&user_id=user&session_id=184f6a01-777a-4974-b575-e79a216574b0", {
  "headers": {
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "sec-websocket-extensions": "permessage-deflate; client_max_window_bits",
    "sec-websocket-key": "fw7ZrLdyD0SQXi9mf/7CDQ==",
    "sec-websocket-version": "13"
  },
  "body": null,
  "method": "GET",
  "mode": "cors",
  "credentials": "include"
});

HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: 8hBIYHWpdxTxJ5HrFXeKfaQrRwg=
Sec-WebSocket-Extensions: permessage-deflate
date: Thu, 29 May 2025 06:28:26 GMT
server: uvicorn

4. fetch("http://localhost:8000/assets/audio-processor.js", {
  "referrer": "http://localhost:8000/dev-ui?app=ai_tutor",
  "referrerPolicy": "strict-origin-when-cross-origin",
  "body": null,
  "method": "GET",
  "mode": "cors",
  "credentials": "omit"
});