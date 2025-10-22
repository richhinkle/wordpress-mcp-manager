# Instagram OAuth Setup Guide

## Overview

This guide shows you how to set up "Login with Instagram" for your WordPress MCP Manager, allowing users to connect their Instagram accounts and import posts directly via the official Instagram API.

## Benefits of Instagram OAuth

✅ **Legal & Reliable** - Uses official Instagram API  
✅ **No Rate Limiting** - Proper API access  
✅ **High Quality Images** - Full resolution media  
✅ **Real-time Data** - Always up-to-date posts  
✅ **User Controlled** - Users grant specific permissions  

## Step 1: Create Instagram App

### 1.1 Go to Facebook Developer Console
Visit: https://developers.facebook.com/

### 1.2 Create New App
1. Click "Create App"
2. Choose "Consumer" as app type
3. Fill in app details:
   - **App Name**: "WordPress MCP Manager" (or your choice)
   - **App Contact Email**: Your email
   - **App Purpose**: "Yourself or your own business"

### 1.3 Add Instagram API Product
1. In your app dashboard, find "Instagram API" in the left sidebar
2. Click on "Instagram API" to access the setup

## Step 2: Configure Instagram API (Current Interface)

Based on the current Meta interface you're seeing:

### 2.1 Step 1: Configure Permissions
1. Go to "Permissions and features" (which you're currently viewing)
2. Find "instagram_basic" permission
3. ✅ **You've already enabled this** - perfect! This allows reading Instagram profile info and media
4. You can ignore the other permissions for now (they're for advanced features)

### 2.2 Step 2: Configure Required Permissions
Based on your "API setup with Facebook login" page, you need to:

1. **Add required content permissions** (for Instagram content access):
   - Click "Add required content permissions" 
   - This will enable: `instagram_basic`, `instagram_content_publishing`, `pages_read_engagement`, etc.

2. **For our WordPress MCP Manager, we only need**:
   - ✅ `instagram_basic` (already enabled)
   - ✅ `pages_read_engagement` (to read Instagram content)

### 2.3 Step 3: Configure Webhooks (Optional)
Scroll down to "Configure webhooks" section and add:
- **Callback URL**: `http://localhost:5000/auth/instagram/callback`
- **Verify Token**: `cardmyyard_webhook_2024` (or any string you choose)

### 2.4 Step 4: Complete App Review (For Production)
For now, you can skip "Complete app review" - your app will work in development mode with test users.

## Important Notes for Current Interface

**Instagram App Name**: I can see yours is "CardMyYard_WP-IG" - that's perfect!

**Instagram App ID**: `1753401634114971` (visible in your screenshot)

**Instagram App Secret**: Click "Show" to reveal (keep this secure!)

### Account Type Requirements
The current Instagram API requires **Instagram Business or Creator accounts**. If @cardmyyard_oviedo is a personal account, you'll need to:

1. Go to Instagram app settings
2. Switch to "Professional account" 
3. Choose "Business" or "Creator"
4. Complete the business profile setup

## Step 3: Configure Your Application

### 3.1 Update Environment Variables
Based on your Instagram app, copy these credentials to your `.env` file:

```bash
# Instagram OAuth Configuration
INSTAGRAM_CLIENT_ID=1753401634114971
INSTAGRAM_CLIENT_SECRET=your-app-secret-from-show-button
INSTAGRAM_REDIRECT_URI=http://localhost:5000/auth/instagram/callback

# Flask Secret Key (required for sessions)
SECRET_KEY=your-random-secret-key-here
```

**To get your app secret:**
1. Click the "Show" button next to "Instagram app secret" in your Meta console
2. Copy the revealed secret key
3. Paste it as your `INSTAGRAM_CLIENT_SECRET`

### 3.2 Generate Secret Key
```python
import secrets
print(secrets.token_hex(32))
```

## Step 4: Test the Integration

### 4.1 Start Your Application
```bash
# Activate virtual environment
venv\Scripts\activate

# Start the app
python run.py
```

### 4.2 Test with API Integration Helper (Recommended First)
Before testing with your WordPress app:

1. **Convert @cardmyyard_oviedo to Business Account**:
   - Open Instagram app → Settings → Account
   - Switch to Professional Account → Business
   - Complete business profile setup

2. **Connect Account in Meta Console**:
   - In the "API integration helper" page you're viewing
   - Connect your Instagram Business account
   - This will populate the access token field

3. **Test API Calls**:
   - Try the "Send messages" feature
   - Test getting user profile and media
   - Verify everything works before using WordPress app

### 4.3 Test OAuth Flow in WordPress App
1. Open http://localhost:5000
2. In chat, type: `connect instagram`
3. Click "Connect Instagram Account"
4. Login with @cardmyyard_oviedo account
5. Grant permissions to your app
6. You should be redirected back with success

### 4.3 Test Import
1. Type: `instagram status` - Should show connected
2. Type: `import my instagram posts` - Should import recent posts
3. Check WordPress drafts for imported content

## Step 5: Production Deployment

### 5.1 Update Redirect URI
Add your production domain to Instagram app settings:
```
https://yourdomain.com/auth/instagram/callback
```

### 5.2 Environment Variables
Update production environment with:
- `INSTAGRAM_CLIENT_ID`
- `INSTAGRAM_CLIENT_SECRET` 
- `INSTAGRAM_REDIRECT_URI` (production URL)
- `SECRET_KEY` (strong random key)

## Available Chat Commands

Once Instagram OAuth is configured:

### Authentication
- `connect instagram` - Start OAuth flow
- `instagram status` - Check connection status
- `disconnect instagram` - Remove connection

### Import Posts
- `import my instagram posts` - Import recent posts (default 10)
- `import my instagram posts 25` - Import specific number
- `instagram help` - Show all commands

## Quick Setup Checklist

Based on your current Meta Developer Console:

### ✅ Step 1: Permissions (DONE)
- You've already enabled "instagram_basic" ✅
- This gives access to profile and media data

### 🔄 Step 2: Add Content Permissions  
- Click "Add required content permissions" button
- This enables reading Instagram posts/media

### 🔄 Step 3: Configure Webhooks
In the "Configure webhooks" section:
- **Callback URL**: `http://localhost:5000/auth/instagram/callback`
- **Verify Token**: `cardmyyard_webhook_2024`

### 🔄 Step 4: Get App Credentials
Go back to main Instagram API page:
- **App ID**: `1753401634114971` ✅ (already visible)
- **App Secret**: Click "Show" button and copy

### 🔄 Step 5: Test API Access (Optional)
The "API integration helper" page you're viewing is great for testing:

1. **Get Access Token**: You'll need to add your Instagram professional account first
2. **Test API Calls**: Use the interface to test Instagram API endpoints
3. **Send Messages**: Test the messaging functionality

### 🔄 Step 6: Update .env File
```bash
INSTAGRAM_CLIENT_ID=1753401634114971
INSTAGRAM_CLIENT_SECRET=your-secret-from-show-button
INSTAGRAM_REDIRECT_URI=http://localhost:5000/auth/instagram/callback
SECRET_KEY=your-random-secret-key
```

## Account Requirements

**Important**: The current Instagram API requires a **Business or Creator account**. 

To convert @cardmyyard_oviedo:
1. Open Instagram app
2. Go to Settings → Account → Switch to professional account
3. Choose "Business" 
4. Complete business information

## Troubleshooting

### Common Issues

**"Instagram OAuth not configured"**
- Check environment variables are set
- Restart the application after adding variables

**"Invalid redirect URI"**
- Ensure callback URL in Meta console matches exactly
- Check for trailing slashes or http vs https

**"Business account required"**
- Convert Instagram account to Business/Creator type
- Personal accounts won't work with current API

**"Token expired"**
- Tokens last 60 days and auto-refresh
- If expired, user needs to reconnect

### Debug Mode
Set `DEBUG=true` in `.env` to see detailed error messages.

## Security Notes

- Keep `INSTAGRAM_CLIENT_SECRET` secure
- Use strong `SECRET_KEY` in production
- Tokens are stored locally in `instagram_tokens.json`
- Users can disconnect anytime to revoke access

## API Limits

Instagram Basic Display API limits:
- 200 requests per hour per user
- 25 media items per request
- Long-lived tokens (60 days, auto-refresh)

## Next Steps

1. **Multi-user Support** - Add user accounts to your app
2. **Scheduled Imports** - Automatically import new posts
3. **Content Filtering** - Import only posts with specific hashtags
4. **Advanced Features** - Stories, Reels (if API supports)

---

## Alternative Content Extraction Methods

Since Instagram blocks automated scraping, here are options to get full content without Facebook OAuth:

### Option 1: Enhanced Scraping Techniques

#### Browser Automation (Most Reliable)
- **Selenium with stealth mode** - Mimics real user behavior
- **Headless Chrome** - Handles JavaScript-rendered content
- **Rotating user agents** - Different browsers/devices to avoid detection

**Pros**: Gets full content including images and captions  
**Cons**: Slower, requires browser installation, still detectable

#### Implementation Example:
```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Headless browser that bypasses basic anti-bot measures
options = Options()
options.add_argument('--headless')
options.add_argument('--user-agent=Mozilla/5.0...')
```

### Option 2: Third-Party Services

#### Instagram API Alternatives
- **RapidAPI Instagram scrapers** ($5-20/month)
- **ScrapingBee, ScrapFly** - Proxy + scraping services
- **InstagramAPI libraries** - Community-maintained packages

#### Social Media Aggregators
- **IFTTT** (If This Then That) - Free tier available
- **Zapier** - Connects Instagram to WordPress automatically
- **Buffer, Hootsuite APIs** - If you use these social media tools

**Pros**: Handle anti-bot measures, often have free tiers  
**Cons**: Monthly costs, may have usage limits

### Option 3: Hybrid Manual Approach

#### Enhanced Manual Import
```python
def manual_import_with_content():
    url = input("Instagram URL: ")
    caption = input("Paste caption: ")
    image_url = input("Paste image URL: ")
    # Process and import to WordPress
```

#### Browser Extension
Create a browser extension that:
- Runs on Instagram pages
- Extracts content when you click a button  
- Sends data to your WordPress app

**Pros**: User-controlled, reliable, respects Instagram ToS  
**Cons**: Manual step required for each import

### Option 4: Instagram Embed Approach

#### Use Official Instagram Embeds
```python
# Access Instagram's embed endpoints
embed_url = f"https://www.instagram.com/p/{shortcode}/embed/"
# Extract oEmbed data (less protected than main pages)
```

**Pros**: Uses Instagram's official embed system  
**Cons**: Limited data available, may still be restricted

### Option 5: Mobile App Approach

#### Instagram Mobile Web
```python
# Mobile endpoints sometimes less protected
mobile_url = f"https://www.instagram.com/p/{shortcode}/?__a=1"
# Try mobile-specific Instagram URLs
```

### Recommended Implementation Strategy

#### Phase 1: Enhanced Manual Import (Quick Win)
1. Add content input fields to chat interface
2. Make copy/paste from Instagram easy
3. Auto-detect image URLs from clipboard
4. Provide helpful prompts for manual entry

#### Phase 2: Browser Automation (If Needed)
1. Selenium with stealth mode for full automation
2. Headless Chrome with realistic user behavior
3. Fallback to manual input if automation fails
4. Respect rate limits and Instagram's terms

#### Phase 3: Hybrid Approach
```python
def enhanced_instagram_import(url, caption=None, image_url=None):
    if not caption or not image_url:
        # Try automated extraction first
        try:
            data = scrape_with_selenium(url)
            caption = caption or data.get('caption')
            image_url = image_url or data.get('image_url')
        except:
            # Graceful fallback to manual input
            caption = prompt_for_caption()
            image_url = prompt_for_image()
    
    return import_to_wordpress(url, caption, image_url)
```

### Current Status

**✅ Working Now:**
- Instagram URL parsing and validation
- WordPress post creation with metadata
- Instagram shortcode and URL preservation
- Custom fields for import tracking

**🔄 Content Extraction Options:**
- Manual copy/paste (immediate solution)
- Browser automation (technical solution)
- Third-party services (paid solution)
- OAuth integration (complex but official)

Choose the approach that best fits your technical requirements, budget, and Instagram usage patterns.

## Quick Test Script

Test your Instagram OAuth setup:

```bash
python instagram_oauth.py
```

This will show you the authorization URL and setup instructions.