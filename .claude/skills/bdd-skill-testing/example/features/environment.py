"""
Behave environment setup for Claude Skill testing.

This module handles sandbox creation/cleanup for each test scenario.
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path


def before_all(context):
    """
    Set up global test configurations.
    Runs once before all scenarios.
    """
    # Ensure Claude CLI is installed
    if shutil.which("claude-code") is None:
        raise Exception(
            "Claude CLI ('claude-code') not found in PATH.\n"
            "Install with: npm install -g @anthropic-ai/claude-code"
        )
    
    # Define the path to your production SKILL.md
    # Adjust this path to point to the skill you want to test
    context.skill_src = Path(__file__).parent.parent.parent / "your-skill/SKILL.md"
    
    # Store test results for reporting
    context.test_results = []


def before_scenario(context, scenario):
    """
    Create a clean sandbox for every test scenario.
    This ensures tests don't interfere with each other.
    """
    # 1. Create a temporary directory (The Sandbox)
    context.temp_dir = tempfile.mkdtemp(prefix="claude_test_")
    context.work_dir = Path(context.temp_dir)
    
    print(f"\n📁 Sandbox created: {context.work_dir}")
    
    # 2. Setup internal Claude structure in the sandbox
    skill_dir = context.work_dir / ".claude/skills"
    skill_dir.mkdir(parents=True)
    
    # 3. Copy your SKILL.md into the sandbox so Claude uses it
    if context.skill_src.exists():
        shutil.copy(context.skill_src, skill_dir / "SKILL.md")
        print(f"✅ Copied SKILL.md to sandbox")
    else:
        print(f"⚠️  Warning: SKILL.md not found at {context.skill_src}")
    
    # 4. Initialize a dummy git repo (since Claude Skills often use Git)
    subprocess.run(
        ["git", "init"],
        cwd=context.work_dir,
        capture_output=True,
        check=True
    )
    
    # Configure git user (required for commits)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=context.work_dir,
        capture_output=True,
        check=True
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=context.work_dir,
        capture_output=True,
        check=True
    )
    
    print(f"✅ Git initialized in sandbox")
    
    # Initialize context variables
    context.last_output = ""
    context.last_stderr = ""
    context.claude_result = None


def after_scenario(context, scenario):
    """
    Clean up the sandbox after each test.
    Preserves sandbox on failure for debugging.
    """
    if scenario.status == "failed":
        print(f"\n❌ Test failed! Sandbox preserved at: {context.temp_dir}")
        print(f"   Inspect files with: cd {context.temp_dir}")
        # Don't delete so you can debug
    else:
        # Clean up temp directory on success
        shutil.rmtree(context.temp_dir)
        print(f"\n✅ Sandbox cleaned up")


def after_all(context):
    """
    Runs once after all scenarios.
    Could be used for generating summary reports.
    """
    print("\n" + "="*60)
    print("📊 Test Summary:")
    print(f"   Total scenarios: {len(context.test_results)}")
    print("="*60)
