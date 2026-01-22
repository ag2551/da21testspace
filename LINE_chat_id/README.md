# LINE AI Chatbot - Google ADK + FastAPI + SDK v3

A high-performance AI-powered LINE chatbot built with FastAPI and Google Agent Development Kit (ADK). This bot uses Google's Gemini AI models with Google Search capabilities to provide intelligent, up-to-date responses instead of static replies. The system transforms responses from robotic repetitions into AI-powered answers tailored to each user's questions.

## Features

- **AI-Powered Responses**: Uses Google ADK with Gemini 2.5 Flash model for intelligent conversations
- **Google Search Integration**: Automatically searches the web to provide current, accurate information
- **Source Citations**: References reliable sources when providing factual information
- **Built with FastAPI** for high performance and async support
- **LINE Bot SDK v3** (latest version) integration
- **Proper webhook signature validation** for security
- **Easy local development** with ngrok
- **Clean, maintainable code structure** with modular agent configuration

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.10 or higher
- pip (Python package manager)
- [ngrok](https://ngrok.com/) (for local webhook testing)
- LINE mobile app (for testing)
- Google Account (for Google AI Studio API key)

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

### Step 4: Test the Bot

1. Find your bot's QR code or LINE ID in the Messaging API tab
2. Add the bot as a friend in your LINE mobile app
3. Send a text message to the bot (try asking questions!)
4. The bot will respond with an AI-generated answer using Google Search when needed!

**Example Queries to Try**:
- "What's the weather like in Tokyo today?"
- "Who won the latest Nobel Prize?"
- "Explain quantum computing in simple terms"
- "What are the latest iPhone features?"
- "Tell me about recent AI developments"

## Project Structure

```
LINEchatbox/
├── .env                    # Environment variables (credentials) - DO NOT COMMIT
├── .env.example           # Example environment variables template
├── main.py                 # FastAPI application entry point
├── agent_config.py         # Google ADK agent configuration
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── PRPs/
    └── PRD/
        ├── INITIAL.md                      # Initial requirements
        └── FastAPI_LINE_Echo_Bot_v3.md    # Comprehensive PRD
```

## How It Works

1. **Startup**: FastAPI lifespan event initializes `AsyncApiClient` and `AsyncMessagingApi` when the event loop starts
2. **Google ADK Agent**: Loads configured AI agent with Google Search tool capabilities
3. User sends a message via LINE app
4. LINE Platform sends a webhook POST request to `/callback`
5. FastAPI receives the request
6. `WebhookParser` validates the signature
7. Application extracts the text message from the user
8. **AI Processing**: 
   - User's message is sent to the Google ADK agent
   - Agent analyzes the query and decides whether to use Google Search
   - If needed, the agent searches the web for current information
   - Agent generates an intelligent, contextual response
9. Application sends the AI-generated response back to the user via `AsyncMessagingApi.reply_message()`
10. User receives an intelligent, informative answer
11. **Shutdown**: Lifespan event closes the async client gracefully

## API Endpoints

### POST /callback

**Purpose**: Receive LINE webhook events

**Headers**:
- `X-Line-Signature`: HMAC-SHA256 signature (automatically sent by LINE)
- `Content-Type`: application/json

**Response**:
- Success: `200 OK` with body "OK"
- Invalid signature: `400 Bad Request`

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

## Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Framework | FastAPI | Latest |
| Server | Uvicorn | Latest |
| SDK | line-bot-sdk | Latest (v3+) |
| AI Agent | Google ADK | Latest |
| AI Model | Gemini 2.5 Flash | Latest |
| Python | Python 3 | ≥ 3.10 |
| Environment | python-dotenv | Latest |

## Security Considerations

- Webhook signatures are validated on every request
- Invalid signatures return HTTP 400
- Environment variables store sensitive credentials
- Never commit `.env` file to version control
- Use HTTPS in production (ngrok provides this for local dev)

## Known Limitations

- Only processes text messages (ignores stickers, images, videos, etc.)
- No conversation history between messages (each query is independent)
- No user state management or personalization
- No rate limiting (consider adding for production)
- ngrok URL changes on restart (free tier)
- Google API free tier has usage limits (check Google AI Studio for current limits)
- Response time depends on Google Search queries (typically 2-5 seconds)

## Next Steps

Want to extend this bot further? Consider adding:
- **Conversation history**: Implement session management to maintain context across messages
- **Multi-modal support**: Handle images, stickers, and other LINE message types
- **Flex messages**: Use LINE's rich message format for better UI/UX
- **Database integration**: Store conversations and user preferences
- **Custom tools**: Add more ADK tools beyond Google Search (calculator, weather API, etc.)
- **Multi-agent architecture**: Use specialized agents for different topics
- **Rate limiting**: Protect against abuse and manage API costs
- **Caching**: Store frequent queries to reduce API calls
- **User preferences**: Personalize responses based on user history
- **Deployment**: Deploy to cloud platform (AWS, GCP, Azure) with proper scaling

## References

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [Google ADK Python GitHub](https://github.com/google/adk-python)
- [Google AI Studio](https://aistudio.google.com/)
- [LINE Bot SDK Python](https://github.com/line/line-bot-sdk-python)
- [LINE Messaging API Documentation](https://developers.line.biz/en/docs/messaging-api/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Uvicorn Documentation](https://www.uvicorn.org/)

## License

This is a sample project for educational purposes.

## Support

For issues related to:
- **LINE Bot SDK**: Check the [official GitHub repository](https://github.com/line/line-bot-sdk-python)
- **LINE Platform**: Visit [LINE Developers Support](https://developers.line.biz/en/support/)
- **FastAPI**: See [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

**Happy coding!** 🤖
