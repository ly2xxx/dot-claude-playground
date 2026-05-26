# Invoice Tracker BDD Test Suite

This directory contains a Proof of Concept (POC) Behavior-Driven Development (BDD) test suite for the `invoice-tracker` skill. It is designed to evaluate how well an LLM follows the instructions in `SKILL.md` to extract data from invoice PDFs into structured CSV format.

## File Structure & Purpose

The test suite is built using `pytest-bdd` and `deepeval`, dividing the test logic into three distinct components:

### 1. `features/invoice_extraction.feature`
**Purpose:** Defines the expected behavior of the LLM in plain English using Gherkin syntax.
**How it works:** It contains Scenarios with `Given`, `When`, and `Then` steps. It acts as both executable documentation and the specification for what the LLM should achieve (e.g., extracting the correct invoice total). It also uses `Scenario Outline` to allow running the same test across multiple LLM models.

### 2. `step_defs/test_invoice_extraction.py`
**Purpose:** The Python code that implements the steps defined in the `.feature` file.
**How it works:** It uses `@given`, `@when`, and `@then` decorators to map the plain English lines from the feature file to Python functions. 
- The `Given` steps load the `SKILL.md` instructions.
- The `When` steps simulate sending the invoice and instructions to the LLM (currently mocked for the POC).
- The `Then` steps use standard assertions and the `deepeval` framework (specifically the `GEval` metric) to score whether the actual output correctly followed the instructions.

### 3. `conftest.py`
**Purpose:** Provides shared test fixtures for the test suite.
**How it works:** Because `pytest-bdd` steps are separate Python functions, they cannot easily share local variables. `conftest.py` provides a `scenario_ctx` fixture—a mutable dictionary injected into every step—allowing the `Given` steps to store context (like the loaded prompt) that the `When` and `Then` steps can read and validate later.

## How They Work Together
When you run `pytest`, it discovers `test_invoice_extraction.py`. That file explicitly binds to `invoice_extraction.feature`. Pytest reads the feature file line by line, looks up the corresponding decorated Python function in the step definitions, injects the `scenario_ctx` from `conftest.py`, and executes the test flow sequentially.

---

## How to Run the Tests

### 1. Environment Setup
You should run these tests inside an isolated Python virtual environment. Open a terminal (PowerShell) and navigate to the `invoice-tracker` directory:

```powershell
# Navigate to the skill directory
cd path\to\invoice-tracker

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment (Windows)
.venv\Scripts\activate

# Install the required testing dependencies
pip install pytest pytest-bdd deepeval
```

### 2. Running the Test Suite
With the virtual environment activated, you can run the test suite using `pytest`:

```powershell
# Run all tests in the tests directory
pytest tests/

# Or run with verbose output to see each step
pytest tests/ -v
```

### 3. DeepEval Configuration Note
The test uses DeepEval's `GEval` metric in the final `Then` step to evaluate the LLM's adherence to instructions. `GEval` uses an "LLM as a judge" mechanism.
By default, DeepEval uses OpenAI models for this evaluation. To see the evaluation succeed, you need to set an OpenAI API key before running the test:

```powershell
$env:OPENAI_API_KEY="your-api-key-here"
pytest tests/ -v
```
*(Note: If the API key is missing, the POC is currently designed to catch the error and print a warning without failing the entire test suite.)*
