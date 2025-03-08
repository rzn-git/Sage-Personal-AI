# Sage: Personal AI

A secure, customizable personal AI assistant built with Streamlit, leveraging OpenAI and Anthropic models.

## Features

- Chat with multiple AI models (OpenAI GPT and Anthropic Claude)
- Secure authentication system
- Chat history management
- Usage tracking and quotas
- Responsive UI

## Getting Started

### Prerequisites

- Python 3.9 or higher
- API keys for OpenAI and Anthropic

### Installation

#### Option 1: Using Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/sage-personal-ai.git
   cd sage-personal-ai
   ```

2. Create a `.env` file with your API keys:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. Build and run with Docker Compose:
   ```bash
   docker-compose up -d
   ```

4. Access the application at http://localhost:8501

#### Option 2: Manual Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/sage-personal-ai.git
   cd sage-personal-ai
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your API keys:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. Run the application:
   ```bash
   streamlit run app.py
   ```

## Development

### Project Structure

```
sage-personal-ai/
├── app.py              # Main Streamlit application
├── auth_config.py      # Authentication configuration
├── error_handler.py    # Error handling utilities
├── logging_config.py   # Logging configuration
├── utils.py            # Utility functions
├── run.py              # Application runner
├── test_app.py         # Unit tests
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose configuration
├── requirements.txt    # Python dependencies
├── Makefile            # Build automation
└── .github/workflows/  # CI/CD pipelines
```

### Using the Makefile

The project includes a Makefile with useful commands:

```bash
# Install dependencies
make install

# Run the application
make run

# Run tests
make test

# Build Docker image
make docker-build

# Run with Docker
make docker-run

# Stop Docker containers
make docker-stop

# Run security checks
make security-check
```

## DevOps and Security

### CI/CD Pipeline

The project includes a GitHub Actions workflow for continuous integration and deployment:

- Automated testing
- Security scanning with Bandit
- Dependency vulnerability checking
- Docker image building

### Security Features

- Environment variables for sensitive configuration
- Authentication system with password protection
- API usage quotas
- Comprehensive error handling and logging
- Docker containerization for isolation

### Deployment Options

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -am 'Add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Streamlit for the web framework
- OpenAI and Anthropic for the AI models 