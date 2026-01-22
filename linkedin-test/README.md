# LinkedIn Python Image & Text Uploader

A simple, standalone Python tool for posting images with text to LinkedIn using the LinkedIn v2 API. Perfect for developers who want to automate LinkedIn content posting or learn about LinkedIn's OAuth and API integration.

## Features

- ✅ OAuth 2.0 authentication flow
- ✅ Automatic browser-based login
- ✅ Secure token storage
- ✅ Image upload to LinkedIn Assets API
- ✅ UGC post creation with images and text
- ✅ Comprehensive error handling
- ✅ Upload status verification

## Prerequisites

### 1. Python Environment
- Python 3.8 or higher
- pip (Python package manager)

### 2. LinkedIn Developer App

You need to create a LinkedIn Developer application to get OAuth credentials:

1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/)
2. Click **"Create app"**
3. Fill in the required information:
   - App name
   - LinkedIn Page (you can use your personal profile)
   - App logo (any image)
4. Click **"Create app"**

5. **Add Products:**
   - Go to the "Products" tab
   - Add **"Sign In with LinkedIn using OpenID Connect"**
   - Add **"Share on LinkedIn"**
   - Wait for approval (usually instant)

6. **Configure OAuth 2.0:**
   - Go to the "Auth" tab
   - Under **"OAuth 2.0 settings"**, add redirect URL:
     ```
     http://localhost:8080/callback
     ```
   - Copy your **Client ID** and **Client Secret**

7. **Verify Scopes:**
   - Ensure these scopes are available:
     - `w_member_social`
     - `openid`
     - `profile`
     - `email`

## Installation

### 1. Clone or Download

```bash
cd linkedin-test
```

### 2. Create Virtual Environment (Recommended)

```bash
# Using venv
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Or using virtualenv
pip install virtualenv
virtualenv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Credentials

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your credentials
nano .env  # or use any text editor
```

Your `.env` file should look like:
```env
LINKEDIN_CLIENT_ID=your_actual_client_id_here
LINKEDIN_CLIENT_SECRET=your_actual_client_secret_here
```

## Usage

### Step 1: Authenticate with LinkedIn

Run the authentication script to obtain an access token:

```bash
python get_token.py
```

**What happens:**
1. A browser window opens to LinkedIn login
2. You log in and grant permissions
3. The script captures the OAuth callback
4. Access token is saved to `.user_token`
5. Token file permissions are set to 600 (secure)

**Expected output:**
```
============================================================
LinkedIn OAuth 2.0 Authentication
============================================================

🌐 Opening browser for LinkedIn authentication...
   Scopes: w_member_social, openid, profile, email

📡 Waiting for authentication callback on http://localhost:8080/callback
   (Timeout: 5 minutes)
✅ Authorization code received
🔄 Exchanging authorization code for access token...
✅ Access token obtained
💾 Token saved to .user_token
🔒 Token file permissions set to 600 (owner read/write only)
⏰ Token expires in approximately 60 days

============================================================
🎉 Authentication Complete!
============================================================

You can now run: python post_to_linkedin.py
```

### Step 2: Prepare Your Image

Place an image file named `test_image.jpg` in the project directory.

**Supported formats:**
- JPG/JPEG
- PNG
- GIF (up to 250 frames)

**Requirements:**
- Max pixels: 36,152,320
- Max file size: ~50MB (recommended)

**To use a different image:**
Edit `TEST_IMAGE_PATH` in `post_to_linkedin.py`:
```python
TEST_IMAGE_PATH = "my_custom_image.png"
```

### Step 3: Post to LinkedIn

Run the posting script:

```bash
python post_to_linkedin.py
```

**What happens:**
1. Loads access token from `.user_token`
2. Fetches your LinkedIn user URN
3. Validates the image file
4. Registers image upload with LinkedIn Assets API
5. Uploads image binary
6. Verifies upload status
7. Creates LinkedIn post with image and text
8. Prints the post URL

**Expected output:**
```
============================================================
LinkedIn Image & Text Poster
============================================================

📁 Loading access token...
✅ Token loaded
👤 Fetching user information...
✅ User URN: urn:li:person:abc123xyz

🖼️  Validating image: test_image.jpg
✅ Image validated

📤 Registering image upload...
✅ Upload registered
   Asset URN: urn:li:digitalmediaAsset:C5622AQHdBDflPp0pEg
📷 Uploading image binary...
✅ Image uploaded successfully
🔍 Verifying upload status...
✅ Upload verified - status: AVAILABLE

📝 Post text: "Testing LinkedIn API v2 image upload! 🚀"
🚀 Creating LinkedIn post...
✅ Post created successfully!

============================================================
🎉 Success!
============================================================

📍 Post URN: urn:li:ugcPost:1234567890
🔗 Post URL: https://www.linkedin.com/feed/update/urn:li:ugcPost:1234567890

💡 Visit the URL above to view your post on LinkedIn
```

### Customizing Post Content

Edit the constants in `post_to_linkedin.py`:

```python
TEST_IMAGE_PATH = "my_image.jpg"  # Change image file
TEST_POST_TEXT = "Check out my amazing project! 🎨"  # Change post text
```

**Text limits:**
- Maximum 3000 characters
- Supports Unicode and emoji

## File Structure

```
linkedin-test/
├── .env                    # Your credentials (excluded from git)
├── .env.example            # Template for credentials
├── .gitignore              # Excludes sensitive files
├── .user_token             # Stored access token (excluded from git)
├── get_token.py            # OAuth authentication script
├── post_to_linkedin.py     # Main posting script
├── test_image.jpg          # Your test image
├── requirements.txt        # Python dependencies
├── README.md               # This file
└── INITIAL.md              # Initial requirements
```

## Troubleshooting

### Error: "No token found"
**Solution:** Run `python get_token.py` first to authenticate.

### Error: "Token expired"
**Solution:** Re-run `python get_token.py` to get a new token.

### Error: "Port 8080 is already in use"
**Solution:**
```bash
# Find process using port 8080
lsof -i :8080  # On macOS/Linux
netstat -ano | findstr :8080  # On Windows

# Kill the process or wait for it to close
```

### Error: "Image file not found"
**Solution:** Ensure `test_image.jpg` exists in the project directory, or update `TEST_IMAGE_PATH`.

### Error: "Unauthorized (401)"
**Possible causes:**
1. Token expired - re-authenticate with `get_token.py`
2. Invalid credentials in `.env`
3. App doesn't have required products/scopes

**Solution:**
- Check LinkedIn Developer portal
- Verify "Share on LinkedIn" product is added
- Verify `w_member_social` scope is enabled

### Error: "Forbidden (403)"
**Solution:**
- Verify your LinkedIn app has "Share on LinkedIn" product enabled
- Check that app is not in "Development" mode with restricted access

### Error: "Rate Limited (429)"
**Solution:** Wait a few minutes before trying again. LinkedIn has rate limits on API calls.

### Error: "Bad Request (400)"
**Possible causes:**
1. Malformed image file
2. Invalid image format
3. Text too long (>3000 chars)

**Solution:**
- Use JPG, PNG, or GIF format
- Ensure image is not corrupted
- Check text length

### Browser doesn't open automatically
**Solution:** The script prints the authorization URL. Copy and paste it into your browser manually.

## Security Best Practices

### Token Security
- ✅ `.user_token` has 600 permissions (owner read/write only)
- ✅ Token file is in `.gitignore`
- ✅ Token is never printed to console
- ⚠️ Token expires after ~60 days - re-authenticate when needed

### Credentials Management
- ✅ `.env` file is in `.gitignore`
- ✅ No credentials hardcoded in source
- ⚠️ Never commit `.env` or `.user_token` to version control

### API Security
- ✅ All requests use HTTPS
- ✅ Required headers included in all API calls
- ✅ Tokens transmitted securely

## API Documentation

### Required Headers

All LinkedIn v2 API calls require:
```python
"X-Restli-Protocol-Version": "2.0.0"  # MANDATORY
```

Assets API additionally requires:
```python
"LinkedIn-Version": "202501"  # Format: YYYYMM
```

### API Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/oauth/v2/authorization` | GET | User authorization |
| `/oauth/v2/accessToken` | POST | Token exchange |
| `/v2/userinfo` | GET | Get user URN |
| `/v2/assets?action=registerUpload` | POST | Register image upload |
| `/v2/assets/{id}` | GET | Check upload status |
| `/v2/ugcPosts` | POST | Create post |

### Limitations

- **Image Size:** Max 36,152,320 pixels
- **Image Formats:** JPG, PNG, GIF only
- **Text Length:** Max 3000 characters
- **GIF Frames:** Max 250 frames
- **Token Expiry:** ~60 days
- **Rate Limits:** Not publicly documented (handle 429 responses)

### Out of Scope (Not Supported)

- ❌ Multiple image uploads (carousel posts)
- ❌ Video uploads
- ❌ Posting to organization pages
- ❌ Scheduling posts
- ❌ Post analytics
- ❌ Editing/deleting posts

## Official LinkedIn Documentation

- [LinkedIn OAuth 2.0](https://learn.microsoft.com/en-us/linkedin/shared/authentication/authentication)
- [Assets API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/vector-asset-api)
- [UGC Post API](https://learn.microsoft.com/en-us/linkedin/compliance/integrations/shares/ugc-post-api)
- [Posts API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api)

## Advanced Usage

### Using Different Images

You can modify `post_to_linkedin.py` to accept command-line arguments:

```python
import sys

if len(sys.argv) > 1:
    TEST_IMAGE_PATH = sys.argv[1]
if len(sys.argv) > 2:
    TEST_POST_TEXT = sys.argv[2]
```

Then run:
```bash
python post_to_linkedin.py my_image.png "My custom text"
```

### Batch Posting

Create a script to post multiple images:

```python
import os
import time
from post_to_linkedin import main as post_main

images = ["image1.jpg", "image2.jpg", "image3.jpg"]

for img in images:
    # Modify TEST_IMAGE_PATH in post_to_linkedin.py
    # Run posting logic
    post_main()

    # Wait to avoid rate limiting
    time.sleep(60)
```

## Development

### Running Tests

The PRD includes test cases. To validate:

```bash
# Test OAuth flow
python get_token.py

# Test posting
python post_to_linkedin.py

# Verify on LinkedIn
# Visit https://www.linkedin.com/feed/
```

### Code Structure

**get_token.py:**
- `construct_auth_url()` - Build authorization URL
- `start_callback_server()` - Handle OAuth callback
- `exchange_code_for_token()` - Exchange code for token
- `save_token()` - Save token securely

**post_to_linkedin.py:**
- `load_token()` - Load saved token
- `get_user_urn()` - Fetch user ID
- `validate_image()` - Validate image file
- `register_image_upload()` - Register with Assets API
- `upload_image_binary()` - Upload image
- `check_upload_status()` - Verify upload
- `create_ugc_post()` - Create LinkedIn post

## Contributing

This is a simple educational tool. Feel free to:
- Report bugs via issues
- Suggest improvements
- Fork and extend functionality

## License

MIT License - feel free to use and modify as needed.

## Credits

Built following the LinkedIn v2 API documentation and best practices for OAuth 2.0 integration.

## Support

For issues with:
- **This tool:** Check troubleshooting section above
- **LinkedIn API:** Visit [LinkedIn Developer Portal](https://www.linkedin.com/developers/)
- **Authentication:** Verify app settings and scopes

---

**Happy posting! 🚀**
