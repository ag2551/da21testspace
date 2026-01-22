## FEATURE
Simple Python LinkedIn Uploader (Image + Text)

## GOAL
Create two Python scripts to handle LinkedIn authentication and content posting.

## CONTEXT & DEPENDENCIES
- Language: Python 3
- Libraries available: `requests`, `python-dotenv`, `os`, `json`, `webbrowser`, `http.server` (standard lib).
- Env file: `.env` contains `LINKEDIN_CLIENT_ID` and `LINKEDIN_CLIENT_SECRET`.

## REQUIRED API HEADERS
All LinkedIn API v2 calls MUST include:
- `Authorization: Bearer {ACCESS_TOKEN}`
- `X-Restli-Protocol-Version: 2.0.0` (**MANDATORY** - API calls will fail without this)
- `Content-Type: application/json`
- `LinkedIn-Version: 202501` (Format: YYYYMM - required for Assets API)

## IMAGE SPECIFICATIONS
- **Supported formats:** JPG, PNG, GIF
- **Max pixels:** 36,152,320 pixels
- **Post text limit:** 3000 characters
- **GIF frames:** Up to 250 frames

## REQUIRED SCRIPTS

### 1. `get_token.py` (OAuth Helper)
This script is for one-time setup to get the `access_token`.
- **Flow**:
  1. Construct the Authorization URL with scope: `w_member_social`, `openid`, `profile`, `email`.
  2. Open the system browser automatically to let user login.
  3. Spin up a temporary local server (localhost:8080) to catch the "callback" from LinkedIn.
     - **Important:** `http://localhost:8080/callback` must be registered in your LinkedIn app's "Authorized redirect URLs" settings.
  4. Exchange the `authorization_code` for an `access_token`.
  5. Save the token to a file named `.user_token` (do not commit this file).
     - **Security:** Add `.user_token` to `.gitignore` and set file permissions (chmod 600 on Unix).
     - **Note:** Tokens expire - implement refresh token logic or re-authenticate when expired.

### 2. `post_to_linkedin.py` (Main Logic)
This script reads the token and posts content.
- **Inputs**: Hardcode a test image path (e.g., `test_image.jpg`) and a test text string for now.
- **Logic**:
  1. Load `access_token` from `.user_token`.

  2. Get the user's URN (ID) via `/v2/userinfo` endpoint.
     - **Endpoint:** `GET https://api.linkedin.com/v2/userinfo`
     - **Response:** Returns `sub` field (e.g., `"abc123"`)
     - **Format as URN:** `urn:li:person:{sub}` (e.g., `urn:li:person:abc123`)

  3. **Image Upload Flow (Crucial)**:
     - **Step A: Register the upload**
       - **Endpoint:** `POST https://api.linkedin.com/v2/assets?action=registerUpload`
       - **Payload:**
         ```json
         {
           "registerUploadRequest": {
             "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
             "owner": "urn:li:person:{USER_URN}",
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
       - **Response:** Save `asset` URN and `uploadUrl` from response.

     - **Step B: Upload binary image**
       - **Method:** `PUT` to the `uploadUrl` from Step A
       - **Headers:** `Authorization: Bearer {TOKEN}` only (no Content-Type)
       - **Body:** Binary image data (use `open(image_path, 'rb')`)
       - **Expected Response:** HTTP 201 Created

     - **Step C: Verify upload status** (Recommended before posting)
       - **Endpoint:** `GET https://api.linkedin.com/v2/assets/{ASSET_ID}`
       - **Check:** Verify `status: "AVAILABLE"` in response
       - **Why:** Prevents creating posts with failed/processing images

  4. **Create Post**:
     - **Endpoint:** `POST https://api.linkedin.com/v2/ugcPosts`
     - **Payload:**
       ```json
       {
         "author": "urn:li:person:{USER_URN}",
         "lifecycleState": "PUBLISHED",
         "specificContent": {
           "com.linkedin.ugc.ShareContent": {
             "shareCommentary": {
               "attributes": [],
               "text": "Your post text here (max 3000 chars)"
             },
             "shareMediaCategory": "IMAGE",
             "media": [
               {
                 "status": "READY",
                 "media": "urn:li:digitalmediaAsset:{ASSET_ID}",
                 "title": {
                   "attributes": [],
                   "text": "Image title"
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
     - **Expected Response:** HTTP 201 Created
     - **Post ID:** Found in response header `x-restli-id`

  5. Print the URL of the new post upon success.
     - **Format:** `https://www.linkedin.com/feed/update/{POST_ID}`

## ERROR HANDLING
Handle these HTTP status codes gracefully:
- **400** - Bad Request (malformed payload, check JSON structure)
- **401** - Unauthorized (invalid/expired token, re-authenticate)
- **403** - Forbidden (insufficient permissions, check scopes)
- **413** - Payload Too Large (image exceeds size limits)
- **429** - Rate Limited (implement exponential backoff)
- **500/502/503** - Server errors (retry with backoff)

## EXPECTED API RESPONSES

### Register Upload Response:
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

### UGC Post Response:
- **Status Code:** 201 Created
- **Header:** `x-restli-id` contains the post URN/ID
- **Body:** May be empty or contain post details

### User Info Response:
```json
{
  "sub": "abc123xyz",
  "name": "John Doe",
  "email": "john@example.com"
}
```

## IMPLEMENTATION TIPS
- Use `requests.post()` and `requests.put()` for API calls.
- Always include the required headers (especially `X-Restli-Protocol-Version: 2.0.0`).
- Use `SYNCHRONOUS_UPLOAD` to ensure image is processed before creating post.
- Extract the asset URN from Step A response - you'll need it for Step 4.
- Check HTTP status codes before proceeding to next step.
- Print detailed error messages including response body for debugging.