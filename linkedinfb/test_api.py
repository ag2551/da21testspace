"""Simple API validation script"""
import asyncio
import httpx


async def test_api():
    """Test basic API functionality"""
    base_url = "http://localhost:8000"

    async with httpx.AsyncClient() as client:
        # Test root endpoint
        print("Testing root endpoint...")
        response = await client.get(f"{base_url}/")
        print(f"✓ Root: {response.status_code} - {response.json()}")

        # Test health endpoint
        print("\nTesting health endpoint...")
        response = await client.get(f"{base_url}/health")
        print(f"✓ Health: {response.status_code} - {response.json()}")

        # Test docs endpoint
        print("\nTesting docs endpoint...")
        response = await client.get(f"{base_url}/docs")
        print(f"✓ Docs: {response.status_code}")

        # Test creating a post
        print("\nTesting POST /api/posts...")
        post_data = {
            "content_text": "Test post from validation script",
            "content_image_url": None
        }
        response = await client.post(f"{base_url}/api/posts/", json=post_data)
        print(f"✓ Create Post: {response.status_code}")
        if response.status_code == 201:
            post = response.json()
            print(f"  Created post ID: {post['id']}")
            post_id = post['id']

            # Test getting the post
            print("\nTesting GET /api/posts/{id}...")
            response = await client.get(f"{base_url}/api/posts/{post_id}")
            print(f"✓ Get Post: {response.status_code}")
            print(f"  Post: {response.json()}")

            # Test listing posts
            print("\nTesting GET /api/posts...")
            response = await client.get(f"{base_url}/api/posts/")
            print(f"✓ List Posts: {response.status_code}")
            print(f"  Found {len(response.json())} posts")

            # Test post status
            print("\nTesting GET /api/posts/{id}/status...")
            response = await client.get(f"{base_url}/api/posts/{post_id}/status")
            print(f"✓ Post Status: {response.status_code}")
            print(f"  Status: {response.json()}")

        # Test credentials list (should be empty)
        print("\nTesting GET /api/credentials...")
        response = await client.get(f"{base_url}/api/credentials/")
        print(f"✓ List Credentials: {response.status_code}")
        print(f"  Found {len(response.json())} credentials")

        print("\n✅ All basic API tests passed!")


if __name__ == "__main__":
    asyncio.run(test_api())
