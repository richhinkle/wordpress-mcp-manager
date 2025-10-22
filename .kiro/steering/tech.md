# Technology Stack & Build System

## Backend Stack
- **Python 3.8+** - Core runtime
- **Flask 2.3.3** - Web framework
- **Flask-CORS** - Cross-origin resource sharing
- **Requests** - HTTP client for MCP communication
- **Gunicorn** - Production WSGI server

## Frontend Stack
- **Vanilla JavaScript** - No framework dependencies
- **Modern CSS** - Grid, flexbox, custom properties
- **Responsive Design** - Mobile-first approach

## External Integrations
- **WordPress MCP Plugin** - AIWU Model Context Protocol
- **Instagram Basic Display API** - OAuth-based post import
- **AIWU AI Services** - Image generation and content tools

## Development Environment

### Setup Commands
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux) 
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment config
cp .env.example .env
# Edit .env with your WordPress details

# Run development server
python run.py
```

### Production Deployment
```bash
# Using Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 2 app:app

# Using Docker
docker build -t wordpress-mcp-manager .
docker run -p 5000:5000 wordpress-mcp-manager
```

### Testing
```bash
# Run integration tests
python test_instagram_integration.py

# Manual API testing via health endpoint
curl http://localhost:5000/api/health
```

## Configuration Management
- Environment variables via `.env` file
- Production overrides via system environment
- Instagram OAuth optional (graceful degradation)