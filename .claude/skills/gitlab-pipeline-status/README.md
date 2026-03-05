# gitlab-pipeline-status Skill

Check GitLab CI/CD pipeline status and generate rich summaries with root cause analysis.

## Sample Invocations

### Check a specific pipeline by URL

```
/gitlab-pipeline-status url=https://gitlab.com/my-org/my-project/-/pipelines/283
```

### Check a specific job by URL

```
/gitlab-pipeline-status url=https://gitlab.com/my-org/my-project/-/jobs/794
```

### Self-hosted GitLab instance (with token for private projects)

```
/gitlab-pipeline-status url=http://gitlab.internal/root/my-app/-/pipelines/50 token=glpat-xxxxxxxxxxxx
```

### With a knowledge base for root cause analysis

```
/gitlab-pipeline-status url=https://gitlab.com/my-org/my-project/-/pipelines/283 knowledge=http://root.pages.host.docker.internal/lab-01-basic-pipeline/
```

### No-exec mode (disables curl fallback)

```
/gitlab-pipeline-status run in No-Exec Mode url=https://gitlab.com/my-org/my-project/-/pipelines/283
```

## How It Works

1. **Parses** the pipeline or job URL to extract project path and ID
2. **Fetches** pipeline details, jobs, and failed job logs via GitLab MCP tools (`mcp__gitlab__*`)
3. **Optionally** fetches knowledge base content for root cause analysis
4. **Generates** a structured summary with verdict (PASS / FAIL / IN PROGRESS)

## Prerequisites

- GitLab MCP server configured in `.mcp.json` (primary)
- Falls back to `curl` if MCP is unavailable (requires token)

## MCP Tools Used

| Tool | Purpose |
|---|---|
| `mcp__gitlab__get_pipeline_job` | Resolve a job URL to its parent pipeline |
| `mcp__gitlab__list_pipelines` | Find the latest pipeline for a project |
| `mcp__gitlab__get_pipeline` | Get pipeline details (status, duration, ref) |
| `mcp__gitlab__list_pipeline_jobs` | List all jobs in a pipeline |
| `mcp__gitlab__get_pipeline_job_output` | Fetch failed job logs |
| `mcp__gitlab__get_file_contents` | Fetch knowledge base files from GitLab repos |
