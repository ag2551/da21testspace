# Quick Start Guide - Social Media Hub

Get up and running in 5 minutes!

## Prerequisites

- Python 3.8+
- pip
- Virtual environment support

## 5-Minute Setup

### Step 1: Activate Virtual Environment (1 min)

```bash
cd linkedinfb
source venv/bin/activate
```

**Note**: The virtual environment is already set up with all dependencies installed!

### Step 2: Verify Configuration (30 sec)

```bash
# Check that .env file exists
cat .env | grep ENCRYPTION_KEY
```

You should see: `ENCRYPTION_KEY=0dKGrRdYWq5vQPhEHPWxvMEvMVgtdXEtybDfaWILSD8=`

### Step 3: Start the Server (30 sec)

```bash
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 4: Test the API (1 min)

Open your browser and go to:
**http://localhost:8000/docs**

You'll see the interactive Swagger UI with all available endpoints!

### Step 5: Try the API (2 min)

#### Create a Post

In Swagger UI, expand `POST /api/posts/` and click "Try it out":

```json
{
  "content_text": "Hello from Social Media Hub! 🚀",
  "content_image_url": null
}
```

Click "Execute" and you'll get:

```json
{
  "id": 1,
  "content_text": "Hello from Social Media Hub! 🚀",
  "status": "draft",
  "created_at": "2026-01-27T...",
  ...
}
```

#### Get Post Status

Expand `GET /api/posts/{post_id}/status` and try with `post_id: 1`

You'll see the publication status for Facebook and LinkedIn!

---

## Next: Add Your Social Media Credentials

### For Facebook:

1. Get a Page Access Token from Facebook Graph API Explorer
2. Use `POST /api/credentials/`:

```json
{
  "platform": "facebook",
  "account_name": "My Business Page",
  "access_token": "YOUR_FB_PAGE_TOKEN",
  "token_expires_at": "2026-03-27T00:00:00Z"
}
```

### For LinkedIn:

1. Get an OAuth access token from LinkedIn Developer Portal
2. Use `POST /api/credentials/`:

```json
{
  "platform": "linkedin",
  "account_name": "My Company",
  "access_token": "YOUR_LINKEDIN_TOKEN",
  "token_expires_at": "2026-03-27T00:00:00Z"
}
```

### Publish Your Post

Once credentials are added, publish your post:

```bash
curl -X POST "http://localhost:8000/api/posts/1/publish" \
  -H "Content-Type: application/json" \
  -d '{"platforms": ["facebook", "linkedin"]}'
```

---

## Quick Reference

### Common Commands

```bash
# Start server
uvicorn app.main:app --reload

# Start server on different port
uvicorn app.main:app --port 8001

# Run validation tests
python test_api.py

# Check database
sqlite3 data/social_hub.db "SELECT * FROM social_posts;"
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root info |
| `/health` | GET | Health check |
| `/docs` | GET | Swagger UI |
| `/api/posts/` | POST | Create post |
| `/api/posts/` | GET | List posts |
| `/api/posts/{id}/publish` | POST | Publish post |
| `/api/credentials/` | POST | Add credential |

### File Locations

- **Application**: `app/main.py`
- **Database**: `data/social_hub.db`
- **Config**: `.env`
- **Logs**: `server.log` (if running in background)

---

## Troubleshooting

### Port Already in Use?

```bash
# Kill existing process
pkill -f "uvicorn app.main:app"

# Or use different port
uvicorn app.main:app --port 8001
```

### Virtual Environment Issues?

```bash
# Deactivate and reactivate
deactivate
source venv/bin/activate
```

### Database Issues?

```bash
# Reset database
rm data/social_hub.db
# Restart server (will recreate)
```

---

## What's Next?

1. ✅ Read the full [README.md](README.md) for detailed usage
2. ✅ Review [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md) for technical details
3. ✅ Check [PRPs/PRD/social-media-hub-prd.md](PRPs/PRD/social-media-hub-prd.md) for complete requirements
4. ✅ Start building your social media automation! 🚀

---

**Status**: Ready to Use ✅
**Setup Time**: ~5 minutes
**Difficulty**: Easy
