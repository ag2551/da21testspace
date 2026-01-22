# Facebook Page Photo & Text Uploader

A simple Python command-line tool for uploading photos with captions to Facebook Pages using the Graph API.

## Features

- Upload photos from local files or remote URLs
- Add text captions to photos
- Secure credential management via `.env` file
- Clear error messages and success confirmations
- Support for JPG, PNG, and GIF formats
- Automatic file validation (size, format, existence)

## Prerequisites

- Python 3.8 or higher
- A Facebook Page (you must be an admin)
- Facebook Developer account
- Page Access Token with `pages_manage_posts` permission

## Installation

1. **Clone or download this repository**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up credentials**
   ```bash
   cp .env.example .env
   ```

4. **Edit `.env` and add your credentials**
   - `FB_PAGE_ID`: Your Facebook Page ID
   - `FB_PAGE_ACCESS_TOKEN`: Your Page Access Token

   See [Token Generation Guide](#token-generation-guide) below for detailed instructions.

## Usage

### Upload a Local Photo

```bash
python fb_uploader.py --file path/to/photo.jpg --caption "Your caption here"
```

### Upload a Photo from URL

```bash
python fb_uploader.py --url https://example.com/photo.jpg --caption "Your caption here"
```

### Caption with Line Breaks

```bash
python fb_uploader.py --file photo.jpg --caption "Line 1
Line 2
Line 3"
```

### Caption with Emojis

```bash
python fb_uploader.py --file photo.jpg --caption "Beautiful sunset! 🌅✨"
```

## Command-Line Options

```
Required (choose one):
  --file PATH     Path to local image file (jpg, jpeg, png, gif)
  --url URL       URL of remote image to upload

Required:
  --caption TEXT  Caption text for the photo

Optional:
  -h, --help      Show help message
```

## File Requirements

- **Supported formats**: JPG, JPEG, PNG, GIF
- **Maximum file size**: 4 MB
- **File must exist** (for local uploads)
- **URL must be publicly accessible** (for URL uploads)

## Token Generation Guide

### Step 1: Create a Facebook App (if you don't have one)

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Click "My Apps" → "Create App"
3. Select "Business" type
4. Fill in app details and create

### Step 2: Generate User Access Token

1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app from the dropdown
3. Click "Generate Access Token"
4. Grant these permissions:
   - `pages_manage_posts` (required)
   - `pages_read_engagement` (optional)
5. Click "Generate Access Token" and copy it

### Step 3: Get Page Access Token

1. In Graph API Explorer, make this request:
   ```
   GET /me/accounts
   ```
2. Find your target Page in the response
3. Copy the `access_token` value for that Page
4. This is your **Page Access Token**

### Step 4: Extend Token to Long-Lived (60 days)

**Method 1: Using Graph API Explorer**

1. Use the [Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/)
2. Paste your Page Access Token
3. Click "Extend Access Token"
4. Copy the new long-lived token

**Method 2: Using API Request**

```bash
curl -X GET "https://graph.facebook.com/v19.0/oauth/access_token?\
grant_type=fb_exchange_token&\
client_id=YOUR_APP_ID&\
client_secret=YOUR_APP_SECRET&\
fb_exchange_token=YOUR_SHORT_LIVED_TOKEN"
```

### Step 5: Find Your Page ID

**Method 1: From Page Settings**
1. Go to your Facebook Page
2. Click "About" in the left menu
3. Scroll down to find "Page ID"

**Method 2: Using Graph API Explorer**
```
GET /me/accounts
```
Look for the `id` field for your Page

**Method 3: From Page URL**
- If your Page URL is `facebook.com/YourPageName`, use Graph API:
  ```
  GET /YourPageName?fields=id
  ```

### Step 6: Add to `.env` File

```
FB_PAGE_ID=123456789012345
FB_PAGE_ACCESS_TOKEN=your_long_lived_page_access_token_here
```

## Troubleshooting

### Error: Missing credentials in .env file

**Solution**: Ensure you have copied `.env.example` to `.env` and filled in your actual credentials.

### Error: Access token expired

**Solution**: Page Access Tokens typically last 60 days. Generate a new long-lived token following the steps above.

### Error: Invalid access token

**Solution**:
- Verify you're using a **Page Access Token**, not a User Access Token
- Ensure the token hasn't expired
- Check that you copied the entire token (no spaces or truncation)

### Error: Missing publish permission

**Solution**: Regenerate your token with `pages_manage_posts` permission enabled.

### Error: Image file does not exist

**Solution**:
- Check the file path is correct
- Use absolute path or path relative to current directory
- Ensure file extension is included

### Error: Image exceeds 4MB limit

**Solution**: Compress or resize your image before uploading.

### Error: Unsupported file type

**Solution**: Convert your image to JPG, PNG, or GIF format.

### Error: Failed to connect to Facebook API

**Solution**:
- Check your internet connection
- Verify Facebook API is not down: [Status Page](https://developers.facebook.com/status/)
- Check if you're behind a firewall or proxy

### Error: Temporarily blocked for unusual activity

**Solution**:
- Wait 15-30 minutes before trying again
- Reduce posting frequency
- This is Facebook's spam prevention system

### Error: API rate limit exceeded

**Solution**:
- Facebook has rate limits on API calls
- Wait a few minutes before retrying
- For Page posts: ~10-15 posts per day is generally safe

## API Rate Limits

Facebook enforces rate limits to prevent spam:

- **Page Posts**: Approximately 10-15 posts per day
- **API Calls**: 200 calls per hour per user
- Exceeding limits results in temporary blocks

**Best Practices**:
- Space out your posts (don't post all at once)
- Monitor your posting frequency
- Use scheduled posting tools for bulk content

## Security Best Practices

1. **Never commit `.env` to version control**
   - It's already in `.gitignore`
   - Contains sensitive credentials

2. **Use long-lived tokens**
   - Tokens last 60 days
   - Set reminders to refresh tokens before expiry

3. **Keep tokens secure**
   - Don't share tokens publicly
   - Don't paste tokens in chat or email
   - Regenerate immediately if compromised

4. **Limit app permissions**
   - Only grant necessary permissions
   - Review app access regularly

## Examples

### Example 1: Simple Local Upload

```bash
python fb_uploader.py --file vacation.jpg --caption "Amazing beach day!"
```

**Output**:
```
Loading credentials...
Page ID: 123456789012345

Validating local file: vacation.jpg
File validation passed
Uploading photo to Facebook Page...

============================================================
SUCCESS! Photo uploaded to Facebook Page
============================================================
Photo ID: 987654321098765
Post ID: 123456789012345_987654321098765
Post URL: https://www.facebook.com/123456789012345/posts/987654321098765

You can view your post at the URL above.
============================================================
```

### Example 2: Upload from URL

```bash
python fb_uploader.py --url https://picsum.photos/800/600 --caption "Random beautiful image"
```

### Example 3: Multi-line Caption

```bash
python fb_uploader.py --file product.jpg --caption "New Product Launch! 🚀

Features:
✅ Feature 1
✅ Feature 2
✅ Feature 3

Available now!"
```

### Example 4: Batch Upload Script

Create a bash script to upload multiple photos:

```bash
#!/bin/bash
# upload_batch.sh

python fb_uploader.py --file photo1.jpg --caption "Caption 1"
sleep 5  # Wait 5 seconds between uploads

python fb_uploader.py --file photo2.jpg --caption "Caption 2"
sleep 5

python fb_uploader.py --file photo3.jpg --caption "Caption 3"
```

Run it:
```bash
chmod +x upload_batch.sh
./upload_batch.sh
```

## Project Structure

```
fb-poster/
├── .env                    # Your credentials (gitignored)
├── .env.example           # Template for credentials
├── .gitignore             # Prevents committing sensitive files
├── requirements.txt       # Python dependencies
├── fb_uploader.py        # Main script
├── README.md             # This file
└── test_fb_uploader.py   # Unit tests
```

## Dependencies

- **requests**: HTTP library for API calls
- **python-dotenv**: Environment variable management

See `requirements.txt` for specific versions.

## Facebook Graph API Reference

This tool uses the Facebook Graph API v19.0.

**Endpoint**: `POST /{page-id}/photos`

**Documentation**: https://developers.facebook.com/docs/graph-api/reference/page/photos/

**Required Permissions**:
- `pages_manage_posts`: To publish content to Pages

**Optional Permissions**:
- `pages_read_engagement`: To read post metrics (not used in this tool)

## Limitations

- Maximum file size: 4 MB (Facebook limit)
- Supported formats: JPG, JPEG, PNG, GIF
- Rate limits apply (see [API Rate Limits](#api-rate-limits))
- Cannot schedule posts for future publication
- Cannot upload multiple photos in a single post (carousel)
- Cannot edit or delete posts after upload

## Future Enhancements

Planned features for future versions:

- [ ] Schedule posts for future publication
- [ ] Upload multiple photos (carousel posts)
- [ ] Add photo tagging and location
- [ ] Support video uploads
- [ ] Batch upload from directory
- [ ] Edit/delete existing posts
- [ ] Post analytics and engagement metrics
- [ ] GUI interface

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is provided as-is for educational and personal use.

Facebook and the Facebook logo are trademarks of Meta Platforms, Inc.

## Support

For issues related to:
- **This tool**: Check [Troubleshooting](#troubleshooting) section
- **Facebook API**: See [Facebook Developers Documentation](https://developers.facebook.com/docs/)
- **Token generation**: See [Token Generation Guide](#token-generation-guide)

## Changelog

### Version 1.0.0 (2026-01-21)
- Initial release
- Local file upload support
- Remote URL upload support
- Comprehensive error handling
- Token validation
- File validation

## Acknowledgments

- Built using Facebook Graph API v19.0
- Thanks to the Facebook Developer community
