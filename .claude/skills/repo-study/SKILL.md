---
name: repo-study
description: Compare two git revisions (tags, branches, or commit hashes) in a GitHub or GitLab repository and generate a structured change summary grouped by JIRA ticket ID or logical path-based commit cluster. Use when generating release notes, auditing changes between versions, reviewing what changed between two refs, summarizing PR impact across GitHub or GitLab repositories, or getting a diff summary between commits. Trigger phrases: "compare tags", "what changed between", "summarize changes between", "release notes between versions", "diff between commits", "changes from base to head".
---

# Repo Study — Change Summary

Compare two revisions in a GitHub or GitLab repository and produce a structured change summary grouped by JIRA ticket or logical commit cluster.

## Quick Start

```bash
python scripts/fetch_changes.py <repo_url> --base <base_ref> --head <head_ref>
```

## Examples

```bash
# GitHub — compare two release tags
python scripts/fetch_changes.py https://github.com/owner/repo --base v1.0.0 --head v2.0.0

# GitLab — compare branches
python scripts/fetch_changes.py https://gitlab.com/group/repo --base main --head feature-branch

# Private repo with API token
python scripts/fetch_changes.py https://github.com/owner/repo --base v1.0.0 --head v2.0.0 --token ghp_xxx

# Read token from environment
export GITHUB_TOKEN=ghp_xxx
python scripts/fetch_changes.py https://github.com/owner/repo --base v1.0.0 --head v2.0.0
```

## Parameters

- `repo_url` — GitHub or GitLab repository URL (`.git` suffix optional)
- `--base` / `-b` — Base revision: tag, branch, or commit hash
- `--head` — Head revision: tag, branch, or commit hash
- `--token` / `-t` — API token (or set `GITHUB_TOKEN` / `GITLAB_TOKEN` env var)

## Workflow

1. Run `scripts/fetch_changes.py` with the repo URL and refs.
2. Commits between base and head are fetched via the GitHub or GitLab REST API.
3. Each commit message is scanned for JIRA ticket IDs (`[A-Z]+-\d+` pattern).
4. Commits with JIRA IDs are grouped under each ticket.
5. Remaining commits are clustered by top-level directory of affected files.
6. A structured summary is printed with the comparison URL.

## Output Format

```
============================================================
  CHANGE SUMMARY: v1.0.0 → v2.0.0
============================================================

JIRA GROUPS:
  [PROJ-123] feat: implement JWT login; fix: handle token expiry
    - feat: implement JWT login (abc1234)
    - fix: handle token expiry edge case (def5678)
    Files: src/auth/ (4 file(s) changed)

  [PROJ-456] chore: upgrade stripe SDK to v12
    - chore: upgrade stripe SDK to v12 (bcd2345)
    Files: src/payments/ (2 file(s) changed)

UNGROUPED COMMITS (by path area):
  [ci/] update GitHub Actions workflow (ef6789a)

COMPARISON URL:
  https://github.com/owner/repo/compare/v1.0.0...v2.0.0
============================================================
```

## Scripts

- [fetch_changes.py](scripts/fetch_changes.py) — Fetch commits via API and print the JIRA-grouped summary
- [repo_compare_url.py](scripts/repo_compare_url.py) — Generate comparison URLs for GitHub and GitLab

## API Tokens

| Provider | Where to create | Required scope |
|----------|----------------|----------------|
| GitHub | Settings → Developer settings → PAT | `repo` (private) or none (public) |
| GitLab | User Settings → Access Tokens | `read_api` |

## Dependencies

```bash
pip install requests
```
