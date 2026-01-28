# Social Media Hub

A lightweight social media management platform for publishing content to Facebook and LinkedIn through a unified REST API.

## Features

✅ **Credential Management**
- Securely store Facebook and LinkedIn access tokens with Fernet encryption
- Support multiple accounts per platform
- Validate credentials with platform APIs
- Track token expiration

✅ **Post Management**
- Create, read, update, and delete posts
- Support text and image content
- Draft mode before publication
- Schedule posts for future publication

✅ **Multi-Platform Publishing**
- Publish to Facebook and LinkedIn simultaneously
- Track publication status per platform
- Store platform-specific post IDs
- Comprehensive error handling

✅ **Modern Architecture**
- FastAPI with async/await patterns
- SQLModel + SQLAlchemy for database operations
- Async SQLite with aiosqlite
- HTTPX for non-blocking HTTP calls
- Adapter pattern for platform abstraction

## Tech Stack

- **FastAPI** - Modern, high-performance web framework
- **SQLModel** - Database ORM with Pydantic validation
- **SQLite** (async) - Embedded database
- **HTTPX** - Async HTTP client
- **Cryptography** - Token encryption
- **Uvicorn** - ASGI server

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repo-url>
cd linkedinfb

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Generate encryption key (already done, but you can regenerate)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Edit .env and set your ENCRYPTION_KEY
nano .env
```

### 3. Run the Server

```bash
# Activate virtual environment
source venv/bin/activate

# Start the server
uvicorn app.main:app --reload

# Server will start on http://localhost:8000
```

### 4. Access API Documentation

Open your browser and navigate to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 5. Platform Credential Setup

Before publishing, you need to configure credentials for each platform:

| Platform | Required Fields | Where to Get |
|----------|----------------|--------------|
| **LinkedIn** | • `access_token`<br>• `page_id_or_urn` (Person URN) | • Access Token: [LinkedIn Developer Portal](https://www.linkedin.com/developers/) (OAuth 2.0)<br>• Person URN: From `/v2/userinfo` API or format: `urn:li:person:YOUR_ID` |
| **Facebook** | • `access_token` (Page Token)<br>• `page_id_or_urn` (Page ID) | • Page Token: [Graph API Explorer](https://developers.facebook.com/tools/explorer/)<br>• Page ID: Your Page's About section or `/me/accounts` API |

**Quick Setup:**
```bash
# LinkedIn
curl -X POST "http://localhost:8000/api/credentials/" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "linkedin",
    "account_name": "Your Name",
    "access_token": "YOUR_TOKEN",
    "page_id_or_urn": "urn:li:person:YOUR_ID"
  }'

# Facebook
curl -X POST "http://localhost:8000/api/credentials/" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "facebook",
    "account_name": "Page Name",
    "access_token": "YOUR_PAGE_TOKEN",
    "page_id_or_urn": "YOUR_PAGE_ID"
  }'
```

## API Endpoints

### Credentials

```
POST   /api/credentials              # Create new credential
GET    /api/credentials              # List all credentials
GET    /api/credentials/{id}         # Get specific credential
PUT    /api/credentials/{id}         # Update credential
DELETE /api/credentials/{id}         # Delete credential
POST   /api/credentials/{id}/validate # Validate credential
```

### Posts

```
POST   /api/posts                    # Create new post
GET    /api/posts                    # List all posts
GET    /api/posts/{id}               # Get specific post
PUT    /api/posts/{id}               # Update post
DELETE /api/posts/{id}               # Delete post
POST   /api/posts/{id}/publish       # Publish post
POST   /api/posts/{id}/schedule      # Schedule post
GET    /api/posts/{id}/status        # Get publication status
```

## Usage Examples

### Step 1: Create a Draft Post

```bash
curl -X POST "http://localhost:8000/api/posts/" \
  -H "Content-Type: application/json" \
  -d '{
    "content_text": "Excited to announce our new product launch! 🚀",
    "content_image_url": "https://images.unsplash.com/photo-1593720213428-28a5b9e94613?w=800"
  }'
```

**Response:**
```json
{
  "id": 1,
  "content_text": "Excited to announce our new product launch! 🚀",
  "content_image_url": "https://images.unsplash.com/photo-1593720213428-28a5b9e94613?w=800",
  "status": "draft",
  ...
}
```

### Step 2: Add Platform Credentials

#### Add LinkedIn Credential

```bash
curl -X POST "http://localhost:8000/api/credentials/" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "linkedin",
    "account_name": "Your Name",
    "access_token": "YOUR_LINKEDIN_ACCESS_TOKEN",
    "page_id_or_urn": "urn:li:person:YOUR_PERSON_ID"
  }'
```

**How to get LinkedIn credentials:**

1. **Access Token**: 
   - Go to [LinkedIn Developer Portal](https://www.linkedin.com/developers/)
   - Create or select your app
   - Request permissions: `w_member_social`, `r_liteprofile`
   - Complete OAuth 2.0 flow to get access token
   - See [LinkedIn OAuth 2.0 Guide](https://learn.microsoft.com/en-us/linkedin/shared/authentication/authentication)

2. **Person URN** (page_id_or_urn):
   - Format: `urn:li:person:YOUR_PERSON_ID`
   - Get from LinkedIn API: `GET https://api.linkedin.com/v2/userinfo`
   - Or use the test value from your `.env` file

**Example response:**
```json
{
  "id": 1,
  "platform": "linkedin",
  "account_name": "Your Name",
  "page_id_or_urn": "urn:li:person:ACoAAFrwP2wB...",
  "is_active": true,
  ...
}
```

#### Add Facebook Credential

```bash
curl -X POST "http://localhost:8000/api/credentials/" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "facebook",
    "account_name": "My Business Page",
    "access_token": "YOUR_FB_PAGE_ACCESS_TOKEN",
    "page_id_or_urn": "YOUR_PAGE_ID"
  }'
```

**How to get Facebook credentials:**

1. **Page Access Token**:
   - Go to [Facebook Graph API Explorer](https://developers.facebook.com/tools/explorer/)
   - Select your Page
   - Add permissions: `pages_manage_posts`, `pages_read_engagement`
   - Generate token
   - For long-lived tokens, see [Facebook Token Guide](https://developers.facebook.com/docs/facebook-login/guides/access-tokens)

2. **Page ID** (page_id_or_urn):
   - Find on your Facebook Page → About section
   - Or via Graph API: `GET /me/accounts`
   - Example: `1015722141619269`

**Example response:**
```json
{
  "id": 2,
  "platform": "facebook",
  "account_name": "My Business Page",
  "page_id_or_urn": "1015722141619269",
  "is_active": true,
  ...
}
```

### Step 3: Validate Credentials (Optional)

```bash
# Validate LinkedIn credential
curl -X POST "http://localhost:8000/api/credentials/1/validate"

# Validate Facebook credential
curl -X POST "http://localhost:8000/api/credentials/2/validate"
```

### Step 4: Publish Post to Platforms

```bash
# Publish to both platforms
curl -X POST "http://localhost:8000/api/posts/1/publish" \
  -H "Content-Type: application/json" \
  -d '{
    "platforms": ["facebook", "linkedin"]
  }'
```

**Response:**
```json
{
  "id": 1,
  "status": "published",
  "results": {
    "facebook": {
      "success": true,
      "post_id": "1015722141619269_1234567890",
      "error": null
    },
    "linkedin": {
      "success": true,
      "post_id": "urn:li:share:7123456789012345678",
      "error": null
    }
  }
}
```

### Step 5: Check Post Status

```bash
curl "http://localhost:8000/api/posts/1/status"
```

**Response:**
```json
{
  "post_id": 1,
  "overall_status": "published",
  "platforms": {
    "facebook": {
      "status": "published",
      "post_id": "1015722141619269_1234567890",
      "published_at": "2026-01-28T06:30:00",
      "error": null
    },
    "linkedin": {
      "status": "published",
      "post_id": "urn:li:share:7123456789012345678",
      "published_at": "2026-01-28T06:30:00",
      "error": null
    }
  }
}
```

### Additional Examples

#### Update Credential

```bash
curl -X PUT "http://localhost:8000/api/credentials/1" \
  -H "Content-Type: application/json" \
  -d '{
    "access_token": "NEW_TOKEN",
    "is_active": true
  }'
```

#### List All Credentials

```bash
curl "http://localhost:8000/api/credentials"
```

#### Publish to Single Platform

```bash
curl -X POST "http://localhost:8000/api/posts/1/publish" \
  -H "Content-Type: application/json" \
  -d '{
    "platforms": ["linkedin"]
  }'
```

## Project Structure

```
linkedinfb/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration
│   ├── database.py             # Async database setup
│   ├── models/
│   │   ├── credential.py       # SocialCredential model
│   │   └── post.py             # SocialPost model
│   ├── schemas/
│   │   ├── credential.py       # Pydantic schemas
│   │   └── post.py
│   ├── adapters/
│   │   ├── base.py             # Base adapter interface
│   │   ├── facebook.py         # Facebook Graph API
│   │   └── linkedin.py         # LinkedIn REST API
│   ├── routers/
│   │   ├── credentials.py      # Credential endpoints
│   │   └── posts.py            # Post endpoints
│   └── services/
│       ├── encryption.py       # Token encryption
│       └── publisher.py        # Publishing service
├── tests/
│   └── test_encryption.py
├── data/
│   └── social_hub.db           # SQLite database
├── requirements.txt
├── .env.example
└── README.md
```

## Development

### Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run validation script
python test_api.py
```

### Database

The SQLite database is created automatically on first run at `data/social_hub.db`.

To inspect the database:

```bash
sqlite3 data/social_hub.db
.tables
.schema social_posts
SELECT * FROM social_posts;
```

## API Integration

### Facebook Graph API

- **Version**: v24.0
- **Endpoints**:
  - Text posts: `POST /{page-id}/feed`
  - Photo posts: `POST /{page-id}/photos`
- **Authentication**: Page Access Token
- **Required Permissions**: `pages_manage_posts`, `pages_read_engagement`

**Note**: You need to obtain a Page Access Token from Facebook's Graph API Explorer or through an OAuth flow.

### LinkedIn REST API

- **Version**: 202601
- **Endpoints**:
  - Posts: `POST /rest/posts`
  - Images: `POST /rest/images?action=initializeUpload`
- **Authentication**: OAuth 2.0 Bearer token
- **Required Headers**:
  - `LinkedIn-Version: 202601`
  - `X-Restli-Protocol-Version: 2.0.0`
- **Required Permissions**: `w_member_social` or `w_organization_social`

**Note**: LinkedIn uses a two-step image upload process:
1. Initialize upload to get image URN
2. Upload binary to provided URL
3. Reference image URN in post

## Security

- **Token Encryption**: All access tokens are encrypted using Fernet (symmetric encryption)
- **Encryption Key**: Must be set in `.env` file
- **Token Storage**: Never exposed in API responses
- **Environment Variables**: Sensitive data stored in `.env` (not committed to git)

## Limitations (MVP)

### Included
- Facebook and LinkedIn only
- Text + single image per post
- Manual credential input
- Basic CRUD operations
- Single-user system

### Not Included (Future)
- Twitter/X, Instagram, TikTok
- OAuth2 flows for token acquisition
- Multi-user support with authentication
- Post analytics and engagement metrics
- Background workers for scheduled publishing
- Video content support

## Troubleshooting

### Server won't start

```bash
# Check if port 8000 is already in use
lsof -i :8000

# Use a different port
uvicorn app.main:app --port 8001
```

### Pydantic Validation Error on Startup

If you see `ValidationError: Extra inputs are not permitted`:

```bash
# The .env file has fields not defined in Settings class
# Check app/config.py Settings class matches your .env variables
# Or remove unused variables from .env
```

### Database errors

```bash
# Delete and recreate database (WARNING: loses all data)
rm data/social_hub.db
# Restart server (will recreate tables)
```

### Database schema mismatch after update

If you added the `page_id_or_urn` field and get database errors:

```bash
# Option 1: Add column manually (preserves data)
sqlite3 data/social_hub.db "ALTER TABLE social_credentials ADD COLUMN page_id_or_urn TEXT;"

# Option 2: Recreate database (loses data)
rm data/social_hub.db
# Restart server
```

### Import errors

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Credential Issues

#### LinkedIn: "Invalid access token" error

- **Cause**: Token expired or invalid permissions
- **Solution**: 
  1. Verify token has `w_member_social` permission
  2. Get fresh token from LinkedIn OAuth flow
  3. LinkedIn tokens typically expire after 60 days

#### LinkedIn: "author URN not configured" error

- **Cause**: Missing `page_id_or_urn` in credential
- **Solution**: Update credential with your Person URN:
  ```bash
  curl -X PUT "http://localhost:8000/api/credentials/1" \
    -H "Content-Type: application/json" \
    -d '{"page_id_or_urn": "urn:li:person:YOUR_ID"}'
  ```

#### Facebook: "page_id not configured" error

- **Cause**: Missing `page_id_or_urn` in credential
- **Solution**: Update credential with your Page ID:
  ```bash
  curl -X PUT "http://localhost:8000/api/credentials/1" \
    -H "Content-Type: application/json" \
    -d '{"page_id_or_urn": "YOUR_PAGE_ID"}'
  ```

#### Publishing fails with empty error

- **Cause**: Network error or API rate limiting
- **Solution**: 
  1. Check server logs for detailed error
  2. Verify internet connection
  3. Wait a few minutes and retry (rate limit)
  4. Validate credential: `POST /api/credentials/{id}/validate`

### Getting Detailed Error Messages

Enable debug mode in `.env`:

```bash
DEBUG=true
```

Then check server console for detailed logs.

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Version**: 1.1.0
**Last Updated**: 2026-01-28
**Status**: Production Ready ✅

**Changelog v1.1.0**:
- Added `page_id_or_urn` field to credentials for per-account Page ID/URN configuration
- Enhanced error messages for LinkedIn publishing failures
- Improved credential management with better validation
- Updated documentation with comprehensive setup guides
