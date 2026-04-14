# Skilo Validation Rules

This document outlines the validation rules that Skilo enforces for Agent Skills.

## Required Fields in Frontmatter

```yaml
---
name: skill-name          # Required: lowercase, hyphens only
description: ...          # Required: comprehensive description
---
```

## Naming Conventions

### Skill Name
- Must match directory name
- Lowercase letters only
- Hyphens for spaces
- Maximum 64 characters
- No special characters

✅ Good Examples:
- `pdf-editor`
- `weather-checker`
- `git-helper`

❌ Bad Examples:
- `Skill Name` (spaces)
- `skill_name` (underscores)
- `SkillName` (camelCase)
- `skill.name` (dots)

## Description Requirements

### Must Include
1. **What the skill does** - Primary functionality
2. **When to trigger** - Specific use cases
3. **Key capabilities** - Main features

### Quality Guidelines
- Comprehensive enough for Codex to decide when to use it
- Include trigger phrases and contexts
- Be specific about use cases

✅ Good:
```yaml
description: PDF manipulation toolkit for text extraction, form filling, and page operations. Use when working with PDF files for extracting text, filling forms, rotating pages, or merging documents.
```

❌ Bad:
```yaml
description: Helps with PDFs
```

## File Structure Requirements

### Required
- `SKILL.md` - Main skill file

### Optional Directories
- `scripts/` - Executable code
- `references/` - Documentation
- `assets/` - Static resources

### Forbidden Files
- `README.md`
- `INSTALLATION_GUIDE.md`
- `CHANGELOG.md`
- Any auxiliary documentation

## Content Guidelines

### Length Limits
- SKILL.md: Under 500 lines
- Use progressive disclosure for large content
- Reference files for detailed information

### Writing Style
- Use imperative/infinitive form ("Create X", not "You should create X")
- Avoid redundancy with references files
- Challenge each sentence: "Does Codex really need this?"

### Resource References
Reference bundled resources clearly:
```markdown
See [API.md](references/api.md) for API documentation
Use [main.py](scripts/main.py) for processing
Templates in [assets/](assets/templates/)
```

## Validation Checks

### 1. Structure Validation
- ✓ SKILL.md exists
- ✓ Directory names are valid
- ✓ No forbidden files present
- ✓ Skill name matches directory

### 2. Frontmatter Validation
- ✓ YAML syntax is valid
- ✓ Required fields present
- ✓ Name follows conventions
- ✓ Description is comprehensive

### 3. Content Validation
- ✓ Line count under limit
- ✓ No duplicate content
- ✓ Resource references are valid
- ✓ Uses imperative mood

### 4. Quality Checks
- ✓ Description triggers appropriately
- ✓ No redundant information
- ✓ Progressive disclosure used
- ✓ Clear organization

## Error Categories

### Errors (Block validation)
- Missing SKILL.md
- Invalid YAML syntax
- Missing required fields
- Forbidden files present
- Invalid naming conventions

### Warnings (Pass validation but noted)
- Long descriptions
- High line count
- Missing resource references
- Non-imperative mood

## Testing Strategy

### Test Skills
1. **good-skill** - Should pass all checks
2. **bad-skill** - Should trigger multiple errors
3. **complex-skill** - Tests multi-resource validation
4. **edge-cases** - Boundary conditions

### Test Matrix
| Rule | Good | Bad | Complex |
|------|------|-----|----------|
| Name format | ✓ | ✗ | ✓ |
| Description | ✓ | ✗ | ✓ |
| Line count | ✓ | ✗ | ✓ |
| Resources | - | - | ✓ |
| Forbidden files | ✓ | ✓ | ✓ |