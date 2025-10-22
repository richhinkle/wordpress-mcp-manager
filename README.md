# WordPress MCP Manager

A standalone Flask application that provides a web interface for managing WordPress sites via the AIWU MCP (Model Context Protocol) plugin.

## Features

- ✅ **WordPress Post Management** - Create, edit, publish, and delete posts
- ✅ **AI Image Generation** - Generate images using AIWU's AI capabilities
- ✅ **Media Upload** - Upload images from URLs to WordPress media library
- ✅ **Site Information** - View plugins, users, and site health
- ✅ **Search & Filter** - Find posts by content, status, or keywords
- ✅ **Responsive Design** - Works on desktop, tablet, and mobile
- 🔄 **Instagram Integration** - Coming soon!

## Prerequisites

1. **WordPress site** with AIWU plugin installed and configured
2. **Python 3.8+** installed on your system
3. **AIWU MCP access token** from your WordPress admin

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd wordpress-mcp-manager

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your WordPress details
WORDPRESS_URL=https://your-site.com/wp-json/mcp/v1/sse
ACCESS_TOKEN=your-32-character-access-token
SECRET_KEY=your-secret-key-for-flask
DEBUG=true
PORT=5000
```

### 3. Run the Application

```bash
# Development server
python run.py

# Or run directly
python app.py
```

Visit `http://localhost:5000` in your browser.

## Production Deployment

### Using Gunicorn

```bash
# Install gunicorn (already in requirements.txt)
pip install gunicorn

# Run with gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 2 app:app
```

### Using Docker

```bash
# Build Docker image
docker build -t wordpress-mcp-manager .

# Run container
docker run -p 5000:5000 \
  -e WORDPRESS_URL="https://your-site.com/wp-json/mcp/v1/sse" \
  -e ACCESS_TOKEN="your-token" \
  -e SECRET_KEY="your-secret" \
  wordpress-mcp-manager
```

### Deploy to Heroku

```bash
# Create Heroku app
heroku create your-wp-manager

# Set environment variables
heroku config:set WORDPRESS_URL="https://your-site.com/wp-json/mcp/v1/sse"
heroku config:set ACCESS_TOKEN="your-token"
heroku config:set SECRET_KEY="your-secret-key"

# Deploy
git push heroku main
```

## API Endpoints

### Posts
- `GET /api/posts` - List posts
- `GET /api/posts/<id>` - Get single post
- `POST /api/posts` - Create post
- `PUT /api/posts/<id>` - Update post
- `DELETE /api/posts/<id>` - Delete post

### Media
- `POST /api/media/upload` - Upload from URL
- `POST /api/ai/image` - Generate AI image

### Site Info
- `GET /api/health` - Health check
- `GET /api/plugins` - List plugins
- `GET /api/users` - List users

## Project Structure

```
wordpress-mcp-manager/
├── app.py              # Main Flask application
├── templates.py        # HTML templates
├── static/
│   └── app.js         # Frontend JavaScript
├── requirements.txt    # Python dependencies
├── .env.example       # Environment template
├── run.py             # Development server
├── README.md          # This file
└── Dockerfile         # Docker configuration
```

## Adding New Features

The application is designed to be easily extensible. To add new features:

1. **Add API endpoints** in `app.py`
2. **Add MCP client methods** in the `WordPressMCPClient` class
3. **Add frontend functions** in `static/app.js`
4. **Update UI** in `templates.py`

### Example: Adding Instagram Integration

```python
# In app.py - Add new client class
class InstagramClient:
    def __init__(self, access_token):
        self.access_token = access_token
    
    def get_recent_posts(self, limit=10):
        # Instagram API implementation
        pass

# Add new route
@app.route('/api/instagram/posts')
def get_instagram_posts():
    # Implementation
    pass
```

## Troubleshooting

### Connection Issues
- Verify WordPress URL and access token
- Check that AIWU plugin is active
- Ensure WordPress site is accessible

### CORS Errors
- Make sure Flask-CORS is installed
- Check that the frontend is served from the same domain

### Performance Issues
- Increase timeout values for slow WordPress sites
- Use gunicorn with multiple workers for production
- Consider caching for frequently accessed data

### AIWU MCP Response Format Issues
The AIWU MCP plugin returns data in a nested format that requires special parsing:

**Expected Format:**
```json
{
  "content": [
    {
      "text": "[{\"ID\": 1, \"post_title\": \"...\"}]",
      "type": "text"
    }
  ]
}
```

**Solution:** The `call_mcp_function` method automatically detects and parses this nested structure, extracting the JSON string from `content[0].text` and converting it to the expected array format.

### Chat Interface Errors
- If chat commands fail, check the MCP logs in the console
- Use the debug endpoint `/api/debug/posts` to inspect raw MCP responses
- Ensure the WordPress site returns valid JSON in the expected nested format

## Security Notes

- Always use HTTPS in production
- Keep access tokens secure
- Use strong secret keys
- Consider adding authentication for multi-user deployments

## License

MIT License - see LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review WordPress and AIWU plugin documentation
3. Open an issue on GitHub