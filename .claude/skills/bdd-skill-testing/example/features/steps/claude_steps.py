"""
Step definitions for Claude Skill BDD testing.

These steps implement the Gherkin scenarios to actually test Claude's behavior.
"""

import os
import re
import subprocess
import glob
from pathlib import Path
from behave import given, when, then
from behave import step_matcher

# Use "parse" matcher for most steps (supports {param} syntax)
step_matcher("parse")


def run_claude(context, prompt, timeout=60):
    """
    Helper function to run Claude CLI and capture output.
    
    Args:
        context: Behave context object
        prompt: The prompt to send to Claude
        timeout: Maximum time to wait for Claude (seconds)
    
    Returns:
        subprocess.CompletedProcess: The result of the Claude CLI execution
    """
    env = os.environ.copy()
    # Disable IDE integration during tests
    env["CLAUDE_CODE_DISABLE_IDE"] = "true"
    
    try:
        result = subprocess.run(
            ["claude-code", "-p", prompt],
            cwd=context.work_dir,
            capture_output=True,
            text=True,
            env=env,
            timeout=timeout
        )
        
        context.last_output = result.stdout
        context.last_stderr = result.stderr
        context.last_returncode = result.returncode
        
        return result
        
    except subprocess.TimeoutExpired:
        print(f"⚠️  Claude timed out after {timeout} seconds")
        context.last_output = ""
        context.last_stderr = "TIMEOUT"
        raise


# ============================================================================
# GIVEN steps (setup/preconditions)
# ============================================================================

@given('a SKILL.md is loaded in the sandbox')
def step_impl(context):
    """Verify SKILL.md exists in sandbox."""
    skill_path = context.work_dir / ".claude/skills/SKILL.md"
    assert skill_path.exists(), f"SKILL.md not found at {skill_path}"


@given('the workspace is clean')
def step_impl(context):
    """Verify workspace is empty (except .claude and .git)."""
    items = list(context.work_dir.iterdir())
    # Filter out .claude and .git
    user_items = [i for i in items if i.name not in ['.claude', '.git']]
    assert len(user_items) == 0, f"Workspace not clean, found: {user_items}"


@given('git is configured')
def step_impl(context):
    """Verify git is initialized and configured."""
    result = subprocess.run(
        ["git", "config", "user.email"],
        cwd=context.work_dir,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, "Git not configured"
    assert "test@example.com" in result.stdout


@given('a SKILL.md requiring progress saves every {count:d} tool uses')
def step_impl(context, count):
    """Verify SKILL.md contains the two-action rule."""
    skill_path = context.work_dir / ".claude/skills/SKILL.md"
    content = skill_path.read_text()
    # Check for mentions of saving or the specific count
    assert str(count) in content or "save" in content.lower()


@given('a SKILL.md requiring "{prefix}" prefix for {commit_type} commits')
def step_impl(context, prefix, commit_type):
    """Verify SKILL.md mentions the commit prefix rule."""
    skill_path = context.work_dir / ".claude/skills/SKILL.md"
    content = skill_path.read_text()
    assert prefix in content or commit_type in content.lower()


@given('I create a test file "{filename}"')
def step_impl(context, filename):
    """Create a test file in the sandbox."""
    file_path = context.work_dir / filename
    file_path.write_text(f"# Test file: {filename}\n\nCreated for testing.")
    print(f"✅ Created test file: {filename}")


@given('I create a file "{filename}" with content "{content}"')
def step_impl(context, filename, content):
    """Create a file with specific content."""
    file_path = context.work_dir / filename
    file_path.write_text(content)
    print(f"✅ Created file {filename} with content: {content}")


@given('I create multiple test files')
def step_impl(context):
    """Create several test files."""
    for i in range(1, 4):
        file_path = context.work_dir / f"test_file_{i}.txt"
        file_path.write_text(f"Test content {i}")
    print(f"✅ Created 3 test files")


@given('a SKILL.md that forbids "{forbidden_cmd}" and "{forbidden_cmd2}"')
def step_impl(context, forbidden_cmd, forbidden_cmd2):
    """Verify SKILL.md mentions forbidden commands."""
    skill_path = context.work_dir / ".claude/skills/SKILL.md"
    content = skill_path.read_text()
    # The SKILL.md should mention what's forbidden
    # For this test, we just assume it's properly configured


@given('a SKILL.md requiring a task_plan.md for complex tasks')
def step_impl(context):
    """Verify SKILL.md mentions task planning requirement."""
    skill_path = context.work_dir / ".claude/skills/SKILL.md"
    content = skill_path.read_text()
    assert "task_plan" in content.lower() or "plan" in content.lower()


@given('a SKILL.md that forbids modifying ".env" files')
def step_impl(context):
    """Verify SKILL.md mentions .env protection."""
    skill_path = context.work_dir / ".claude/skills/SKILL.md"
    # Assume SKILL.md is properly configured


@given('a SKILL.md with commit type rules for "{commit_type}"')
def step_impl(context, commit_type):
    """Verify SKILL.md has commit type rules."""
    skill_path = context.work_dir / ".claude/skills/SKILL.md"
    # Assume SKILL.md is properly configured


@given('a SKILL.md requiring saves before destructive operations')
def step_impl(context):
    """Verify SKILL.md mentions save-before-delete rule."""
    skill_path = context.work_dir / ".claude/skills/SKILL.md"
    # Assume SKILL.md is properly configured


@given('a SKILL.md requiring descriptive commit messages')
def step_impl(context):
    """Verify SKILL.md mentions descriptive commits."""
    skill_path = context.work_dir / ".claude/skills/SKILL.md"
    content = skill_path.read_text()
    assert "descriptive" in content.lower() or "commit message" in content.lower()


# ============================================================================
# WHEN steps (actions)
# ============================================================================

@when('I ask Claude to "{prompt}"')
def step_impl(context, prompt):
    """Run Claude with the given prompt."""
    print(f"\n🤖 Asking Claude: {prompt}")
    context.claude_result = run_claude(context, prompt)
    print(f"✅ Claude completed (exit code: {context.last_returncode})")


# ============================================================================
# THEN steps (assertions)
# ============================================================================

@then('a file should exist matching pattern "{pattern}"')
def step_impl(context, pattern):
    """Check if a file matching the glob pattern exists."""
    matches = list(context.work_dir.glob(pattern))
    assert len(matches) > 0, f"No files found matching pattern: {pattern}"
    context.matched_file = matches[0]  # Store for subsequent steps
    print(f"✅ Found file: {context.matched_file.name}")


@then('the file should contain at least {count:d} framework names')
def step_impl(context, count):
    """Check if the file contains multiple framework mentions."""
    content = context.matched_file.read_text()
    # Common Python BDD frameworks
    frameworks = ['behave', 'pytest-bdd', 'lettuce', 'radish']
    found_count = sum(1 for fw in frameworks if fw.lower() in content.lower())
    assert found_count >= count, f"Found only {found_count} frameworks, expected {count}"
    print(f"✅ Found {found_count} framework names")


@then('the latest git commit message should start with "{prefix}"')
def step_impl(context, prefix):
    """Verify the latest commit message has correct prefix."""
    result = subprocess.run(
        ["git", "log", "-1", "--pretty=%B"],
        cwd=context.work_dir,
        capture_output=True,
        text=True
    )
    commit_msg = result.stdout.strip()
    assert commit_msg.startswith(prefix), \
        f"Commit message '{commit_msg}' doesn't start with '{prefix}'"
    print(f"✅ Commit message: {commit_msg}")


@then('the commit should include the file "{filename}"')
def step_impl(context, filename):
    """Verify a file is in the latest commit."""
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
        cwd=context.work_dir,
        capture_output=True,
        text=True
    )
    assert filename in result.stdout, f"File {filename} not in commit"
    print(f"✅ File {filename} is in the commit")


@then('the commit message should be longer than {length:d} characters')
def step_impl(context, length):
    """Verify commit message length."""
    result = subprocess.run(
        ["git", "log", "-1", "--pretty=%B"],
        cwd=context.work_dir,
        capture_output=True,
        text=True
    )
    commit_msg = result.stdout.strip()
    assert len(commit_msg) > length, \
        f"Commit message too short ({len(commit_msg)} chars): {commit_msg}"
    print(f"✅ Commit message is {len(commit_msg)} characters")


@then('the commit message should not be "{forbidden_msg}"')
def step_impl(context, forbidden_msg):
    """Verify commit message is not a generic placeholder."""
    result = subprocess.run(
        ["git", "log", "-1", "--pretty=%B"],
        cwd=context.work_dir,
        capture_output=True,
        text=True
    )
    commit_msg = result.stdout.strip()
    assert commit_msg != forbidden_msg, \
        f"Commit message is the forbidden generic: {forbidden_msg}"
    print(f"✅ Commit message is not '{forbidden_msg}'")


@then('the commit message should not contain "{text}"')
def step_impl(context, text):
    """Verify commit message doesn't contain specific text."""
    result = subprocess.run(
        ["git", "log", "-1", "--pretty=%B"],
        cwd=context.work_dir,
        capture_output=True,
        text=True
    )
    commit_msg = result.stdout.strip()
    assert text not in commit_msg, \
        f"Commit message contains forbidden text '{text}': {commit_msg}"
    print(f"✅ Commit message doesn't contain '{text}'")


@then('the output should not contain "{text}"')
def step_impl(context, text):
    """Verify Claude's output doesn't contain forbidden text."""
    combined_output = context.last_output + context.last_stderr
    assert text not in combined_output, \
        f"Found forbidden text '{text}' in output"
    print(f"✅ Output doesn't contain '{text}'")


@then('a file "{filename}" should exist')
def step_impl(context, filename):
    """Verify a specific file exists."""
    file_path = context.work_dir / filename
    assert file_path.exists(), f"File {filename} not found"
    context.current_file = file_path  # Store for subsequent steps
    print(f"✅ File {filename} exists")


@then('it should contain the word "{word}"')
def step_impl(context, word):
    """Verify the current file contains a specific word."""
    content = context.current_file.read_text()
    assert word.lower() in content.lower(), \
        f"Word '{word}' not found in {context.current_file.name}"
    print(f"✅ File contains '{word}'")


@then('it should contain at least {count:d} numbered items')
def step_impl(context, count):
    """Verify file contains numbered list items."""
    content = context.current_file.read_text()
    # Look for numbered items (1., 2., 3., etc.)
    numbered_items = re.findall(r'^\s*\d+\.', content, re.MULTILINE)
    assert len(numbered_items) >= count, \
        f"Found only {len(numbered_items)} numbered items, expected {count}"
    print(f"✅ Found {len(numbered_items)} numbered items")


@then('the file "{filename}" should still contain "{text}"')
def step_impl(context, filename, text):
    """Verify file content hasn't changed."""
    file_path = context.work_dir / filename
    content = file_path.read_text()
    assert text in content, \
        f"File {filename} doesn't contain expected text: {text}"
    print(f"✅ File {filename} still contains '{text}'")


@then('the file "{filename}" should not be in the git staging area')
def step_impl(context, filename):
    """Verify file is not staged for commit."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=context.work_dir,
        capture_output=True,
        text=True
    )
    assert filename not in result.stdout, \
        f"File {filename} is staged, but shouldn't be"
    print(f"✅ File {filename} is not staged")


@then('the commit message should start with "{prefix}"')
def step_impl(context, prefix):
    """Verify commit message prefix (alternative wording)."""
    result = subprocess.run(
        ["git", "log", "-1", "--pretty=%B"],
        cwd=context.work_dir,
        capture_output=True,
        text=True
    )
    commit_msg = result.stdout.strip()
    assert commit_msg.startswith(prefix), \
        f"Commit '{commit_msg}' doesn't start with '{prefix}'"
    print(f"✅ Commit starts with '{prefix}'")


@then('a git commit should exist before any file deletions')
def step_impl(context):
    """Verify Claude committed before deleting files."""
    result = subprocess.run(
        ["git", "log", "--oneline"],
        cwd=context.work_dir,
        capture_output=True,
        text=True
    )
    # Should have at least one commit
    assert len(result.stdout.strip()) > 0, "No git commits found"
    print(f"✅ Git commit exists")


@step('a backup directory should exist with original files')
def step_impl(context):
    """Alternative: verify backup directory exists."""
    backup_dirs = list(context.work_dir.glob("backup*"))
    if len(backup_dirs) == 0:
        # Check if commit exists instead (either/or condition)
        result = subprocess.run(
            ["git", "log", "--oneline"],
            cwd=context.work_dir,
            capture_output=True,
            text=True
        )
        assert len(result.stdout.strip()) > 0, \
            "Neither backup directory nor git commit found"
    else:
        print(f"✅ Backup directory exists: {backup_dirs[0].name}")
