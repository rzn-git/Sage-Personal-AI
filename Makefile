.PHONY: run test clean install

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

# Help
help:
	@echo "Available targets:"
	@echo "  all      - Install dependencies and run the application"
	@echo "  install  - Install dependencies"
	@echo "  run      - Run the application"
	@echo "  test     - Run tests"
	@echo "  clean    - Clean up generated files"
	@echo "  venv     - Create a virtual environment"
	@echo "  help     - Show this help message" 