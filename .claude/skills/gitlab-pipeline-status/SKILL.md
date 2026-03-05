---
name: gitlab-pipeline-status
description: Check GitLab CI/CD pipeline status and generate summary with verdict. Use when user asks to check GitLab pipeline status, monitor CI/CD jobs, or get a pipeline summary from gitlab.com or any self-hosted GitLab instance.
---

# GitLab Pipeline Status

Check GitLab CI/CD pipeline status and generate rich summaries with root cause analysis using the **GitLab MCP server** tools.

> **Tool preference:**
> - **Primary**: Use `mcp__gitlab__*` MCP tools for all GitLab API queries.
> - **Fallback**: If MCP tools are unavailable or fail, use `curl` via the Bash tool with the equivalent REST API endpoints.
> - **Never** use `wget` or `python` scripts.

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
- **GitLab Pages URLs**: Fetch directly with `WebFetch`.
- **Any other URL**: Fetch directly with `WebFetch`.
- **Pasted text**: Use as-is.

---

## Step 6: Analyze and Summarize

### Root Cause Analysis (if knowledge base provided)

Analyze the failed job logs against the knowledge base:

- Identify error messages, file names, module paths, and identifiers in the failure logs.
- Compare against the knowledge base content.
- Estimate relevance:
  - **High (60%+)**: Failure references files/modules described in the KB
  - **Moderate (30-59%)**: Some overlap
  - **Low (<30%)**: Little overlap — likely environmental, infrastructure, or config issue

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
| MCP tool unavailable | Fall back to `curl` via Bash with REST API endpoints |
| No pipelines found | Tell the user no pipelines exist for the project |

### Curl Fallback

If MCP tools are not available, use `curl` with the GitLab REST API. The user must provide a token and the GitLab instance URL.

```
curl -s "{gitlab_url}/api/v4/projects/{encoded_project}/jobs/{job_id}?private_token={token}"
curl -s "{gitlab_url}/api/v4/projects/{encoded_project}/pipelines/{pipeline_id}?private_token={token}"
curl -s "{gitlab_url}/api/v4/projects/{encoded_project}/pipelines/{pipeline_id}/jobs?private_token={token}"
curl -s "{gitlab_url}/api/v4/projects/{encoded_project}/jobs/{job_id}/trace?private_token={token}"
```

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
