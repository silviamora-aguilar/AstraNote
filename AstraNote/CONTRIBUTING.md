# Contributing to AstraNote

Thank you for your interest in contributing to AstraNote! This document provides guidelines and instructions for development.

## Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/astranote.git
cd astranote
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 4. Verify Setup
```bash
python -m pytest tests/ -v
```

## Workflow

### Branch Naming Convention
Follow this naming pattern for branches:

```
<type>/<requirement-id>-<short-description>
```

**Types:**
- `feat/` - New feature (e.g., `feat/WEB-01-user-registration`)
- `test/` - Test improvements (e.g., `test/BL-15-coverage`)
- `fix/` - Bug fixes (e.g., `fix/SRG-25-xss-validation`)
- `docs/` - Documentation updates (e.g., `docs/api-reference`)
- `refactor/` - Code refactoring (e.g., `refactor/services-layer`)
- `chore/` - Maintenance tasks (e.g., `chore/dependency-update`)

**Example:**
```bash
git checkout -b feat/WEB-09-user-authentication
```

### Commit Message Convention
Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:** `feat`, `fix`, `test`, `docs`, `refactor`, `chore`, `perf`

**Examples:**
```
feat(auth): add bcrypt password hashing (WEB-09)

Implement user registration with bcrypt-hashed passwords.
Relates to requirement WEB-09 (User Model).

Closes #42
```

```
test(repositories): add NoteRepository unit tests (BL-15)

Added 12 unit tests for CRUD operations.
```

### Development Cycle

#### 1. Pull Latest Changes
```bash
git pull origin develop
```

#### 2. Create Feature Branch
```bash
git checkout -b feat/WEB-XX-description
```

#### 3. Write Tests First (TDD)
```bash
# Create test file: tests/unit/test_your_feature.py
# Implement failing tests based on acceptance criteria
pytest tests/unit/test_your_feature.py -v
```

#### 4. Implement Feature
```bash
# Write code to pass the tests
# Update src/app/... files
# Ensure types are annotated (mypy compatible)
```

#### 5. Run Quality Checks
```bash
# Format code
black src tests

# Lint code
flake8 src tests

# Type check
mypy src --ignore-missing-imports

# Run all tests
pytest tests/ -v --cov=src
```

#### 6. Commit & Push
```bash
git add .
git commit -m "feat(scope): description (REQ-ID)"
git push origin feat/WEB-XX-description
```

#### 7. Create Pull Request
Push to GitHub and create a PR with:
- Clear title: `feat: Add user authentication (WEB-09)`
- Reference the requirement ID in the description
- Link related issues: `Closes #42`
- Complete the PR template checklist

### Testing Requirements

#### Unit Tests (`tests/unit/`)
- Test individual functions/methods in isolation
- Use mocks for external dependencies
- Aim for >80% code coverage
- Mark with `@pytest.mark.unit`

```python
import pytest
from src.app.services import NoteService

@pytest.mark.unit
def test_create_note_with_valid_data():
    # Arrange
    service = NoteService()
    # Act
    result = service.create_note(title="Test", content="...")
    # Assert
    assert result.id is not None
```

#### Integration Tests (`tests/integration/`)
- Test interactions between multiple components
- Use TestClient for API endpoints
- Test database operations
- Mark with `@pytest.mark.integration`

```python
import pytest
from fastapi.testclient import TestClient
from src.main import app

@pytest.mark.integration
def test_create_note_endpoint():
    client = TestClient(app)
    response = client.post("/api/notes", json={"title": "Test", "content": "..."})
    assert response.status_code == 201
```

#### Feature Tests (`tests/feature/`)
- Write Gherkin scenarios in `features/` folder
- Implement step definitions in `steps/` folder
- Mark with `@pytest.mark.feature`

```gherkin
# tests/feature/features/user_registration.feature
Feature: User Registration
  Scenario: User registers with valid credentials
    Given I am on the registration page
    When I submit valid registration data
    Then I should be logged in
    And I should see the dashboard
```

### Code Style

#### Black (Formatting)
Auto-format your code:
```bash
black src tests
```

#### Flake8 (Linting)
Check for style violations:
```bash
flake8 src tests --max-line-length=100
```

#### Mypy (Type Checking)
Check type annotations:
```bash
mypy src --ignore-missing-imports
```

### Documentation

- Update docstrings for public functions/classes
- Update README.md if adding user-facing features
- Add comments for complex business logic
- Update docs/ folder for architectural decisions

## Code Review Process

1. **Self-Review:** Run all checks locally before pushing
2. **Automated Tests:** GitHub Actions runs CI/CD on PR
3. **Code Review:** At least one maintainer reviews code
4. **Merge:** Squash-and-merge to main branch (or standard merge to develop)

## Questions or Issues?

- Open a GitHub issue for bugs
- Discuss design decisions in issue threads
- Reference the [requirements.md](planning/requirements.md) for specification details
- Check [architecture decisions](planning/decisions.md) for design rationale

Happy coding! 🚀
