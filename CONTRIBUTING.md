# Contributing to AllStarLink Transcriber

First off, thank you for considering contributing to AllStarLink Transcriber! It's people like you that make this project such a great tool for the amateur radio community.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps which reproduce the problem**
* **Provide specific examples to demonstrate the steps**
* **Describe the behavior you observed after following the steps**
* **Describe the behavior you expected to see**
* **Include screenshots if possible**
* **Include your environment details** (Docker version, OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title**
* **Provide a step-by-step description of the suggested enhancement**
* **Provide specific examples to demonstrate the steps**
* **Describe the current behavior and the expected behavior**
* **Explain why this enhancement would be useful**

### Pull Requests

* Follow the Python PEP 8 style guide for backend code
* Follow React/JavaScript best practices for frontend code
* Include comments explaining complex logic
* Update documentation as needed
* Add tests if applicable
* End all files with a newline

## Development Setup

1. Fork the repository
2. Clone your fork
3. Create a feature branch (`git checkout -b feature/AmazingFeature`)
4. Make your changes
5. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
6. Push to your branch (`git push origin feature/AmazingFeature`)
7. Open a Pull Request

### Local Development

```bash
# Backend development
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend development
cd frontend
npm install
npm run dev
```

### Building Docker Image

```bash
docker-compose build --no-cache
docker-compose up -d
```

## Styleguides

### Python (Backend)

* Follow PEP 8
* Use type hints where possible
* Write docstrings for all functions
* Use meaningful variable names

### JavaScript/React (Frontend)

* Use functional components with hooks
* Use meaningful component names
* Write comments for complex logic
* Use Tailwind CSS for styling
* No inline styles unless necessary

### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

### Documentation

* Use Markdown formatting
* Include code examples where helpful
* Keep documentation up-to-date with code changes
* Use clear, simple language

## Project Structure

```
allstarlink-transcriber/
├── backend/                 # Python FastAPI backend
├── frontend/                # React frontend
├── Dockerfile               # Docker image definition
├── docker-compose.yml       # Multi-container orchestration
├── .github/                 # GitHub configuration
├── docs/                    # Additional documentation
└── README.md                # Main documentation
```

## Testing

While this project doesn't have automated tests yet, please manually test your changes:

1. Test locally with Docker
2. Verify API endpoints work
3. Test WebSocket connections
4. Check frontend functionality
5. Verify theme switching
6. Test with different configuration values

## Additional Notes

### Issue and Pull Request Labels

* `bug` - Something isn't working
* `enhancement` - New feature or request
* `documentation` - Improvements or additions to documentation
* `good first issue` - Good for newcomers
* `help wanted` - Extra attention is needed
* `question` - Further information is requested

## Recognition

Contributors will be recognized in:
* The project README
* Release notes
* GitHub contributors page

Thank you for contributing! 🎉
