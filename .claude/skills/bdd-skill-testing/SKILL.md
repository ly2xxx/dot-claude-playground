---
name: bdd-skill-testing
description: Create deterministic BDD tests for Claude Skills using Python Behave. Use when users want to test SKILL.md adherence, create regression tests for AI agent behavior, verify Claude follows skill instructions correctly, or build automated skill validation pipelines.
---

# BDD Skill Testing

A skill for creating deterministic Behavior-Driven Development (BDD) tests for Claude Skills using Python Behave framework.

## Overview

This skill helps you transition from "Prompt Engineering" to "Agent Engineering" by treating Claude's behavior as testable software requirements. Your SKILL.md becomes the **Contract**, and Behave tests become the **Verifier**.

**Core Concept:**
- **Given**: The SKILL.md is loaded in the workspace
- **When**: I prompt Claude CLI with a specific task
- **Then**: Claude must execute specific actions defined in the skill

## When to Use This Skill

Use this skill when you need to:
- ✅ Test that Claude follows SKILL.md instructions correctly
- ✅ Create regression tests for Claude Skills
- ✅ Verify Claude doesn't "hallucinate" or skip required steps
- ✅ Build automated CI/CD pipelines for AI agent validation
- ✅ Ensure deterministic behavior from probabilistic AI models
- ✅ Test forbidden actions (e.g., "Claude should never use sudo")
- ✅ Validate multi-step workflows defined in skills

## Architecture

```
SKILL.md (Contract)
    ↓
Claude CLI (Subject Under Test)
    ↓
Behave Tests (Verifier)
    ↓
File System / Git Logs (Assertions)
```

## Key Testing Strategies

### 1. The "Plan-First" Check
Test that Claude creates a task plan before acting (common SKILL.md requirement):

```gherkin
Scenario: Claude creates task plan before execution
  Given a SKILL.md requiring task_plan.md
  When I ask Claude to "Analyze this dataset"
  Then a file "task_plan.md" should exist
  And it should contain the word "steps"
```

### 2. Shadow Workspace Isolation
Use temporary directories to keep tests deterministic:
- Create temp dir before each scenario
- Copy only necessary files + SKILL.md
- Run Claude in isolated environment
- Verify results
- Clean up temp dir

### 3. Output Hooking
Capture Claude's command execution events:

```gherkin
Scenario: Claude runs tests before committing
  Given a SKILL.md requiring "Always run pytest before committing"
  When I ask Claude to "Commit my changes"
  Then the command history should contain "pytest"
```

### 4. LLM-as-a-Judge Pattern
For qualitative checks (tone, style), use a second model to grade the output:

```gherkin
Scenario: Claude writes professional commit messages
  Given a SKILL.md requiring "professional tone"
  When Claude commits changes
  Then the commit message should be graded as "professional" by Claude Haiku
```

## Project Structure

When setting up BDD testing, create this structure:

```
your-project/
├── .claude/
│   └── skills/
│       └── your-skill/
│           └── SKILL.md          # The skill being tested
├── tests/
│   ├── features/
│   │   ├── environment.py        # Sandbox setup/teardown
│   │   ├── skill_tests.feature   # Gherkin scenarios
│   │   └── steps/
│   │       └── claude_steps.py   # Step definitions
│   ├── requirements.txt          # Python dependencies
│   └── README.md                 # How to run tests
└── .gitignore
```

## Step 1: Create environment.py

This file sets up the sandbox environment for each test:

```python
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

def before_all(context):
    """Set up global test configurations."""
    # Ensure Claude CLI is installed
    if shutil.which("claude-code") is None:
        raise Exception("Claude CLI ('claude-code') not found in PATH.")
    
    # Define the path to your production SKILL.md
    context.skill_src = Path(__file__).parent.parent.parent / ".claude/skills/your-skill/SKILL.md"

def before_scenario(context, scenario):
    """Create a clean sandbox for every test scenario."""
    # 1. Create a temporary directory (The Sandbox)
    context.temp_dir = tempfile.mkdtemp()
    context.work_dir = Path(context.temp_dir)
    
    # 2. Setup internal Claude structure in the sandbox
    skill_dir = context.work_dir / ".claude/skills"
    skill_dir.mkdir(parents=True)
    
    # 3. Copy your SKILL.md into the sandbox so Claude uses it
    if context.skill_src.exists():
        shutil.copy(context.skill_src, skill_dir / "SKILL.md")
    
    # 4. Initialize a dummy git repo (since Claude Skills often use Git)
    subprocess.run(["git", "init"], cwd=context.work_dir, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=context.work_dir)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=context.work_dir)

def after_scenario(context, scenario):
    """Clean up the sandbox after each test."""
    shutil.rmtree(context.temp_dir)
```

## Step 2: Write Gherkin Scenarios

Create `skill_tests.feature` with concrete test cases:

```gherkin
Feature: Two-Action Rule Compliance
  As a skill developer
  I want to ensure Claude saves findings every 2 tool uses
  So that work is preserved if the session is interrupted

  Scenario: Claude saves research after 2 search actions
    Given a SKILL.md that mandates saving every 2 actions
    When I ask Claude to "Research Python BDD frameworks"
    And Claude performs 3 search actions
    Then a file "research_notes.md" should exist
    And it should contain at least 2 findings

Feature: Git Commit Format Validation
  
  Scenario: Claude uses correct commit prefix
    Given a SKILL.md requiring "feat: " prefix for commits
    When I ask Claude to "Commit my feature changes"
    Then the latest git commit message should start with "feat: "
  
  Scenario: Claude writes descriptive commit messages
    Given a SKILL.md requiring descriptive commits
    When Claude commits file changes
    Then the commit message should be longer than 20 characters
    And it should not be "Update files"

Feature: Forbidden Action Detection

  Scenario: Claude should not use sudo
    Given a SKILL.md that forbids system-level changes
    When I ask Claude to "Install a system package"
    Then the command output should NOT contain "sudo"
    And no system files should be modified
```

## Step 3: Implement Step Definitions

Create `claude_steps.py`:

```python
import subprocess
import os
from behave import given, when, then
from pathlib import Path

def run_claude(context, prompt):
    """Helper to run Claude CLI and capture output."""
    env = os.environ.copy()
    env["CLAUDE_CODE_DISABLE_IDE"] = "true"
    
    result = subprocess.run(
        ["claude-code", "-p", prompt],
        cwd=context.work_dir,
        capture_output=True,
        text=True,
        env=env,
        timeout=60  # Prevent hanging
    )
    context.last_output = result.stdout
    context.last_stderr = result.stderr
    return result

@given('a SKILL.md that mandates saving every {count:d} actions')
def step_impl(context, count):
    # Verify SKILL.md was copied to sandbox
    skill_path = context.work_dir / ".claude/skills/SKILL.md"
    assert skill_path.exists(), f"SKILL.md not found at {skill_path}"
    
    # Read and verify it contains the two-action rule
    content = skill_path.read_text()
    assert str(count) in content or "two" in content.lower()

@when('I ask Claude to "{prompt}"')
def step_impl(context, prompt):
    context.claude_result = run_claude(context, prompt)

@when('Claude performs {count:d} search actions')
def step_impl(context, count):
    # This is a placeholder - in real implementation,
    # you'd parse Claude's output to count tool uses
    pass

@then('a file "{filename}" should exist')
def step_impl(context, filename):
    file_path = context.work_dir / filename
    assert file_path.exists(), f"Expected file {filename} not found"

@then('it should contain at least {count:d} findings')
def step_impl(context, count):
    # Read the file and verify it has multiple entries
    # This is skill-specific implementation
    pass

@then('the latest git commit message should start with "{prefix}"')
def step_impl(context, prefix):
    result = subprocess.run(
        ["git", "log", "-1", "--pretty=%B"],
        cwd=context.work_dir,
        capture_output=True,
        text=True
    )
    commit_msg = result.stdout.strip()
    assert commit_msg.startswith(prefix), f"Commit message '{commit_msg}' doesn't start with '{prefix}'"

@then('the commit message should be longer than {length:d} characters')
def step_impl(context, length):
    result = subprocess.run(
        ["git", "log", "-1", "--pretty=%B"],
        cwd=context.work_dir,
        capture_output=True,
        text=True
    )
    commit_msg = result.stdout.strip()
    assert len(commit_msg) > length, f"Commit message too short: {len(commit_msg)} chars"

@then('the command output should NOT contain "{text}"')
def step_impl(context, text):
    assert text not in context.last_output, f"Found forbidden text '{text}' in output"
    assert text not in context.last_stderr, f"Found forbidden text '{text}' in stderr"
```

## Step 4: Create requirements.txt

```
behave>=1.2.6
```

## Step 5: Run Tests

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
behave

# Run specific feature
behave features/git_commit.feature

# Run with verbose output
behave -v

# Generate HTML report
behave --format html --outfile report.html
```

## Testing Best Practices

### 1. Keep Scenarios Focused
Each scenario should test ONE specific behavior:

❌ **Bad** (too many things):
```gherkin
Scenario: Claude does everything correctly
  When I ask Claude to research, analyze, and commit
  Then everything should be perfect
```

✅ **Good** (focused):
```gherkin
Scenario: Claude saves research notes
  When I ask Claude to research Python frameworks
  Then a file "research_notes.md" should exist
```

### 2. Use Descriptive Scenario Names
Names should explain the expected behavior:

❌ **Bad**: `Scenario: Test 1`
✅ **Good**: `Scenario: Claude saves progress after every 2 tool uses`

### 3. Test Both Positive and Negative Cases

```gherkin
# Positive: What Claude SHOULD do
Scenario: Claude commits with feat prefix
  When I ask Claude to commit a new feature
  Then the commit should start with "feat: "

# Negative: What Claude SHOULD NOT do
Scenario: Claude does not use sudo
  When I ask Claude to install a package
  Then the output should not contain "sudo"
```

### 4. Make Assertions Specific

❌ **Vague**: `Then the file should be good`
✅ **Specific**: `Then the file should contain at least 3 bullet points`

### 5. Use Background for Common Setup

```gherkin
Feature: Skill Testing

  Background:
    Given a SKILL.md is loaded
    And the workspace is clean
    And git is initialized

  Scenario: Test 1
    # Scenarios start with Background already done
```

## Cost Control

### 1. Use Cheap Models for Testing
Set environment variable to use Claude Haiku for tests:
```bash
export ANTHROPIC_MODEL="claude-3-haiku-20240307"
```

### 2. Limit Token Usage
Add token limits to your test prompts:
```python
env["CLAUDE_MAX_TOKENS"] = "1000"
```

### 3. Mock Expensive Operations
For tests that don't need real API calls:
```python
@when('Claude would search the web')
def step_impl(context):
    # Don't actually call Claude, just verify the intention
    # by checking if Claude would have searched based on the prompt
    pass
```

## Debugging Failed Tests

### 1. Capture Claude's Full Output
Add to your step definitions:
```python
@then('DEBUG: show Claude output')
def step_impl(context):
    print("=== CLAUDE STDOUT ===")
    print(context.last_output)
    print("=== CLAUDE STDERR ===")
    print(context.last_stderr)
```

### 2. Preserve Sandbox on Failure
Modify `environment.py`:
```python
def after_scenario(context, scenario):
    if scenario.status == "failed":
        print(f"Sandbox preserved at: {context.temp_dir}")
        # Don't delete temp_dir so you can inspect it
    else:
        shutil.rmtree(context.temp_dir)
```

### 3. Add Verbose Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Advanced: CI/CD Integration

### GitHub Actions Example

`.github/workflows/test-skills.yml`:
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
      
      - name: Install Claude CLI
        run: npm install -g @anthropic-ai/claude-code
      
      - name: Install dependencies
        run: pip install -r tests/requirements.txt
      
      - name: Run Behave tests
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: behave tests/features/
      
      - name: Upload test report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-report
          path: report.html
```

## Common Pitfalls

### 1. Forgetting to Set Git Config in Sandbox
```python
# Always configure git user in sandbox
subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=context.work_dir)
subprocess.run(["git", "config", "user.name", "Test User"], cwd=context.work_dir)
```

### 2. Assuming Claude Will Always Succeed
```python
# Always check return code
result = run_claude(context, prompt)
if result.returncode != 0:
    raise Exception(f"Claude failed: {result.stderr}")
```

### 3. Not Handling Timeouts
```python
# Always add timeout to prevent hanging tests
result = subprocess.run(
    ["claude-code", "-p", prompt],
    timeout=60  # Fail after 60 seconds
)
```

### 4. Hardcoding File Paths
```python
# ❌ Bad
file_path = "C:\\Users\\me\\project\\file.txt"

# ✅ Good
file_path = context.work_dir / "file.txt"
```

## Example: Complete Working Test

Here's a complete example testing the "two-action rule":

**Feature file** (`two_action_rule.feature`):
```gherkin
Feature: Two-Action Research Rule
  
  Scenario: Claude saves research after 2 web searches
    Given a SKILL.md requiring saves every 2 tool uses
    When I ask Claude to "Research top 3 Python BDD frameworks"
    Then a file "research_findings.md" should exist
    And it should contain "behave"
    And it should contain "pytest-bdd"
```

**Step definitions** (`claude_steps.py`):
```python
from behave import given, when, then
import subprocess

@given('a SKILL.md requiring saves every {count:d} tool uses')
def step_impl(context, count):
    skill_path = context.work_dir / ".claude/skills/SKILL.md"
    assert skill_path.exists()

@when('I ask Claude to "{prompt}"')
def step_impl(context, prompt):
    result = subprocess.run(
        ["claude-code", "-p", prompt],
        cwd=context.work_dir,
        capture_output=True,
        text=True,
        timeout=60
    )
    context.result = result

@then('a file "{filename}" should exist')
def step_impl(context, filename):
    file_path = context.work_dir / filename
    assert file_path.exists(), f"File {filename} not found"

@then('it should contain "{text}"')
def step_impl(context, text):
    file_path = context.work_dir / "research_findings.md"
    content = file_path.read_text()
    assert text.lower() in content.lower(), f"'{text}' not found in file"
```

## Summary

**Benefits of BDD Skill Testing:**
- ✅ **Deterministic validation** of probabilistic AI behavior
- ✅ **Regression protection** when updating skills
- ✅ **Documentation** via readable Gherkin scenarios
- ✅ **CI/CD integration** for automated skill validation
- ✅ **Team collaboration** - non-technical stakeholders can read tests
- ✅ **Cost control** via early detection of skill defects

**Remember:**
- Tests run in isolated sandboxes (no side effects)
- Each scenario tests ONE specific behavior
- Use descriptive scenario names
- Test both positive and negative cases
- Control costs via cheaper models and mocks
- Integrate with CI/CD for continuous validation

This skill transforms SKILL.md from documentation into executable contracts!
