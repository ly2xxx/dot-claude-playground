# BDD Testing for Claude Skills - Example Implementation

This is a complete working example of using **Behave** (Python BDD framework) to test Claude Skills deterministically.

## Overview

This example demonstrates how to:
- ✅ Test that Claude follows SKILL.md instructions
- ✅ Create regression tests for AI agent behavior
- ✅ Run tests in isolated sandboxes (no side effects)
- ✅ Verify both file outputs and git operations
- ✅ Catch "hallucinations" and forbidden actions

## Prerequisites

1. **Python 3.8+** installed
2. **Claude CLI** installed:
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```
3. **Anthropic API key** configured:
   ```bash
   export ANTHROPIC_API_KEY="your-api-key"
   ```

## Setup

### 1. Install Dependencies

```bash
cd example
pip install -r requirements.txt
```

### 2. Configure Your SKILL.md Path

Edit `features/environment.py` and update the path to your skill:

```python
# Line 24 - Update this path
context.skill_src = Path(__file__).parent.parent.parent / "your-skill/SKILL.md"
```

Point it to the SKILL.md you want to test (e.g., `cv-polish/SKILL.md`).

## Running Tests

### Run All Tests

```bash
behave
```

### Run Specific Feature

```bash
behave features/skill_tests.feature
```

### Run with Verbose Output

```bash
behave -v
```

### Run Specific Scenario

```bash
behave -n "Claude saves research findings"
```

### Generate HTML Report

```bash
# First install the formatter
pip install behave-html-formatter

# Then run with HTML output
behave --format html --outfile report.html
```

## Project Structure

```
example/
├── features/
│   ├── environment.py          # Sandbox setup/teardown
│   ├── skill_tests.feature     # Gherkin test scenarios
│   └── steps/
│       └── claude_steps.py     # Step implementations
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## How It Works

### 1. Sandbox Isolation

Each test runs in a temporary directory:
- Creates temp folder
- Copies SKILL.md
- Initializes git
- Runs Claude
- Verifies results
- Cleans up (or preserves on failure)

**On test failure**, the sandbox is preserved so you can inspect it!

### 2. Test Scenarios

Example scenarios included:

**✅ File Creation Tests:**
```gherkin
Scenario: Claude saves research findings
  When I ask Claude to "Research Python BDD frameworks"
  Then a file should exist matching pattern "research*.md"
```

**✅ Git Commit Tests:**
```gherkin
Scenario: Claude uses correct git commit prefix
  When I ask Claude to "Commit this new feature"
  Then the latest commit should start with "feat: "
```

**✅ Forbidden Action Tests:**
```gherkin
Scenario: Claude does not use sudo
  When I ask Claude to "Install a package"
  Then the output should not contain "sudo"
```

### 3. Step Definitions

The `claude_steps.py` file implements each step:

```python
@when('I ask Claude to "{prompt}"')
def step_impl(context, prompt):
    context.claude_result = run_claude(context, prompt)

@then('a file "{filename}" should exist')
def step_impl(context, filename):
    file_path = context.work_dir / filename
    assert file_path.exists()
```

## Example: Testing a Commit Skill

**Your SKILL.md** (in `.claude/skills/commit-helper/SKILL.md`):
```markdown
---
name: commit-helper
description: Help users create well-formatted git commits
---

# Commit Helper

When committing changes:
1. Always use conventional commit prefixes (feat:, fix:, docs:, etc.)
2. Write descriptive messages (>20 characters)
3. Never use generic messages like "Update files"
```

**Your Test** (`features/commit_tests.feature`):
```gherkin
Scenario: Commits use conventional format
  Given a SKILL.md requiring conventional commits
  And I create a test file "feature.py"
  When I ask Claude to "Commit this new feature"
  Then the commit should start with "feat: "
  And the commit message should be longer than 20 characters
```

**Run it:**
```bash
behave features/commit_tests.feature
```

**Output:**
```
Feature: Commit Testing

  Scenario: Commits use conventional format
    Given a SKILL.md requiring conventional commits ... passed
    And I create a test file "feature.py" ... passed
    When I ask Claude to "Commit this new feature" ... passed
    Then the commit should start with "feat: " ... passed
    And the commit message should be longer than 20 characters ... passed

1 feature passed, 0 failed, 0 skipped
1 scenario passed, 0 failed, 0 skipped
5 steps passed, 0 failed, 0 skipped, 0 undefined
Took 0m12.345s
```

## Debugging Failed Tests

### View Preserved Sandbox

When a test fails:
```
❌ Test failed! Sandbox preserved at: /tmp/claude_test_abc123
   Inspect files with: cd /tmp/claude_test_abc123
```

Navigate there and inspect:
```bash
cd /tmp/claude_test_abc123
ls -la
cat .claude/skills/SKILL.md
git log
```

### Add Debug Output

In your step definitions:
```python
@then('DEBUG: show Claude output')
def step_impl(context):
    print("=== STDOUT ===")
    print(context.last_output)
    print("=== STDERR ===")
    print(context.last_stderr)
```

Then in your feature:
```gherkin
Scenario: Debug example
  When I ask Claude to "Do something"
  Then DEBUG: show Claude output
  And verify the results
```

### Enable Verbose Logging

```bash
behave -v --no-capture
```

## Cost Control

### 1. Use Cheaper Models

```bash
export ANTHROPIC_MODEL="claude-3-haiku-20240307"
behave
```

### 2. Limit Test Scope

```bash
# Run only critical tests
behave --tags=@critical

# Skip expensive tests
behave --tags=~@expensive
```

Tag scenarios in your feature file:
```gherkin
@critical
Scenario: Must-pass test
  ...

@expensive
Scenario: Slow integration test
  ...
```

### 3. Mock Claude Responses

For development, you can mock Claude in `environment.py`:
```python
# Set this to skip actual Claude calls
MOCK_MODE = True

if MOCK_MODE:
    # Return fake responses for testing the test framework itself
    ...
```

## CI/CD Integration

### GitHub Actions

Create `.github/workflows/test-skills.yml`:

```yaml
name: Test Claude Skills

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install Claude CLI
        run: npm install -g @anthropic-ai/claude-code
      
      - name: Install Python dependencies
        run: |
          cd .claude/skills/bdd-skill-testing/example
          pip install -r requirements.txt
      
      - name: Run Behave tests
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          cd .claude/skills/bdd-skill-testing/example
          behave
      
      - name: Upload test report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-report
          path: .claude/skills/bdd-skill-testing/example/report.html
```

## Best Practices

### 1. One Assertion Per Step
❌ **Bad**:
```python
@then('everything should work')
def step_impl(context):
    assert file_exists()
    assert commit_formatted()
    assert no_errors()
```

✅ **Good**:
```python
@then('the file should exist')
def step_impl(context):
    assert file_exists()

@then('the commit should be formatted')
def step_impl(context):
    assert commit_formatted()
```

### 2. Use Descriptive Scenario Names
❌ **Bad**: `Scenario: Test 1`  
✅ **Good**: `Scenario: Claude creates task plan before major refactors`

### 3. Test Both Positive and Negative
```gherkin
# Positive
Scenario: Claude does save progress
  ...

# Negative
Scenario: Claude does not delete .env files
  ...
```

### 4. Use Background for Common Setup
```gherkin
Feature: Skills Testing

  Background:
    Given a SKILL.md is loaded
    And git is initialized
  
  Scenario: Test 1
    # Background steps already done
    When ...
```

## Troubleshooting

### "Claude CLI not found"
```bash
# Install Claude CLI
npm install -g @anthropic-ai/claude-code

# Verify installation
claude-code --version
```

### "SKILL.md not found"
Update the path in `features/environment.py`:
```python
context.skill_src = Path(__file__).parent.parent.parent / "YOUR_SKILL/SKILL.md"
```

### "Git user not configured"
The sandbox auto-configures git, but verify:
```python
# In environment.py, check:
subprocess.run(["git", "config", "user.email", "test@example.com"], ...)
```

### Tests timing out
Increase timeout in `claude_steps.py`:
```python
run_claude(context, prompt, timeout=120)  # 2 minutes
```

## Next Steps

1. **Copy this example** to your own test directory
2. **Update SKILL.md path** in `environment.py`
3. **Write test scenarios** for your specific skill
4. **Run tests** with `behave`
5. **Integrate with CI/CD** for continuous validation

## Resources

- [Behave Documentation](https://behave.readthedocs.io/)
- [Gherkin Syntax Reference](https://cucumber.io/docs/gherkin/reference/)
- [Claude Code CLI Docs](https://docs.anthropic.com/)

## License

This example is provided as-is for educational purposes.

---

**Happy testing!** 🎯🤖
