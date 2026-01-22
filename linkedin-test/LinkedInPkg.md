## FEATURE
LinkedIn Image Uploader Using Official Python Client

## GOAL
Create two Python scripts that use the official `linkedin-api-python-client` package for OAuth and API operations, while handling image upload with custom code where the package doesn't provide support.

## CONTEXT & DEPENDENCIES
- Language: Python 3
- Required Packages:
  - `linkedin-api>=0.2.0` (Official LinkedIn API client)
  - `requests>=2.31.0` (For custom image upload operations)
  - `python-dotenv>=1.0.0` (Environment variable management)
- Env file: `.env` contains `LINKEDIN_CLIENT_ID` and `LINKEDIN_CLIENT_SECRET`
- Local callback server: `http://localhost:8080/callback` must be registered in LinkedIn app settings

## PACKAGE OVERVIEW

### linkedin-api-python-client
The official Python client provides two main classes:
- **AuthClient**: Handles OAuth 2.0 authorization flow, token exchange, and refresh
- **RestliClient**: Makes Rest.li protocol API requests with automatic protocol compliance

**Package Status:** Beta (subject to breaking changes)

### What the Package Handles
- OAuth 2.0 authorization URL generation with scopes
- Authorization code exchange for access token
- Automatic Rest.li protocol header management (`X-Restli-Protocol-Version: 2.0.0`)
- API GET/POST/PUT/DELETE requests with typed responses
- Token introspection and refresh logic

### What Requires Custom Implementation
- Assets API image registration (package has no media upload methods)
- Binary image upload to pre-signed URLs
- Upload status verification
- UGC Posts API with image media (not exposed by package)
- LinkedIn-Version header for Assets API (must set manually)

## REQUIRED API HEADERS

All custom requests MUST include:
- `Authorization: Bearer {ACCESS_TOKEN}`
- `X-Restli-Protocol-Version: 2.0.0` (**MANDATORY** - API calls will fail without this)
- `Content-Type: application/json` (except for binary upload)
- `LinkedIn-Version: 202501` (Format: YYYYMM - required for Assets API)

## IMAGE SPECIFICATIONS
- **Supported formats:** JPG, PNG, GIF
- **Max pixels:** 36,152,320 pixels
- **Post text limit:** 3000 characters
- **GIF frames:** Up to 250 frames

## REQUIRED SCRIPTS

### 1. `get_token_pkg.py` (OAuth Helper Using Package)

This script uses `AuthClient` from `linkedin-api-python-client` to simplify OAuth flow.

**Flow:**
1. Initialize `AuthClient` with `client_id`, `client_secret`, and `redirect_url` from `.env`
2. Call `AuthClient.generate_member_auth_url()` with scopes: `w_member_social`, `openid`, `profile`, `email`
3. Open the system browser automatically to the authorization URL
4. Spin up temporary local server (localhost:8080) to catch the callback
   - **Important:** `http://localhost:8080/callback` must be registered in LinkedIn app's redirect URLs
5. Extract `authorization_code` from callback parameters
6. Call `AuthClient.exchange_auth_code_for_access_token(code)` to get token response
7. Save token response to `.user_token` file (JSON format)
   - **Security:** Add `.user_token` to `.gitignore` and set file permissions (chmod 600 on Unix)
   - **Note:** Store `access_token`, `expires_in`, `scope`, and `created_at` timestamp

**Expected Token Response Structure:**
- `access_token` (string): The OAuth 2.0 access token
- `expires_in` (int): Seconds until token expires (typically ~60 days)
- `scope` (string): Granted permission scopes
- Token should be saved with `created_at` timestamp for expiration checking

### 2. `post_to_linkedin_pkg.py` (Hybrid Posting Logic)

This script combines `RestliClient` for simple API calls with custom requests for image handling.

**Inputs:** Hardcode test image path (e.g., `test_image.jpg`) and test text string for now.

**Logic:**

1. **Load Token:** Read `access_token` from `.user_token` file

2. **Get User URN (Using RestliClient):**
   - Initialize `RestliClient` instance
   - Call `restli_client.get(resource_path="/userinfo", access_token=token)`
   - Extract `sub` field from response entity (e.g., `"abc123"`)
   - Format as URN: `urn:li:person:{sub}` (e.g., `urn:li:person:abc123`)

3. **Image Upload Flow (Custom requests - Crucial):**

   **Step A: Register the upload**
   - **Method:** `requests.post()`
   - **Endpoint:** `POST https://api.linkedin.com/v2/assets?action=registerUpload`
   - **Headers:** Authorization, X-Restli-Protocol-Version: 2.0.0, LinkedIn-Version: 202501, Content-Type: application/json
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
   - **Response:** Extract `asset` URN and `uploadUrl` from `value` object

   **Step B: Upload binary image**
   - **Method:** `requests.put()`
   - **URL:** Use `uploadUrl` from Step A
   - **Headers:** `Authorization: Bearer {TOKEN}` only (no Content-Type)
   - **Body:** Binary image data (use `open(image_path, 'rb').read()`)
   - **Expected Response:** HTTP 201 Created

   **Step C: Verify upload status** (Recommended before posting)
   - **Method:** `requests.get()`
   - **Endpoint:** `GET https://api.linkedin.com/v2/assets/{ASSET_ID}`
   - **Headers:** Authorization, X-Restli-Protocol-Version: 2.0.0, LinkedIn-Version: 202501
   - **Extract asset ID:** Parse from asset URN (last segment after colon)
   - **Check:** Verify `status: "AVAILABLE"` in response
   - **Why:** Prevents creating posts with failed/processing images

4. **Create Post (Custom requests):**
   - **Method:** `requests.post()`
   - **Endpoint:** `POST https://api.linkedin.com/v2/ugcPosts`
   - **Headers:** Authorization, X-Restli-Protocol-Version: 2.0.0, Content-Type: application/json
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

5. **Print Success:** Format and display post URL: `https://www.linkedin.com/feed/update/{POST_ID}`

## ERROR HANDLING

Handle these HTTP status codes gracefully:
- **400** - Bad Request (malformed payload, check JSON structure)
- **401** - Unauthorized (invalid/expired token, re-authenticate)
- **403** - Forbidden (insufficient permissions, check scopes and product access)
- **413** - Payload Too Large (image exceeds size limits)
- **429** - Rate Limited (implement exponential backoff)
- **500/502/503** - Server errors (retry with backoff)

## EXPECTED API RESPONSES

### AuthClient Token Exchange Response:
```json
{
  "access_token": "AQVdw...",
  "expires_in": 5183999,
  "scope": "w_member_social,openid,profile,email"
}
```

### RestliClient User Info Response:
The response entity contains:
```json
{
  "sub": "abc123xyz",
  "name": "John Doe",
  "email": "john@example.com"
}
```

### Register Upload Response (Custom):
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

### UGC Post Response (Custom):
- **Status Code:** 201 Created
- **Header:** `x-restli-id` contains the post URN/ID
- **Body:** May be empty or contain post details

## IMPLEMENTATION TIPS

### Using linkedin-api-python-client
- Import `AuthClient` from `linkedin_api.clients.auth.client`
- Import `RestliClient` from `linkedin_api.clients.restli.client`
- AuthClient methods return response objects with properties like `access_token`, `expires_in`
- RestliClient methods return response objects with `entity`, `status_code`, `headers` properties
- Both clients handle Rest.li protocol headers automatically
- Token refresh can be handled via `AuthClient.exchange_refresh_token_for_access_token()`

### Custom requests for Image Upload
- Always include the required headers (especially `X-Restli-Protocol-Version: 2.0.0` and `LinkedIn-Version: 202501`)
- Use `SYNCHRONOUS_UPLOAD` to ensure image is processed before creating post
- Extract the asset URN from Step A response - you'll need it for Step 4
- Check HTTP status codes before proceeding to next step
- Print detailed error messages including response body for debugging

### General Guidelines
- Check token expiration before API calls: `current_time > created_at + expires_in`
- Use `requests.post()` and `requests.put()` for custom API calls
- Validate image format and size before upload
- Verify upload status is AVAILABLE before creating post

## BENEFITS OF PACKAGE APPROACH

**Advantages:**
- Official LinkedIn support and maintenance
- Automatic Rest.li protocol compliance
- Reduced OAuth boilerplate code
- Token refresh capabilities built-in
- Type-safe response handling
- Future LinkedIn API updates benefit from package maintenance

**Trade-offs:**
- Additional ~10 package dependencies (vs 2 in custom approach)
- Package is in beta (subject to breaking changes)
- Still requires custom code for 80% of image posting workflow
- Hybrid approach mixing package and custom requests
- Learning curve for Rest.li client patterns

## COMPARISON WITH CUSTOM IMPLEMENTATION

| Aspect | Custom Implementation | Package-Based |
|--------|----------------------|---------------|
| OAuth Code | ~100 lines | ~50 lines (AuthClient) |
| User Info API | Custom requests | RestliClient.get() |
| Image Upload | Custom requests (~250 lines) | Custom requests (~250 lines) - same |
| Total Dependencies | 2 packages | ~12 packages |
| Package Stability | Stable (requests) | Beta (linkedin-api) |
| Total Lines | ~550 | ~500 |
| Maintenance | Your code only | Package + your code |

## SUCCESS CRITERIA

After implementation, verify:
- [ ] OAuth flow opens browser and captures callback successfully
- [ ] Token saved with correct structure (`access_token`, `expires_in`, `scope`, `created_at`)
- [ ] RestliClient retrieves user URN from `/v2/userinfo`
- [ ] Assets API registers upload and returns asset URN + upload URL
- [ ] Binary image uploads successfully (HTTP 201)
- [ ] Upload status verification shows AVAILABLE
- [ ] UGC post created with image (HTTP 201)
- [ ] Post URL accessible on LinkedIn
- [ ] Image and text display correctly in LinkedIn feed

## MIGRATION NOTES

If refactoring from existing custom implementation:
1. Install `linkedin-api` package
2. Replace OAuth URL construction with `AuthClient.generate_member_auth_url()`
3. Replace token exchange with `AuthClient.exchange_auth_code_for_access_token()`
4. Replace user info API call with `RestliClient.get()`
5. Keep all image upload code unchanged (Assets API, binary upload, status check, UGC post)
6. Update error handling to work with both RestliClient responses and raw requests responses

## SECURITY CONSIDERATIONS
- Store `.user_token` securely with restricted file permissions (chmod 600)
- Add `.user_token` to `.gitignore`
- Never commit credentials or tokens to version control
- Implement token expiration checking before API calls
- Consider implementing automatic token refresh for production use

## REFERENCES
- [linkedin-api-python-client GitHub Repository](https://github.com/linkedin-developers/linkedin-api-python-client)
- [LinkedIn Assets API Documentation](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/images-api)
- [LinkedIn UGC Posts API](https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/share-on-linkedin)
- [LinkedIn OAuth 2.0 Documentation](https://learn.microsoft.com/en-us/linkedin/shared/authentication/authentication)
