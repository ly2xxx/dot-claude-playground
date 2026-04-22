# repo-study

A Claude Code skill that compares two git revisions in a GitHub or GitLab repository and produces a structured change summary grouped by JIRA ticket or logical path cluster.

## When Claude triggers this skill

Say things like:
- "what changed between v1.0.3 and v1.0.4 in \<repo URL\>"
- "compare tags v2 and v3 in \<repo\>"
- "summarize changes between main and release/1.5"
- "release notes between versions"
- "diff between commits"

## Usage

```bash
python scripts/fetch_changes.py <repo_url> --base <base_ref> --head <head_ref>
```

Both tags and branches work as refs. The `.git` suffix in the URL is optional.

### Examples

```bash
# Public repo, two release tags — no token needed
python scripts/fetch_changes.py https://github.com/owner/repo --base v1.0.3 --head v1.0.4

# GitLab, compare branches
python scripts/fetch_changes.py https://gitlab.com/group/repo --base main --head feature-branch

# Private repo — pass token explicitly
python scripts/fetch_changes.py https://github.com/owner/repo --base v1.0.0 --head v2.0.0 --token ghp_xxx

# Private repo — read token from environment
export GITHUB_TOKEN=ghp_xxx
python scripts/fetch_changes.py https://github.com/owner/repo --base v1.0.0 --head v2.0.0
```

## Parameters

| Flag | Short | Description |
|------|-------|-------------|
| `repo_url` | — | GitHub or GitLab URL (`.git` suffix optional) |
| `--base` | `-b` | Base revision: tag, branch, or commit SHA |
| `--head` | — | Head revision: tag, branch, or commit SHA |
| `--token` | `-t` | API token (or set `GITHUB_TOKEN` / `GITLAB_TOKEN`) |

## Output

Commits are grouped first by JIRA ticket ID (pattern `[A-Z]+-\d+`), then by top-level directory for anything unmatched:

```
============================================================
  CHANGE SUMMARY: v1.0.3 → v1.0.4
============================================================

JIRA GROUPS:
  [PROJ-123] feat: implement login
    - feat: implement JWT login (abc1234)
    Files: src/auth/ (4 file(s) changed)

UNGROUPED COMMITS (by path area):
  [.github/] add github ci example (1b395b5)
  [demo/] Add md-mcp Infographic (9c6487f)

COMPARISON URL:
  https://github.com/owner/repo/compare/v1.0.3...v1.0.4
============================================================
```

## Known issues

**Windows Unicode error** — the `→` character in the summary header fails on Windows terminals using the default cp1252 encoding. Fix by setting:

```bash
export PYTHONIOENCODING=utf-8
```

or on Windows cmd/PowerShell:

```powershell
$env:PYTHONIOENCODING = "utf-8"
```

## API tokens

| Provider | Where to create | Required scope |
|----------|----------------|----------------|
| GitHub | Settings → Developer settings → Personal access tokens | `repo` (private repos) or none (public) |
| GitLab | User Settings → Access Tokens | `read_api` |

Public repos on GitHub do not require a token.

## Dependencies

```bash
pip install requests
```

## Scripts

- [fetch_changes.py](scripts/fetch_changes.py) — main entry point; fetches commits via REST API and prints the grouped summary
- [repo_compare_url.py](scripts/repo_compare_url.py) — utility to generate comparison URLs for GitHub and GitLab
