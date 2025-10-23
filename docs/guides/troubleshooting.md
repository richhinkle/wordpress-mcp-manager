# Troubleshooting Guide

## Common Issues and Solutions

### Instagram Scraping Issues

#### "No posts found for user"

**Symptoms:**
- Chat command returns empty results
- API response shows 0 posts
- User exists but no content is retrieved

**Solutions:**
1. **Check if account is public**
   ```
   Chat: "instagram profile @username"
   ```
   Look for `"isPrivate": false` in the response

2. **Verify username spelling**
   - Instagram usernames are case-sensitive
   - Remove @ symbol when using API directly
   - Check for typos or special characters

3. **Clear user cache**
   ```
   Chat: "clear cache @username"
   ```

4. **Check Apify account limits**
   ```
   Chat: "apify status"
   ```

#### "Apify API error" or "Rate limit exceeded"

**Symptoms:**
- Error messages mentioning Apify
- Scraping stops working suddenly
- API returns 429 status codes

**Solutions:**
1. **Check Apify account status**
   - Visit https://console.apify.com
   - Check compute unit balance
   - Review usage statistics

2. **Use cache to reduce API calls**
   ```
   Chat: "cache stats"
   ```
   Cached data is used automatically for 1 hour

3. **Clear expired cache to free up space**
   ```
   Chat: "clear expired cache"
   ```

4. **Upgrade Apify plan if needed**
   - Free tier: 625 compute units/month
   - Paid plans available for higher usage

#### "Images not displaying in post viewer"

**Symptoms:**
- Post viewer shows broken image icons
- Images load slowly or not at all
- Console shows CORS errors

**Solutions:**
1. **This is expected behavior**
   - Instagram blocks direct image display
   - Images will work when imported to WordPress
   - Use image URLs for reference only

2. **Check network connection**
   - Slow connections may timeout
   - Try refreshing the page

### WordPress Integration Issues

#### "WordPress connection failed"

**Symptoms:**
- "Site health" command shows errors
- Posts fail to import
- API returns connection errors

**Solutions:**
1. **Verify WordPress URL**
   ```bash
   # Check .env file
   WORDPRESS_URL=https://your-site.com/wp-json/mcp/v1/sse
   ```
   - Must include `/wp-json/mcp/v1/sse`
   - Use HTTPS if available
   - No trailing slash

2. **Check MCP plugin status**
   - Login to WordPress admin
   - Go to Plugins → Installed Plugins
   - Ensure AIWU MCP plugin is active
   - Check plugin version compatibility

3. **Verify access token**
   ```bash
   # In .env file
   ACCESS_TOKEN=your-32-character-token
   ```
   - Token must be exactly 32 characters
   - Generate new token if needed
   - Check for extra spaces or characters

4. **Test connection manually**
   ```bash
   curl -X POST "https://your-site.com/wp-json/mcp/v1/sse" \
     -H "Authorization: Bearer your-token" \
     -H "Content-Type: application/json" \
     -d '{"action": "get_posts", "params": {"numberposts": 1}}'
   ```

#### "Post import failed" or "Media upload failed"

**Symptoms:**
- Instagram posts don't appear in WordPress
- Images fail to upload
- Import process completes but no posts created

**Solutions:**
1. **Check WordPress permissions**
   - Ensure uploads directory is writable
   - Check file size limits in WordPress
   - Verify user has post creation permissions

2. **Check disk space**
   - WordPress server needs space for images
   - Large Instagram images may fail upload
   - Monitor server storage usage

3. **Review WordPress error logs**
   - Check WordPress debug.log
   - Look for PHP errors or warnings
   - Check server error logs

4. **Test with smaller batch**
   ```
   Chat: "scrape instagram @username"
   # Import one post at a time to isolate issues
   ```

#### "Posts created but images missing"

**Symptoms:**
- WordPress posts exist but show broken images
- Media library doesn't contain Instagram images
- Post content has image placeholders

**Solutions:**
1. **Check image URL accessibility**
   - Instagram may block server requests
   - Try importing again (URLs may refresh)
   - Check server firewall settings

2. **Verify media upload permissions**
   ```bash
   # Check WordPress uploads directory
   ls -la wp-content/uploads/
   ```

3. **Manual image upload**
   - Download images manually
   - Upload via WordPress media library
   - Update post content with new URLs

### Application Issues

#### "Application won't start"

**Symptoms:**
- `python run.py` fails
- Import errors on startup
- Port already in use errors

**Solutions:**
1. **Check Python version**
   ```bash
   python --version
   # Should be 3.8 or higher
   ```

2. **Verify virtual environment**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   
   # Check if activated
   which python
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Check port availability**
   ```bash
   # Windows
   netstat -an | findstr :5000
   
   # macOS/Linux
   lsof -i :5000
   ```
   
   Change port in .env if needed:
   ```bash
   PORT=5001
   ```

5. **Check .env file**
   ```bash
   # Copy template if missing
   cp .env.example .env
   ```

#### "Chat interface not responding"

**Symptoms:**
- Chat messages don't process
- No response to commands
- JavaScript errors in console

**Solutions:**
1. **Check browser console**
   - Press F12 to open developer tools
   - Look for JavaScript errors
   - Check network tab for failed requests

2. **Clear browser cache**
   - Hard refresh: Ctrl+F5 (Windows) or Cmd+Shift+R (Mac)
   - Clear browser cache and cookies
   - Try incognito/private mode

3. **Check Flask server logs**
   - Look at terminal where `python run.py` is running
   - Check for Python errors or exceptions
   - Restart server if needed

4. **Verify API endpoints**
   ```bash
   # Test health endpoint
   curl http://localhost:5000/api/health
   ```

#### "Cache issues" or "Stale data"

**Symptoms:**
- Old Instagram data showing
- Changes not reflected
- Cache statistics show errors

**Solutions:**
1. **Check cache directory**
   ```bash
   ls -la cache/apify/
   ```

2. **Clear all cache**
   ```
   Chat: "clear all cache"
   ```

3. **Check cache permissions**
   ```bash
   # Ensure cache directory is writable
   chmod 755 cache/
   chmod 644 cache/apify/*
   ```

4. **Reset cache system**
   ```bash
   # Remove cache directory and restart
   rm -rf cache/apify/
   python run.py
   ```

### Environment and Configuration Issues

#### "Environment variables not loading"

**Symptoms:**
- Application uses default values
- API tokens not recognized
- Configuration seems ignored

**Solutions:**
1. **Check .env file location**
   ```bash
   # Must be in project root
   ls -la .env
   ```

2. **Verify .env format**
   ```bash
   # No spaces around = sign
   WORDPRESS_URL=https://example.com
   # Not: WORDPRESS_URL = https://example.com
   ```

3. **Check for hidden characters**
   ```bash
   # View file with cat to see hidden chars
   cat -A .env
   ```

4. **Restart application**
   ```bash
   # Environment variables loaded on startup
   python run.py
   ```

#### "SSL/HTTPS certificate errors"

**Symptoms:**
- HTTPS requests fail
- Certificate verification errors
- SSL handshake failures

**Solutions:**
1. **Use HTTP for testing**
   ```bash
   # Temporarily use HTTP
   WORDPRESS_URL=http://your-site.com/wp-json/mcp/v1/sse
   ```

2. **Update certificates**
   ```bash
   # Update system certificates
   pip install --upgrade certifi
   ```

3. **Disable SSL verification (not recommended for production)**
   ```python
   # In development only
   import ssl
   ssl._create_default_https_context = ssl._create_unverified_context
   ```

### Performance Issues

#### "Slow response times"

**Symptoms:**
- Chat commands take long to respond
- API requests timeout
- Page loads slowly

**Solutions:**
1. **Check network connection**
   - Test internet speed
   - Try different network
   - Check for proxy/firewall issues

2. **Optimize cache usage**
   ```
   Chat: "cache stats"
   ```
   - Use cached data when possible
   - Clear expired cache regularly

3. **Reduce batch sizes**
   ```
   # Instead of bulk import 50 posts
   Chat: "scrape instagram @username"
   # Import in smaller batches
   ```

4. **Check server resources**
   - Monitor CPU and memory usage
   - Close unnecessary applications
   - Consider upgrading hardware

#### "High memory usage"

**Symptoms:**
- Application becomes slow
- System runs out of memory
- Frequent crashes

**Solutions:**
1. **Clear cache regularly**
   ```
   Chat: "clear expired cache"
   ```

2. **Reduce concurrent operations**
   - Import posts one at a time
   - Avoid multiple browser tabs
   - Close other applications

3. **Restart application periodically**
   ```bash
   # Stop and restart
   Ctrl+C
   python run.py
   ```

## Diagnostic Commands

### System Health Check
```
Chat: "site health"
```
Tests WordPress connection, MCP plugin status, and basic functionality.

### Apify Status Check
```
Chat: "apify status"
```
Verifies Apify API connection and account status.

### Cache Statistics
```
Chat: "cache stats"
```
Shows cache usage, hit rates, and storage information.

### Debug Information
```
Chat: "debug info"
```
Displays system information, versions, and configuration status.

## Getting Help

### Log Files
- **Application logs**: Check terminal output where `python run.py` is running
- **WordPress logs**: Check `wp-content/debug.log` if WP_DEBUG is enabled
- **Server logs**: Check web server error logs

### Debug Mode
Enable debug mode in .env:
```bash
DEBUG=true
```
This provides more detailed error messages and logging.

### Support Channels
1. **Check documentation**: Review setup guides and API documentation
2. **Search issues**: Look for similar problems in project issues
3. **Create issue**: Provide detailed error messages and steps to reproduce

### Information to Include When Reporting Issues
- Operating system and version
- Python version
- Error messages (full text)
- Steps to reproduce
- .env configuration (without sensitive tokens)
- Browser and version (for UI issues)
- WordPress version and plugin versions