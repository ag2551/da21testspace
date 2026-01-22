#!/usr/bin/env python3
"""
LinkedIn OAuth 2.0 Authentication Handler

This script handles the OAuth 2.0 flow to obtain an access token from LinkedIn.
It opens a browser for user authentication and runs a local server to capture
the authorization callback.

Usage:
    python get_token.py

Requirements:
    - .env file with LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET
    - Port 8080 must be available
    - System default browser
"""

import os
import sys
import json
import time
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlencode, urlparse, parse_qs
from typing import Optional, Dict, Any

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OAuth Constants
AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
REDIRECT_URI = "http://localhost:8080/callback"
SCOPES = ["w_member_social", "openid", "profile", "email"]

# Token storage
TOKEN_FILE = ".user_token"

# Global variable to store authorization code
auth_code: Optional[str] = None


class CallbackHandler(BaseHTTPRequestHandler):
    """HTTP request handler for OAuth callback."""

    def do_GET(self):
        """Handle GET request to capture OAuth callback."""
        global auth_code

        # Parse the URL to get query parameters
        parsed_path = urlparse(self.path)
        params = parse_qs(parsed_path.query)

        if parsed_path.path == "/callback":
            if "code" in params:
                auth_code = params["code"][0]
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"""
                    <html>
                        <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                            <h1 style="color: #0077B5;">Authentication Successful!</h1>
                            <p>You can close this window and return to the terminal.</p>
                        </body>
                    </html>
                """)
            elif "error" in params:
                error = params["error"][0]
                error_description = params.get("error_description", ["Unknown error"])[0]
                self.send_response(400)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(f"""
                    <html>
                        <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                            <h1 style="color: #D32F2F;">Authentication Failed</h1>
                            <p><strong>Error:</strong> {error}</p>
                            <p>{error_description}</p>
                        </body>
                    </html>
                """.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """Suppress default HTTP server logs."""
        # Intentionally suppress logging by not calling parent method
        return


def construct_auth_url(client_id: str) -> str:
    """
    Construct the LinkedIn authorization URL.

    Args:
        client_id: LinkedIn app client ID

    Returns:
        Complete authorization URL with all required parameters
    """
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "scope": " ".join(SCOPES),
    }
    return f"{AUTH_URL}?{urlencode(params)}"


def start_callback_server() -> Optional[str]:
    """
    Start local HTTP server to capture OAuth callback.

    Returns:
        Authorization code if successful, None otherwise

    Raises:
        OSError: If port 8080 is already in use
    """
    global auth_code
    auth_code = None

    try:
        server = HTTPServer(("localhost", 8080), CallbackHandler)
        print("📡 Waiting for authentication callback on http://localhost:8080/callback")
        print("   (Timeout: 5 minutes)")

        # Wait for callback with timeout
        timeout = time.time() + 300  # 5 minutes
        while auth_code is None and time.time() < timeout:
            server.handle_request()

        if auth_code is None:
            print("\n⏱️  Timeout: No authentication response received within 5 minutes.")
            return None

        return auth_code

    except OSError as e:
        if e.errno == 48 or e.errno == 98:  # Port already in use (macOS/Linux)
            print("❌ Error: Port 8080 is already in use.")
            print("   Please free the port and try again.")
            print("   You can check with: lsof -i :8080")
        else:
            print(f"❌ Server error: {e}")
        return None


def exchange_code_for_token(code: str, client_id: str, client_secret: str) -> Optional[Dict[str, Any]]:
    """
    Exchange authorization code for access token.

    Args:
        code: Authorization code from OAuth callback
        client_id: LinkedIn app client ID
        client_secret: LinkedIn app client secret

    Returns:
        Token data dictionary if successful, None otherwise

    Raises:
        requests.RequestException: If token exchange fails
    """
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": client_id,
        "client_secret": client_secret,
    }

    try:
        print("\n🔄 Exchanging authorization code for access token...")
        response = requests.post(TOKEN_URL, data=data, timeout=30)

        if response.status_code == 200:
            token_data = response.json()
            token_data["created_at"] = int(time.time())
            return token_data
        else:
            print(f"❌ Token exchange failed: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return None

    except requests.RequestException as e:
        print(f"❌ Network error during token exchange: {e}")
        return None


def save_token(token_data: Dict[str, Any]) -> bool:
    """
    Save token to file with secure permissions.

    Args:
        token_data: Token data dictionary containing access_token, expires_in, etc.

    Returns:
        True if saved successfully, False otherwise
    """
    try:
        # Write token to file
        with open(TOKEN_FILE, "w") as f:
            json.dump(token_data, f, indent=2)

        # Set secure permissions (600) on Unix systems
        if os.name != "nt":  # Not Windows
            os.chmod(TOKEN_FILE, 0o600)
            print(f"🔒 Token file permissions set to 600 (owner read/write only)")

        expires_in_days = token_data.get("expires_in", 0) // 86400
        print(f"💾 Token saved to {TOKEN_FILE}")
        print(f"⏰ Token expires in approximately {expires_in_days} days")

        return True

    except Exception as e:
        print(f"❌ Error saving token: {e}")
        return False


def main():
    """Main function to orchestrate OAuth flow."""
    print("=" * 60)
    print("LinkedIn OAuth 2.0 Authentication")
    print("=" * 60)

    # Check for environment variables
    client_id = os.getenv("LINKEDIN_CLIENT_ID")
    client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("\n❌ Error: Missing LinkedIn credentials")
        print("   Please create a .env file with:")
        print("   - LINKEDIN_CLIENT_ID=your_client_id")
        print("   - LINKEDIN_CLIENT_SECRET=your_client_secret")
        print("\n   You can copy .env.example to .env and fill in your credentials.")
        sys.exit(1)

    # Construct authorization URL
    auth_url = construct_auth_url(client_id)

    print(f"\n🌐 Opening browser for LinkedIn authentication...")
    print(f"   Scopes: {', '.join(SCOPES)}")
    print(f"\n   If browser doesn't open automatically, visit:")
    print(f"   {auth_url}\n")

    # Open browser
    try:
        webbrowser.open(auth_url)
    except Exception as e:
        print(f"⚠️  Could not open browser automatically: {e}")
        print(f"   Please open the URL manually.")

    # Start callback server
    code = start_callback_server()

    if not code:
        print("\n❌ Authentication failed: No authorization code received")
        sys.exit(1)

    print("✅ Authorization code received")

    # Exchange code for token
    token_data = exchange_code_for_token(code, client_id, client_secret)

    if not token_data:
        print("\n❌ Failed to obtain access token")
        sys.exit(1)

    print("✅ Access token obtained")

    # Save token
    if save_token(token_data):
        print("\n" + "=" * 60)
        print("🎉 Authentication Complete!")
        print("=" * 60)
        print("\nYou can now run: python post_to_linkedin.py")
        print("\n⚠️  Important:")
        print("   - Keep .user_token secure (already in .gitignore)")
        print("   - Re-run this script when token expires")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
