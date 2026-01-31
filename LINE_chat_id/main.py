import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException, Depends
import aiosqlite
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

# Import Google ADK components
from google.adk.runners import InMemoryRunner
from agent_config import search_agent

# Import database components (native SQLite)
from app.database import init_db, get_db_connection
from app.routes import social_posts

# Load environment variables from .env file
load_dotenv()

# Get credentials from environment variables
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
channel_secret = os.getenv('LINE_CHANNEL_SECRET')

# Validate that required environment variables are set
if not channel_access_token or not channel_secret:
    print("ERROR: LINE_CHANNEL_ACCESS_TOKEN and LINE_CHANNEL_SECRET must be set in .env file")
    sys.exit(1)

# Initialize Configuration and WebhookParser (these don't need event loop)
configuration = Configuration(access_token=channel_access_token)
parser = WebhookParser(channel_secret)

# Global variables for async clients (initialized in lifespan)
async_api_client = None
line_bot_api = None
agent_runner = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI.
    Initializes async clients, database, and Google ADK runner when the event loop is running.
    """
    global async_api_client, line_bot_api, agent_runner

    # Startup: Create database tables with native SQLite
    print("Initializing database with native SQLite (aiosqlite)...")
    await init_db()

    # Startup: Initialize async clients
    async_api_client = AsyncApiClient(configuration)
    line_bot_api = AsyncMessagingApi(async_api_client)

    # Initialize Google ADK runner with the search agent
    agent_runner = InMemoryRunner(agent=search_agent)

    yield

    # Shutdown: Cleanup if needed
    await async_api_client.close()


# Create FastAPI application with lifespan
app = FastAPI(lifespan=lifespan)

# Include CRUD API routes
app.include_router(social_posts.router)


@app.post("/callback")
async def callback(request: Request, db: aiosqlite.Connection = Depends(get_db_connection)):
    """
    LINE Webhook callback endpoint.
    Receives webhook events from LINE Platform and processes them.
    Includes automatic user profile capture and database persistence using native SQL.
    """
    # Extract the X-Line-Signature header
    signature = request.headers['X-Line-Signature']

    # Get request body as bytes and decode to string
    body = await request.body()
    body = body.decode()

    # Parse and validate the webhook signature
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Process each event
    for event in events:
        # Only handle text messages
        if isinstance(event, MessageEvent) and isinstance(event.message, TextMessageContent):
            # Extract user ID from event
            user_id = event.source.user_id

            # Database operations: Check if user exists and update/create profile (NATIVE SQL)
            try:
                # Check if user exists
                cursor = await db.execute(
                    "SELECT * FROM users WHERE line_user_id = ?",
                    (user_id,)
                )
                user = await cursor.fetchone()

                if user is None:
                    # New user - fetch profile from LINE API
                    print(f"New user detected: {user_id}")
                    try:
                        profile = await line_bot_api.get_profile(user_id)

                        # Create new user record with profile data
                        await db.execute(
                            """
                            INSERT INTO users (line_user_id, display_name, picture_url, status_message, language)
                            VALUES (?, ?, ?, ?, ?)
                            """,
                            (user_id, profile.display_name, profile.picture_url,
                             profile.status_message, getattr(profile, 'language', 'zh-TW'))
                        )
                        await db.commit()
                        print(f"✓ New user registered: {user_id} ({profile.display_name})")

                    except Exception as profile_error:
                        # Handle cases where profile fetch fails (user blocked bot, API error, etc.)
                        print(f"⚠ Could not fetch profile for {user_id}: {profile_error}")
                        # Create minimal user record with default language
                        await db.execute(
                            "INSERT INTO users (line_user_id, language, created_at, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)",
                            (user_id, "zh-TW")
                        )
                        await db.commit()
                        print(f"✓ Minimal user record created for {user_id}")
                else:
                    # Existing user - update timestamp and refresh display name
                    try:
                        profile = await line_bot_api.get_profile(user_id)
                        await db.execute(
                            """
                            UPDATE users
                            SET display_name = ?, updated_at = CURRENT_TIMESTAMP
                            WHERE line_user_id = ?
                            """,
                            (profile.display_name, user_id)
                        )
                        await db.commit()
                        print(f"✓ User profile updated: {user_id} ({profile.display_name})")

                    except Exception as profile_error:
                        # If profile fetch fails, just update timestamp
                        print(f"⚠ Could not refresh profile for {user_id}: {profile_error}")
                        await db.execute(
                            "UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE line_user_id = ?",
                            (user_id,)
                        )
                        await db.commit()

            except Exception as db_error:
                # Database errors should not break the chatbot
                print(f"❌ Database error for user {user_id}: {db_error}")
                await db.rollback()

            # Get user's message
            user_message = event.message.text
            
            try:
                # Generate AI response using Google ADK agent with search capabilities
                # run_debug returns a list of events from the agent execution
                adk_events = await agent_runner.run_debug(
                    user_message,
                    quiet=True  # Suppress console output
                )
                
                # Extract the text response from the last agent response event
                response_text = ""
                for adk_event in reversed(adk_events):
                    if hasattr(adk_event, 'content') and adk_event.content:
                        if hasattr(adk_event.content, 'parts') and adk_event.content.parts:
                            for part in adk_event.content.parts:
                                if hasattr(part, 'text') and part.text:
                                    response_text = part.text
                                    break
                        if response_text:
                            break
                
                # Fallback if no text response found
                if not response_text:
                    response_text = "I received your message but couldn't generate a response."
                
            except Exception as e:
                # Fallback response if AI agent fails
                print(f"Error generating AI response: {e}")
                import traceback
                traceback.print_exc()
                response_text = "Sorry, I encountered an error processing your message. Please try again."
            
            # Send the AI-powered response back to the user
            await line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=response_text)]
                )
            )

    return "OK"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
