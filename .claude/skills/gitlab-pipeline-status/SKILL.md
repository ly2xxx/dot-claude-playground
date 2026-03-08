---
name: gitlab-pipeline-status
description: Check GitLab CI/CD pipeline status and generate summary with verdict. Use when user asks to check GitLab pipeline status, monitor CI/CD jobs, or get pipeline summary from gitlab.com or self-hosted GitLab instances.
---

# GitLab Pipeline Status

Check GitLab CI/CD pipeline status and generate comprehensive summaries with verdicts.

## Quick Start

The `check_pipeline.py` script connects to GitLab API (gitlab.com or self-hosted) and generates a summary with:
- Pipeline status and metadata
- Job breakdown by status
- Failed jobs details with log tails
- Root cause analysis against an optional knowledge base (with confidence %)
- Simple verdict (PASS/FAIL/IN PROGRESS)

## Usage

### Check via Direct URL (Easiest)

Paste a pipeline or job URL directly — the script extracts the instance, project, and ID automatically:

```bash
python scripts/check_pipeline.py --link https://gitlab.example.com/group/project/-/pipelines/283
python scripts/check_pipeline.py --link https://gitlab.example.com/group/project/-/jobs/794
```

For private projects, add `--token`:

```bash
python scripts/check_pipeline.py --link https://gitlab.example.com/group/project/-/pipelines/283 --token YOUR_TOKEN
```

Job URLs are resolved to their parent pipeline automatically.

### Check Latest Pipeline (Public Project)

For public projects on gitlab.com, only the project ID is required:

```bash
python scripts/check_pipeline.py --project 278964
```

### Check Specific Pipeline

Specify a pipeline ID to check a specific run:

```bash
python scripts/check_pipeline.py --project 278964 --pipeline 123456789
```

### Private Projects (With Token)

For private projects, provide a GitLab API token:

```bash
python scripts/check_pipeline.py --project 278964 --token YOUR_GITLAB_TOKEN
```

### Self-Hosted GitLab

Use the `--url` flag to specify a custom GitLab instance:

```bash
python scripts/check_pipeline.py \
  --url https://gitlab.example.com \
  --project 42 \
  --token YOUR_TOKEN
```

## Parameters

- `--link`: Direct GitLab pipeline or job URL (extracts instance, project, and ID automatically)
- `--url`: GitLab instance URL (default: https://gitlab.com)
- `--project`: Project ID or path - e.g., '278964' or 'group/project' (required if `--link` not used)
- `--pipeline`: Pipeline ID (optional - fetches latest if not specified)
- `--token`: GitLab API token (required for private projects)
- `--tail`: Number of log lines per failed job (default: 50, 0 = full log)
- `--knowledge`: One or more knowledge base sources for root cause analysis (URLs or local file paths)

## Knowledge Base (Root Cause Analysis)

Provide `--knowledge` sources to correlate failed job logs against known issues.
The script extracts error phrases from logs, matches them against the knowledge base,
and reports a confidence percentage for each failed job.

### Supported Sources

- **URLs**: Any HTTP(S) URL returning text (GitLab blob URLs are auto-converted to raw)
- **Local files**: Paths relative to the `knowledge/` folder, or absolute paths

### Crawling static documentation sites

Knowledge base URLs often point to generated documentation sites (Docusaurus, MkDocs, Jekyll, Hugo, Sphinx, GitLab Pages). These sites have navigation structures that must be explored to find relevant content.

Strategy — crawl with purpose, not exhaustively:

- Fetch the landing page first. Parse it for navigation links (sidebar, table of contents, `<nav>`, `<ul>` link lists).
- Extract error keywords from the failed job logs — error messages, module names, command names, exit codes, package names.
- Follow only links whose text or URL path matches the error keywords. For example, if the error is about Docker, follow links containing "docker", "container", "dind", "runner", etc. If the error is about a test framework, follow links about "testing", "pytest", "jest", etc.
- Limit crawl depth to 2 levels from the landing page to avoid excessive fetching.
- Stop early once you find content that directly addresses the failure (e.g. a troubleshooting page, a runbook entry, a FAQ about the error).

Common static site patterns to recognize:

- **Docusaurus**: Sidebar links in `<nav>`, docs at `/docs/...` paths
- **MkDocs / Material**: Navigation in `<nav>`, pages often at `/topic/subtopic/`
- **Jekyll**: Posts at `/YYYY/MM/DD/...`, pages linked from index
- **Sphinx**: Table of contents with `toctree`, pages at `/topic.html`
- **Plain HTML**: Follow `<a href>` links from the index page

Do NOT:

- Fetch every link on the site — only those relevant to the error keywords
- Follow external links (different domain) unless they are explicitly part of the KB
- Fetch asset files (CSS, JS, images, fonts)

### Examples

```bash
# Use a project README as knowledge base
python scripts/check_pipeline.py \
  --link https://gitlab.example.com/group/project/-/pipelines/283 \
  --token YOUR_TOKEN \
  --knowledge https://gitlab.example.com/group/project/-/blob/main/README.md

# Use a local runbook
python scripts/check_pipeline.py \
  --link https://gitlab.example.com/group/project/-/pipelines/283 \
  --knowledge example-runbook.md

# Multiple sources
python scripts/check_pipeline.py \
  --link https://gitlab.example.com/group/project/-/pipelines/283 \
  --knowledge example-runbook.md https://gitlab.example.com/group/project/-/blob/main/docs/ci-troubleshooting.md
```

### Knowledge Folder

Place local knowledge files under the `knowledge/` folder (next to `scripts/`).
An example runbook is provided at `knowledge/example-runbook.md`.

## Finding Project/Pipeline IDs

### Project ID
- Navigate to your GitLab project
- Look under the project name - the ID is displayed there
- Or use the project path like 'group/subgroup/project'

### Pipeline ID
- Go to CI/CD → Pipelines in your project
- Click on a pipeline - the ID is in the URL: `/pipelines/123456789`

## Creating a GitLab Token

For private projects or self-hosted instances:

1. Go to GitLab → User Settings → Access Tokens
2. Create a token with `read_api` scope
3. Copy the token and use it with `--token`

## Output Format

The script generates a structured summary:

```
============================================================
🔍 GITLAB PIPELINE STATUS SUMMARY
============================================================

Pipeline ID:  123456789
Status:       ✅ SUCCESS
Branch/Tag:   main
Duration:     5m 23s
Created:      2026-02-26T08:00:00.000Z
URL:          https://gitlab.com/group/project/-/pipelines/123456789

📊 JOB BREAKDOWN:
------------------------------------------------------------
  ✅ Success: 8 job(s)
  ❌ Failed: 1 job(s)

❌ FAILED JOBS:
------------------------------------------------------------
  • test:integration (stage: test)

🎯 VERDICT:
------------------------------------------------------------
  ❌ FAIL - Pipeline failed (1 job(s) failed)

============================================================
```

## Exit Codes

The script returns different exit codes for automation:
- `0`: Pipeline succeeded
- `1`: Pipeline failed or canceled
- `2`: Pipeline running/pending/other status
- `3`: Error (API error, network error, etc.)

## Dependencies

The script requires the `requests` library:

```bash
pip install requests
```

## Example: Monitoring Latest Pipeline

To check if the latest pipeline on a public project is passing:

```bash
python scripts/check_pipeline.py --project 278964
echo "Exit code: $LASTEXITCODE"
```

## Example: Checking Private Project

For private projects, store your token securely and use it:

```bash
python scripts/check_pipeline.py \
  --project my-group/my-project \
  --token $env:GITLAB_TOKEN
```
