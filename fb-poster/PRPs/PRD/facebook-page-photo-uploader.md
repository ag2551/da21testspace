# Product Requirement Document: Facebook Page Photo & Text Uploader

## 1. Overview

### 1.1 Feature Summary
A Python command-line tool that enables users to upload photos with text captions to Facebook Pages using the Facebook Graph API.

### 1.2 Goals
- Provide a simple, reliable way to programmatically post photos to Facebook Pages
- Support both local file uploads and remote URL-based uploads
- Handle authentication securely via environment variables
- Provide clear error messages and success confirmations

### 1.3 Target Users
- Social media managers automating content posting
- Developers integrating Facebook posting into applications
- Marketing teams scheduling photo content

---

## 2. User Stories

### Story 1: Upload Local Photo
**As a** social media manager
**I want to** upload a photo from my local filesystem to a Facebook Page
**So that** I can share visual content with my audience without using the Facebook web interface

**Acceptance Criteria:**
- Script accepts a local file path as input
- Photo is successfully uploaded to the specified Facebook Page
- Caption text appears with the photo
- Post ID and URL are returned for verification

### Story 2: Upload Photo from URL
**As a** developer
**I want to** upload a photo from a remote URL to a Facebook Page
**So that** I can share images hosted on CDNs or external sources without downloading them first

**Acceptance Criteria:**
- Script accepts a remote image URL as input
- Photo is fetched and uploaded to the Facebook Page
- Caption text appears with the photo
- Post ID and URL are returned for verification

### Story 3: Handle Authentication Errors
**As a** user
**I want to** receive clear error messages when my access token is invalid or expired
**So that** I can quickly identify and fix authentication issues

**Acceptance Criteria:**
- Expired tokens produce a clear error message
- Invalid tokens produce a clear error message
- Missing credentials produce helpful guidance

### Story 4: Handle Upload Errors
**As a** user
**I want to** receive informative error messages when uploads fail
**So that** I can understand and resolve issues (e.g., file too large, unsupported format)

**Acceptance Criteria:**
- File size limits are checked and reported
- Unsupported file formats are detected
- Network errors are caught and reported
- API rate limits are handled gracefully

---

## 3. Technical Specification

### 3.1 Technology Stack
- **Language**: Python 3.8+
- **HTTP Library**: `requests`
- **Environment Management**: `python-dotenv`
- **API**: Facebook Graph API v19.0+

### 3.2 Dependencies
```
requests>=2.31.0
python-dotenv>=1.0.0
```

### 3.3 Architecture

#### 3.3.1 File Structure
```
fb-poster/
├── .env                    # Environment variables (gitignored)
├── .env.example           # Template for environment variables
├── requirements.txt       # Python dependencies
├── fb_uploader.py        # Main script
└── README.md             # Usage documentation
```

#### 3.3.2 Environment Variables
```
FB_PAGE_ID=<your_page_id>
FB_PAGE_ACCESS_TOKEN=<your_long_lived_page_access_token>
```

### 3.4 API Integration

#### 3.4.1 Endpoint
```
POST https://graph.facebook.com/v19.0/{page-id}/photos
```

#### 3.4.2 Request Format - Local File Upload
```python
files = {
    'source': open(image_path, 'rb')
}
data = {
    'message': caption,
    'access_token': access_token
}
response = requests.post(url, files=files, data=data)
```

#### 3.4.3 Request Format - Remote URL Upload
```python
data = {
    'url': image_url,
    'message': caption,
    'access_token': access_token
}
response = requests.post(url, data=data)
```

#### 3.4.4 Success Response
```json
{
  "id": "photo_id",
  "post_id": "page_id_post_id"
}
```

#### 3.4.5 Error Response
```json
{
  "error": {
    "message": "Error message",
    "type": "OAuthException",
    "code": 190
  }
}
```

---

## 4. Implementation Plan

### 4.1 Files to Create

#### File 1: `.env.example`
**Purpose**: Template for users to set up their credentials
**Content**:
```
FB_PAGE_ID=your_page_id_here
FB_PAGE_ACCESS_TOKEN=your_page_access_token_here
```

#### File 2: `requirements.txt`
**Purpose**: Python dependencies
**Content**:
```
requests>=2.31.0
python-dotenv>=1.0.0
```

#### File 3: `fb_uploader.py`
**Purpose**: Main implementation script

**Key Functions**:

1. **`load_credentials()`**
   - Load environment variables using `python-dotenv`
   - Validate that required variables exist
   - Return page_id and access_token

2. **`validate_local_file(image_path)`**
   - Check file exists
   - Verify file size (max 4MB for photos)
   - Validate file extension (.jpg, .jpeg, .png, .gif)
   - Return boolean and error message

3. **`upload_photo_local(page_id, access_token, image_path, caption)`**
   - Construct API endpoint URL
   - Prepare multipart/form-data request
   - Send POST request with file
   - Parse and return response

4. **`upload_photo_url(page_id, access_token, image_url, caption)`**
   - Construct API endpoint URL
   - Prepare form data with URL
   - Send POST request
   - Parse and return response

5. **`handle_response(response)`**
   - Parse JSON response
   - Extract photo_id and post_id
   - Construct post URL
   - Handle API errors with clear messages
   - Return success/failure status and data

6. **`main()`**
   - Parse command-line arguments (image source, caption, upload type)
   - Load credentials
   - Validate input
   - Call appropriate upload function
   - Display results

**Command-line Interface**:
```bash
# Local file upload
python fb_uploader.py --file path/to/image.jpg --caption "My photo caption"

# URL upload
python fb_uploader.py --url https://example.com/image.jpg --caption "My photo caption"
```

#### File 4: `README.md`
**Purpose**: Documentation and usage guide

**Sections**:
- Overview
- Prerequisites
- Installation
- Configuration
- Usage Examples
- Troubleshooting
- API Token Generation Guide

---

## 5. Error Handling

### 5.1 Authentication Errors
| Error Code | Error Type | Message | User Action |
|------------|-----------|---------|-------------|
| 190 | OAuthException | Access token expired | Regenerate long-lived token |
| 190 | OAuthException | Invalid access token | Verify token in .env file |
| 200 | PermissionsError | Missing publish permission | Request pages_manage_posts permission |

### 5.2 File Upload Errors
| Error | Message | User Action |
|-------|---------|-------------|
| File not found | Image file does not exist at path: {path} | Check file path |
| File too large | Image exceeds 4MB limit: {size}MB | Compress image |
| Invalid format | Unsupported file type: {ext}. Use jpg, png, or gif | Convert image format |
| Network error | Failed to connect to Facebook API | Check internet connection |

### 5.3 API Errors
| Error Code | Meaning | Handling |
|------------|---------|----------|
| 100 | Invalid parameter | Display which parameter is invalid |
| 368 | Temporarily blocked | Suggest retry after waiting |
| 4 | Rate limit | Display retry-after time |
| 190 | Token issue | Prompt for token refresh |

---

## 6. Security Considerations

### 6.1 Credential Management
- Store credentials in `.env` file
- Add `.env` to `.gitignore`
- Never hardcode tokens in source code
- Use long-lived tokens (60 days) instead of short-lived

### 6.2 Input Validation
- Validate file paths to prevent directory traversal
- Sanitize URLs to prevent injection attacks
- Limit file sizes to prevent memory issues
- Verify MIME types match extensions

### 6.3 Token Permissions
**Required Permissions**:
- `pages_manage_posts` - To publish content to Pages
- `pages_read_engagement` - To verify post creation (optional)

**Token Type**: Page Access Token (not User Access Token)

---

## 7. Verification Steps

### 7.1 Unit Testing
Create `test_fb_uploader.py` to verify:

**Test 1: Credential Loading**
- Valid .env file loads correctly
- Missing credentials raise appropriate errors
- Empty credentials are detected

**Test 2: File Validation**
- Existing files pass validation
- Non-existent files fail validation
- Oversized files are rejected
- Invalid formats are rejected

**Test 3: API Response Parsing**
- Success responses are parsed correctly
- Error responses are handled gracefully
- Network errors are caught
- Malformed JSON is handled

### 7.2 Integration Testing

**Test 1: Upload Local Photo**
```bash
python fb_uploader.py --file test_image.jpg --caption "Test post"
```
**Expected**:
- Photo appears on Facebook Page
- Caption matches input
- Post ID and URL are displayed
- No errors in console

**Test 2: Upload from URL**
```bash
python fb_uploader.py --url https://picsum.photos/800/600 --caption "URL test"
```
**Expected**:
- Photo from URL appears on Page
- Caption matches input
- Post ID and URL are displayed

**Test 3: Handle Expired Token**
- Use an expired token
- Run upload command
**Expected**:
- Clear error message about token expiration
- Guidance on refreshing token

**Test 4: Handle Invalid File**
```bash
python fb_uploader.py --file nonexistent.jpg --caption "Test"
```
**Expected**:
- Error message indicating file not found
- Script exits gracefully

**Test 5: Handle Large File**
- Attempt to upload file > 4MB
**Expected**:
- Error message about file size
- Actual size displayed

### 7.3 Manual Verification Checklist

After implementation, verify:

- [ ] Photos appear correctly on Facebook Page timeline
- [ ] Captions are properly formatted (line breaks, emojis work)
- [ ] Post URLs are clickable and correct
- [ ] Both local and URL uploads work
- [ ] Error messages are clear and actionable
- [ ] `.env.example` provides clear setup instructions
- [ ] README.md includes token generation steps
- [ ] Script works on Windows, macOS, and Linux
- [ ] No credentials are committed to git
- [ ] Dependencies install without conflicts

### 7.4 End-to-End Test Scenario

**Scenario**: First-time user setup and photo upload

1. Clone repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env`
4. Add Facebook Page credentials to `.env`
5. Run: `python fb_uploader.py --file photo.jpg --caption "Hello World"`
6. Verify photo appears on Facebook Page
7. Verify console shows success message with post URL
8. Click post URL and confirm it opens correct post

**Success Criteria**: User completes all steps without errors and photo appears on Page with correct caption.

---

## 8. Future Enhancements (Out of Scope)

- Schedule posts for future publication
- Upload multiple photos (carousel posts)
- Add photo tagging and location
- Support video uploads
- Batch upload from directory
- Edit/delete existing posts
- Analytics and engagement metrics
- GUI interface

---

## 9. Success Metrics

- **Functionality**: 100% success rate for valid inputs
- **Error Handling**: All error cases display helpful messages
- **Documentation**: New users can set up and use tool in < 10 minutes
- **Reliability**: API rate limits are respected
- **Security**: No credentials exposed in code or logs

---

## 10. Documentation Requirements

### 10.1 README.md Must Include
- Prerequisites (Python version, Facebook Page requirements)
- Step-by-step setup instructions
- How to generate Page Access Token
- Usage examples for both upload methods
- Troubleshooting common issues
- API rate limit information
- License and contribution guidelines

### 10.2 Code Documentation
- Docstrings for all functions
- Inline comments for complex logic
- Type hints for function parameters
- Example usage in function docstrings

### 10.3 .env.example
- Clear variable names
- Comments explaining each variable
- Links to Facebook developer documentation
- Token generation instructions

---

## 11. Acceptance Criteria

This PRD is complete when:

1. All files listed in Implementation Plan are created
2. Script successfully uploads photos using both methods
3. All error cases are handled gracefully
4. Verification steps all pass
5. Documentation is complete and accurate
6. No credentials are hardcoded or committed
7. Code follows Python best practices (PEP 8)
8. Dependencies are minimal and well-maintained

---

## Appendix A: Facebook Graph API Reference

**Endpoint Documentation**: https://developers.facebook.com/docs/graph-api/reference/page/photos/

**Required Fields**:
- `source` (file) or `url` (string): The photo content
- `message` (string): Photo caption (optional but recommended)
- `access_token` (string): Page access token

**Optional Fields**:
- `published` (boolean): Whether to publish immediately (default: true)
- `temporary` (boolean): For temporary profile pictures
- `targeting` (object): Audience targeting

**Response Fields**:
- `id`: Photo ID
- `post_id`: Full post ID (page_id_photo_id)

## Appendix B: Token Generation Guide

1. Go to https://developers.facebook.com/tools/explorer/
2. Select your app
3. Click "Generate Access Token"
4. Grant permissions: `pages_manage_posts`, `pages_read_engagement`
5. Copy User Access Token
6. Use Graph API Explorer to get Page Access Token:
   ```
   GET /me/accounts
   ```
7. Copy the `access_token` for your target Page
8. Extend token to long-lived (60 days):
   ```
   GET /oauth/access_token?grant_type=fb_exchange_token&client_id={app_id}&client_secret={app_secret}&fb_exchange_token={short_lived_token}
   ```
