# Instagram Integration TODO

## Overview
Add Instagram integration to the WordPress MCP Manager to automatically pull Instagram posts and images into WordPress.

## Current Status
- ✅ **Base WordPress MCP Manager** - Complete and working
- ✅ **AI Chat Interface** - Implemented with natural language commands
- ✅ **AIWU MCP Integration** - Successfully connected and parsing responses
- 🔄 **Instagram Integration** - Next phase

## Instagram Integration Features to Implement

### Phase 1: Basic Instagram Connection
- [ ] **Instagram Basic Display API Setup**
  - [ ] Create Instagram App in Facebook Developer Console
  - [ ] Implement OAuth flow for user authentication
  - [ ] Store Instagram access tokens securely
  - [ ] Add Instagram credentials to environment configuration

- [ ] **Instagram API Client**
  - [ ] Create `InstagramClient` class in new file `instagram_client.py`
  - [ ] Implement methods to fetch user's recent posts
  - [ ] Handle Instagram API rate limiting
  - [ ] Add error handling for expired tokens

### Phase 2: Content Import Features
- [ ] **Image Import**
  - [ ] Fetch Instagram images and upload to WordPress media library
  - [ ] Preserve image metadata (caption, date, hashtags)
  - [ ] Handle different image sizes/formats
  - [ ] Add image optimization options

- [ ] **Post Creation**
  - [ ] Convert Instagram posts to WordPress posts
  - [ ] Map Instagram captions to WordPress content
  - [ ] Extract and convert hashtags to WordPress tags
  - [ ] Set appropriate post status (draft/publish)

### Phase 3: Automation & Scheduling
- [ ] **Automated Import**
  - [ ] Background task to check for new Instagram posts
  - [ ] Configurable import frequency
  - [ ] Duplicate detection to avoid re-importing
  - [ ] Import history tracking

- [ ] **Content Filtering**
  - [ ] Filter posts by hashtags
  - [ ] Skip certain post types (stories, reels, etc.)
  - [ ] Content moderation options
  - [ ] Custom import rules

### Phase 4: Chat Interface Integration
- [ ] **Instagram Chat Commands**
  - [ ] "import instagram posts" - Import recent posts
  - [ ] "connect instagram" - Setup Instagram connection
  - [ ] "instagram status" - Check connection and recent activity
  - [ ] "import instagram post [URL]" - Import specific post

- [ ] **Enhanced AI Features**
  - [ ] Auto-generate WordPress content from Instagram captions
  - [ ] Suggest WordPress categories based on Instagram content
  - [ ] Create WordPress galleries from Instagram carousel posts

## Technical Implementation Plan

### File Structure
```
instagram_client.py     # Instagram API client
instagram_routes.py     # Flask routes for Instagram features
instagram_auth.py       # OAuth and token management
templates/instagram.py  # Instagram-specific UI components
static/instagram.js     # Frontend Instagram functionality
```

### Environment Variables to Add
```bash
# Instagram API Configuration
INSTAGRAM_CLIENT_ID=your-instagram-client-id
INSTAGRAM_CLIENT_SECRET=your-instagram-client-secret
INSTAGRAM_REDIRECT_URI=http://localhost:5000/auth/instagram/callback

# Instagram User Configuration
INSTAGRAM_ACCESS_TOKEN=user-access-token-after-oauth
INSTAGRAM_USER_ID=instagram-user-id
```

### Database Considerations
- Consider adding SQLite database for:
  - Import history tracking
  - Instagram post metadata
  - User preferences and settings
  - Scheduled import tasks

### API Endpoints to Add
```
GET  /api/instagram/auth          # Start Instagram OAuth flow
GET  /auth/instagram/callback     # Handle OAuth callback
GET  /api/instagram/posts         # Get Instagram posts
POST /api/instagram/import        # Import posts to WordPress
GET  /api/instagram/status        # Check connection status
```

## Research & Prerequisites

### Instagram API Requirements
- [ ] **Research Instagram Basic Display API limits**
  - Rate limits and quotas
  - Required permissions and scopes
  - Long-lived vs short-lived tokens

- [ ] **Understand Instagram content types**
  - Image posts vs carousel posts
  - Video content handling
  - Stories and Reels (if applicable)

### WordPress Integration Points
- [ ] **Media Library Integration**
  - Optimal image upload methods
  - Metadata preservation
  - File naming conventions

- [ ] **Content Mapping Strategy**
  - Instagram caption → WordPress content
  - Instagram hashtags → WordPress tags
  - Instagram location → WordPress custom fields

## Testing Strategy
- [ ] **Unit Tests**
  - Instagram API client methods
  - Content parsing and conversion
  - WordPress integration functions

- [ ] **Integration Tests**
  - End-to-end import workflow
  - Error handling scenarios
  - Rate limiting behavior

- [ ] **User Acceptance Testing**
  - Chat interface commands
  - Manual import processes
  - Automated import scheduling

## Security Considerations
- [ ] **Token Security**
  - Secure storage of Instagram access tokens
  - Token refresh mechanisms
  - Encryption of sensitive data

- [ ] **API Security**
  - Input validation for Instagram data
  - Rate limiting on import endpoints
  - User authentication for Instagram features

## Documentation Updates Needed
- [ ] Update README.md with Instagram setup instructions
- [ ] Add Instagram API configuration guide
- [ ] Document new chat commands
- [ ] Create troubleshooting section for Instagram issues

## Success Criteria
- [ ] Successfully authenticate with Instagram API
- [ ] Import Instagram images to WordPress media library
- [ ] Create WordPress posts from Instagram content
- [ ] Chat interface commands work seamlessly
- [ ] Automated import runs without errors
- [ ] Proper error handling and user feedback

## Future Enhancements (Phase 5+)
- [ ] **Multi-Account Support** - Handle multiple Instagram accounts
- [ ] **Advanced Filtering** - AI-powered content curation
- [ ] **Cross-Platform Sync** - Sync with other social media platforms
- [ ] **Analytics Integration** - Track import success rates and engagement
- [ ] **Custom Templates** - WordPress post templates for different Instagram content types

## Notes
- Instagram Basic Display API is read-only (perfect for our use case)
- Consider implementing webhook support for real-time imports
- May need to handle Instagram's content policy restrictions
- Plan for Instagram API changes and deprecations