#!/usr/bin/env python3
"""
LinkedIn Image & Text Poster

This script posts an image with text to LinkedIn using the LinkedIn v2 API.
It handles the complete flow: loading token, uploading image, and creating post.

Usage:
    python post_to_linkedin.py

Requirements:
    - .user_token file (run get_token.py first)
    - test_image.jpg (or modify TEST_IMAGE_PATH)
"""

import os
import sys
import json
import time
from typing import Dict, Any, Tuple, Optional

import requests

# API Configuration
API_BASE = "https://api.linkedin.com"
USER_INFO_URL = f"{API_BASE}/v2/userinfo"
ASSETS_URL = f"{API_BASE}/v2/assets"
UGC_POSTS_URL = f"{API_BASE}/v2/ugcPosts"

# Required headers for all API calls
BASE_HEADERS = {
    "X-Restli-Protocol-Version": "2.0.0",
}

# Headers for Assets API
ASSETS_HEADERS = {
    **BASE_HEADERS,
    "LinkedIn-Version": "202501",
    "Content-Type": "application/json",
}

# Headers for UGC Posts API
UGC_HEADERS = {
    **BASE_HEADERS,
    "Content-Type": "application/json",
}

# Configuration
TOKEN_FILE = ".user_token"
TEST_IMAGE_PATH = "test_image.jpg"
TEST_POST_TEXT = "Testing LinkedIn API v2 image upload! 🚀"

# Image specifications
MAX_PIXELS = 36_152_320
MAX_TEXT_LENGTH = 3000
SUPPORTED_FORMATS = [".jpg", ".jpeg", ".png", ".gif"]


def load_token() -> Optional[str]:
    """
    Load access token from file.

    Returns:
        Access token string if successful, None otherwise

    Raises:
        FileNotFoundError: If token file doesn't exist
        json.JSONDecodeError: If token file is invalid
    """
    try:
        if not os.path.exists(TOKEN_FILE):
            print(f"❌ Error: No token found at {TOKEN_FILE}")
            print("   Please run: python get_token.py")
            return None

        with open(TOKEN_FILE, "r") as f:
            token_data = json.load(f)

        access_token = token_data.get("access_token")
        if not access_token:
            print(f"❌ Error: Token file is missing 'access_token' field")
            return None

        # Check if token might be expired (basic check)
        created_at = token_data.get("created_at", 0)
        expires_in = token_data.get("expires_in", 0)
        expires_at = created_at + expires_in

        if time.time() > expires_at:
            print("⚠️  Warning: Token appears to be expired")
            print("   If authentication fails, please run: python get_token.py")

        return access_token

    except json.JSONDecodeError:
        print(f"❌ Error: Token file {TOKEN_FILE} is corrupted")
        print("   Please run: python get_token.py")
        return None
    except Exception as e:
        print(f"❌ Error loading token: {e}")
        return None


def get_user_urn(token: str) -> Optional[str]:
    """
    Fetch user's URN via LinkedIn userinfo endpoint.

    Args:
        token: OAuth 2.0 access token

    Returns:
        User URN in format "urn:li:person:{id}" if successful, None otherwise

    Raises:
        requests.RequestException: If API request fails
    """
    headers = {
        **BASE_HEADERS,
        "Authorization": f"Bearer {token}",
    }

    try:
        print("👤 Fetching user information...")
        response = requests.get(USER_INFO_URL, headers=headers, timeout=30)

        if response.status_code == 200:
            user_info = response.json()
            sub = user_info.get("sub")

            if not sub:
                print("❌ Error: User info response missing 'sub' field")
                print(f"   Response: {response.text}")
                return None

            user_urn = f"urn:li:person:{sub}"
            print(f"✅ User URN: {user_urn}")
            return user_urn

        elif response.status_code == 401:
            print("❌ Error: Unauthorized (401)")
            print("   Your token is invalid or expired.")
            print("   Please run: python get_token.py")
            return None

        else:
            print(f"❌ Error: Failed to get user info (HTTP {response.status_code})")
            print(f"   Response: {response.text}")
            return None

    except requests.RequestException as e:
        print(f"❌ Network error: {e}")
        return None


def validate_image(image_path: str) -> bool:
    """
    Validate image file before upload.

    Args:
        image_path: Path to image file

    Returns:
        True if valid, False otherwise
    """
    # Check if file exists
    if not os.path.exists(image_path):
        print(f"❌ Error: Image file not found: {image_path}")
        return False

    # Check file extension
    _, ext = os.path.splitext(image_path.lower())
    if ext not in SUPPORTED_FORMATS:
        print(f"❌ Error: Unsupported image format: {ext}")
        print(f"   Supported formats: {', '.join(SUPPORTED_FORMATS)}")
        return False

    # Check file size (basic check - actual pixel count would require image library)
    file_size = os.path.getsize(image_path)
    if file_size > 50 * 1024 * 1024:  # 50MB rough limit
        print(f"❌ Error: Image file too large: {file_size / 1024 / 1024:.2f} MB")
        print("   Consider reducing image size")
        return False

    return True


def register_image_upload(token: str, user_urn: str) -> Optional[Tuple[str, str]]:
    """
    Register image upload with LinkedIn Assets API.

    Args:
        token: OAuth 2.0 access token
        user_urn: User's LinkedIn URN (e.g., "urn:li:person:abc123")

    Returns:
        Tuple of (asset_urn, upload_url) if successful, None otherwise
        - asset_urn: URN of the registered asset
        - upload_url: URL to upload image binary

    Raises:
        requests.RequestException: If API request fails
    """
    headers = {
        **ASSETS_HEADERS,
        "Authorization": f"Bearer {token}",
    }

    payload = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": user_urn,
            "serviceRelationships": [
                {
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent"
                }
            ],
            "supportedUploadMechanism": ["SYNCHRONOUS_UPLOAD"]
        }
    }

    try:
        print("\n📤 Registering image upload...")
        response = requests.post(
            f"{ASSETS_URL}?action=registerUpload",
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            value = data.get("value", {})

            asset_urn = value.get("asset")
            upload_mechanism = value.get("uploadMechanism", {})
            http_request = upload_mechanism.get("com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest", {})
            upload_url = http_request.get("uploadUrl")

            if not asset_urn or not upload_url:
                print("❌ Error: Response missing required fields")
                print(f"   Response: {response.text}")
                return None

            print(f"✅ Upload registered")
            print(f"   Asset URN: {asset_urn}")
            return (asset_urn, upload_url)

        elif response.status_code == 401:
            print("❌ Error: Unauthorized (401)")
            print("   Your token is invalid or expired.")
            print("   Please run: python get_token.py")
            return None

        elif response.status_code == 403:
            print("❌ Error: Forbidden (403)")
            print("   Check that your LinkedIn app has 'Share on LinkedIn' product enabled")
            print("   and the w_member_social scope is granted.")
            return None

        else:
            print(f"❌ Error: Failed to register upload (HTTP {response.status_code})")
            print(f"   Response: {response.text}")
            return None

    except requests.RequestException as e:
        print(f"❌ Network error: {e}")
        return None


def upload_image_binary(token: str, upload_url: str, image_path: str) -> bool:
    """
    Upload image binary to LinkedIn.

    Args:
        token: OAuth 2.0 access token
        upload_url: Upload URL from register_image_upload
        image_path: Path to image file

    Returns:
        True if upload successful, False otherwise

    Raises:
        requests.RequestException: If upload fails
    """
    headers = {
        "Authorization": f"Bearer {token}",
    }

    try:
        print("📷 Uploading image binary...")

        with open(image_path, "rb") as image_file:
            image_data = image_file.read()

        response = requests.put(
            upload_url,
            headers=headers,
            data=image_data,
            timeout=60
        )

        if response.status_code == 201:
            print("✅ Image uploaded successfully")
            return True

        elif response.status_code == 413:
            print("❌ Error: Image too large (413)")
            print(f"   Maximum pixels: {MAX_PIXELS:,}")
            return False

        else:
            print(f"❌ Error: Upload failed (HTTP {response.status_code})")
            print(f"   Response: {response.text}")
            return False

    except FileNotFoundError:
        print(f"❌ Error: Image file not found: {image_path}")
        return False
    except requests.RequestException as e:
        print(f"❌ Network error during upload: {e}")
        return False


def check_upload_status(token: str, asset_urn: str) -> bool:
    """
    Verify upload completion status.

    Args:
        token: OAuth 2.0 access token
        asset_urn: Asset URN from register_image_upload

    Returns:
        True if status is AVAILABLE, False otherwise

    Raises:
        requests.RequestException: If API request fails
    """
    # Extract asset ID from URN
    asset_id = asset_urn.split(":")[-1]

    headers = {
        **ASSETS_HEADERS,
        "Authorization": f"Bearer {token}",
    }

    try:
        print("🔍 Verifying upload status...")
        response = requests.get(
            f"{ASSETS_URL}/{asset_id}",
            headers=headers,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            status = data.get("status")

            if status == "AVAILABLE":
                print("✅ Upload verified - status: AVAILABLE")
                return True
            elif status == "PROCESSING":
                print("⏳ Status: PROCESSING (may need to wait)")
                return False
            elif status == "WAITING_UPLOAD":
                print("⏳ Status: WAITING_UPLOAD (upload may have failed)")
                return False
            else:
                print(f"⚠️  Unknown status: {status}")
                return False

        else:
            print(f"⚠️  Could not verify upload status (HTTP {response.status_code})")
            print("   Proceeding anyway...")
            return True  # Assume success if we can't verify

    except requests.RequestException as e:
        print(f"⚠️  Network error checking status: {e}")
        print("   Proceeding anyway...")
        return True  # Assume success if we can't verify


def create_ugc_post(token: str, user_urn: str, asset_urn: str, text: str) -> Optional[str]:
    """
    Create LinkedIn UGC post with image and text.

    Args:
        token: OAuth 2.0 access token
        user_urn: User's LinkedIn URN
        asset_urn: Asset URN of uploaded image
        text: Post text/commentary

    Returns:
        Post URN if successful, None otherwise

    Raises:
        requests.RequestException: If API request fails
    """
    # Validate text length
    if len(text) > MAX_TEXT_LENGTH:
        print(f"⚠️  Warning: Post text exceeds {MAX_TEXT_LENGTH} characters")
        print(f"   Truncating from {len(text)} to {MAX_TEXT_LENGTH} characters")
        text = text[:MAX_TEXT_LENGTH]

    headers = {
        **UGC_HEADERS,
        "Authorization": f"Bearer {token}",
    }

    payload = {
        "author": user_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "attributes": [],
                    "text": text
                },
                "shareMediaCategory": "IMAGE",
                "media": [
                    {
                        "status": "READY",
                        "media": asset_urn,
                        "title": {
                            "attributes": [],
                            "text": "Image"
                        }
                    }
                ]
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    try:
        print("\n🚀 Creating LinkedIn post...")
        response = requests.post(
            UGC_POSTS_URL,
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code == 201:
            post_urn = response.headers.get("x-restli-id")

            if post_urn:
                print("✅ Post created successfully!")
                return post_urn
            else:
                print("⚠️  Post created, but couldn't extract post ID from headers")
                return "unknown"

        elif response.status_code == 400:
            print("❌ Error: Bad Request (400)")
            print("   The request payload may be malformed.")
            print(f"   Response: {response.text}")
            return None

        elif response.status_code == 401:
            print("❌ Error: Unauthorized (401)")
            print("   Your token is invalid or expired.")
            print("   Please run: python get_token.py")
            return None

        elif response.status_code == 429:
            print("❌ Error: Rate Limited (429)")
            print("   You've made too many requests. Please wait before retrying.")
            return None

        else:
            print(f"❌ Error: Failed to create post (HTTP {response.status_code})")
            print(f"   Response: {response.text}")
            return None

    except requests.RequestException as e:
        print(f"❌ Network error: {e}")
        return None


def main():
    """Main function to orchestrate posting flow."""
    print("=" * 60)
    print("LinkedIn Image & Text Poster")
    print("=" * 60)

    # Step 1: Load token
    print("\n📁 Loading access token...")
    token = load_token()
    if not token:
        sys.exit(1)
    print("✅ Token loaded")

    # Step 2: Get user URN
    user_urn = get_user_urn(token)
    if not user_urn:
        sys.exit(1)

    # Step 3: Validate image
    print(f"\n🖼️  Validating image: {TEST_IMAGE_PATH}")
    if not validate_image(TEST_IMAGE_PATH):
        sys.exit(1)
    print("✅ Image validated")

    # Step 4: Register image upload
    result = register_image_upload(token, user_urn)
    if not result:
        sys.exit(1)

    asset_urn, upload_url = result

    # Step 5: Upload image binary
    if not upload_image_binary(token, upload_url, TEST_IMAGE_PATH):
        sys.exit(1)

    # Step 6: Verify upload status
    if not check_upload_status(token, asset_urn):
        print("⚠️  Upload status check inconclusive, proceeding anyway...")

    # Step 7: Create post
    print(f"\n📝 Post text: \"{TEST_POST_TEXT}\"")
    post_urn = create_ugc_post(token, user_urn, asset_urn, TEST_POST_TEXT)

    if not post_urn:
        sys.exit(1)

    # Success!
    print("\n" + "=" * 60)
    print("🎉 Success!")
    print("=" * 60)
    print(f"\n📍 Post URN: {post_urn}")

    # Construct post URL
    if post_urn != "unknown":
        post_url = f"https://www.linkedin.com/feed/update/{post_urn}"
        print(f"🔗 Post URL: {post_url}")
        print("\n💡 Visit the URL above to view your post on LinkedIn")
    else:
        print("\n💡 Check your LinkedIn feed to view the post")

    print("\n✨ You can run this script again to create another post")
    print("   (Modify TEST_IMAGE_PATH and TEST_POST_TEXT in the script)")


if __name__ == "__main__":
    main()
