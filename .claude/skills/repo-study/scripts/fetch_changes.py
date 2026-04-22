#!/usr/bin/env python3
"""
Fetch commits between two git refs in a GitHub or GitLab repository,
group by JIRA ticket ID found in commit messages, then cluster remaining
commits by top-level directory of affected files.

Usage:
    python fetch_changes.py <repo_url> --base <ref> --head <ref> [--token TOKEN]

Examples:
    python fetch_changes.py https://github.com/owner/repo --base v1.0.0 --head v2.0.0
    python fetch_changes.py https://gitlab.com/group/repo --base main --head develop --token glpat-xxx
"""

import argparse
import os
import re
import sys
from collections import defaultdict
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    print("Error: 'requests' is required. Install with: pip install requests")
    sys.exit(1)


JIRA_RE = re.compile(r"\b([A-Z][A-Z0-9]+-\d+)\b")


def detect_provider(url: str) -> str:
    host = urlparse(url).netloc.lower()
    if "github" in host:
        return "github"
    if "gitlab" in host:
        return "gitlab"
    return "unknown"


def repo_path(url: str) -> str:
    p = urlparse(url).path.strip("/")
    return p[:-4] if p.endswith(".git") else p


def gh_compare(path: str, base: str, head: str, token: str) -> tuple:
    hdrs = {"Accept": "application/vnd.github+json"}
    if token:
        hdrs["Authorization"] = f"Bearer {token}"

    r = requests.get(
        f"https://api.github.com/repos/{path}/compare/{base}...{head}",
        headers=hdrs,
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()

    commits = []
    for c in data.get("commits", []):
        commits.append(
            {
                "sha": c["sha"][:7],
                "message": c["commit"]["message"].split("\n")[0],
                "files": [f["filename"] for f in c.get("files", [])],
            }
        )

    # The compare endpoint may omit per-commit file lists; fetch individually if needed.
    if commits and not commits[0]["files"]:
        for c in commits:
            dr = requests.get(
                f"https://api.github.com/repos/{path}/commits/{c['sha']}",
                headers=hdrs,
                timeout=30,
            )
            if dr.ok:
                c["files"] = [f["filename"] for f in dr.json().get("files", [])]

    compare_url = f"https://github.com/{path}/compare/{base}...{head}"
    return commits, compare_url


def gl_compare(path: str, base: str, head: str, token: str, base_url: str) -> tuple:
    hdrs = {"PRIVATE-TOKEN": token} if token else {}
    encoded = path.replace("/", "%2F")

    r = requests.get(
        f"{base_url}/api/v4/projects/{encoded}/repository/compare",
        headers=hdrs,
        params={"from": base, "to": head},
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()

    all_files = [d["new_path"] for d in data.get("diffs", [])]
    commits = [
        {"sha": c["id"][:7], "message": c["title"], "files": all_files}
        for c in data.get("commits", [])
    ]
    compare_url = f"{base_url}/{path}/-/compare/{base}...{head}"
    return commits, compare_url


def top_prefix(files: list) -> str:
    if not files:
        return "(root)"
    parts = [f.split("/")[0] for f in files]
    return max(set(parts), key=parts.count) + "/"


def group_by_jira(commits: list) -> tuple:
    jira: dict = defaultdict(list)
    other: list = []
    for c in commits:
        ids = list(dict.fromkeys(JIRA_RE.findall(c["message"])))
        if ids:
            for jid in ids:
                jira[jid].append(c)
        else:
            other.append(c)
    return jira, other


def print_report(jira_groups, ungrouped, compare_url, base, head) -> None:
    sep = "=" * 60
    print(f"\n{sep}")
    print(f"  CHANGE SUMMARY: {base} → {head}")
    print(f"{sep}\n")

    if jira_groups:
        print("JIRA GROUPS:")
        for ticket, commits in sorted(jira_groups.items()):
            all_files = sorted({f for c in commits for f in c["files"]})
            prefix = top_prefix(all_files) if all_files else ""
            title = "; ".join(dict.fromkeys(c["message"][:55] for c in commits))
            print(f"\n  [{ticket}] {title[:80]}")
            for c in commits:
                print(f"    - {c['message'][:68]} ({c['sha']})")
            if all_files:
                print(f"    Files: {prefix} ({len(all_files)} file(s) changed)")
    else:
        print("  No JIRA tickets detected in commit messages.\n")

    if ungrouped:
        clusters: dict = defaultdict(list)
        for c in ungrouped:
            clusters[top_prefix(c["files"])].append(c)
        print("\nUNGROUPED COMMITS (by path area):")
        for prefix, commits in sorted(clusters.items()):
            for c in commits:
                print(f"  [{prefix}] {c['message'][:68]} ({c['sha']})")

    print(f"\nCOMPARISON URL:\n  {compare_url}")
    print(f"\n{sep}\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Summarize repo changes grouped by JIRA ticket or file-path cluster"
    )
    parser.add_argument("repo_url", help="GitHub or GitLab repository URL")
    parser.add_argument("--base", "-b", required=True, help="Base ref (tag, branch, or commit hash)")
    parser.add_argument("--head", required=True, help="Head ref (tag, branch, or commit hash)")
    parser.add_argument("--token", "-t", help="API token (or GITHUB_TOKEN / GITLAB_TOKEN env var)")
    args = parser.parse_args()

    provider = detect_provider(args.repo_url)
    if provider == "unknown":
        print("Error: Only GitHub and GitLab repositories are supported.")
        sys.exit(1)

    path = repo_path(args.repo_url)
    token = args.token or os.getenv("GITHUB_TOKEN") or os.getenv("GITLAB_TOKEN")

    try:
        if provider == "github":
            commits, url = gh_compare(path, args.base, args.head, token)
        else:
            parsed = urlparse(args.repo_url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            commits, url = gl_compare(path, args.base, args.head, token, base_url)
    except requests.HTTPError as e:
        print(f"API error {e.response.status_code}: {e.response.text[:300]}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    jira_groups, ungrouped = group_by_jira(commits)
    print_report(jira_groups, ungrouped, url, args.base, args.head)


if __name__ == "__main__":
    main()
