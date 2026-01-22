## FEATURE
FastAPI LINE Echo Bot (SDK v3)

## GOAL
Create a high-performance LINE Chatbot using FastAPI that simply "echoes" (repeats) whatever text message the user sends.

## CONTEXT & DEPENDENCIES
- **Framework**: FastAPI (standard `app = FastAPI()`)
- **Server**: Uvicorn
- **SDK**: `line-bot-sdk` (Must use v3 `AsyncMessagingApi` and `WebhookParser`)
- **Environment**: WSL / Linux
- **Port**: **5000** (Crucial: Must match the running Ngrok tunnel)

## REQUIRED FILES & CONFIG

### 1. `.env`
- Must contain:
  - `LINE_CHANNEL_ACCESS_TOKEN`
  - `LINE_CHANNEL_SECRET`

### 2. `main.py` (The Application)
- **Setup**:
  - Load environment variables.
  - Initialize `Configuration` with access token.
  - Initialize `AsyncApiClient` and `AsyncMessagingApi`.
  - Initialize `WebhookParser` with channel secret.
  
- **Route: POST /callback**
  - This is the entry point for LINE Webhook.
  - Must be defined as `async def callback(request: Request)`.
  - **Logic**:
    1. Read `X-Line-Signature` header from request.
    2. Read request body as bytes (`await request.body()`).
    3. Decode body to string (utf-8).
    4. Parse events using `parser.parse(body, signature)`.
    5. Handle `InvalidSignatureError` by raising HTTPException 400.
    6. Iterate through events and process MessageEvent with TextMessageContent.
    7. Return "OK" string.

- **Event Handling**:
  - Inside the `/callback` route, iterate through parsed events.
  - **Logic**:
    - Check if event is `isinstance(event, MessageEvent)` and message is `isinstance(event.message, TextMessageContent)`.
    - Extract `reply_token` from event and user's text from `event.message.text`.
    - Use `await line_bot_api.reply_message()` with `ReplyMessageRequest`.
    - Message should be `TextMessage(text=user_text)`.
    - Note: `line_bot_api` should be initialized at module level, not inside the handler.

- **Execution**:
  - The script should allow running via `uvicorn main:app --host 0.0.0.0 --port 5000 --reload`.

## EXAMPLES (SDK v3 Syntax for FastAPI)
- Do NOT use `LineBotApi` (deprecated).
- Do NOT use `WebhookHandler` (use `WebhookParser` for FastAPI).
- Use async imports: `from linebot.v3.messaging import AsyncApiClient, AsyncMessagingApi, Configuration`
- Use webhook parser: `from linebot.v3.webhook import WebhookParser`
- Use event types: `from linebot.v3.webhooks import MessageEvent, TextMessageContent`
- Use exceptions: `from linebot.v3.exceptions import InvalidSignatureError`