## FEATURE
Facebook Page Photo & Text Uploader

## GOAL
Create a Python script that uploads a photo with a text caption to a specific Facebook Page using the Graph API.

## CONTEXT & DEPENDENCIES
- **Target Platform**: Facebook Graph API (v19.0 or latest)
- **Library**: `requests` (Direct HTTP calls are preferred over outdated SDKs)
- **Auth**: Page Access Token (Long-lived)

## REQUIRED FILES

### 1. `.env`
- `FB_PAGE_ID`
- `FB_PAGE_ACCESS_TOKEN`

### 2. `fb_uploader.py`
- **Functionality**:
  - Load credentials from `.env`.
  - Accept `image_path` and `caption` as arguments.
  - **Logic**:
    - Endpoint: `https://graph.facebook.com/{page_id}/photos`
    - Method: POST
    - **For local file upload**:
      - `files={'source': open(image_path, 'rb')}`
      - `data={'message': caption, 'access_token': token}`
    - **For remote URL upload** (alternative):
      - `data={'url': image_url, 'message': caption, 'access_token': token}`
  - Handle errors (e.g., Token expired, Image too large).
  - Print the resulting Post ID and URL.

## EXAMPLES
- Local file: `requests.post(url, files={'source': open(image_path, 'rb')}, data={'message': caption, 'access_token': token})`
- Remote URL: `requests.post(url, data={'url': image_url, 'message': caption, 'access_token': token})`