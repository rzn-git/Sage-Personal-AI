.PHONY: run test clean install venv docker-build docker-run docker-stop security-check

# Default target
all: install run

# Install dependencies
install:
	pip install -r requirements.txt

# Run the application
run:
	python run.py

# Run tests
test:
	python -m unittest test_app.py

# Clean up generated files
clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -f app.log
	find . -name "*.pyc" -delete

# Create a virtual environment
venv:
	python -m venv venv
	@echo "Virtual environment created. Activate it with:"
	@echo "  source venv/bin/activate (Linux/Mac)"
	@echo "  venv\\Scripts\\activate (Windows)"

# Docker commands
docker-build:
	docker-compose build

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

# Security checks
security-check:
	@echo "Running security checks..."
	@if command -v bandit >/dev/null 2>&1; then \
		bandit -r . -x ./venv,./tests; \
	else \
		echo "Bandit not installed. Install with: pip install bandit"; \
	fi
	@if command -v safety >/dev/null 2>&1; then \
		safety check -r requirements.txt; \
	else \
		echo "Safety not installed. Install with: pip install safety"; \
	fi

# Help
help:
	@echo "Available targets:"
	@echo "  all            - Install dependencies and run the application"
	@echo "  install        - Install dependencies"
	@echo "  run            - Run the application"
	@echo "  test           - Run tests"
	@echo "  clean          - Clean up generated files"
	@echo "  venv           - Create a virtual environment"
	@echo "  docker-build   - Build Docker image"
	@echo "  docker-run     - Run application in Docker"
	@echo "  docker-stop    - Stop Docker containers"
	@echo "  security-check - Run security checks"
	@echo "  help           - Show this help message" 