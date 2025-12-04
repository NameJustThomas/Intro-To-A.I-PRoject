# Contributing to AI Attendance System

Thank you for your interest in contributing to the AI Attendance System!

## Development Setup

1. **Prerequisites**
   - Docker & Docker Compose
   - Python 3.11+ (for local development)
   - Git

2. **Local Development**
   ```bash
   cd infra
   docker compose up --build
   ```

3. **Backend Development**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

## Code Style

We use the following tools for code quality:
- **black** - Code formatting
- **isort** - Import sorting
- **flake8** - Linting

### Pre-commit Hooks

Install pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```

## Testing

Run tests:
```bash
cd backend
pytest
```

## Pull Request Process

1. **All changes MUST be submitted via Pull Request**
   - DO NOT push directly to `main` branch
   - Create a feature branch from `main`

2. **PR Requirements**
   - All tests must pass
   - Code must be linted and formatted
   - Include tests for new functionality
   - Update documentation if needed
   - Add migration files if database changes are made

3. **PR Template**
   - Use the PR template in `.github/PULL_REQUEST_TEMPLATE.md`
   - Fill out all sections
   - Check all items in the checklist

## Database Migrations

- All database changes must be accompanied by migration files
- Migration files should be in `infra/migrations/`
- Name migrations with sequential numbers: `001_init.sql`, `002_add_field.sql`, etc.

## Commit Messages

Use clear, descriptive commit messages:
- Start with a verb (Add, Fix, Update, Remove)
- Be specific about what changed
- Reference issue numbers if applicable

Example:
```
Add face registration endpoint with multi-image support
Fix attendance log timestamp timezone issue
Update OpenAPI spec with new response schemas
```

## Questions?

If you have questions, please open an issue or contact the maintainers.

