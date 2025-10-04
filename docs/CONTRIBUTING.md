# Contributing to Smart Stadium

We love your input! We want to make contributing to Smart Stadium as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

## Pull Requests

Pull requests are the best way to propose changes to the codebase. We actively welcome your pull requests:

1. Fork the repo and create your branch from `master`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## Any contributions you make will be under the MIT Software License

In short, when you submit code changes, your submissions are understood to be under the same [MIT License](http://choosealicense.com/licenses/mit/) that covers the project. Feel free to contact the maintainers if that's a concern.

## Report bugs using GitHub's [issue tracker](https://github.com/mdhenninger/smart-lights-football-celebration/issues)

We use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/mdhenninger/smart-lights-football-celebration/issues/new).

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## Development Setup

### Prerequisites

- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Git** for version control
- **WiZ Smart Lights** on same network

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/mdhenninger/smart-lights-football-celebration.git
   cd smart-lights-football-celebration
   ```

2. **Backend Setup**
   ```bash
   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Start FastAPI server
   cd api
   python start_server.py
   ```

3. **Frontend Setup**
   ```bash
   # Install dependencies
   cd frontend/smart-stadium-dashboard
   npm install
   
   # Start development server
   npm run dev
   ```

4. **Test Your Setup**
   ```bash
   # Test API
   cd api
   python test_enhanced_websocket.py
   
   # Test light connectivity
   cd ../src
   python bills_celebrations.py
   ```

## Code Style

### Python
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints where possible
- Use async/await for asynchronous operations
- Include docstrings for functions and classes

### TypeScript/React
- Use [Prettier](https://prettier.io/) for formatting
- Follow [React TypeScript best practices](https://react-typescript-cheatsheet.netlify.app/)
- Use strict TypeScript configuration
- Prefer functional components with hooks

### General
- Write meaningful commit messages
- Keep commits focused and atomic
- Update documentation for API changes
- Add tests for new functionality

## Testing

### Backend Tests
```bash
cd api
python test_comprehensive.py
python test_enhanced_websocket.py
```

### Frontend Tests
```bash
cd frontend/smart-stadium-dashboard
npm run test
npm run type-check
npm run lint
```

### Integration Tests
```bash
# Test full system
python test_smart_stadium.py
python test_dashboard_api.py
```

## Feature Requests

We love feature requests! Please provide:

1. **Clear description** of the feature
2. **Use case** - why would this be useful?
3. **Implementation ideas** (optional)
4. **Mockups or examples** (if applicable)

## Code of Conduct

### Our Pledge

We pledge to make participation in our project and our community a harassment-free experience for everyone.

### Our Standards

Examples of behavior that contributes to creating a positive environment include:

- Using welcoming and inclusive language
- Being respectful of differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

## Recognition

Contributors who make significant improvements will be recognized in our README and release notes.

## Questions?

Feel free to open an issue or reach out to the maintainers. We're here to help!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.