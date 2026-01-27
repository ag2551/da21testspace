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

### Create a Draft Post

```bash
curl -X POST "http://localhost:8000/api/posts/" \
  -H "Content-Type: application/json" \
  -d '{
    "content_text": "Excited to announce our new product launch! 🚀",
    "content_image_url": "https://example.com/product.jpg"
  }'
```

### Add Facebook Credential

```bash
curl -X POST "http://localhost:8000/api/credentials/" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "facebook",
    "account_name": "My Business Page",
    "access_token": "YOUR_FB_PAGE_TOKEN"
  }'
```

### Publish Post to Both Platforms

```bash
curl -X POST "http://localhost:8000/api/posts/1/publish" \
  -H "Content-Type: application/json" \
  -d '{
    "platforms": ["facebook", "linkedin"]
  }'
```

### Check Post Status

```bash
curl "http://localhost:8000/api/posts/1/status"
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

### Database errors

```bash
# Delete and recreate database
rm data/social_hub.db
# Restart server (will recreate tables)
```

### Import errors

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

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

**Version**: 1.0.0
**Last Updated**: 2026-01-27
**Status**: Production Ready ✅
