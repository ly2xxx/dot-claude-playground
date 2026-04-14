# Skilo Lab

Experimental space for testing Agent Skills validation and linting using Skilo CLI tool.

## What is Skilo?

Skilo is a CLI tool for Agent Skills development that provides:
- **Validation** - Check skill structure and compliance
- **Formatting** - Auto-format SKILL.md files
- **Template generation** - Create skills from templates

## Installation

⚠️ **Note**: Skilo is currently installing via cargo (compiling from source). This may take 10-30 minutes on first install.

```bash
# Quick install
curl -sSfL https://raw.githubusercontent.com/manuelmauro/skilo/main/install.sh | sh

# Or from crates.io (what we're doing now)
cargo install skilo
```

## Quick Start

```bash
# Create a new skill from template
skilo new test-skill

# Validate an existing skill
skilo validate test-skill/

# Format all SKILL.md files
skilo fmt .

# Check formatting without making changes
skilo fmt --check .
```

## Testing Area

This directory contains sample skills to test Skilo's validation capabilities:

### Skills to Test
- `good-skill/` - Properly structured skill
- `bad-skill/` - Various validation issues (bad name, short description)
- `complex-skill/` - Multi-resource skill with scripts/, references/, assets/
- `test-skill/` - Simple test skill

### Test Scripts
- `test-skilo.ps1` - PowerShell script to run all tests
- `validation-rules.md` - Detailed documentation of validation rules

## Validation Rules Skilo Checks

1. **YAML Frontmatter**
   - Required fields: `name`, `description`
   - Proper YAML syntax
   - Name format (lowercase, hyphens)

2. **File Structure**
   - SKILL.md must exist
   - Valid directory names (scripts/, references/, assets/)
   - No forbidden files (README.md, etc.)

3. **Content Quality**
   - Description completeness
   - Line count limits
   - Resource references validity

4. **Naming Conventions**
   - Skill name matches directory
   - Hyphen-case naming
   - Length restrictions

## Running Tests

Once Skilo is installed, run:

```powershell
cd C:\code\dot-claude-playground\skilo_lab
.\test-skilo.ps1
```

This will:
1. Validate each test skill
2. Check formatting
3. Show expected errors/warnings

## Expected Results

### good-skill/
- ✅ Should pass all validation
- ✅ No formatting issues

### bad-skill/
- ❌ Name validation error (spaces not allowed)
- ❌ Description too short
- ⚠️ May have formatting suggestions

### complex-skill/
- ✅ Should pass validation
- ✅ All resources properly referenced

## Manual Tests

You can also test individual commands:

```bash
# Validate just one skill
skilo validate bad-skill/

# Check formatting of a specific file
skilo fmt --check good-skill/SKILL.md

# Format all files in place
skilo fmt .
```

## Status

- ✅ Skilo installing (cargo compilation in progress)
- ✅ Test skills created
- ✅ Documentation ready
- ⏳ Waiting for installation to complete testing

## Resources

- [Skilo GitHub](https://github.com/manuelmauro/skilo)
- [Agent Skills Spec](https://agentskills.io/specification)
- [Best Practices Guide](https://agentskills.io/skill-creation/best-practices)