# PRD: LinkedIn Python Image & Text Uploader

## Document Information
- **Feature Name:** LinkedIn Python Image & Text Uploader
- **Version:** 1.0
- **Created:** 2026-01-14
- **Status:** Draft
- **Author:** System Generated from INITIAL.md

---

## 1. Executive Summary

### Overview
A simple, standalone Python-based tool that enables users to authenticate with LinkedIn OAuth 2.0 and programmatically post content (images + text) to their LinkedIn feed using the LinkedIn v2 API.

### Business Value
- **Automation:** Enables automated content posting for social media managers and developers
- **Integration:** Provides foundation for LinkedIn integration in larger applications
- **Developer Tool:** Educational tool for understanding LinkedIn API v2 OAuth flow and UGC posting

### Success Metrics
- Successful OAuth authentication flow completion
- Successful image upload to LinkedIn Assets API (100% success rate)
- Successful post creation with image and text
- Clear error messages for all failure scenarios

---

## 2. User Stories

### Primary User Stories

#### US-1: As a developer, I want to authenticate with LinkedIn OAuth 2.0
**Acceptance Criteria:**
- System opens browser automatically for LinkedIn login
- User can grant permissions for required scopes
- System captures OAuth callback successfully
- Access token is securely stored locally
- Token file is excluded from version control

**Priority:** High
**Effort:** Medium

---

#### US-2: As a developer, I want to post an image with text to LinkedIn
**Acceptance Criteria:**
- System loads stored access token
- System uploads image to LinkedIn Assets API
- System verifies image upload success
- System creates UGC post with uploaded image and text
- System prints the post URL upon success

**Priority:** High
**Effort:** High

---

#### US-3: As a developer, I want clear error messages when API calls fail
**Acceptance Criteria:**
- All HTTP error codes (400, 401, 403, 413, 429, 500+) are handled
- Error messages include status code and response body
- Expired token errors prompt re-authentication
- Network errors are caught and reported

**Priority:** High
**Effort:** Low

---

### Secondary User Stories

#### US-4: As a developer, I want to verify image uploads before posting
**Acceptance Criteria:**
- System checks upload status via Assets API
- System waits for status "AVAILABLE" before proceeding
- System handles upload failures gracefully

**Priority:** Medium
**Effort:** Low

---

#### US-5: As a security-conscious user, I want my tokens stored securely
**Acceptance Criteria:**
- Token file has restricted permissions (600 on Unix)
- Token file is in .gitignore
- Token is never printed to console or logs

**Priority:** High
**Effort:** Low

---

## 3. Technical Architecture

### 3.1 System Components

```
┌─────────────────────────────────────────────────────────┐
│                    User Environment                      │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────────┐         ┌──────────────────┐      │
│  │  get_token.py   │         │ post_to_linkedin │      │
│  │                 │         │      .py         │      │
│  │ - OAuth flow    │────────▶│ - Load token     │      │
│  │ - Browser auth  │  .token │ - Get user URN   │      │
│  │ - Save token    │         │ - Upload image   │      │
│  └─────────────────┘         │ - Create post    │      │
│                               └──────────────────┘      │
│           │                            │                 │
│           │                            │                 │
└───────────┼────────────────────────────┼─────────────────┘
            │                            │
            ▼                            ▼
┌─────────────────────────────────────────────────────────┐
│              LinkedIn API v2 Endpoints                   │
├─────────────────────────────────────────────────────────┤
│  - /oauth/v2/authorization (User login)                 │
│  - /oauth/v2/accessToken (Token exchange)               │
│  - /v2/userinfo (Get user URN)                          │
│  - /v2/assets?action=registerUpload (Register image)    │
│  - /v2/assets/{id} (Check upload status)                │
│  - /v2/ugcPosts (Create post)                           │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Technology Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Language | Python | 3.8+ | Core implementation |
| HTTP Client | requests | Latest | API communication |
| Environment | python-dotenv | Latest | Configuration management |
| Auth Server | http.server | stdlib | OAuth callback handler |
| Browser Control | webbrowser | stdlib | Auto-open auth URL |

### 3.3 External Dependencies

**LinkedIn API Requirements:**
- LinkedIn Developer App with OAuth credentials
- App permissions: `w_member_social`, `openid`, `profile`, `email`
- Redirect URI: `http://localhost:8080/callback` (must be registered)

**LinkedIn API Rate Limits:**
- Assets API: Not publicly documented (monitor for 429 responses)
- UGC Posts API: Not publicly documented (monitor for 429 responses)

---

## 4. Technical Implementation Plan

### 4.1 File Structure

```
linkedin-test/
├── .env                      # Configuration (not committed)
├── .env.example              # Configuration template
├── .gitignore                # Excludes .user_token, .env
├── .user_token               # Stored access token (not committed)
├── get_token.py              # OAuth authentication script
├── post_to_linkedin.py       # Main posting logic
├── test_image.jpg            # Sample test image
├── requirements.txt          # Python dependencies
└── README.md                 # Usage instructions
```

### 4.2 New Files to Create

#### File 1: `.env.example`
**Purpose:** Configuration template
**Content:**
```env
LINKEDIN_CLIENT_ID=your_client_id_here
LINKEDIN_CLIENT_SECRET=your_client_secret_here
```

---

#### File 2: `requirements.txt`
**Purpose:** Python dependencies
**Content:**
```txt
requests>=2.31.0
python-dotenv>=1.0.0
```

---

#### File 3: `.gitignore`
**Purpose:** Exclude sensitive files
**Content:**
```gitignore
.env
.user_token
*.pyc
__pycache__/
.venv/
venv/
```

---

#### File 4: `get_token.py`
**Purpose:** OAuth 2.0 authentication handler
**Key Functions:**
- `construct_auth_url()` - Build LinkedIn authorization URL
- `start_callback_server()` - Handle OAuth callback on localhost:8080
- `exchange_code_for_token(code)` - Exchange authorization code for access token
- `save_token(token)` - Save token to `.user_token` with secure permissions
- `main()` - Orchestrate OAuth flow

**Implementation Details:**

**Constants:**
```python
AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
REDIRECT_URI = "http://localhost:8080/callback"
SCOPES = ["w_member_social", "openid", "profile", "email"]
```

**OAuth Flow:**
1. Load CLIENT_ID and CLIENT_SECRET from `.env`
2. Construct authorization URL with scopes and redirect URI
3. Open URL in default browser using `webbrowser.open()`
4. Start HTTP server on port 8080
5. Wait for callback with authorization code
6. Exchange code for access token via POST to TOKEN_URL
7. Save token to `.user_token` with permissions 0o600
8. Print success message with token expiration info

**Error Handling:**
- Missing environment variables
- Port 8080 already in use
- Token exchange failures (400, 401 errors)
- Network connectivity issues

---

#### File 5: `post_to_linkedin.py`
**Purpose:** Main posting logic with image upload
**Key Functions:**
- `load_token()` - Load access token from `.user_token`
- `get_user_urn(token)` - Fetch user's URN via `/v2/userinfo`
- `register_image_upload(token, user_urn)` - Register upload with Assets API
- `upload_image_binary(token, upload_url, image_path)` - Upload image binary
- `check_upload_status(token, asset_id)` - Verify upload completion
- `create_ugc_post(token, user_urn, asset_urn, text)` - Create LinkedIn post
- `main()` - Orchestrate posting flow

**Implementation Details:**

**Constants:**
```python
API_BASE = "https://api.linkedin.com"
USER_INFO_URL = f"{API_BASE}/v2/userinfo"
ASSETS_URL = f"{API_BASE}/v2/assets"
UGC_POSTS_URL = f"{API_BASE}/v2/ugcPosts"

# Required headers for all API calls
HEADERS = {
    "X-Restli-Protocol-Version": "2.0.0",
    "Content-Type": "application/json"
}

# Headers for Assets API
ASSETS_HEADERS = {
    **HEADERS,
    "LinkedIn-Version": "202501"
}
```

**Posting Flow:**
1. Load token from `.user_token`
2. GET `/v2/userinfo` to retrieve user's `sub` field
3. Format URN as `urn:li:person:{sub}`
4. POST to `/v2/assets?action=registerUpload` with:
   - Recipe: `urn:li:digitalmediaRecipe:feedshare-image`
   - Owner: User URN
   - Upload mechanism: `SYNCHRONOUS_UPLOAD`
5. Extract `asset` URN and `uploadUrl` from response
6. PUT binary image data to `uploadUrl`
7. GET `/v2/assets/{asset_id}` to verify status is "AVAILABLE"
8. POST to `/v2/ugcPosts` with:
   - Author: User URN
   - Media: Asset URN
   - Share commentary: Post text
   - Visibility: PUBLIC
9. Extract post ID from `x-restli-id` response header
10. Print post URL: `https://www.linkedin.com/feed/update/{post_id}`

**Error Handling:**
- Missing or invalid token (401) → Prompt to run `get_token.py`
- Token expired (401) → Prompt to re-authenticate
- Image file not found → Clear error message
- Image too large (413) → Check file size and report
- Malformed payload (400) → Print full response for debugging
- Rate limiting (429) → Suggest waiting and retry
- Server errors (500+) → Log and suggest retry

**Hardcoded Test Values:**
```python
TEST_IMAGE_PATH = "test_image.jpg"
TEST_POST_TEXT = "Testing LinkedIn API v2 image upload! 🚀"
```

---

#### File 6: `README.md`
**Purpose:** User documentation
**Sections:**
- Overview
- Prerequisites
- Setup Instructions
- Usage
- Troubleshooting
- API Documentation Links

---

### 4.3 API Request Specifications

#### Request 1: Get User Info
```
GET https://api.linkedin.com/v2/userinfo
Headers:
  Authorization: Bearer {ACCESS_TOKEN}
  X-Restli-Protocol-Version: 2.0.0
```

**Expected Response (200):**
```json
{
  "sub": "abc123xyz",
  "name": "John Doe",
  "email": "john@example.com"
}
```

---

#### Request 2: Register Image Upload
```
POST https://api.linkedin.com/v2/assets?action=registerUpload
Headers:
  Authorization: Bearer {ACCESS_TOKEN}
  X-Restli-Protocol-Version: 2.0.0
  Content-Type: application/json
  LinkedIn-Version: 202501

Body:
{
  "registerUploadRequest": {
    "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
    "owner": "urn:li:person:abc123xyz",
    "serviceRelationships": [
      {
        "relationshipType": "OWNER",
        "identifier": "urn:li:userGeneratedContent"
      }
    ],
    "supportedUploadMechanism": ["SYNCHRONOUS_UPLOAD"]
  }
}
```

**Expected Response (200):**
```json
{
  "value": {
    "asset": "urn:li:digitalmediaAsset:C5622AQHdBDflPp0pEg",
    "uploadMechanism": {
      "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest": {
        "uploadUrl": "https://www.linkedin.com/dms-uploads/...",
        "headers": {
          "media-type-family": "STILLIMAGE"
        }
      }
    }
  }
}
```

---

#### Request 3: Upload Image Binary
```
PUT {uploadUrl from previous response}
Headers:
  Authorization: Bearer {ACCESS_TOKEN}
Body:
  <binary image data>
```

**Expected Response (201):**
```
HTTP/2 201 Created
Content-Length: 0
```

---

#### Request 4: Check Upload Status
```
GET https://api.linkedin.com/v2/assets/C5622AQHdBDflPp0pEg
Headers:
  Authorization: Bearer {ACCESS_TOKEN}
  X-Restli-Protocol-Version: 2.0.0
  LinkedIn-Version: 202501
```

**Expected Response (200):**
```json
{
  "id": "C5622AQHdBDflPp0pEg",
  "status": "AVAILABLE",
  "mediaTypeFamily": "STILLIMAGE",
  "recipes": [
    {
      "recipe": "urn:li:digitalmediaRecipe:feedshare-image",
      "status": "AVAILABLE"
    }
  ]
}
```

---

#### Request 5: Create UGC Post
```
POST https://api.linkedin.com/v2/ugcPosts
Headers:
  Authorization: Bearer {ACCESS_TOKEN}
  X-Restli-Protocol-Version: 2.0.0
  Content-Type: application/json

Body:
{
  "author": "urn:li:person:abc123xyz",
  "lifecycleState": "PUBLISHED",
  "specificContent": {
    "com.linkedin.ugc.ShareContent": {
      "shareCommentary": {
        "attributes": [],
        "text": "Testing LinkedIn API v2 image upload! 🚀"
      },
      "shareMediaCategory": "IMAGE",
      "media": [
        {
          "status": "READY",
          "media": "urn:li:digitalmediaAsset:C5622AQHdBDflPp0pEg",
          "title": {
            "attributes": [],
            "text": "Test Image"
          }
        }
      ]
    }
  },
  "visibility": {
    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
  }
}
```

**Expected Response (201):**
```
HTTP/2 201 Created
x-restli-id: urn:li:ugcPost:1234567890
```

---

### 4.4 Data Models

#### Token Storage Format (`.user_token`)
```json
{
  "access_token": "AQVxxx...",
  "expires_in": 5184000,
  "created_at": 1705190400
}
```

#### User URN Format
```
urn:li:person:{linkedin_user_id}
```

#### Asset URN Format
```
urn:li:digitalmediaAsset:{asset_id}
```

#### Post URN Format
```
urn:li:ugcPost:{post_id}
```

---

## 5. Verification & Testing Plan

### 5.1 Test Cases

#### TC-1: OAuth Authentication Flow
**Preconditions:**
- `.env` file exists with valid CLIENT_ID and CLIENT_SECRET
- Port 8080 is available
- No existing `.user_token` file

**Steps:**
1. Run `python get_token.py`
2. Browser opens automatically to LinkedIn login
3. Login with test LinkedIn account
4. Grant permissions
5. Redirected to localhost:8080/callback
6. Script prints success message

**Expected Results:**
- `.user_token` file created
- File permissions set to 600
- Token contains valid `access_token` field
- Script exits cleanly

**Pass Criteria:** ✅ Token file created and valid

---

#### TC-2: Image Upload and Post Creation
**Preconditions:**
- Valid `.user_token` exists
- `test_image.jpg` exists (size < 5MB, format JPG/PNG)

**Steps:**
1. Run `python post_to_linkedin.py`
2. Script loads token
3. Script fetches user URN
4. Script uploads image
5. Script verifies upload status
6. Script creates post
7. Script prints post URL

**Expected Results:**
- No errors printed
- HTTP 201 responses for upload and post creation
- Post URL printed in format: `https://www.linkedin.com/feed/update/urn:li:ugcPost:...`
- Post visible on LinkedIn feed with image and text

**Pass Criteria:** ✅ Post created and visible on LinkedIn

---

#### TC-3: Expired Token Handling
**Preconditions:**
- `.user_token` exists but token is expired

**Steps:**
1. Run `python post_to_linkedin.py`
2. Script attempts to fetch user URN

**Expected Results:**
- HTTP 401 error caught
- Clear error message: "Token expired. Please run get_token.py to re-authenticate."
- Script exits gracefully with non-zero exit code

**Pass Criteria:** ✅ Clear re-authentication prompt

---

#### TC-4: Missing Token File
**Preconditions:**
- No `.user_token` file exists

**Steps:**
1. Run `python post_to_linkedin.py`

**Expected Results:**
- File not found error caught
- Clear error message: "No token found. Please run get_token.py first."
- Script exits gracefully

**Pass Criteria:** ✅ Clear first-time setup instructions

---

#### TC-5: Image File Not Found
**Preconditions:**
- Valid token exists
- `test_image.jpg` does not exist

**Steps:**
1. Run `python post_to_linkedin.py`

**Expected Results:**
- FileNotFoundError caught
- Clear error message: "Image file not found: test_image.jpg"
- Script exits gracefully

**Pass Criteria:** ✅ Clear file path error

---

#### TC-6: Large Image Rejection
**Preconditions:**
- Valid token exists
- Image file > 36M pixels

**Steps:**
1. Run `python post_to_linkedin.py`

**Expected Results:**
- HTTP 413 or 400 error during upload
- Error message includes: "Image too large. Max pixels: 36,152,320"

**Pass Criteria:** ✅ Size limit error detected

---

#### TC-7: Rate Limiting
**Preconditions:**
- Valid token exists
- Multiple rapid API calls (simulate with loop)

**Steps:**
1. Run posting script multiple times rapidly

**Expected Results:**
- HTTP 429 error caught
- Error message: "Rate limited. Please wait before retrying."

**Pass Criteria:** ✅ Rate limit handled gracefully

---

### 5.2 Manual Verification Checklist

- [ ] Token file permissions are 600 (Unix/Linux)
- [ ] `.gitignore` includes `.user_token` and `.env`
- [ ] Token is never printed to console
- [ ] All API calls include `X-Restli-Protocol-Version: 2.0.0` header
- [ ] Assets API calls include `LinkedIn-Version: 202501` header
- [ ] Error messages include HTTP status code and response body
- [ ] Post URL is printed in correct format
- [ ] Post appears on LinkedIn feed within 30 seconds
- [ ] Image is visible in post (not broken)
- [ ] Post text matches input text exactly
- [ ] Post visibility is PUBLIC

---

### 5.3 Integration Testing

#### Test Scenario 1: End-to-End First-Time User Flow
1. Fresh install (no tokens, no .env)
2. Copy `.env.example` to `.env`
3. Add LinkedIn app credentials
4. Run `python get_token.py` → Authenticate successfully
5. Add test image file
6. Run `python post_to_linkedin.py` → Post created successfully
7. Verify post on LinkedIn

**Expected Duration:** 2-3 minutes
**Pass Criteria:** Post visible on LinkedIn feed

---

#### Test Scenario 2: Retry After Token Expiry
1. Existing setup with expired token
2. Run `python post_to_linkedin.py` → Error message
3. Run `python get_token.py` → Re-authenticate
4. Run `python post_to_linkedin.py` → Success

**Expected Duration:** 1-2 minutes
**Pass Criteria:** Seamless re-authentication flow

---

### 5.4 Edge Cases to Test

| Case | Input | Expected Behavior |
|------|-------|-------------------|
| Empty post text | `""` | Should succeed (image-only post) |
| 3000 char text | Max length string | Should succeed |
| 3001 char text | Over limit | Should fail with clear error |
| GIF image | `test.gif` | Should succeed |
| PNG image | `test.png` | Should succeed |
| Invalid format | `test.bmp` | Should fail during upload |
| Special characters in text | Unicode, emoji | Should succeed and display correctly |
| Concurrent posts | Run script twice simultaneously | Both should succeed or one waits |

---

## 6. Security Considerations

### 6.1 Token Security
- **Storage:** Token stored in local file with 600 permissions
- **Transmission:** Token sent only over HTTPS
- **Logging:** Token never logged or printed
- **Expiration:** Token expires per LinkedIn's policy (typically 60 days)
- **Refresh:** No refresh token support (must re-authenticate)

### 6.2 Credentials Management
- **CLIENT_ID/SECRET:** Stored in `.env` file (excluded from git)
- **Environment Variables:** Loaded via `python-dotenv`
- **Never Hardcoded:** No credentials in source code

### 6.3 Input Validation
- **Image Path:** Validate file exists and is readable
- **Post Text:** Validate length ≤ 3000 characters
- **Image Size:** Check file size before upload
- **Image Format:** Validate extension is .jpg, .png, or .gif

### 6.4 OAuth Security
- **Redirect URI:** Must match registered URI exactly
- **State Parameter:** Not implemented (optional for local script)
- **PKCE:** Not implemented (not required for confidential clients)

---

## 7. Monitoring & Observability

### 7.1 Logging Strategy
**Log Levels:**
- **INFO:** Successful operations (token saved, post created)
- **WARNING:** Rate limits, retryable errors
- **ERROR:** Authentication failures, API errors

**Log Format:**
```
[TIMESTAMP] [LEVEL] [FUNCTION] Message
```

**Example:**
```
[2026-01-14 10:30:45] [INFO] [create_ugc_post] Post created successfully: urn:li:ugcPost:123456
[2026-01-14 10:31:02] [ERROR] [upload_image_binary] Upload failed: HTTP 413 - Image too large
```

### 7.2 Error Tracking
- All exceptions caught and logged with full traceback
- HTTP error responses include status code and response body
- Network errors include retry suggestions

### 7.3 Success Metrics
- Token acquisition success rate: Target 100%
- Image upload success rate: Target 100%
- Post creation success rate: Target 100%
- Average execution time: Target < 5 seconds

---

## 8. Documentation Requirements

### 8.1 README.md Sections
1. **Overview** - What the tool does
2. **Prerequisites** - Python version, LinkedIn app setup
3. **Installation** - Dependency installation steps
4. **Configuration** - `.env` setup instructions
5. **Usage** - Step-by-step commands
6. **Troubleshooting** - Common errors and solutions
7. **API Documentation** - Links to LinkedIn docs
8. **License** - MIT or similar

### 8.2 Code Documentation
- **Docstrings:** All functions documented with:
  - Purpose
  - Parameters with types
  - Return values with types
  - Raises (exceptions)
  - Example usage
- **Comments:** Complex logic explained inline
- **Type Hints:** All function signatures typed

**Example Function Docstring:**
```python
def register_image_upload(token: str, user_urn: str) -> tuple[str, str]:
    """
    Register an image upload with LinkedIn Assets API.

    Args:
        token: OAuth 2.0 access token
        user_urn: User's LinkedIn URN (e.g., "urn:li:person:abc123")

    Returns:
        Tuple of (asset_urn, upload_url)
        - asset_urn: URN of the registered asset
        - upload_url: URL to upload image binary

    Raises:
        requests.HTTPError: If API request fails
        ValueError: If response is missing required fields

    Example:
        >>> asset_urn, upload_url = register_image_upload(token, "urn:li:person:123")
        >>> print(asset_urn)
        urn:li:digitalmediaAsset:C5622AQHdBDflPp0pEg
    """
```

---

## 9. Constraints & Limitations

### 9.1 Technical Constraints
- **Python Version:** Requires Python 3.8+ (for type hints)
- **Network:** Requires active internet connection
- **Port:** Requires port 8080 available for OAuth callback
- **Browser:** Requires system default browser for OAuth flow

### 9.2 LinkedIn API Limitations
- **Image Size:** Max 36,152,320 pixels
- **Image Formats:** JPG, PNG, GIF only
- **Text Length:** Max 3000 characters
- **Rate Limits:** Not publicly documented (handle 429 responses)
- **Token Expiry:** Tokens expire after ~60 days

### 9.3 Feature Limitations (Out of Scope)
- ❌ Multiple image uploads (carousel posts)
- ❌ Video uploads
- ❌ Posting to organization pages
- ❌ Scheduling posts for future
- ❌ Post analytics/metrics
- ❌ Edit/delete existing posts
- ❌ Comment on posts
- ❌ GUI/web interface
- ❌ Configuration via CLI arguments (hardcoded for now)

---

## 10. Future Enhancements (Post-MVP)

### Phase 2 Features
- [ ] CLI argument support for image path and post text
- [ ] Support for multiple images (carousel posts)
- [ ] Support for video uploads
- [ ] Post scheduling functionality
- [ ] Configuration file for post templates

### Phase 3 Features
- [ ] Organization page posting support
- [ ] Interactive mode with prompts
- [ ] Bulk posting from CSV file
- [ ] Post analytics/metrics retrieval
- [ ] Web dashboard for monitoring

---

## 11. Dependencies & Prerequisites

### 11.1 Development Environment
- **Python:** 3.8 or higher
- **pip:** Latest version
- **Virtual Environment:** Recommended (venv or conda)

### 11.2 LinkedIn Developer Setup
1. Create LinkedIn Developer account at https://www.linkedin.com/developers/
2. Create new app
3. Add product: "Sign In with LinkedIn using OpenID Connect"
4. Add product: "Share on LinkedIn"
5. Configure OAuth 2.0 settings:
   - Redirect URLs: `http://localhost:8080/callback`
   - Scopes: `w_member_social`, `openid`, `profile`, `email`
6. Copy Client ID and Client Secret

### 11.3 Python Dependencies
```
requests>=2.31.0        # HTTP client
python-dotenv>=1.0.0    # Environment variable management
```

---

## 12. Rollout Plan

### Phase 1: Development (Week 1)
- [ ] Set up project structure
- [ ] Implement `get_token.py`
- [ ] Test OAuth flow end-to-end
- [ ] Implement `post_to_linkedin.py`
- [ ] Test image upload flow
- [ ] Test post creation flow

### Phase 2: Testing (Week 1-2)
- [ ] Execute all test cases (TC-1 through TC-7)
- [ ] Test edge cases
- [ ] Security review
- [ ] Code review

### Phase 3: Documentation (Week 2)
- [ ] Write comprehensive README.md
- [ ] Add code docstrings
- [ ] Create troubleshooting guide
- [ ] Add example images

### Phase 4: Release (Week 2)
- [ ] Create GitHub repository
- [ ] Tag v1.0.0 release
- [ ] Publish documentation
- [ ] Share with users

---

## 13. Success Criteria

### Definition of Done
- ✅ All test cases passing (TC-1 through TC-7)
- ✅ README.md complete and accurate
- ✅ All functions documented with docstrings
- ✅ Error handling for all API calls
- ✅ Security review passed
- ✅ Successfully posts image + text to LinkedIn
- ✅ Token stored securely with proper permissions
- ✅ Clean error messages for all failure scenarios

### Acceptance Criteria
- New user can complete first-time setup in < 5 minutes
- Post creation completes in < 10 seconds
- Zero credentials in source code or logs
- All security best practices followed
- Code is maintainable and well-documented

---

## 14. Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| LinkedIn API changes | High | Low | Monitor API changelog, version API calls |
| Token expiration during upload | Medium | Low | Check token before each API call |
| Rate limiting | Medium | Medium | Implement exponential backoff, respect 429 responses |
| Port 8080 already in use | Low | Medium | Detect port conflict, suggest alternatives |
| Image file too large | Low | Low | Validate file size before upload |
| Network timeout | Medium | Low | Set reasonable timeouts, retry logic |

---

## 15. Appendix

### 15.1 LinkedIn API Documentation Links
- [LinkedIn OAuth 2.0 Documentation](https://learn.microsoft.com/en-us/linkedin/shared/authentication/authentication)
- [Assets API (Vector Asset API)](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/vector-asset-api)
- [UGC Post API](https://learn.microsoft.com/en-us/linkedin/compliance/integrations/shares/ugc-post-api)
- [Posts API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api)

### 15.2 HTTP Status Code Reference
| Code | Meaning | Action |
|------|---------|--------|
| 200 | OK | Success - parse response |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Check payload structure |
| 401 | Unauthorized | Token invalid/expired - re-authenticate |
| 403 | Forbidden | Check app permissions/scopes |
| 413 | Payload Too Large | Reduce image size |
| 429 | Too Many Requests | Wait and retry with backoff |
| 500 | Internal Server Error | LinkedIn issue - retry later |
| 502 | Bad Gateway | LinkedIn issue - retry later |
| 503 | Service Unavailable | LinkedIn maintenance - retry later |

### 15.3 Glossary
- **URN:** Uniform Resource Name - LinkedIn's identifier format
- **UGC:** User Generated Content - LinkedIn's content posting API
- **OAuth 2.0:** Authorization framework for delegated access
- **Access Token:** Credential used to access protected resources
- **Asset:** Uploaded media file (image/video) on LinkedIn
- **Recipe:** LinkedIn's template for media processing

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-14 | System | Initial PRD generated from INITIAL.md |

---

## Approval

| Role | Name | Status | Date |
|------|------|--------|------|
| Product Owner | TBD | Pending | - |
| Tech Lead | TBD | Pending | - |
| Security | TBD | Pending | - |
