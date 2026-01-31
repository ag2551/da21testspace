# LINE Messaging Platform - AI Chatbot + Management API

A comprehensive LINE messaging platform built with FastAPI that combines two powerful features:
1. **AI-Powered Chatbot** - Intelligent conversational bot using Google ADK (Gemini 2.5 Flash) with Google Search
2. **Messaging Management API** - Full CRUD REST API for managing LINE push messages with native SQLite

## Key Features

### AI Chatbot
- **Intelligent Conversations**: Google ADK with Gemini 2.5 Flash for context-aware responses
- **Real-time Search**: Integrated Google Search for up-to-date information
- **Auto User Management**: Captures and stores user profiles automatically
- **Secure Webhook**: LINE signature validation for security

### Messaging Management API
- **CRUD Operations**: Create, Read, Update, Delete LINE push messages
- **Native SQLite**: High-performance database with raw SQL (no ORM overhead)
- **LINE API Integration**: Direct LINE Messaging API interaction
- **Status Tracking**: Monitor message lifecycle (draft, published, failed, deleted)
- **Multi-credential Support**: Manage multiple LINE channels

## Technology Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Framework | FastAPI | Latest | Async web framework |
| Server | Uvicorn | Latest | ASGI server |
| SDK | line-bot-sdk | v3+ | LINE Bot API |
| AI Agent | Google ADK | Latest | Conversational AI |
| AI Model | Gemini 2.5 Flash | Latest | Language model |
| Database | SQLite | 3.x | Data persistence |
| DB Driver | aiosqlite | ≥0.19.0 | Async SQLite |
| HTTP Client | httpx | ≥0.24.0 | Async HTTP requests |
| Validation | Pydantic | v2 | Schema validation |
| Python | Python 3 | ≥3.10 | Runtime |

## Architecture

### Database Layer
- **Native SQLite** with `aiosqlite` driver (NO ORM)
- Raw SQL queries with parameterized statements for security
- `aiosqlite.Row` as row_factory for dict-like access
- Connection management via FastAPI dependency injection

### Service Layer
- **LineAdapter**: Handles LINE Messaging API interactions
- **Google ADK Runner**: Manages AI agent execution
- Async/await pattern throughout for performance

### API Layer
- **Webhook Endpoint** (`/callback`): Receives LINE events, processes with AI
- **Management API** (`/api/*`): RESTful CRUD operations for messages
- Automatic user profile capture and database persistence

## Prerequisites

Before you begin, ensure you have:

- **Python 3.10+** and pip installed
- **LINE Developers Account** - [Sign up here](https://developers.line.biz/)
- **Google API Key** - [Get from AI Studio](https://aistudio.google.com/apikey)
- **ngrok** (for local development) - [Download here](https://ngrok.com/)
- LINE mobile app (for testing)

## Setup Instructions

### 1. LINE Bot Setup

1. Create a LINE Developers account at https://developers.line.biz/
2. Create a new Messaging API channel
3. Get your credentials:
   - Channel Access Token (Long-lived)
   - Channel Secret
4. Keep these credentials handy for the next step

### 2. Google API Setup

1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Sign in with your Google account
3. Click **"Get API Key"** or **"Create API Key"**
4. Copy the generated API key
5. Keep this API key secure - you'll need it for the `.env` file

**Note**: The Google ADK with Gemini models and Google Search tool requires a valid Google API key. The free tier provides generous usage limits suitable for development and testing.

## Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd /home/arexsguo/LINEchatbox
   ```

2. **Create and activate a virtual environment** (recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Linux/WSL
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

The project uses a `.env` file for storing sensitive credentials.

1. **Create a `.env` file** in the project root with the following variables:
   ```env
   # LINE Bot Credentials
   LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token_here
   LINE_CHANNEL_SECRET=your_channel_secret_here
   
   # Google API Credentials
   GOOGLE_API_KEY=your_google_api_key_here
   
   # Optional: Specify ADK model (default: gemini-2.5-flash)
   ADK_MODEL=gemini-2.5-flash
   ```

2. **Replace the placeholder values** with your actual credentials:
   - `LINE_CHANNEL_ACCESS_TOKEN`: From LINE Developers Console
   - `LINE_CHANNEL_SECRET`: From LINE Developers Console
   - `GOOGLE_API_KEY`: From Google AI Studio

3. **Important**: Never commit the `.env` file to version control! (It's already in `.gitignore`)

## Running the Application

### Step 1: Start the FastAPI Server

Run the application using one of these methods:

**Method 1: Using uvicorn directly (Recommended)**
```bash
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

**Method 2: Using the Python script**
```bash
python3 main.py
```

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:5000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Note**: The application uses FastAPI's lifespan events to properly initialize async clients when the event loop is running. Both methods work correctly.

### Step 2: Setup ngrok Tunnel

In a **new terminal window**, start ngrok:

```bash
ngrok http 5000
```

You'll see output with your public URL:
```
Forwarding    https://abc123.ngrok.io -> http://localhost:5000
```

**Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`)

### Step 3: Configure LINE Webhook

1. Go to [LINE Developers Console](https://developers.line.biz/console/)
2. Select your Messaging API channel
3. Go to the "Messaging API" tab
4. Find the "Webhook settings" section
5. Set **Webhook URL**: `https://your-ngrok-url/callback`
   - Example: `https://abc123.ngrok.io/callback`
6. Click **Update**
7. Click **Verify** to test the connection (should show success)
8. Enable **Use webhook** toggle

### Step 4: Test the Application

#### Test AI Chatbot

1. Find your bot's QR code or LINE ID in the Messaging API tab
2. Add the bot as a friend in your LINE mobile app
3. Send a text message to the bot
4. The bot will respond with an AI-generated answer using Google Search when needed

**Example Queries to Try**:
- "What's the weather like in Tokyo today?"
- "Who won the latest Nobel Prize?"
- "Explain quantum computing in simple terms"
- "What are the latest iPhone features?"
- "Tell me about recent AI developments"

#### Test Management API

Use curl, Postman, or any HTTP client to test the REST API:

**1. Create a credential**:
```bash
curl -X POST http://localhost:5000/api/credentials \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "line",
    "channel_access_token": "YOUR_TOKEN",
    "channel_secret": "YOUR_SECRET",
    "target_id": "LINE_USER_ID"
  }'
```

**2. Create and publish a message**:
```bash
curl -X POST http://localhost:5000/api/posts \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "line",
    "content": "Hello from the API!",
    "credential_id": 1,
    "target_id": "LINE_USER_ID"
  }'
```

**3. List all posts**:
```bash
curl http://localhost:5000/api/posts?limit=10&status=published
```

**4. Get specific post**:
```bash
curl http://localhost:5000/api/posts/1
```

**5. Update a post (sends new message)**:
```bash
curl -X PUT http://localhost:5000/api/posts/1 \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Updated message content"
  }'
```

**6. Delete a post (soft delete)**:
```bash
curl -X DELETE http://localhost:5000/api/posts/1
```

---

## Interactive API Documentation

FastAPI provides automatic interactive API documentation:

- **Swagger UI**: http://localhost:5000/docs
- **ReDoc**: http://localhost:5000/redoc

These interfaces allow you to:
- View all endpoints and their parameters
- Test API calls directly from the browser
- See request/response schemas
- Download OpenAPI spec

---

## Project Structure

```
LINE_chat_id/
├── .env                        # Environment variables (DO NOT COMMIT)
├── .env.example               # Environment template
├── main.py                     # FastAPI app entry point + webhook handler
├── agent_config.py             # Google ADK agent configuration
├── requirements.txt            # Python dependencies
├── line_bot.db                # SQLite database (auto-created)
├── README.md                  # This file
├── CLAUDE.md                  # Project context and coding guidelines
├── DATABASE_QUICKSTART.md     # Database setup guide
├── app/
│   ├── __init__.py
│   ├── database.py            # Database initialization (native SQL)
│   ├── schemas.py             # Pydantic models for validation
│   ├── line_adapter.py        # LINE API service layer
│   └── routes/
│       ├── __init__.py
│       └── social_posts.py    # CRUD API endpoints
└── PRPs/                      # Project Requirements & Plans
    └── PRD/
        ├── INITIAL.md
        └── FastAPI_LINE_Echo_Bot_v3.md
```

## How It Works

### AI Chatbot Flow
1. **Startup**: FastAPI lifespan initializes database, LINE API clients, and Google ADK runner
2. User sends message in LINE app
3. LINE Platform sends webhook POST to `/callback`
4. Application validates signature and parses event
5. **User Management**: 
   - New users: Fetch profile from LINE API, store in database
   - Existing users: Update profile and timestamp
6. **AI Processing**:
   - Send user message to Google ADK agent
   - Agent uses Google Search if needed for current information
   - Generate contextual, intelligent response
7. Reply to user via LINE Messaging API
8. **Shutdown**: Gracefully close async clients

### API Management Flow
1. **Create**: `POST /api/posts` → Push message via LINE API → Store message_id
2. **Read**: `GET /api/posts/{id}` → Return from database (no LINE API call)
3. **Update**: `PUT /api/posts/{id}` → Send new message → Update database (original stays visible)
4. **Delete**: `DELETE /api/posts/{id}` → Soft delete in database (message stays visible in LINE)

## Database Schema

### Tables

**users** - User profiles captured from LINE
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    line_user_id TEXT UNIQUE NOT NULL,
    display_name TEXT,
    picture_url TEXT,
    status_message TEXT,
    language TEXT DEFAULT 'zh-TW',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**social_credentials** - LINE channel credentials
```sql
CREATE TABLE social_credentials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT DEFAULT 'line',
    channel_access_token TEXT NOT NULL,
    channel_secret TEXT,
    target_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**social_posts** - Published LINE messages
```sql
CREATE TABLE social_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT DEFAULT 'line',
    content TEXT NOT NULL,
    credential_id INTEGER NOT NULL,
    line_message_id TEXT,
    line_published_at TIMESTAMP,
    line_status TEXT DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (credential_id) REFERENCES social_credentials (id)
)
```

## API Endpoints

### Webhook Endpoint

#### `POST /callback`
**Purpose**: Receive LINE webhook events (chatbot functionality)

**Headers**:
- `X-Line-Signature`: HMAC-SHA256 signature (from LINE)
- `Content-Type`: application/json

**Response**:
- `200 OK`: Event processed successfully
- `400 Bad Request`: Invalid signature

**Features**:
- Validates webhook signature
- Captures and stores user profiles
- Generates AI responses using Google ADK
- Replies to users automatically

---

### Management API Endpoints

#### `POST /api/credentials`
**Purpose**: Create new LINE channel credential

**Request Body**:
```json
{
  "platform": "line",
  "channel_access_token": "your_channel_access_token",
  "channel_secret": "your_channel_secret",
  "target_id": "LINE_USER_ID"
}
```

**Response**: `201 Created` with credential object

---

#### `GET /api/credentials/{credential_id}`
**Purpose**: Retrieve specific credential

**Response**: `200 OK` with credential details

---

#### `POST /api/posts`
**Purpose**: Create and publish LINE push message

**Request Body**:
```json
{
  "platform": "line",
  "content": "Your message text",
  "credential_id": 1,
  "target_id": "LINE_USER_ID"
}
```

**Flow**:
1. Insert post as 'draft' status
2. Call LINE API `/v2/bot/message/push`
3. Update with `message_id` and 'published' status

**Response**: `201 Created` with post object

**Errors**:
- `404`: Credential not found
- `500`: LINE API error (invalid token, user blocked bot, etc.)

---

#### `GET /api/posts/{post_id}`
**Purpose**: Read single post from database

**Response**: `200 OK` with post details  
**Note**: No LINE API call - returns database record only

---

#### `GET /api/posts?skip=0&limit=20&status=published`
**Purpose**: List posts with pagination and filtering

**Query Parameters**:
- `skip`: Offset for pagination (default: 0)
- `limit`: Max results per page (default: 20, max: 100)
- `status`: Filter by status (draft, published, failed, deleted, updated)

**Response**: `200 OK` with array of posts

---

#### `PUT /api/posts/{post_id}`
**Purpose**: Update post by sending new LINE message

**Request Body**:
```json
{
  "content": "Updated message text"
}
```

**⚠️ LINE API Limitation**: Original message remains visible in LINE app.  
This endpoint sends a **new message** with updated content.

**Flow**:
1. Retrieve existing post data
2. Call LINE API to push new message
3. Update database with new `message_id` and timestamp

**Response**: `200 OK` with updated post object

---

#### `DELETE /api/posts/{post_id}`
**Purpose**: Soft delete post in database

**⚠️ LINE API Limitation**: Message remains visible in LINE app.  
LINE Messaging API does **not** support deleting bot messages (verified across all 68 MessagingApi methods).

**Implementation**: Marks post as 'deleted' status in database only.

**Response**: `200 OK` with:
```json
{
  "success": true,
  "message": "Post marked as deleted in database",
  "note": "Message remains visible in LINE. LINE Messaging API does not support deleting bot messages.",
  "post_id": 1
}
```

---

## LINE API Limitations

### Important Constraints

1. **No Delete/Unsend for Bot Messages**
   - Verified: All 68 methods in `MessagingApi` checked
   - User-sent messages: Cannot be deleted by bot
   - Bot-sent messages: No unsend endpoint exists
   - Workaround: Soft delete in database, send follow-up message if needed

2. **No Edit Message**
   - Messages cannot be modified after sending
   - Workaround: Send new message with updated content

3. **Message Permanence**
   - All sent messages remain visible in chat history
   - Users can delete messages manually on their device
   - Bot has no control over message visibility

### Implementation Strategy

Given these limitations, the API provides:
- **Clear error messages** explaining API constraints
- **Database status tracking** for message lifecycle
- **Soft delete** to mark messages as deleted in your system
- **New message on update** with database record of changes

---

## Troubleshooting

### Bot doesn't respond to messages

**Check these items**:
- [ ] FastAPI server is running (check terminal)
- [ ] ngrok tunnel is active (check ngrok terminal)
- [ ] Webhook URL is correct in LINE Console
- [ ] Webhook is enabled in LINE Console
- [ ] Webhook verification passed
- [ ] Bot is added as a friend in LINE app

**View logs**: Check the FastAPI terminal for incoming requests and errors

### "Invalid signature" error

**Solution**: Verify that `LINE_CHANNEL_SECRET` in `.env` matches the one in LINE Developers Console

### "Port already in use" error

**Solution**: Kill the process using port 5000
```bash
lsof -ti:5000 | xargs kill -9
```

### Environment variables not loading

**Solution**: Ensure `.env` file is in the same directory as `main.py`

### Google API errors or "Invalid API key"

**Check these items**:
- [ ] GOOGLE_API_KEY is set correctly in `.env` file
- [ ] API key is valid and not expired (check Google AI Studio)
- [ ] API key has proper permissions enabled
- [ ] You haven't exceeded Google API free tier limits

**Solution**: Generate a new API key from [Google AI Studio](https://aistudio.google.com/apikey) if needed

### Bot responds with "Sorry, I encountered an error"

**Possible causes**:
- Google API rate limits exceeded
- Network connectivity issues
- Invalid model name in ADK_MODEL
- Google Search tool temporarily unavailable

**Solution**: Check the FastAPI terminal logs for detailed error messages

### "RuntimeError: no running event loop" error

**Cause**: This occurred in older versions where AsyncApiClient was initialized at module level

**Solution**: The current code uses FastAPI's lifespan events to initialize async clients properly. Make sure you're using the latest version of `main.py` with the `@asynccontextmanager` lifespan function

### ngrok URL changes

**Note**: Free ngrok URLs change every time you restart ngrok. You'll need to:
1. Update the webhook URL in LINE Console
2. Verify the webhook again

**Solution for stable URL**: Get a paid ngrok plan or deploy to a cloud platform

## Development

### Reload on Changes

The `--reload` flag automatically restarts the server when you modify `main.py`:
```bash
uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

### Code Structure

The application follows this flow:
1. Load environment variables with `python-dotenv`
2. Initialize Configuration and WebhookParser (synchronous components)
3. Create FastAPI app instance with lifespan context manager
4. **Lifespan startup**: Initialize AsyncApiClient and AsyncMessagingApi when event loop is ready
5. Define `/callback` endpoint with async request handler
6. Validate signatures and parse webhook events
7. Process MessageEvent with TextMessageContent
8. Reply with echoed text using AsyncMessagingApi
9. **Lifespan shutdown**: Close async client gracefully when app stops

## Security Considerations

### Implemented Security Measures
- **Webhook signature validation** on every LINE callback request
- **SQL injection prevention** via parameterized queries (never string concatenation)
- **Environment variable isolation** for credentials (`.env` never committed)
- **HTTPS enforcement** in production (ngrok provides this for local dev)
- **Token-based authentication** for LINE API calls
- **Input validation** via Pydantic schemas
- **Error message sanitization** to avoid leaking sensitive data

### Production Security Checklist
- [ ] Use HTTPS for all endpoints
- [ ] Implement rate limiting (consider using `slowapi`)
- [ ] Add API key authentication for management endpoints
- [ ] Enable CORS only for trusted origins
- [ ] Rotate LINE channel access tokens periodically
- [ ] Monitor and log suspicious activity
- [ ] Use secrets manager (AWS Secrets Manager, Azure Key Vault, etc.)
- [ ] Implement request size limits
- [ ] Add input sanitization for user-generated content
- [ ] Regular security audits and dependency updates

---

## Known Limitations

### Chatbot Limitations
- **Text-only processing**: Ignores stickers, images, videos, audio, and other media types
- **No conversation memory**: Each query is independent (no context between messages)
- **No user state**: No personalization based on conversation history
- **Response latency**: Depends on Google Search queries (typically 2-5 seconds)
- **API rate limits**: Google API free tier has usage limits (check Google AI Studio)

### LINE API Platform Limitations
- **No message delete**: LINE Messaging API does not support deleting/unsending bot messages
- **No message edit**: Cannot modify messages after sending (must send new message)
- **Message permanence**: All sent messages remain visible in chat history
- **No read receipts**: Bot cannot detect if user read the message
- **Push message limits**: LINE enforces rate limits on push messages

### Development Limitations
- **ngrok URL changes**: Free tier URL changes on restart (requires webhook URL update)
- **No authentication**: Management API endpoints lack auth (add before production)
- **No rate limiting**: Consider adding for production use
- **Single database**: SQLite not ideal for high-concurrency production workloads

---

## Next Steps

### Chatbot Enhancements
- **Conversation history**: Implement session management with context retention
- **Multi-modal support**: Handle images, stickers, location, and other LINE content types
- **Flex messages**: Use LINE's rich message format for interactive UI
- **Quick reply buttons**: Add structured response options
- **Rich menus**: Implement persistent menu at bottom of chat
- **Broadcast messages**: Send bulk messages to all users
- **User analytics**: Track engagement metrics and popular queries

### API Enhancements
- **Authentication**: Add API key or JWT authentication for endpoints
- **Rate limiting**: Implement request throttling (`slowapi`)
- **Pagination metadata**: Return total count and page info
- **Bulk operations**: Batch create/update/delete endpoints
- **Message templates**: Store and reuse message templates
- **Scheduled messages**: Queue messages for future delivery
- **Webhook notifications**: Notify external systems on message events
- **Message analytics**: Track delivery status and engagement

### Infrastructure Enhancements
- **Production deployment**: Deploy to AWS/GCP/Azure with auto-scaling
- **Database migration**: Move to PostgreSQL or MySQL for production
- **Caching layer**: Add Redis for frequent queries and rate limiting
- **Message queue**: Use Celery/RabbitMQ for async message processing
- **Monitoring**: Integrate with DataDog, New Relic, or Prometheus
- **Logging**: Structured logging with ELK stack
- **CI/CD pipeline**: Automated testing and deployment
- **Docker containerization**: Package app with Docker for easy deployment
- **Load balancing**: Handle high traffic with multiple instances

### AI/ML Enhancements
- **Custom tools**: Add specialized ADK tools (calculator, weather API, database queries)
- **Multi-agent system**: Route queries to specialized agents by topic
- **Sentiment analysis**: Analyze user sentiment and adjust responses
- **Language detection**: Auto-detect and respond in user's language
- **Named entity recognition**: Extract and act on entities (dates, names, places)
- **User preferences**: Personalize responses based on user history and preferences

---

## References

### LINE Platform
- [LINE Developers Console](https://developers.line.biz/console/)
- [LINE Messaging API Documentation](https://developers.line.biz/en/docs/messaging-api/)
- [LINE Bot SDK Python (v3)](https://github.com/line/line-bot-sdk-python)
- [LINE Developers Support](https://developers.line.biz/en/support/)

### Google AI
- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [Google ADK Python GitHub](https://github.com/google/adk-python)
- [Google AI Studio](https://aistudio.google.com/)
- [Gemini API Documentation](https://ai.google.dev/docs)

### FastAPI & Python
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
- [Pydantic V2 Documentation](https://docs.pydantic.dev/)
- [aiosqlite Documentation](https://aiosqlite.omnilib.dev/)
- [httpx Documentation](https://www.python-httpx.org/)

### Development Tools
- [ngrok Documentation](https://ngrok.com/docs)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

---

## FAQ

### Q: Can the bot remember previous conversations?
**A**: Currently no. Each message is processed independently. To add conversation memory, you'd need to implement session management and pass conversation history to the AI agent.

### Q: Why can't I delete messages sent by the bot?
**A**: This is a LINE Messaging API limitation. The platform does not provide any endpoint to delete or unsend bot messages. Once sent, messages are permanent in the user's chat history.

### Q: How do I get a LINE User ID for push messages?
**A**: When a user messages your bot, their User ID is captured in the webhook event (`event.source.user_id`). It's automatically stored in the `users` table. You can also find it in the LINE Developers Console webhook logs.

### Q: What's the difference between reply and push messages?
**A**: 
- **Reply**: Free, must use `reply_token` from webhook event, works within webhook handler
- **Push**: Counted towards quota, requires User ID, can be sent anytime via API

### Q: Can I send messages to users who haven't added the bot?
**A**: No. Users must add your bot as a friend before you can send them messages (either reply or push).

### Q: How many free push messages can I send?
**A**: LINE provides a monthly free quota. Check your LINE Developers Console for current limits. Limits vary by account type and region.

### Q: Can I use this in production?
**A**: The code is production-ready with proper async handling, error management, and security. However, you should:
- Add authentication to API endpoints
- Implement rate limiting
- Use a production ASGI server configuration
- Consider migrating to PostgreSQL for high traffic
- Set up proper monitoring and logging
- Use a stable domain instead of ngrok

### Q: How do I handle images and files?
**A**: The current implementation only processes text. To handle media:
1. Check event type: `ImageMessageContent`, `VideoMessageContent`, etc.
2. Download media from LINE using `get_message_content()`
3. Process the media (store, analyze, etc.)
4. Send appropriate response

---

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow the coding conventions in `CLAUDE.md`
4. Write tests for new features
5. Commit with clear messages
6. Push to your branch
7. Open a Pull Request

---

## License

This project is provided as-is for educational and development purposes. Feel free to use, modify, and distribute according to your needs.

---

## Support

### Getting Help

For issues related to:

**LINE Platform**
- [LINE Developers Documentation](https://developers.line.biz/en/docs/)
- [LINE Bot SDK Issues](https://github.com/line/line-bot-sdk-python/issues)
- [LINE Developers Community](https://www.line-community.me/)

**Google AI**
- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [Google AI Forum](https://discuss.ai.google.dev/)

**FastAPI**
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [FastAPI GitHub Discussions](https://github.com/tiangolo/fastapi/discussions)

**This Project**
- Check the [Troubleshooting](#troubleshooting) section
- Review `CLAUDE.md` for coding guidelines
- Check `DATABASE_QUICKSTART.md` for database help

---

## Changelog

### Current Version (2026-02-01)
- ✅ AI-powered chatbot with Google ADK (Gemini 2.5 Flash)
- ✅ Google Search integration for real-time information
- ✅ Automatic user profile capture and persistence
- ✅ Full CRUD API for LINE message management
- ✅ Native SQLite with aiosqlite (no ORM)
- ✅ LINE Messaging API v3 integration
- ✅ Webhook signature validation
- ✅ Async/await throughout for performance
- ✅ Interactive API documentation (Swagger UI)
- ✅ Comprehensive error handling
- ✅ Production-ready architecture

---

**Built with ❤️ using FastAPI, Google ADK, and LINE Messaging API**
