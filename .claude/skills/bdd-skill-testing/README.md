# BDD Skill Testing - Claude Skill

Test your Claude Skills deterministically using Python Behave (BDD framework).

## Quick Start

**See the complete example implementation:**
```
./example/
├── features/
│   ├── environment.py          # Sandbox setup
│   ├── skill_tests.feature     # Test scenarios
│   └── steps/claude_steps.py   # Step definitions
├── requirements.txt
└── README.md                   # Full documentation
```

**To use:**
1. Read `SKILL.md` for the complete guide
2. Check `example/README.md` for hands-on tutorial
3. Run `behave` in the example directory to see it work

## What This Skill Does

This skill helps you create **deterministic tests** for Claude Skills using BDD (Behavior-Driven Development).

**Instead of manually testing:**
> "Did Claude follow the SKILL.md correctly? Let me try it a few times..."

**You write automated tests:**
```gherkin
Scenario: Claude commits with correct prefix
  When I ask Claude to "Commit my feature"
  Then the commit should start with "feat: "
```

## Key Benefits

- ✅ **Regression protection** - Detect when skills break
- ✅ **Deterministic validation** - Test AI behavior reliably
- ✅ **Documentation** - Tests serve as examples
- ✅ **CI/CD integration** - Automate skill validation
- ✅ **Team collaboration** - Non-coders can read Gherkin

## Files in This Skill

| File | Purpose |
|------|---------|
| `SKILL.md` | Complete guide to BDD testing for Claude Skills |
| `example/` | Working implementation with test scenarios |
| `README.md` | This quick start guide |

## Example Test

**Your SKILL.md says:**
> "Always create a task_plan.md before major refactors"

**Your Behave test verifies it:**
```gherkin
Scenario: Claude creates task plan
  Given a SKILL.md requiring task plans
  When I ask Claude to "Refactor the codebase"
  Then a file "task_plan.md" should exist
```

**Run it:**
```bash
cd example
pip install -r requirements.txt
behave
```

**If Claude skips the task plan, the test fails!** ❌

## When to Use This Skill

Ask Claude Code to use this skill when you need to:
- Test that a skill follows its own rules
- Create regression tests for AI behavior
- Verify Claude doesn't do forbidden actions
- Build automated validation pipelines
- Ensure multi-step workflows work correctly

## Getting Started

**1. Read the full guide:**
```bash
# Open SKILL.md in your editor
code .claude/skills/bdd-skill-testing/SKILL.md
```

**2. Try the example:**
```bash
cd .claude/skills/bdd-skill-testing/example
pip install -r requirements.txt
behave
```

**3. Create tests for your own skills:**
- Copy the example directory
- Update the SKILL.md path in `environment.py`
- Write Gherkin scenarios for your skill
- Run tests!

---

**Made possible by:** Behave (Python BDD) + Claude Code CLI

**Inspired by:** The conversation with Gemini about deterministic AI agent testing 🤖
