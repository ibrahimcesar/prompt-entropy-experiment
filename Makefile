.PHONY: help install test lint paper clean setup check-env collect-data calculate-metrics run-experiment view-logs
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "======================================"
	@echo "  Prompt Entropy Experiment - Makefile"
	@echo "======================================"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Setup & Installation:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; /^(setup|install|init|check)/ {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Development:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; /^(format|lint|type|test)/ {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Research Workflow:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; /^(notebook|analysis|figures|data)/ {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Documentation:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; /^(paper|docs)/ {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Utilities:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; /^(clean|status)/ {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""

# ============================================================================
# Setup & Installation
# ============================================================================

setup: init-dirs install check-env ## Complete first-time setup (dirs + install + env check)
	@echo "✓ Setup complete! Run 'make help' to see available commands."

init-dirs: ## Create required project directories
	@echo "Creating directory structure..."
	@mkdir -p data/raw data/processed
	@mkdir -p results/tables results/stats
	@mkdir -p figures/plots figures/charts
	@mkdir -p tests/unit tests/integration
	@mkdir -p logs
	@echo "✓ Directories created"

install: ## Install Python dependencies
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	pip install -e .
	@echo "✓ Dependencies installed"

install-dev: ## Install development dependencies
	@echo "Installing development dependencies..."
	pip install -r requirements.txt
	pip install -e ".[dev]"
	@echo "✓ Development environment ready"

check-env: ## Check for required environment variables
	@echo "Checking environment..."
	@if [ ! -f .env ]; then \
		echo "⚠ Warning: .env file not found"; \
		echo "Create .env with:"; \
		echo "  OPENAI_API_KEY=your_key_here"; \
		echo "  ANTHROPIC_API_KEY=your_key_here"; \
	else \
		echo "✓ .env file exists"; \
	fi
	@which python > /dev/null || (echo "✗ Python not found" && exit 1)
	@which pip > /dev/null || (echo "✗ pip not found" && exit 1)
	@echo "✓ Environment check passed"

init-env: ## Create .env template file
	@if [ -f .env ]; then \
		echo "⚠ .env already exists, not overwriting"; \
	else \
		echo "# API Keys for LLM providers" > .env; \
		echo "OPENAI_API_KEY=your_openai_key_here" >> .env; \
		echo "ANTHROPIC_API_KEY=your_anthropic_key_here" >> .env; \
		echo "" >> .env; \
		echo "# Experiment Configuration" >> .env; \
		echo "TEMPERATURE=1.0" >> .env; \
		echo "N_SAMPLES=30" >> .env; \
		echo "✓ Created .env template - please edit with your API keys"; \
	fi

# ============================================================================
# Development
# ============================================================================

format: ## Format code with black
	@echo "Formatting code..."
	black src/ tests/
	@echo "✓ Code formatted"

format-check: ## Check code formatting without changes
	@echo "Checking code format..."
	black --check src/ tests/

lint: ## Run linting with flake8
	@echo "Running linter..."
	flake8 src/ tests/ --max-line-length=100 --extend-ignore=E203,W503
	@echo "✓ Linting passed"

type-check: ## Run type checking with mypy
	@echo "Running type checker..."
	mypy src/ --ignore-missing-imports
	@echo "✓ Type checking passed"

test: ## Run all tests
	@echo "Running tests..."
	@if [ -d tests ] && [ -n "$$(find tests -name 'test_*.py' -o -name '*_test.py')" ]; then \
		pytest tests/ -v; \
	else \
		echo "⚠ No tests found. Create tests in tests/ directory"; \
	fi

test-cov: ## Run tests with coverage report
	@echo "Running tests with coverage..."
	@if [ -d tests ] && [ -n "$$(find tests -name 'test_*.py' -o -name '*_test.py')" ]; then \
		pytest --cov=src tests/ --cov-report=html --cov-report=term; \
		echo "✓ Coverage report generated in htmlcov/index.html"; \
	else \
		echo "⚠ No tests found. Create tests in tests/ directory"; \
	fi

test-fast: ## Run tests without coverage (faster)
	@pytest tests/ -v --tb=short

# ============================================================================
# Research Workflow
# ============================================================================

notebook: ## Start Jupyter notebook server
	@echo "Starting Jupyter notebook..."
	jupyter notebook notebooks/

notebook-lab: ## Start JupyterLab server
	@echo "Starting JupyterLab..."
	jupyter lab notebooks/

analysis: ## Run main analysis notebook
	@echo "Running analysis..."
	jupyter nbconvert --to notebook --execute notebooks/01_entropy_analysis.ipynb
	@echo "✓ Analysis complete"

data-stats: ## Show statistics about collected data
	@echo "Data statistics:"
	@if [ -d data/raw ] && [ -n "$$(ls -A data/raw)" ]; then \
		echo "Raw data files: $$(find data/raw -type f | wc -l)"; \
		echo "Total size: $$(du -sh data/raw | cut -f1)"; \
	else \
		echo "⚠ No raw data found in data/raw/"; \
	fi
	@if [ -d data/processed ] && [ -n "$$(ls -A data/processed)" ]; then \
		echo "Processed data files: $$(find data/processed -type f | wc -l)"; \
		echo "Total size: $$(du -sh data/processed | cut -f1)"; \
	else \
		echo "⚠ No processed data found in data/processed/"; \
	fi

figures: ## Generate all figures
	@echo "Generating figures..."
	@echo "⚠ Not yet implemented - add figure generation script"
	@echo "Suggestion: Create scripts/generate_figures.py"

# ============================================================================
# Experimental Workflow (with Audit Logging)
# ============================================================================

EXPERIMENT ?= $(shell date +%Y%m%d_%H%M%S)
CONFIG ?= config/tasks.example.json
MODELS ?= gpt-4 claude-3.5-sonnet
PROMPT_TYPES ?= specification vague
N_SAMPLES ?= 30
TEMPERATURE ?= 1.0

collect-data: ## Collect LLM responses with full audit logging
	@echo "Starting data collection: $(EXPERIMENT)"
	@echo "Config: $(CONFIG)"
	@echo "Models: $(MODELS)"
	@python scripts/collect_data.py \
		--experiment $(EXPERIMENT) \
		--config $(CONFIG) \
		--models $(MODELS) \
		--prompt-types $(PROMPT_TYPES) \
		--n-samples $(N_SAMPLES) \
		--temperature $(TEMPERATURE)
	@echo ""
	@echo "✓ Data collection complete"
	@echo "Review audit log: logs/$(EXPERIMENT).jsonl"

collect-sample: ## Collect small sample (3 tasks, 5 samples) for testing
	@echo "Collecting test sample..."
	@python scripts/collect_data.py \
		--experiment $(EXPERIMENT)_sample \
		--config $(CONFIG) \
		--task-ids 0 1 2 \
		--models gpt-4 \
		--prompt-types specification \
		--n-samples 5 \
		--temperature $(TEMPERATURE)
	@echo "✓ Sample collection complete"

calculate-metrics: ## Calculate entropy and MI metrics with audit logging
	@echo "Calculating metrics: $(EXPERIMENT)_metrics"
	@python scripts/calculate_metrics.py \
		--experiment $(EXPERIMENT)_metrics \
		--input-dir data/raw \
		--output-dir data/processed
	@echo ""
	@echo "✓ Metrics calculation complete"
	@echo "Review audit log: logs/$(EXPERIMENT)_metrics.jsonl"
	@echo "Results: data/processed/metrics_summary.csv"

run-experiment: init-env ## Run complete experiment (collect + metrics)
	@echo "======================================"
	@echo "  Running Complete Experiment"
	@echo "======================================"
	@echo ""
	@echo "Experiment ID: $(EXPERIMENT)"
	@echo ""
	@$(MAKE) collect-data EXPERIMENT=$(EXPERIMENT)
	@echo ""
	@$(MAKE) calculate-metrics EXPERIMENT=$(EXPERIMENT)
	@echo ""
	@echo "======================================"
	@echo "✓ Experiment Complete!"
	@echo "======================================"
	@echo ""
	@echo "Audit logs:"
	@ls -lh logs/$(EXPERIMENT)*.jsonl 2>/dev/null || echo "  No logs found"
	@echo ""
	@echo "Results:"
	@ls -lh data/processed/*.csv 2>/dev/null || echo "  No results found"

view-logs: ## View recent audit logs
	@echo "Recent audit logs:"
	@echo ""
	@ls -lt logs/*.jsonl 2>/dev/null | head -10 || echo "No logs found"
	@echo ""
	@echo "Use: cat logs/<experiment>.jsonl | jq"
	@echo "Or:  cat logs/<experiment>_summary.json | jq"

# ============================================================================
# Documentation
# ============================================================================

paper: ## Compile LaTeX paper to PDF
	@echo "Compiling paper..."
	cd paper && pdflatex prompt_entropy_paper.tex
	cd paper && pdflatex prompt_entropy_paper.tex
	@echo "✓ Paper compiled to paper/prompt_entropy_paper.pdf"

paper-full: ## Compile paper with bibliography
	@echo "Compiling paper with bibliography..."
	cd paper && pdflatex prompt_entropy_paper.tex
	cd paper && bibtex prompt_entropy_paper || true
	cd paper && pdflatex prompt_entropy_paper.tex
	cd paper && pdflatex prompt_entropy_paper.tex
	@echo "✓ Paper compiled to paper/prompt_entropy_paper.pdf"

paper-clean: ## Clean LaTeX auxiliary files
	@echo "Cleaning LaTeX files..."
	cd paper && rm -f *.aux *.log *.out *.toc *.synctex.gz *.fdb_latexmk *.fls *.bbl *.blg
	@echo "✓ LaTeX files cleaned"

docs: ## Generate code documentation (if using sphinx)
	@echo "⚠ Documentation generation not yet configured"
	@echo "Suggestion: Set up Sphinx with 'sphinx-quickstart docs/'"

# ============================================================================
# Utilities
# ============================================================================

status: ## Show project status and structure
	@echo "======================================"
	@echo "  Project Status"
	@echo "======================================"
	@echo ""
	@echo "Git Branch: $$(git branch --show-current 2>/dev/null || echo 'Not in git repo')"
	@echo "Git Status: $$(git status --short | wc -l) changed files"
	@echo ""
	@echo "Directory Structure:"
	@tree -L 2 -I '__pycache__|*.pyc|.git|venv|htmlcov|.pytest_cache|.mypy_cache' || \
	 (echo "  src/" && ls -la src/ && echo "  notebooks/" && ls -la notebooks/)
	@echo ""
	@echo "Python Version: $$(python --version)"
	@echo "Installed Packages: $$(pip list | wc -l) packages"

clean: ## Clean generated files and caches
	@echo "Cleaning generated files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -name ".coverage" -delete 2>/dev/null || true
	@echo "✓ Cleaned Python cache files"

clean-all: clean paper-clean ## Clean all generated files including paper
	@echo "✓ Deep clean complete"

clean-data: ## Clean generated data (BE CAREFUL!)
	@echo "⚠ This will delete all data in data/processed/ and results/"
	@echo "Press Ctrl+C to cancel, or Enter to continue..."
	@read confirm
	rm -rf data/processed/*
	rm -rf results/*
	rm -rf figures/*
	@echo "✓ Data cleaned"
