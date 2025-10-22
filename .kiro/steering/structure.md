# Project Structure & File Organization

## Current Structure Overview
```
wordpress-mcp-manager/
├── docs/                    # Documentation files
├── src/                     # Source code (future organization)
├── static/                  # Frontend assets
├── tests/                   # Test files
├── config/                  # Configuration templates
├── scripts/                 # Utility scripts
├── .kiro/                   # Kiro IDE settings
├── venv/                    # Python virtual environment
└── [root files]             # Main application files
```

## File Organization Rules

### Documentation (`docs/`)
- **Setup guides**: `docs/setup/`
- **API documentation**: `docs/api/`
- **User guides**: `docs/guides/`
- **Architecture docs**: `docs/architecture/`

**Current files to move:**
- `AIWU-WordPress-MCP-Setup-Guide.md` → `docs/setup/`
- `INSTAGRAM_OAUTH_SETUP.md` → `docs/setup/`
- `WordPress-MCP-User-Interface-Options*.md` → `docs/architecture/`
- `Standalone-WordPress-MCP-Application.md` → `docs/architecture/`

### Source Code (`src/`)
- **Core application**: `src/core/`
- **API handlers**: `src/api/`
- **Integrations**: `src/integrations/`
- **Utilities**: `src/utils/`

**Current files to organize:**
- `app.py` → `src/core/`
- `chat_handler.py` → `src/core/`
- `templates.py` → `src/core/`
- `instagram_*.py` → `src/integrations/instagram/`
- `wordpress_mcp_*.py` → `src/integrations/wordpress/`

### Frontend Assets (`static/`)
- **JavaScript**: `static/js/`
- **CSS**: `static/css/`
- **Images**: `static/images/`
- **Icons**: `static/icons/`

### Tests (`tests/`)
- **Unit tests**: `tests/unit/`
- **Integration tests**: `tests/integration/`
- **Test data**: `tests/fixtures/`

**Current files:**
- `test_instagram_integration.py` → `tests/integration/`

### Configuration (`config/`)
- **Environment templates**: `config/env/`
- **Docker configs**: `config/docker/`
- **Deployment configs**: `config/deploy/`

### Scripts (`scripts/`)
- **Development utilities**: `scripts/dev/`
- **Deployment scripts**: `scripts/deploy/`
- **Data migration**: `scripts/migration/`

## Naming Conventions

### Python Files
- **Modules**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions**: `snake_case()`
- **Constants**: `UPPER_SNAKE_CASE`

### Documentation
- **Guides**: `kebab-case.md`
- **API docs**: `api-endpoint-name.md`
- **Setup docs**: `setup-service-name.md`

### Configuration Files
- **Environment**: `.env`, `.env.example`, `.env.production`
- **Docker**: `Dockerfile`, `docker-compose.yml`
- **Requirements**: `requirements.txt`, `requirements-dev.txt`

## Import Patterns

### Relative Imports
```python
# Within same package
from .module_name import ClassName
from .utils import helper_function

# From parent package
from ..core.app import app
from ..integrations.wordpress import WordPressMCPClient
```

### Absolute Imports
```python
# External libraries first
import os
import json
from flask import Flask

# Then project imports
from src.core.app import create_app
from src.integrations.instagram import InstagramOAuth
```

## File Placement Guidelines

### New Features
1. **API endpoints** → `src/api/`
2. **Integration modules** → `src/integrations/service_name/`
3. **Utility functions** → `src/utils/`
4. **Documentation** → `docs/guides/`

### Configuration
1. **Environment variables** → `.env.example` (template), `.env` (local)
2. **Service configs** → `config/service_name/`
3. **Deployment configs** → `config/deploy/platform_name/`

### Assets
1. **JavaScript modules** → `static/js/modules/`
2. **CSS components** → `static/css/components/`
3. **Images/media** → `static/images/category/`

## Migration Strategy

When reorganizing existing files:
1. **Create new directory structure first**
2. **Move files in logical groups**
3. **Update import statements**
4. **Test functionality after each group**
5. **Update documentation references**