# Documentation Index

Welcome to the Instagram-to-WordPress Manager documentation. This comprehensive guide will help you set up, use, and maintain the application.

## 🚀 Getting Started

### Quick Start
- **[Quick Start Guide](QUICK_START.md)** - Get up and running in 5 minutes
- **[Project Summary](PROJECT_SUMMARY.md)** - Complete technical overview

### Setup Guides
- **[WordPress MCP Setup](setup/AIWU-WordPress-MCP-Setup-Guide.md)** - Configure WordPress with MCP plugin
- **[Instagram OAuth Setup](setup/INSTAGRAM_OAUTH_SETUP.md)** - Optional Instagram OAuth configuration

## 📖 User Guides

### Basic Usage
- **[Chat Commands](guides/chat-commands.md)** - Complete list of available commands
- **[Instagram Import Workflow](guides/instagram-workflow.md)** - Step-by-step import process
- **[WordPress Management](guides/wordpress-management.md)** - Managing posts and media

### Advanced Features
- **[Cache Management](guides/cache-management.md)** - Optimizing API usage and performance
- **[Bulk Operations](guides/bulk-operations.md)** - Importing multiple posts efficiently
- **[Troubleshooting](guides/troubleshooting.md)** - Common issues and solutions

## 🔧 Technical Documentation

### API Reference
- **[REST API Endpoints](api/endpoints.md)** - Complete API documentation
- **[Authentication](api/authentication.md)** - API security and tokens
- **[Error Handling](api/errors.md)** - Error codes and responses

### Architecture
- **[System Architecture](architecture/Standalone-WordPress-MCP-Application.md)** - High-level system design
- **[Instagram OAuth Journey](architecture/Instagram-OAuth-Journey.md)** - OAuth implementation details
- **[User Interface Options](architecture/WordPress-MCP-User-Interface-Options-v2.md)** - UI design decisions

### Development
- **[Development Setup](guides/development-setup.md)** - Setting up development environment
- **[Contributing Guidelines](guides/contributing.md)** - How to contribute to the project
- **[Code Style Guide](guides/code-style.md)** - Coding standards and conventions

## 🚀 Deployment

### Deployment Options
- **[Deployment Guide](guides/deployment.md)** - Complete deployment instructions
- **[Docker Deployment](guides/docker-deployment.md)** - Containerized deployment
- **[Cloud Platforms](guides/cloud-deployment.md)** - Heroku, AWS, GCP, DigitalOcean

### Production
- **[Production Checklist](guides/production-checklist.md)** - Pre-deployment verification
- **[Monitoring & Maintenance](guides/monitoring.md)** - Keeping your deployment healthy
- **[Security Best Practices](guides/security.md)** - Securing your installation

## 📊 Reference

### Configuration
- **[Environment Variables](reference/environment-variables.md)** - All configuration options
- **[Cache Configuration](reference/cache-config.md)** - Cache system settings
- **[WordPress Integration](reference/wordpress-integration.md)** - MCP plugin details

### Integrations
- **[Apify Integration](reference/apify-integration.md)** - Instagram scraping service
- **[Instagram API](reference/instagram-api.md)** - Instagram data structures
- **[WordPress MCP](reference/wordpress-mcp.md)** - MCP plugin API reference

## 📝 Development History

### Session Logs
- **[Apify Integration Session](guides/APIFY_INTEGRATION_SESSION.md)** - Development session log
- **[Implementation Complete](guides/IMPLEMENTATION_COMPLETE.md)** - Final implementation summary
- **[Project Reorganization](guides/PROJECT_REORGANIZATION.md)** - File structure reorganization

### Change Log
- **[Version History](CHANGELOG.md)** - Version changes and updates
- **[Migration Guide](guides/migration.md)** - Upgrading between versions

## 🆘 Support

### Getting Help
- **[FAQ](guides/faq.md)** - Frequently asked questions
- **[Troubleshooting](guides/troubleshooting.md)** - Common problems and solutions
- **[Support Channels](guides/support.md)** - Where to get help

### Community
- **[Contributing](guides/contributing.md)** - How to contribute
- **[Code of Conduct](CODE_OF_CONDUCT.md)** - Community guidelines
- **[License](../LICENSE)** - Project license

## 📋 Checklists

### Setup Checklists
- [ ] **WordPress Setup**
  - [ ] Install AIWU MCP plugin
  - [ ] Generate access token
  - [ ] Test MCP connection
  
- [ ] **Application Setup**
  - [ ] Clone repository
  - [ ] Install dependencies
  - [ ] Configure environment variables
  - [ ] Test application startup

- [ ] **Apify Setup** (Optional)
  - [ ] Create Apify account
  - [ ] Get API token
  - [ ] Test Instagram scraping
  - [ ] Configure cache settings

### Deployment Checklist
- [ ] **Pre-deployment**
  - [ ] Test in development environment
  - [ ] Configure production environment variables
  - [ ] Set up SSL certificates
  - [ ] Configure monitoring

- [ ] **Deployment**
  - [ ] Deploy application
  - [ ] Test all endpoints
  - [ ] Verify WordPress integration
  - [ ] Test Instagram scraping

- [ ] **Post-deployment**
  - [ ] Set up monitoring alerts
  - [ ] Configure backups
  - [ ] Document deployment details
  - [ ] Train users

## 🔍 Quick Reference

### Essential Commands
```bash
# Development
python run.py                    # Start development server
pip install -r requirements.txt # Install dependencies

# Chat Commands
"scrape instagram @username"     # Scrape Instagram posts
"bulk import @username"          # Import posts to WordPress
"list drafts"                    # Show draft posts
"publish post 35"                # Publish specific post
"cache stats"                    # Check cache usage
"site health"                    # Test WordPress connection
```

### Key Files
```
├── app.py                       # Main application
├── .env                         # Environment configuration
├── requirements.txt             # Python dependencies
├── docs/                        # Documentation
├── static/app.js               # Frontend JavaScript
└── cache/apify/                # Cached API responses
```

### Important URLs
- **Application**: `http://localhost:5000`
- **Health Check**: `http://localhost:5000/api/health`
- **API Docs**: `http://localhost:5000/api/docs`

---

## 📚 Documentation Structure

This documentation is organized into several main sections:

1. **Getting Started** - Quick setup and overview
2. **User Guides** - How to use the application
3. **Technical Docs** - API reference and architecture
4. **Deployment** - Production deployment guides
5. **Reference** - Configuration and integration details
6. **Support** - Help and troubleshooting

Each section builds upon the previous ones, starting with basic setup and progressing to advanced topics. Use the navigation above to jump to specific topics, or follow the guides in order for a complete understanding of the system.

For immediate help, start with the [Quick Start Guide](QUICK_START.md) or check the [Troubleshooting Guide](guides/troubleshooting.md) if you're experiencing issues.