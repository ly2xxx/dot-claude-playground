# Example Knowledge Base

This is a placeholder knowledge file. Replace it with your own project-specific
content to enable relevance-based root cause analysis.

## What to Put Here

The knowledge base should describe your **project's code and structure** so the
tool can measure how likely a pipeline failure is related to your project code
vs. an environmental/infrastructure issue.

Good knowledge sources:
- **Repomix output** — a single-file summary of your entire project
- **Project README.md** — fetched via URL from GitLab
- **Architecture docs** — describing modules, file structure, dependencies
- **CI/CD config explanation** — what each pipeline stage/job does

## How It Works

The tool extracts technical terms (file names, module paths, identifiers,
function names) from both the failed job logs and the knowledge base, then
measures the overlap:

- **High relevance (60%+)**: The failure references files, modules, or
  identifiers described in the KB → likely a code-level issue
- **Moderate relevance (30-59%)**: Some overlap → may involve KB content
- **Low relevance (<30%)**: Little overlap → likely environmental, config,
  or infrastructure issue (tokens, credits, network, etc.)

## Example Usage

```bash
# Use a project README from GitLab
python scripts/check_pipeline.py \
  --link https://gitlab.example.com/group/project/-/pipelines/283 \
  --knowledge https://gitlab.example.com/group/project/-/blob/main/README.md

# Use a local repomix output
python scripts/check_pipeline.py \
  --link https://gitlab.example.com/group/project/-/pipelines/283 \
  --knowledge repomix-output.md

# Multiple sources
python scripts/check_pipeline.py \
  --link https://gitlab.example.com/group/project/-/pipelines/283 \
  --knowledge repomix-output.md https://gitlab.example.com/group/project/-/blob/main/docs/architecture.md
```
