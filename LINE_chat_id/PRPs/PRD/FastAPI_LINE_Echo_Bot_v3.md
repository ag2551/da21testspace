# Product Requirement Document (PRD)
## FastAPI LINE Echo Bot with SDK v3

**Version**: 1.0
**Date**: 2026-01-16
**Author**: System Generated from INITIAL.md

---

## 1. Executive Summary

### 1.1 Feature Overview
Create a high-performance LINE chatbot using FastAPI that echoes (repeats) any text message sent by users. This bot serves as a foundation for understanding the LINE Bot SDK v3 integration with FastAPI's async patterns.

### 1.2 Business Value
- Demonstrates proper async webhook handling with FastAPI
- Provides a working reference implementation for LINE Bot SDK v3
- Establishes a foundation for more complex chatbot features
- Validates the complete LINE webhook integration pipeline

---

## 2. User Stories

### 2.1 Primary User Story
**As a** LINE user
**I want to** send a text message to the bot
**So that** I can receive the same message back as a reply

**Acceptance Criteria**:
- User sends "Hello" to the bot
- Bot replies with "Hello" immediately
- Response time is under 2 seconds
- Works for any text message (up to LINE's message length limit)

### 2.2 Developer User Story
**As a** developer
**I want to** run the bot locally with ngrok tunneling
**So that** I can test LINE webhook integration without deploying to production

**Acceptance Criteria**:
- Bot runs on port 5000 (matching ngrok tunnel)
- Environment variables are loaded from `.env` file
- Invalid webhook signatures are rejected with HTTP 400
- Application can be restarted with `--reload` flag for development

### 2.3 Operations User Story
**As an** operations engineer
**I want to** see clear error messages when something fails
**So that** I can quickly diagnose and fix issues

**Acceptance Criteria**:
- Invalid signatures return HTTP 400 with clear error
- Missing environment variables cause startup failure with helpful message
- Webhook events are processed reliably
- Application logs show incoming requests and responses

---

## 3. Technical Requirements

### 3.1 Technology Stack
| Component | Technology | Version |
|-----------|------------|---------|
| Framework | FastAPI | Latest |
| Server | Uvicorn | Latest |
| SDK | line-bot-sdk | Latest (v3+) |
| Python | Python 3 | ≥ 3.10 |
| Environment | WSL/Linux | - |

### 3.2 Dependencies
```
fastapi
uvicorn
line-bot-sdk
python-dotenv
```

### 3.3 Architecture Components

#### 3.3.1 Configuration Layer
- **Purpose**: Load and validate environment variables
- **Implementation**: Use `python-dotenv` to load `.env` file
- **Required Variables**:
  - `LINE_CHANNEL_ACCESS_TOKEN` (from LINE Developers Console)
  - `LINE_CHANNEL_SECRET` (from LINE Developers Console)
- **Validation**: Exit with error message if variables are missing

#### 3.3.2 LINE SDK Initialization
- **Configuration Object**: `Configuration(access_token=<token>)`
- **API Client**: `AsyncApiClient(configuration)` for async operations
- **Messaging API**: `AsyncMessagingApi(async_api_client)` for sending messages
- **Webhook Parser**: `WebhookParser(channel_secret)` for signature validation

#### 3.3.3 FastAPI Application
- **App Instance**: `app = FastAPI()`
- **Host**: `0.0.0.0` (accept connections from ngrok)
- **Port**: `5000` (must match ngrok tunnel configuration)
- **Reload**: Enabled for development

#### 3.3.4 Webhook Endpoint
- **Route**: `POST /callback`
- **Purpose**: Receive webhook events from LINE Platform
- **Handler Signature**: `async def callback(request: Request)`

---

## 4. Technical Implementation Plan

### 4.1 File Structure
```
/home/arexsguo/LINEchatbox/
├── .env                    # Environment variables (already exists)
├── main.py                 # Application entry point (to be created)
├── requirements.txt        # Python dependencies (to be created)
└── PRPs/
    └── PRD/
        ├── INITIAL.md      # Original requirements
        └── FastAPI_LINE_Echo_Bot_v3.md  # This document
```

### 4.2 Files to Create

#### 4.2.1 `requirements.txt`
```txt
fastapi
uvicorn[standard]
line-bot-sdk
python-dotenv
```

#### 4.2.2 `main.py`
**Structure**:
```python
# 1. Imports (linebot.v3 modules)
# 2. Load environment variables from .env
# 3. Validate required environment variables exist
# 4. Initialize LINE SDK components (Configuration, AsyncApiClient, AsyncMessagingApi, WebhookParser)
# 5. Create FastAPI app instance
# 6. Define POST /callback endpoint
# 7. Add uvicorn runner (if __name__ == "__main__")
```

**Key Implementation Details**:

##### Imports
```python
import os
import sys
from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv

from linebot.v3.webhook import WebhookParser
from linebot.v3.messaging import (
    AsyncApiClient,
    AsyncMessagingApi,
    Configuration,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent
```

##### Environment Variable Loading
```python
load_dotenv()

channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
channel_secret = os.getenv('LINE_CHANNEL_SECRET')

if not channel_access_token or not channel_secret:
    print("ERROR: LINE_CHANNEL_ACCESS_TOKEN and LINE_CHANNEL_SECRET must be set")
    sys.exit(1)
```

##### SDK Initialization (Module Level)
```python
configuration = Configuration(access_token=channel_access_token)
async_api_client = AsyncApiClient(configuration)
line_bot_api = AsyncMessagingApi(async_api_client)
parser = WebhookParser(channel_secret)

app = FastAPI()
```

##### Webhook Endpoint Implementation
```python
@app.post("/callback")
async def callback(request: Request):
    # 1. Extract signature header
    signature = request.headers['X-Line-Signature']

    # 2. Get request body and decode
    body = await request.body()
    body = body.decode()

    # 3. Parse and validate webhook
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # 4. Process events
    for event in events:
        if isinstance(event, MessageEvent) and isinstance(event.message, TextMessageContent):
            # Echo the text back
            await line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=event.message.text)]
                )
            )

    return "OK"
```

##### Server Runner (Optional)
```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
```

### 4.3 API Endpoints

#### 4.3.1 POST /callback
**Purpose**: Receive LINE webhook events

**Request Headers**:
- `X-Line-Signature`: HMAC-SHA256 signature of request body
- `Content-Type`: application/json

**Request Body**:
```json
{
  "destination": "U1234567890abcdef1234567890abcdef",
  "events": [
    {
      "type": "message",
      "message": {
        "type": "text",
        "id": "1234567890",
        "text": "Hello"
      },
      "timestamp": 1234567890123,
      "source": {
        "type": "user",
        "userId": "U1234567890abcdef1234567890abcdef"
      },
      "replyToken": "abcdefghijklmnopqrstuvwxyz123456"
    }
  ]
}
```

**Response**:
- **Success**: HTTP 200, body: "OK"
- **Invalid Signature**: HTTP 400, body: {"detail": "Invalid signature"}

**Processing Logic**:
1. Extract `X-Line-Signature` header
2. Read request body as bytes and decode to string
3. Use `WebhookParser` to parse and validate
4. Iterate through events array
5. Filter for `MessageEvent` with `TextMessageContent`
6. Extract `reply_token` and `event.message.text`
7. Call `line_bot_api.reply_message()` with echo message
8. Return "OK" string

### 4.4 Security Considerations

#### 4.4.1 Signature Validation
- **Purpose**: Ensure requests originate from LINE Platform
- **Method**: HMAC-SHA256 signature validation via WebhookParser
- **Implementation**: Automatic via `parser.parse(body, signature)`
- **Failure Handling**: Raise HTTPException with 400 status code

#### 4.4.2 Environment Variable Protection
- **Storage**: `.env` file (excluded from version control)
- **Loading**: python-dotenv at application startup
- **Validation**: Exit immediately if required variables are missing

#### 4.4.3 Best Practices
- Never log or expose `LINE_CHANNEL_SECRET` or `LINE_CHANNEL_ACCESS_TOKEN`
- Validate all incoming webhook signatures before processing
- Use HTTPS in production (ngrok provides this for local development)

---

## 5. Data Flow

### 5.1 Echo Message Flow
```
1. User sends message via LINE app
   ↓
2. LINE Platform receives message
   ↓
3. LINE Platform generates webhook event
   ↓
4. LINE Platform signs request with channel secret
   ↓
5. LINE Platform sends POST request to https://your-ngrok-url/callback
   ↓
6. FastAPI receives request at /callback endpoint
   ↓
7. Extract X-Line-Signature header and request body
   ↓
8. WebhookParser validates signature
   ↓ (if valid)
9. Parse events from webhook payload
   ↓
10. Filter for MessageEvent with TextMessageContent
    ↓
11. Extract user's text and reply_token
    ↓
12. Call AsyncMessagingApi.reply_message() with echo text
    ↓
13. LINE Platform receives reply request
    ↓
14. LINE Platform sends echoed message to user
    ↓
15. User receives echoed message in LINE app
```

### 5.2 Error Handling Flow
```
Invalid Signature:
  WebhookParser raises InvalidSignatureError
  ↓
  FastAPI catches exception
  ↓
  Return HTTP 400 with error message

Missing Environment Variables:
  Application checks at startup
  ↓
  Print error message
  ↓
  Exit with sys.exit(1)

Non-text Messages (stickers, images, etc.):
  Event type check fails
  ↓
  Skip processing for this event
  ↓
  Continue to next event
```

---

## 6. Testing & Verification Plan

### 6.1 Pre-deployment Setup

#### 6.1.1 Install Dependencies
```bash
cd /home/arexsguo/LINEchatbox
pip install -r requirements.txt
```

#### 6.1.2 Verify Environment Variables
```bash
cat .env
# Should show:
# LINE_CHANNEL_ACCESS_TOKEN=<token>
# LINE_CHANNEL_SECRET=<secret>
```

#### 6.1.3 Start Ngrok Tunnel
```bash
ngrok http 5000
# Note the https URL (e.g., https://abc123.ngrok.io)
```

#### 6.1.4 Configure LINE Webhook URL
1. Go to LINE Developers Console: https://developers.line.biz/console/
2. Select your channel
3. Go to "Messaging API" tab
4. Set Webhook URL: `https://your-ngrok-url/callback`
5. Enable "Use webhook"
6. Click "Verify" to test connection

### 6.2 Manual Testing

#### Test Case 1: Basic Echo
**Steps**:
1. Start application: `uvicorn main:app --host 0.0.0.0 --port 5000 --reload`
2. Add bot as friend on LINE app
3. Send message: "Hello World"
4. **Expected**: Bot replies with "Hello World"

#### Test Case 2: Special Characters
**Steps**:
1. Send message: "Hello 🎉 Test 123 @#$"
2. **Expected**: Bot replies with "Hello 🎉 Test 123 @#$"

#### Test Case 3: Long Message
**Steps**:
1. Send a message with 500+ characters
2. **Expected**: Bot replies with the exact same long message

#### Test Case 4: Invalid Signature
**Steps**:
1. Use curl to send request with wrong signature:
```bash
curl -X POST http://localhost:5000/callback \
  -H "X-Line-Signature: invalid" \
  -H "Content-Type: application/json" \
  -d '{"events":[]}'
```
2. **Expected**: HTTP 400 response

#### Test Case 5: Non-text Messages
**Steps**:
1. Send a sticker to the bot
2. **Expected**: No response (bot ignores non-text messages)

#### Test Case 6: Multiple Messages
**Steps**:
1. Send "Test 1"
2. Send "Test 2"
3. Send "Test 3"
4. **Expected**: Bot replies to each message in order

### 6.3 Verification Checklist

- [ ] Application starts without errors
- [ ] Application binds to port 5000
- [ ] Ngrok tunnel is active and accessible
- [ ] LINE webhook URL is configured and verified
- [ ] Environment variables are loaded correctly
- [ ] Bot responds to text messages with exact echo
- [ ] Bot handles special characters correctly
- [ ] Invalid signatures are rejected (HTTP 400)
- [ ] Non-text messages are ignored gracefully
- [ ] Multiple rapid messages are all processed
- [ ] Application logs show incoming webhooks
- [ ] Application can be stopped and restarted (--reload works)

### 6.4 Performance Criteria

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Response Time | < 2 seconds | User perception in LINE app |
| Webhook Processing | < 500ms | Server logs |
| Memory Usage | < 100MB | `ps aux` or `top` command |
| Startup Time | < 5 seconds | Time from `uvicorn` start to ready |

---

## 7. Known Limitations

### 7.1 Functional Limitations
- Only echoes text messages (ignores stickers, images, videos, etc.)
- No conversation history or context
- No user state management
- No rate limiting implementation
- Single-threaded processing (though async)

### 7.2 Technical Constraints
- Requires active ngrok tunnel for local development
- Port 5000 must be available
- Depends on LINE Platform availability
- No built-in monitoring or alerting

### 7.3 Security Considerations
- `.env` file must never be committed to version control
- Ngrok tunnel URL changes on restart (free tier)
- No authentication beyond webhook signature validation
- No DoS protection

---

## 8. Future Enhancements

### 8.1 Phase 2 Features
- Support for rich messages (flex messages, template messages)
- Handle stickers, images, and other media types
- Add message logging to database
- Implement user session management
- Add rate limiting

### 8.2 Phase 3 Features
- Natural language processing integration
- Multi-user conversation support
- Admin dashboard for monitoring
- Automated testing suite
- Docker containerization

### 8.3 Production Readiness
- Deploy to cloud platform (AWS, GCP, Azure)
- Add structured logging
- Implement health check endpoint
- Set up monitoring and alerting
- Add CI/CD pipeline

---

## 9. Dependencies & Prerequisites

### 9.1 External Services
- **LINE Developers Account**: Required for channel credentials
- **LINE Messaging API Channel**: Must be created in LINE Developers Console
- **Ngrok Account**: For local webhook testing (free tier sufficient)

### 9.2 Development Environment
- Python 3.10 or higher installed
- pip package manager
- WSL/Linux environment
- Internet connectivity
- LINE mobile app for testing

### 9.3 Configuration Required
- LINE channel access token (long-lived)
- LINE channel secret
- Ngrok authentication token (optional but recommended)

---

## 10. Success Metrics

### 10.1 Technical Success Metrics
- Application starts without errors: 100%
- Webhook signature validation: 100% accuracy
- Echo accuracy: 100% (exact text match)
- Uptime during development: > 95%

### 10.2 User Experience Metrics
- Response time: < 2 seconds per message
- Message delivery rate: > 99%
- Error rate: < 1%

### 10.3 Development Metrics
- Time to first successful echo: < 30 minutes
- Code readability: Pass review
- Documentation completeness: 100%

---

## 11. Appendix

### 11.1 LINE Bot SDK v3 Key Differences from v2
- Use `linebot.v3` imports instead of `linebot`
- Use `AsyncApiClient` and `AsyncMessagingApi` for async operations
- Use `WebhookParser` instead of `WebhookHandler` for FastAPI
- Configuration object takes only `access_token` parameter
- Event classes are in `linebot.v3.webhooks` module

### 11.2 Reference Links
- LINE Bot SDK Python: https://github.com/line/line-bot-sdk-python
- FastAPI Documentation: https://fastapi.tiangolo.com/
- LINE Developers Console: https://developers.line.biz/console/
- Ngrok Documentation: https://ngrok.com/docs

### 11.3 Troubleshooting

#### Problem: "Invalid signature" errors
**Solution**: Verify channel secret is correct in `.env` file

#### Problem: Bot doesn't respond
**Solutions**:
- Check ngrok tunnel is active
- Verify webhook URL in LINE Console
- Check application is running on port 5000
- Review application logs for errors

#### Problem: "Port already in use"
**Solution**: Kill existing process on port 5000
```bash
lsof -ti:5000 | xargs kill -9
```

#### Problem: Environment variables not loaded
**Solution**: Ensure `.env` file is in the same directory as `main.py`

---

**End of Document**
