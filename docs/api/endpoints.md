# API Documentation

## Overview

The Instagram-to-WordPress Manager provides a comprehensive REST API for managing Instagram content import and WordPress post management.

## Base URL

```
http://localhost:5000/api
```

## Authentication

All WordPress-related endpoints require the MCP access token configured in your environment variables. Instagram scraping endpoints require an Apify API token.

## Instagram Endpoints

### Scrape Instagram User Posts

**POST** `/instagram/apify/scrape-user`

Scrape posts from a specific Instagram user using Apify's professional scraper.

**Request Body:**
```json
{
  "username": "cardmyyard_oviedo",
  "limit": 20
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "posts": [
      {
        "id": "instagram_post_id",
        "shortCode": "ABC123",
        "caption": "Post caption text",
        "hashtags": ["#tag1", "#tag2"],
        "mentions": ["@user1"],
        "url": "https://instagram.com/p/ABC123/",
        "displayUrl": "https://instagram.com/image.jpg",
        "timestamp": "2024-01-15T10:30:00Z",
        "likesCount": 150,
        "commentsCount": 25,
        "type": "GraphImage"
      }
    ],
    "profile": {
      "username": "cardmyyard_oviedo",
      "fullName": "Card My Yard Oviedo",
      "followersCount": 1250,
      "isVerified": false
    }
  },
  "cached": false,
  "cache_key": "apify_user_cardmyyard_oviedo"
}
```

### Bulk Import to WordPress

**POST** `/instagram/apify/bulk-import`

Import multiple Instagram posts directly to WordPress as drafts.

**Request Body:**
```json
{
  "username": "cardmyyard_oviedo",
  "limit": 10,
  "import_images": true
}
```

**Response:**
```json
{
  "success": true,
  "imported_count": 8,
  "skipped_count": 2,
  "posts": [
    {
      "wordpress_id": 35,
      "instagram_id": "instagram_post_id",
      "title": "Generated post title",
      "status": "draft",
      "url": "https://your-site.com/?p=35"
    }
  ],
  "errors": []
}
```

### Get Instagram Profile

**GET** `/instagram/apify/profile/<username>`

Get detailed profile information for an Instagram user.

**Response:**
```json
{
  "success": true,
  "data": {
    "username": "cardmyyard_oviedo",
    "fullName": "Card My Yard Oviedo",
    "biography": "Profile bio text",
    "followersCount": 1250,
    "followingCount": 500,
    "postsCount": 150,
    "isVerified": false,
    "isPrivate": false,
    "profilePicUrl": "https://instagram.com/profile.jpg"
  },
  "cached": true
}
```

## WordPress Endpoints

### List Posts

**GET** `/posts`

Get a list of WordPress posts with optional filtering.

**Query Parameters:**
- `status` - Filter by post status (draft, publish, private)
- `limit` - Number of posts to return (default: 10)
- `search` - Search posts by title or content

**Response:**
```json
{
  "success": true,
  "posts": [
    {
      "ID": 35,
      "post_title": "Instagram Post Title",
      "post_content": "Post content...",
      "post_status": "draft",
      "post_date": "2024-01-15 10:30:00",
      "meta": {
        "instagram_id": "instagram_post_id",
        "instagram_url": "https://instagram.com/p/ABC123/",
        "likes_count": "150",
        "comments_count": "25"
      }
    }
  ]
}
```

### Get Single Post

**GET** `/posts/<id>`

Get detailed information about a specific WordPress post.

**Response:**
```json
{
  "success": true,
  "post": {
    "ID": 35,
    "post_title": "Instagram Post Title",
    "post_content": "Full post content...",
    "post_status": "draft",
    "post_date": "2024-01-15 10:30:00",
    "post_author": "1",
    "meta": {
      "instagram_id": "instagram_post_id",
      "instagram_url": "https://instagram.com/p/ABC123/",
      "hashtags": "#tag1,#tag2",
      "likes_count": "150",
      "comments_count": "25"
    }
  }
}
```

### Create Post

**POST** `/posts`

Create a new WordPress post.

**Request Body:**
```json
{
  "title": "Post Title",
  "content": "Post content...",
  "status": "draft",
  "meta": {
    "custom_field": "value"
  }
}
```

**Response:**
```json
{
  "success": true,
  "post_id": 36,
  "message": "Post created successfully"
}
```

### Update Post

**PUT** `/posts/<id>`

Update an existing WordPress post.

**Request Body:**
```json
{
  "title": "Updated Title",
  "content": "Updated content...",
  "status": "publish"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Post updated successfully"
}
```

### Delete Post

**DELETE** `/posts/<id>`

Delete a WordPress post.

**Response:**
```json
{
  "success": true,
  "message": "Post deleted successfully"
}
```

## Media Endpoints

### Upload Media from URL

**POST** `/media/upload`

Upload an image to WordPress media library from a URL.

**Request Body:**
```json
{
  "url": "https://instagram.com/image.jpg",
  "filename": "instagram-image.jpg",
  "alt_text": "Instagram image description"
}
```

**Response:**
```json
{
  "success": true,
  "attachment_id": 45,
  "url": "https://your-site.com/wp-content/uploads/2024/01/instagram-image.jpg"
}
```

## Cache Management Endpoints

### Get Cache Statistics

**GET** `/instagram/apify/cache/stats`

Get information about the current cache state.

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_files": 15,
    "total_size_mb": 2.5,
    "expired_files": 3,
    "cache_hit_rate": "85%",
    "oldest_file": "2024-01-14T08:00:00Z",
    "newest_file": "2024-01-15T14:30:00Z"
  }
}
```

### Clear Expired Cache

**POST** `/instagram/apify/cache/clear-expired`

Remove expired cache files to free up space.

**Response:**
```json
{
  "success": true,
  "cleared_files": 3,
  "freed_space_mb": 0.8,
  "message": "Expired cache cleared successfully"
}
```

### Clear User Cache

**POST** `/instagram/apify/cache/clear-user`

Clear cache for a specific Instagram user.

**Request Body:**
```json
{
  "username": "cardmyyard_oviedo"
}
```

**Response:**
```json
{
  "success": true,
  "cleared_files": 2,
  "message": "Cache cleared for user: cardmyyard_oviedo"
}
```

## System Endpoints

### Health Check

**GET** `/health`

Check the health status of the application and its dependencies.

**Response:**
```json
{
  "success": true,
  "status": "healthy",
  "checks": {
    "wordpress_connection": "ok",
    "apify_connection": "ok",
    "cache_system": "ok"
  },
  "timestamp": "2024-01-15T15:00:00Z"
}
```

### Get Site Information

**GET** `/site-info`

Get information about the connected WordPress site.

**Response:**
```json
{
  "success": true,
  "site": {
    "name": "My WordPress Site",
    "url": "https://your-site.com",
    "version": "6.4.2",
    "plugins": {
      "aiwu-mcp": "1.0.0"
    }
  }
}
```

## Error Responses

All endpoints return consistent error responses:

```json
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {
    "additional": "error details"
  }
}
```

### Common Error Codes

- `INVALID_REQUEST` - Malformed request data
- `AUTHENTICATION_FAILED` - Invalid or missing access token
- `RATE_LIMIT_EXCEEDED` - API rate limit reached
- `RESOURCE_NOT_FOUND` - Requested resource doesn't exist
- `WORDPRESS_ERROR` - WordPress MCP communication error
- `APIFY_ERROR` - Apify API error
- `CACHE_ERROR` - Cache system error

## Rate Limits

- **Instagram Scraping**: Limited by Apify account (625 compute units/month free)
- **WordPress Operations**: No specific limits (depends on WordPress server)
- **Cache Operations**: No limits

## SDK Examples

### JavaScript/Node.js

```javascript
// Scrape Instagram posts
const response = await fetch('/api/instagram/apify/scrape-user', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    username: 'cardmyyard_oviedo',
    limit: 20
  })
});

const data = await response.json();
console.log(data.data.posts);
```

### Python

```python
import requests

# Bulk import Instagram posts
response = requests.post('http://localhost:5000/api/instagram/apify/bulk-import', 
  json={
    'username': 'cardmyyard_oviedo',
    'limit': 10,
    'import_images': True
  }
)

data = response.json()
print(f"Imported {data['imported_count']} posts")
```

### cURL

```bash
# Get WordPress posts
curl -X GET "http://localhost:5000/api/posts?status=draft&limit=5"

# Publish a post
curl -X PUT "http://localhost:5000/api/posts/35" \
  -H "Content-Type: application/json" \
  -d '{"status": "publish"}'
```