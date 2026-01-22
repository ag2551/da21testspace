#!/usr/bin/env python3
"""
Facebook Page Photo Uploader
Uploads photos with captions to Facebook Pages using the Graph API.
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
import requests
from dotenv import load_dotenv


# Constants
API_VERSION = "v19.0"
MAX_FILE_SIZE_MB = 4
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif'}


def load_credentials() -> Tuple[str, str]:
    """
    Load Facebook credentials from environment variables.

    Returns:
        Tuple of (page_id, access_token)

    Raises:
        SystemExit: If required credentials are missing

    Example:
        >>> page_id, token = load_credentials()
    """
    load_dotenv()

    page_id = os.getenv('FB_PAGE_ID')
    access_token = os.getenv('FB_PAGE_ACCESS_TOKEN')

    if not page_id or not access_token:
        print("Error: Missing credentials in .env file")
        print("\nRequired environment variables:")
        print("  - FB_PAGE_ID")
        print("  - FB_PAGE_ACCESS_TOKEN")
        print("\nPlease copy .env.example to .env and fill in your credentials.")
        print("See README.md for instructions on generating tokens.")
        sys.exit(1)

    if page_id == 'your_page_id_here' or access_token == 'your_page_access_token_here':
        print("Error: Please replace placeholder values in .env file")
        print("Current values appear to be from .env.example template")
        sys.exit(1)

    return page_id, access_token


def validate_local_file(image_path: str) -> Tuple[bool, Optional[str]]:
    """
    Validate that a local image file is suitable for upload.

    Args:
        image_path: Path to the local image file

    Returns:
        Tuple of (is_valid, error_message)
        error_message is None if valid

    Example:
        >>> valid, error = validate_local_file('photo.jpg')
        >>> if not valid:
        ...     print(f"Validation failed: {error}")
    """
    file_path = Path(image_path)

    # Check if file exists
    if not file_path.exists():
        return False, f"Image file does not exist at path: {image_path}"

    if not file_path.is_file():
        return False, f"Path is not a file: {image_path}"

    # Check file extension
    ext = file_path.suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file type: {ext}. Use jpg, jpeg, png, or gif"

    # Check file size
    file_size_bytes = file_path.stat().st_size
    file_size_mb = file_size_bytes / (1024 * 1024)

    if file_size_mb > MAX_FILE_SIZE_MB:
        return False, f"Image exceeds {MAX_FILE_SIZE_MB}MB limit: {file_size_mb:.2f}MB"

    return True, None


def upload_photo_local(
    page_id: str,
    access_token: str,
    image_path: str,
    caption: str
) -> requests.Response:
    """
    Upload a local photo file to a Facebook Page.

    Args:
        page_id: Facebook Page ID
        access_token: Page access token
        image_path: Path to local image file
        caption: Text caption for the photo

    Returns:
        requests.Response object

    Example:
        >>> response = upload_photo_local(page_id, token, 'photo.jpg', 'My caption')
        >>> if response.status_code == 200:
        ...     print("Upload successful!")
    """
    url = f"https://graph.facebook.com/{API_VERSION}/{page_id}/photos"

    try:
        with open(image_path, 'rb') as image_file:
            files = {'source': image_file}
            data = {
                'message': caption,
                'access_token': access_token
            }

            response = requests.post(url, files=files, data=data, timeout=30)
            return response

    except IOError as e:
        print(f"Error: Failed to read image file: {e}")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to connect to Facebook API: {e}")
        print("Please check your internet connection and try again.")
        sys.exit(1)


def upload_photo_url(
    page_id: str,
    access_token: str,
    image_url: str,
    caption: str
) -> requests.Response:
    """
    Upload a photo from a remote URL to a Facebook Page.

    Args:
        page_id: Facebook Page ID
        access_token: Page access token
        image_url: URL of the remote image
        caption: Text caption for the photo

    Returns:
        requests.Response object

    Example:
        >>> response = upload_photo_url(page_id, token, 'https://example.com/pic.jpg', 'Caption')
        >>> if response.status_code == 200:
        ...     print("Upload successful!")
    """
    url = f"https://graph.facebook.com/{API_VERSION}/{page_id}/photos"

    data = {
        'url': image_url,
        'message': caption,
        'access_token': access_token
    }

    try:
        response = requests.post(url, data=data, timeout=30)
        return response

    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to connect to Facebook API: {e}")
        print("Please check your internet connection and try again.")
        sys.exit(1)


def handle_response(response: requests.Response) -> Dict[str, Any]:
    """
    Parse and handle the API response.

    Args:
        response: requests.Response object from the API call

    Returns:
        Dictionary containing response data

    Raises:
        SystemExit: If the API returned an error

    Example:
        >>> result = handle_response(response)
        >>> print(f"Photo ID: {result['id']}")
        >>> print(f"Post URL: {result['post_url']}")
    """
    try:
        response_data = response.json()
    except ValueError:
        print(f"Error: Invalid response from Facebook API")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        sys.exit(1)

    # Handle error responses
    if 'error' in response_data:
        error = response_data['error']
        error_code = error.get('code', 'Unknown')
        error_type = error.get('type', 'Unknown')
        error_message = error.get('message', 'No message provided')

        print(f"\nFacebook API Error:")
        print(f"  Type: {error_type}")
        print(f"  Code: {error_code}")
        print(f"  Message: {error_message}")

        # Provide helpful guidance based on error code
        if error_code == 190:
            print("\nAction Required:")
            print("  Your access token is invalid or expired.")
            print("  Please generate a new long-lived Page Access Token.")
            print("  See README.md for token generation instructions.")
        elif error_code == 200:
            print("\nAction Required:")
            print("  Missing required permissions.")
            print("  Ensure your token has 'pages_manage_posts' permission.")
        elif error_code == 100:
            print("\nAction Required:")
            print("  Invalid parameter in request.")
            print("  Check that your image URL is accessible or file is valid.")
        elif error_code == 368:
            print("\nAction Required:")
            print("  Temporarily blocked for unusual activity.")
            print("  Please wait a few minutes and try again.")
        elif error_code == 4:
            print("\nAction Required:")
            print("  API rate limit exceeded.")
            print("  Please wait before making more requests.")

        sys.exit(1)

    # Handle success response
    if response.status_code == 200:
        photo_id = response_data.get('id')
        post_id = response_data.get('post_id', '')

        # Construct post URL
        if post_id:
            # post_id format is usually: page_id_post_id
            post_url = f"https://www.facebook.com/{post_id.replace('_', '/posts/')}"
        else:
            post_url = f"https://www.facebook.com/photo.php?fbid={photo_id}"

        return {
            'id': photo_id,
            'post_id': post_id,
            'post_url': post_url
        }
    else:
        print(f"Error: Unexpected response status code: {response.status_code}")
        print(f"Response: {response_data}")
        sys.exit(1)


def main():
    """
    Main entry point for the Facebook photo uploader.
    Parses command-line arguments and orchestrates the upload process.
    """
    parser = argparse.ArgumentParser(
        description='Upload photos with captions to Facebook Pages',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Upload a local file:
    python fb_uploader.py --file photo.jpg --caption "Beautiful sunset!"

  Upload from URL:
    python fb_uploader.py --url https://example.com/photo.jpg --caption "Check this out!"

  Caption with line breaks:
    python fb_uploader.py --file photo.jpg --caption "Line 1
    Line 2
    Line 3"

For setup instructions, see README.md
        """
    )

    # Create mutually exclusive group for file vs URL
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        '--file',
        type=str,
        help='Path to local image file (jpg, jpeg, png, gif)'
    )
    source_group.add_argument(
        '--url',
        type=str,
        help='URL of remote image to upload'
    )

    parser.add_argument(
        '--caption',
        type=str,
        required=True,
        help='Caption text for the photo'
    )

    args = parser.parse_args()

    # Load credentials
    print("Loading credentials...")
    page_id, access_token = load_credentials()
    print(f"Page ID: {page_id}")

    # Handle local file upload
    if args.file:
        print(f"\nValidating local file: {args.file}")
        valid, error = validate_local_file(args.file)

        if not valid:
            print(f"Error: {error}")
            sys.exit(1)

        print("File validation passed")
        print(f"Uploading photo to Facebook Page...")

        response = upload_photo_local(page_id, access_token, args.file, args.caption)

    # Handle URL upload
    else:
        print(f"\nUploading photo from URL: {args.url}")
        response = upload_photo_url(page_id, access_token, args.url, args.caption)

    # Handle response
    result = handle_response(response)

    # Display success message
    print("\n" + "="*60)
    print("SUCCESS! Photo uploaded to Facebook Page")
    print("="*60)
    print(f"Photo ID: {result['id']}")
    if result['post_id']:
        print(f"Post ID: {result['post_id']}")
    print(f"Post URL: {result['post_url']}")
    print("\nYou can view your post at the URL above.")
    print("="*60)


if __name__ == '__main__':
    main()
