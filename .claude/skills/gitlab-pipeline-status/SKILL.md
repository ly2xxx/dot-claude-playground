---
name: gitlab-pipeline-status
description: Check GitLab CI/CD pipeline status and generate summary with verdict. Use when user asks to check GitLab pipeline status, monitor CI/CD jobs, or get a pipeline summary from gitlab.com or any self-hosted GitLab instance. Works without command execution — no curl, no scripts, no Bash.
---

# GitLab Pipeline Status (No-Exec Mode)

Check GitLab CI/CD pipeline status and generate rich summaries with root cause analysis — without running any scripts, curl commands, or shell tools.

> ⛔ **NO-EXEC RULES — follow these strictly:**
> - **Never** use `curl`, `wget`, `python`, `bash`, or any shell/terminal tool.
> - **Never** propose a command for the user to run (unless they explicitly ask for a manual workaround).
> - **First choice**: use the `read_url_content` tool to fetch API responses directly.
> - **If `read_url_content` is unavailable**: provide the user with fully-formed URLs to open in their browser or Postman, and ask them to paste the JSON response back into the chat. Then analyse the pasted JSON.

---

## Step 1: Gather Inputs

Ask the user for the following information. All items except the pipeline URL/ID are optional:

| Input | Required | Notes |
|---|---|---|
| Pipeline or job URL **or** project ID/path + pipeline ID | Yes (one of) | e.g. `https://gitlab.com/group/project/-/pipelines/123` or project `278964` |
| GitLab instance URL | No | Default: `https://gitlab.com` |
| GitLab API token | No | Required for private projects — user pastes it in chat |
| Knowledge base sources | No | URLs (including GitLab Pages) or text pasted in chat |
| Log tail size | No | Number of log lines to show per failed job (default: 50) |

> **Token note**: Since there is no command execution, the user should paste their token directly in the chat. Remind them it will only be used for this session and not stored. For read-only access, a token with `read_api` scope is sufficient.

---

## Step 2: Parse the Input

**If a pipeline or job URL was provided**, extract from it:
- `gitlab_url` — the scheme + host (e.g. `https://gitlab.com`)
- `project` — the path between the host and `/-/` (e.g. `group/subgroup/project`)
- `type` — `pipelines` or `jobs`
- `id` — the numeric ID at the end

Supported URL formats:
```
https://gitlab.example.com/group/project/-/pipelines/283
https://gitlab.example.com/group/project/-/jobs/794
```

**If `--project` and optional `--pipeline` were provided**, use them directly with the configured GitLab URL.

URL-encode the project path for API calls by replacing `/` with `%2F` (e.g. `group/project` → `group%2Fproject`).

---

## Step 3: Fetch Pipeline Data

**Try `read_url_content` first.** If that tool is not available, skip to [Step 3 — Manual Fallback](#step-3-manual-fallback-if-read_url_content-is-unavailable) below.

Tokens are appended as a query parameter (e.g. `?private_token=<token>`) since `read_url_content` does not support custom headers.

### 3a. If a Job URL was given — resolve to pipeline ID

```
GET {gitlab_url}/api/v4/projects/{encoded_project}/jobs/{job_id}?private_token={token}
```

Extract `pipeline.id` from the response to get the parent pipeline ID.

### 3b. Fetch pipeline details

If no pipeline ID is known, fetch the latest:
```
GET {gitlab_url}/api/v4/projects/{encoded_project}/pipelines?per_page=1&private_token={token}
```
Take the first result's `id`.

Then fetch the specific pipeline:
```
GET {gitlab_url}/api/v4/projects/{encoded_project}/pipelines/{pipeline_id}?private_token={token}
```

### 3c. Fetch pipeline jobs

```
GET {gitlab_url}/api/v4/projects/{encoded_project}/pipelines/{pipeline_id}/jobs?private_token={token}
```

---

## Step 4: Fetch Failed Job Logs

For each job where `status == "failed"`, fetch its trace log:

```
GET {gitlab_url}/api/v4/projects/{encoded_project}/jobs/{job_id}/trace?private_token={token}
```

Retain the last `tail` lines (default 50) from each log.

---

## Step 3 — Manual Fallback (if `read_url_content` is unavailable)

> Only use this path if the `read_url_content` tool is not available. Do **not** use `curl` or any shell command.

Construct the full API URLs below (substituting real values) and ask the user to open them in a **browser** or **Postman**, then paste the JSON response back into the chat:

**1. Resolve job → pipeline (only if a job URL was given)**
```
{gitlab_url}/api/v4/projects/{encoded_project}/jobs/{job_id}?private_token={token}
```

**2. Get latest pipeline** (omit if pipeline ID already known)
```
{gitlab_url}/api/v4/projects/{encoded_project}/pipelines?per_page=1&private_token={token}
```

**3. Get pipeline details**
```
{gitlab_url}/api/v4/projects/{encoded_project}/pipelines/{pipeline_id}?private_token={token}
```

**4. Get pipeline jobs**
```
{gitlab_url}/api/v4/projects/{encoded_project}/pipelines/{pipeline_id}/jobs?private_token={token}
```

**5. Get failed job trace(s)** — ask for each failed job ID found in step 4
```
{gitlab_url}/api/v4/projects/{encoded_project}/jobs/{job_id}/trace?private_token={token}
```

> For **public** projects, omit `?private_token={token}`. For **private** projects, the user can also open the browser while already logged into GitLab — the session cookie will authenticate automatically (no token needed in the URL).

Once the user pastes each JSON/text response, continue with Step 5 using the pasted data.

---

## Step 5: Fetch Knowledge Base (Optional)

If the user provided knowledge base sources:

- **GitLab blob URLs**: Auto-convert `/-/blob/` → `/-/raw/` before fetching.
- **GitLab Pages URLs**: Fetch directly (they are standard HTTPS).
- **Any other URL**: Fetch directly with `read_url_content`.
- **Pasted text**: Use as-is.

Token may be needed for private GitLab repos; append `?private_token={token}` as needed.

---

## Step 6: Analyze and Summarize

### Root Cause Analysis (if knowledge base provided)

Using LLM reasoning (no scripts needed), analyze the failed job logs against the knowledge base:

- Identify error messages, file names, module paths, and identifiers in the failure logs.
- Compare against the knowledge base content.
- Estimate relevance:
  - **High (60%+)**: Failure references files/modules described in the KB → likely a code-level issue
  - **Moderate (30–59%)**: Some overlap → may involve KB content
  - **Low (<30%)**: Little overlap → likely environmental, infrastructure, or config issue

### Generate Summary

Produce a structured summary in this format:

```
============================================================
🔍 GITLAB PIPELINE STATUS SUMMARY
============================================================

Pipeline ID:  <id>
Status:       <emoji> <STATUS>
Branch/Tag:   <ref>
Duration:     <Xm Ys>
Created:      <timestamp>
URL:          <web_url>

📊 JOB BREAKDOWN:
------------------------------------------------------------
  ✅ Success: N job(s)
  ❌ Failed: N job(s)
  🔄 Running: N job(s)   (if applicable)

❌ FAILED JOBS:
------------------------------------------------------------
  • <job-name> (stage: <stage>)

📋 FAILED JOB LOGS:
============================================================
--- <job-name> (job #<id>) ---
<last N lines of trace log>

📚 KNOWLEDGE BASE:          (if provided)
------------------------------------------------------------
  📄 <source>
     <120-char preview>...

🔬 ROOT CAUSE ANALYSIS:    (if knowledge base provided)
============================================================
  Job: <job-name> (#<id>)
  Error: <first error line>
  KB relevance: [████████░░░░░░░░░░░░] <N>%
  → <low/moderate/high relevance interpretation>

🎯 VERDICT:
------------------------------------------------------------
  ✅ PASS - All jobs completed successfully
  — or —
  ❌ FAIL - Pipeline failed (N job(s) failed)
  — or —
  🔄 IN PROGRESS - Pipeline is currently running

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
| 401 Unauthorized | Ask user to provide or re-check their GitLab API token |
| 404 Not Found | Ask user to verify the project path and pipeline ID |
| Network/timeout | Report the error and suggest retrying |
| No pipelines found | Tell the user no pipelines exist for the project |

---

## Knowledge Base Tips

The knowledge base is most useful when it contains **project-specific content** that describes your code and infrastructure:

- **GitLab Pages runbook**: Host a `runbook.md` on GitLab Pages and pass the URL as a knowledge source — works without any token since Pages can be public.
- **Project README**: Pass the GitLab blob URL for the README; it will be auto-converted to a raw fetch.
- **CI/CD config docs**: Descriptions of what each pipeline stage/job does helps identify root causes.
- **Repomix output**: A single-file summary of the entire project codebase.

### Example GitLab Pages Knowledge Base

If your team hosts docs on GitLab Pages at `https://your-team.gitlab.io/runbook/ci-failures.html`, simply pass that URL when prompted for knowledge sources. Claude will fetch and use it during root cause analysis.

---

## Finding Project and Pipeline IDs

**Project ID / path**:
- Navigate to your GitLab project → the numeric ID is shown below the project name
- Or use the path directly: `group/subgroup/project`

**Pipeline ID**:
- Go to CI/CD → Pipelines → click a pipeline → the ID is in the URL: `/-/pipelines/123456789`

**Creating a token** (if needed):
1. GitLab → User Settings → Access Tokens
2. Create a token with `read_api` scope
3. Paste it into the chat when prompted

---

## Alternative: Script-Based Mode

If command execution is available, the `scripts/check_pipeline.py` script provides identical functionality and can be run directly:

```bash
python scripts/check_pipeline.py --link https://gitlab.example.com/group/project/-/pipelines/283
python scripts/check_pipeline.py --link https://gitlab.example.com/group/project/-/pipelines/283 \
  --token YOUR_TOKEN \
  --knowledge https://your-team.gitlab.io/runbook/ci-failures.html
```

See the script's `--help` output for all options.
