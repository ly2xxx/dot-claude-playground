---
name: gitlab-pipeline-status
description: Check GitLab CI/CD pipeline status and generate summary with verdict. Use when user asks to check GitLab pipeline status, monitor CI/CD jobs, or get a pipeline summary from gitlab.com or any self-hosted GitLab instance.
---

# GitLab Pipeline Status

Check GitLab CI/CD pipeline status and generate rich summaries with root cause analysis using the **GitLab MCP server** tools.

> **Tool preference:**
> - Use `mcp__gitlab__*` MCP tools for **all** GitLab API queries.
> - Use `WebFetch` for fetching external knowledge base URLs.
> - **Never** use `Bash`, `curl`, `wget`, or `python` scripts — even as a fallback.

---

## Step 1: Gather Inputs

Ask the user for the following information. All items except the pipeline URL/ID are optional:

| Input | Required | Notes |
|---|---|---|
| Pipeline or job URL **or** project ID/path + pipeline ID | Yes (one of) | e.g. `https://gitlab.com/group/project/-/pipelines/123` or project `278964` |
| Knowledge base sources | No | URLs (including GitLab Pages) or text pasted in chat |
| Log tail size | No | Number of log lines to show per failed job (default: 50) |

> **Note**: Authentication is handled by the MCP server configuration. No token is needed in the chat unless using the curl fallback.

---

## Step 2: Parse the Input

**If a pipeline or job URL was provided**, extract from it:
- `project_path` — the path between the host and `/-/` (e.g. `group/subgroup/project`)
- `type` — `pipelines` or `jobs`
- `id` — the numeric ID at the end

Supported URL formats:
```
https://gitlab.example.com/group/project/-/pipelines/283
https://gitlab.example.com/group/project/-/jobs/794
```

**If `--project` and optional `--pipeline` were provided**, use them directly.

URL-encode the project path for MCP tool calls by replacing `/` with `%2F` (e.g. `group/project` → `group%2Fproject`).

---

## Step 3: Fetch Pipeline Data

### 3a. If a Job URL was given — resolve to pipeline ID

Use `mcp__gitlab__get_pipeline_job` with:
- `project_id`: URL-encoded project path
- `job_id`: the job ID from the URL

Extract the pipeline ID from the response.

### 3b. Fetch pipeline details

If no pipeline ID is known, fetch the latest pipeline:

Use `mcp__gitlab__list_pipelines` with:
- `project_id`: URL-encoded project path
- `per_page`: 1

Take the first result's `id`.

Then fetch the specific pipeline:

Use `mcp__gitlab__get_pipeline` with:
- `project_id`: URL-encoded project path
- `pipeline_id`: the pipeline ID

### 3c. Fetch pipeline jobs

Use `mcp__gitlab__list_pipeline_jobs` with:
- `project_id`: URL-encoded project path
- `pipeline_id`: the pipeline ID

---

## Step 4: Fetch Failed Job Logs

For each job where `status == "failed"`, fetch its log output:

Use `mcp__gitlab__get_pipeline_job_output` with:
- `project_id`: URL-encoded project path
- `job_id`: the failed job's ID
- `start`: negative value for tail lines (e.g. `-50` for last 50 lines)
- `limit`: the tail size (default: 50)

---

## Step 5: Fetch Knowledge Base (Optional)

If the user provided knowledge base sources:

- **GitLab repository files**: Use `mcp__gitlab__get_file_contents` with the `project_id`, `file_path`, and optional `ref` (branch/tag).
- **GitLab blob URLs**: Extract the project path, file path, and ref from the URL and use `mcp__gitlab__get_file_contents`.
- **GitLab Pages URLs**: Fetch with `WebFetch`. If WebFetch fails (e.g. HTTP-only internal URLs that get upgraded to HTTPS), provide the URL to the user and ask them to paste the content.
- **Any other URL**: Fetch directly with `WebFetch`.
- **Pasted text**: Use as-is.

### Crawling static documentation sites

Knowledge base URLs often point to **generated documentation sites** (Docusaurus, MkDocs, Jekyll, Hugo, Sphinx, GitLab Pages). These sites have navigation structures that must be explored to find relevant content.

**Strategy — crawl with purpose, not exhaustively:**

1. **Fetch the landing page** first. Parse it for navigation links (sidebar, table of contents, `<nav>`, `<ul>` link lists).
2. **Extract error keywords** from the failed job logs — error messages, module names, command names, exit codes, package names.
3. **Follow only links whose text or URL path matches the error keywords**. For example, if the error is about Docker, follow links containing "docker", "container", "dind", "runner", etc. If the error is about a test framework, follow links about "testing", "pytest", "jest", etc.
4. **Limit crawl depth to 2 levels** from the landing page to avoid excessive fetching.
5. **Stop early** once you find content that directly addresses the failure (e.g. a troubleshooting page, a runbook entry, a FAQ about the error).

**Common static site patterns to recognize:**
- **Docusaurus**: Sidebar links in `<nav>`, docs at `/docs/...` paths
- **MkDocs / Material**: Navigation in `<nav>`, pages often at `/topic/subtopic/`
- **Jekyll**: Posts at `/YYYY/MM/DD/...`, pages linked from index
- **Sphinx**: Table of contents with `toctree`, pages at `/topic.html`
- **Plain HTML**: Follow `<a href>` links from the index page

**Do NOT:**
- Fetch every link on the site — only those relevant to the error keywords
- Follow external links (different domain) unless they are explicitly part of the KB
- Fetch asset files (CSS, JS, images, fonts)

---

## Step 6: Analyze and Summarize

### Root Cause Analysis (if knowledge base provided)

Analyze the failed job logs against the knowledge base content gathered in Step 5:

1. **Extract failure signals** from each failed job log:
   - Error messages and exit codes
   - File paths, module names, package names
   - Command names and flags
   - Stack traces and assertion failures

2. **Search the KB content** for matches against these signals:
   - Direct mentions of the error message or error code
   - Documentation about the failing command, tool, or module
   - Troubleshooting sections, FAQs, or known issues
   - Configuration guidance related to the failure

3. **Score KB relevance per failed job** based on how much the KB content explains or addresses the failure:
   - **High (60-100%)**: KB directly describes the error, provides a fix, or documents the failing component in detail
   - **Moderate (30-59%)**: KB covers related topics (e.g. documents the tool that failed but not this specific error)
   - **Low (0-29%)**: KB has little or no content related to the failure — likely an environmental, infrastructure, or config issue outside the KB's scope

4. **Compute an overall KB relevance score** — weighted average across all failed jobs (blocking jobs weighted higher than allow_failure jobs)

### Generate Summary

Produce a structured summary in this format:

```
============================================================
GITLAB PIPELINE STATUS SUMMARY
============================================================

Pipeline ID:  <id>
Status:       <emoji> <STATUS>
Branch/Tag:   <ref>
Duration:     <Xm Ys>
Created:      <timestamp>
URL:          <web_url>

JOB BREAKDOWN:
------------------------------------------------------------
  Success: N job(s)
  Failed: N job(s)
  Running: N job(s)   (if applicable)

FAILED JOBS:
------------------------------------------------------------
  - <job-name> (stage: <stage>)

FAILED JOB LOGS:
============================================================
--- <job-name> (job #<id>) ---
<last N lines of trace log>

KNOWLEDGE BASE:          (if provided)
------------------------------------------------------------
  <source>
     <120-char preview>...

ROOT CAUSE ANALYSIS:    (if knowledge base provided)
============================================================
  Job: <job-name> (#<id>)
  Error: <first error line>
  KB relevance: [========............] <N>%
  -> <low/moderate/high relevance interpretation>

VERDICT:
------------------------------------------------------------
  PASS - All jobs completed successfully
  -- or --
  FAIL - Pipeline failed (N job(s) failed)
  -- or --
  IN PROGRESS - Pipeline is currently running

  KB RELEVANCE: <N>%         (if knowledge base provided)
  [========............]
  <interpretation of how useful the KB was for diagnosing the failure>

============================================================
```

Status emoji reference:
| Status | Emoji |
|--------|-------|
| success | ✅ |
| failed | ❌ |
| running | 🔄 |
| pending | ⏳ |
| canceled | 🚫 |
| skipped | ⏭️ |
| manual | 🤚 |
| created | 🆕 |

---

## Handling Errors

| Error | Action |
|---|---|
| MCP tool returns 401/403 | Ask user to check their GitLab token in MCP server config |
| MCP tool returns 404 | Ask user to verify the project path and pipeline ID |
| MCP tool unavailable | Inform the user that the GitLab MCP server is required and ask them to check `.mcp.json` configuration |
| No pipelines found | Tell the user no pipelines exist for the project |

---

## Knowledge Base Tips

The knowledge base is most useful when it contains **project-specific content** that describes your code and infrastructure:

- **GitLab repo files**: Use `mcp__gitlab__get_file_contents` to fetch README, runbooks, or CI config docs directly from the repository.
- **GitLab Pages runbook**: Host a `runbook.md` on GitLab Pages and pass the URL as a knowledge source.
- **CI/CD config docs**: Descriptions of what each pipeline stage/job does helps identify root causes.
- **Repomix output**: A single-file summary of the entire project codebase.

---

## Finding Project and Pipeline IDs

**Project ID / path**:
- Navigate to your GitLab project — the numeric ID is shown below the project name
- Or use the path directly: `group/subgroup/project`

**Pipeline ID**:
- Go to CI/CD > Pipelines > click a pipeline — the ID is in the URL: `/-/pipelines/123456789`
