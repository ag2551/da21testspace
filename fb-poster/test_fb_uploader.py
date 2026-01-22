#!/usr/bin/env python3
"""
Unit tests for Facebook Page Photo Uploader
"""

import os
import sys
import unittest
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path
import tempfile
import json

# Import the module to test
import fb_uploader


class TestLoadCredentials(unittest.TestCase):
    """Test credential loading functionality"""

    @patch.dict(os.environ, {
        'FB_PAGE_ID': '123456789',
        'FB_PAGE_ACCESS_TOKEN': 'valid_token_here'
    })
    def test_valid_credentials(self):
        """Test loading valid credentials"""
        page_id, token = fb_uploader.load_credentials()
        self.assertEqual(page_id, '123456789')
        self.assertEqual(token, 'valid_token_here')

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_credentials(self):
        """Test handling of missing credentials"""
        with self.assertRaises(SystemExit) as cm:
            fb_uploader.load_credentials()
        self.assertEqual(cm.exception.code, 1)

    @patch.dict(os.environ, {
        'FB_PAGE_ID': 'your_page_id_here',
        'FB_PAGE_ACCESS_TOKEN': 'your_page_access_token_here'
    })
    def test_placeholder_credentials(self):
        """Test detection of placeholder credentials"""
        with self.assertRaises(SystemExit) as cm:
            fb_uploader.load_credentials()
        self.assertEqual(cm.exception.code, 1)


class TestValidateLocalFile(unittest.TestCase):
    """Test file validation functionality"""

    def setUp(self):
        """Create temporary test files"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_file_not_exists(self):
        """Test validation of non-existent file"""
        valid, error = fb_uploader.validate_local_file('/nonexistent/file.jpg')
        self.assertFalse(valid)
        self.assertIn('does not exist', error)

    def test_valid_jpg_file(self):
        """Test validation of valid JPG file"""
        # Create a small test file
        test_file = os.path.join(self.temp_dir, 'test.jpg')
        with open(test_file, 'wb') as f:
            f.write(b'fake image data' * 100)  # Small file

        valid, error = fb_uploader.validate_local_file(test_file)
        self.assertTrue(valid)
        self.assertIsNone(error)

    def test_valid_png_file(self):
        """Test validation of valid PNG file"""
        test_file = os.path.join(self.temp_dir, 'test.png')
        with open(test_file, 'wb') as f:
            f.write(b'fake png data' * 100)

        valid, error = fb_uploader.validate_local_file(test_file)
        self.assertTrue(valid)
        self.assertIsNone(error)

    def test_invalid_file_extension(self):
        """Test validation of invalid file type"""
        test_file = os.path.join(self.temp_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('not an image')

        valid, error = fb_uploader.validate_local_file(test_file)
        self.assertFalse(valid)
        self.assertIn('Unsupported file type', error)

    def test_file_too_large(self):
        """Test validation of oversized file"""
        test_file = os.path.join(self.temp_dir, 'large.jpg')
        with open(test_file, 'wb') as f:
            # Create a file larger than 4MB
            f.write(b'x' * (5 * 1024 * 1024))  # 5MB

        valid, error = fb_uploader.validate_local_file(test_file)
        self.assertFalse(valid)
        self.assertIn('exceeds', error)
        self.assertIn('MB limit', error)

    def test_directory_not_file(self):
        """Test validation when path is a directory"""
        valid, error = fb_uploader.validate_local_file(self.temp_dir)
        self.assertFalse(valid)
        self.assertIn('not a file', error)


class TestHandleResponse(unittest.TestCase):
    """Test API response handling"""

    def test_success_response(self):
        """Test handling of successful API response"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': '123456',
            'post_id': '789_123456'
        }

        result = fb_uploader.handle_response(mock_response)

        self.assertEqual(result['id'], '123456')
        self.assertEqual(result['post_id'], '789_123456')
        self.assertIn('post_url', result)
        self.assertIn('facebook.com', result['post_url'])

    def test_oauth_error_response(self):
        """Test handling of OAuth error"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            'error': {
                'message': 'Invalid OAuth access token',
                'type': 'OAuthException',
                'code': 190
            }
        }

        with self.assertRaises(SystemExit) as cm:
            fb_uploader.handle_response(mock_response)
        self.assertEqual(cm.exception.code, 1)

    def test_rate_limit_error(self):
        """Test handling of rate limit error"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            'error': {
                'message': 'Rate limit exceeded',
                'type': 'RateLimitError',
                'code': 4
            }
        }

        with self.assertRaises(SystemExit) as cm:
            fb_uploader.handle_response(mock_response)
        self.assertEqual(cm.exception.code, 1)

    def test_invalid_json_response(self):
        """Test handling of invalid JSON response"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.text = "Not JSON"

        with self.assertRaises(SystemExit) as cm:
            fb_uploader.handle_response(mock_response)
        self.assertEqual(cm.exception.code, 1)


class TestUploadFunctions(unittest.TestCase):
    """Test upload functionality"""

    def setUp(self):
        """Create temporary test file"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_image = os.path.join(self.temp_dir, 'test.jpg')
        with open(self.test_image, 'wb') as f:
            f.write(b'fake image data' * 100)

    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    @patch('fb_uploader.requests.post')
    def test_upload_photo_local_success(self, mock_post):
        """Test successful local photo upload"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        response = fb_uploader.upload_photo_local(
            '123456',
            'token',
            self.test_image,
            'Test caption'
        )

        self.assertEqual(response, mock_response)
        mock_post.assert_called_once()

        # Verify the call was made with correct parameters
        call_args = mock_post.call_args
        self.assertIn('files', call_args.kwargs)
        self.assertIn('data', call_args.kwargs)
        self.assertEqual(call_args.kwargs['data']['message'], 'Test caption')

    @patch('fb_uploader.requests.post')
    def test_upload_photo_url_success(self, mock_post):
        """Test successful URL photo upload"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        response = fb_uploader.upload_photo_url(
            '123456',
            'token',
            'https://example.com/photo.jpg',
            'URL test caption'
        )

        self.assertEqual(response, mock_response)
        mock_post.assert_called_once()

        # Verify the call parameters
        call_args = mock_post.call_args
        self.assertIn('data', call_args.kwargs)
        self.assertEqual(call_args.kwargs['data']['url'], 'https://example.com/photo.jpg')
        self.assertEqual(call_args.kwargs['data']['message'], 'URL test caption')

    @patch('fb_uploader.requests.post')
    def test_upload_network_error(self, mock_post):
        """Test handling of network errors"""
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError("Network error")

        with self.assertRaises(SystemExit) as cm:
            fb_uploader.upload_photo_url(
                '123456',
                'token',
                'https://example.com/photo.jpg',
                'Caption'
            )
        self.assertEqual(cm.exception.code, 1)

    def test_upload_file_not_found(self):
        """Test handling of missing file during upload"""
        with self.assertRaises(SystemExit) as cm:
            fb_uploader.upload_photo_local(
                '123456',
                'token',
                '/nonexistent/file.jpg',
                'Caption'
            )
        self.assertEqual(cm.exception.code, 1)


class TestConstants(unittest.TestCase):
    """Test module constants"""

    def test_api_version(self):
        """Test API version constant"""
        self.assertEqual(fb_uploader.API_VERSION, 'v19.0')

    def test_max_file_size(self):
        """Test maximum file size constant"""
        self.assertEqual(fb_uploader.MAX_FILE_SIZE_MB, 4)

    def test_allowed_extensions(self):
        """Test allowed file extensions"""
        expected_extensions = {'.jpg', '.jpeg', '.png', '.gif'}
        self.assertEqual(fb_uploader.ALLOWED_EXTENSIONS, expected_extensions)


def run_tests():
    """Run all tests and return results"""
    # Suppress print statements during tests
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
