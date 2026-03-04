#!/usr/bin/env python3
"""
GitLab Pipeline Status Checker

Fetches and summarizes GitLab pipeline status from gitlab.com or self-hosted instances.
"""

import argparse
import re
import sys
import io
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List

# Fix encoding for Windows console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def format_duration(seconds: Optional[int]) -> str:
    """Format duration in seconds to human-readable format."""
    if seconds is None:
        return "N/A"
    
    minutes, secs = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def get_status_emoji(status: str) -> str:
    """Get emoji representation for pipeline status."""
    status_map = {
        "success": "✅",
        "failed": "❌",
        "running": "🔄",
        "pending": "⏳",
        "canceled": "🚫",
        "skipped": "⏭️",
        "manual": "🤚",
        "created": "🆕"
    }
    return status_map.get(status, "❓")


def get_verdict(status: str, failed_jobs: int = 0) -> str:
    """Generate a simple verdict based on pipeline status."""
    if status == "success":
        return "✅ PASS - All jobs completed successfully"
    elif status == "failed":
        return f"❌ FAIL - Pipeline failed ({failed_jobs} job(s) failed)"
    elif status == "running":
        return "🔄 IN PROGRESS - Pipeline is currently running"
    elif status == "pending":
        return "⏳ PENDING - Pipeline is waiting to start"
    elif status == "canceled":
        return "🚫 CANCELED - Pipeline was canceled"
    elif status == "skipped":
        return "⏭️ SKIPPED - Pipeline was skipped"
    else:
        return f"❓ UNKNOWN - Status: {status}"


def parse_gitlab_link(link: str) -> Dict[str, str]:
    """Parse a GitLab pipeline or job URL into components.

    Supports:
      - http://gitlab.example.com/group/project/-/pipelines/283
      - http://gitlab.example.com/group/sub/project/-/jobs/794
    """
    match = re.match(r'^(https?://[^/]+)/(.+?)/-/(pipelines|jobs)/(\d+)$', link)
    if not match:
        raise ValueError(
            f"Cannot parse GitLab URL: {link}\n"
            "Expected format: <gitlab-url>/<project-path>/-/pipelines/<id> "
            "or <gitlab-url>/<project-path>/-/jobs/<id>"
        )
    return {
        "gitlab_url": match.group(1),
        "project": match.group(2),
        "type": match.group(3),       # "pipelines" or "jobs"
        "id": match.group(4),
    }


def resolve_job_to_pipeline(gitlab_url: str, project_id: str, job_id: str, token: Optional[str]) -> str:
    """Given a job ID, return its parent pipeline ID."""
    from urllib.parse import quote
    encoded = quote(project_id, safe='')
    headers = {"PRIVATE-TOKEN": token} if token else {}
    url = f"{gitlab_url}/api/v4/projects/{encoded}/jobs/{job_id}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    job = response.json()
    return str(job["pipeline"]["id"])


def fetch_job_trace(gitlab_url: str, project_id: str, job_id: int, token: Optional[str], tail: int = 50) -> str:
    """Fetch a job's log trace and return the last `tail` lines."""
    from urllib.parse import quote
    encoded = quote(project_id, safe='')
    headers = {"PRIVATE-TOKEN": token} if token else {}
    url = f"{gitlab_url}/api/v4/projects/{encoded}/jobs/{job_id}/trace"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    # Trace comes back as plain text; strip ANSI escape codes for readability
    raw = response.text
    clean = re.sub(r'\x1b\[[0-9;]*m', '', raw)
    lines = clean.splitlines()
    if tail and len(lines) > tail:
        return "\n".join(lines[-tail:])
    return "\n".join(lines)


def fetch_knowledge(sources: List[str], token: Optional[str] = None) -> List[Dict[str, str]]:
    """Fetch knowledge base content from URLs or local files.

    Supports:
      - HTTP(S) URLs (GitLab blob URLs are auto-converted to raw)
      - Local file paths (absolute or relative to knowledge/ folder)
    """
    script_dir = Path(__file__).resolve().parent.parent
    knowledge_dir = script_dir / "knowledge"
    results: List[Dict[str, str]] = []

    for source in sources:
        try:
            if source.startswith(("http://", "https://")):
                # Convert GitLab blob URLs to raw so we get plain text
                url = source.replace("/-/blob/", "/-/raw/")
                headers = {"PRIVATE-TOKEN": token} if token else {}
                resp = requests.get(url, headers=headers)
                resp.raise_for_status()
                results.append({"source": source, "content": resp.text})
            else:
                # Local file: try as-is first, then under knowledge/ folder
                path = Path(source)
                if not path.is_absolute() and not path.exists():
                    path = knowledge_dir / source
                results.append({
                    "source": str(path),
                    "content": path.read_text(encoding="utf-8"),
                })
        except Exception as e:
            results.append({"source": source, "content": f"(failed to load: {e})"})

    return results


def _extract_error_lines(log: str) -> List[str]:
    """Pull lines from a job log that look like error/failure messages."""
    markers = ["error", "fatal", "denied", "exception", "failed", "panic", "traceback"]
    errors = []
    for line in log.splitlines():
        stripped = line.strip()
        if not stripped or len(stripped) < 10:
            continue
        lower = stripped.lower()
        if any(m in lower for m in markers):
            clean = re.sub(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}\S*", "", stripped)
            clean = re.sub(r"^\s*\S+\s*-\s*\S+\s*-\s*(ERROR|FATAL|WARNING)\s*-\s*", "", clean)
            clean = clean.strip()
            if len(clean) > 10:
                errors.append(clean)
    return errors


# Words too common to be meaningful for relevance matching
_STOP_WORDS = frozenset({
    "the", "and", "for", "are", "but", "not", "you", "all", "can", "had",
    "her", "was", "one", "our", "out", "has", "have", "from", "that", "this",
    "with", "been", "will", "would", "could", "should", "does", "done", "into",
    "than", "them", "then", "what", "when", "where", "which", "while", "about",
    "each", "make", "like", "just", "over", "such", "take", "also", "some",
    "file", "line", "code", "exit", "info", "none", "true", "false", "null",
    "section", "start", "step", "script", "stage",
})


def _extract_technical_terms(text: str) -> set:
    """Extract technical identifiers from text.

    Captures: file paths, module.paths, snake_case, camelCase, class names,
    function/method names, and other identifiers likely to be project-specific.
    """
    terms: set = set()

    # File paths (e.g., python/git_operations.py, src/utils.ts)
    for m in re.finditer(r'[\w./-]+\.\w{1,4}', text):
        terms.add(m.group().lower())

    # Dotted module paths (e.g., requests.exceptions.HTTPError)
    for m in re.finditer(r'\b\w+(?:\.\w+){1,}', text):
        terms.add(m.group().lower())

    # snake_case identifiers (e.g., git_operations, update_base_images)
    for m in re.finditer(r'\b[a-z]\w*_\w+', text, re.IGNORECASE):
        terms.add(m.group().lower())

    # CamelCase / PascalCase identifiers (e.g., HTTPError, DockerImage)
    for m in re.finditer(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b', text):
        terms.add(m.group().lower())

    # Remaining words (4+ chars, not stop words)
    for m in re.finditer(r'\b[a-zA-Z]{4,}\b', text):
        word = m.group().lower()
        if word not in _STOP_WORDS:
            terms.add(word)

    return terms


def analyze_root_cause(
    failed_jobs: List[Dict[str, Any]],
    job_logs: Dict[int, str],
    knowledge: List[Dict[str, str]],
) -> List[Dict[str, Any]]:
    """Measure how relevant the knowledge base is to each failure.

    The confidence % answers: 'How likely is this failure related to /
    caused by the code or content described in the knowledge base?'

    It works by extracting technical terms (file names, identifiers,
    module paths, etc.) from both the job log and the KB, then measuring
    the overlap.
    """
    if not knowledge:
        return []

    # Build KB technical term set
    kb_text = "\n".join(k["content"] for k in knowledge if not k["content"].startswith("("))
    kb_terms = _extract_technical_terms(kb_text)

    analyses: List[Dict[str, Any]] = []

    for job in failed_jobs:
        log = job_logs.get(job["id"], "")
        error_lines = _extract_error_lines(log)

        # Extract terms from the full log (not just error lines) for broader relevance
        log_terms = _extract_technical_terms(log)

        if not log_terms:
            analyses.append({
                "job": job,
                "error_lines": error_lines,
                "relevance": 0,
                "matched_terms": [],
                "kb_excerpts": [],
            })
            continue

        matched = sorted(log_terms & kb_terms)
        relevance = int((len(matched) / len(log_terms)) * 100)
        relevance = min(relevance, 95)  # cap at 95%

        # Find short KB excerpts for the most specific matched terms (longest first)
        kb_lower = kb_text.lower()
        kb_excerpts: List[str] = []
        for term in sorted(matched, key=len, reverse=True)[:5]:
            idx = kb_lower.find(term)
            if idx != -1:
                start = max(0, idx - 30)
                end = min(len(kb_text), idx + len(term) + 30)
                excerpt = kb_text[start:end].replace("\n", " ").strip()
                if start > 0:
                    excerpt = "..." + excerpt
                if end < len(kb_text):
                    excerpt = excerpt + "..."
                kb_excerpts.append(excerpt)

        analyses.append({
            "job": job,
            "error_lines": error_lines,
            "relevance": relevance,
            "matched_terms": matched[:15],
            "kb_excerpts": kb_excerpts,
        })

    return analyses


def fetch_pipeline(gitlab_url: str, project_id: str, pipeline_id: Optional[str], token: Optional[str]) -> Dict[str, Any]:
    """Fetch pipeline data from GitLab API."""
    from urllib.parse import quote
    # URL-encode project path (e.g., "root/my-project" -> "root%2Fmy-project")
    project_id = quote(project_id, safe='')
    base_url = f"{gitlab_url}/api/v4"
    headers = {}

    if token:
        headers["PRIVATE-TOKEN"] = token

    # If no pipeline_id specified, get the latest pipeline
    if not pipeline_id:
        url = f"{base_url}/projects/{project_id}/pipelines?per_page=1"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        pipelines = response.json()

        if not pipelines:
            raise ValueError("No pipelines found for this project")

        pipeline_id = pipelines[0]["id"]

    # Fetch pipeline details
    url = f"{base_url}/projects/{project_id}/pipelines/{pipeline_id}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    pipeline = response.json()

    # Fetch pipeline jobs
    jobs_url = f"{base_url}/projects/{project_id}/pipelines/{pipeline_id}/jobs"
    jobs_response = requests.get(jobs_url, headers=headers)
    jobs_response.raise_for_status()
    jobs = jobs_response.json()

    return {"pipeline": pipeline, "jobs": jobs}


def summarize_pipeline(
    data: Dict[str, Any],
    job_logs: Optional[Dict[int, str]] = None,
    knowledge: Optional[List[Dict[str, str]]] = None,
    root_cause: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """Generate a summary of the pipeline status, optionally including failed job logs and root cause analysis."""
    pipeline = data["pipeline"]
    jobs = data["jobs"]

    # Extract key info
    pipeline_id = pipeline["id"]
    status = pipeline["status"]
    ref = pipeline.get("ref", "N/A")
    created_at = pipeline.get("created_at", "N/A")
    duration = pipeline.get("duration")
    web_url = pipeline.get("web_url", "N/A")

    # Count job statuses
    job_statuses: Dict[str, int] = {}
    failed_jobs: List[Dict[str, Any]] = []

    for job in jobs:
        job_status = job["status"]
        job_statuses[job_status] = job_statuses.get(job_status, 0) + 1

        if job_status == "failed":
            failed_jobs.append({
                "id": job["id"],
                "name": job["name"],
                "stage": job["stage"],
            })

    # Build summary
    summary = []
    summary.append("=" * 60)
    summary.append("🔍 GITLAB PIPELINE STATUS SUMMARY")
    summary.append("=" * 60)
    summary.append("")
    summary.append(f"Pipeline ID:  {pipeline_id}")
    summary.append(f"Status:       {get_status_emoji(status)} {status.upper()}")
    summary.append(f"Branch/Tag:   {ref}")
    summary.append(f"Duration:     {format_duration(duration)}")
    summary.append(f"Created:      {created_at}")
    summary.append(f"URL:          {web_url}")
    summary.append("")

    # Job breakdown
    summary.append("📊 JOB BREAKDOWN:")
    summary.append("-" * 60)
    for job_status, count in sorted(job_statuses.items()):
        emoji = get_status_emoji(job_status)
        summary.append(f"  {emoji} {job_status.capitalize()}: {count} job(s)")
    summary.append("")

    # Failed jobs details
    if failed_jobs:
        summary.append("❌ FAILED JOBS:")
        summary.append("-" * 60)
        for job in failed_jobs:
            summary.append(f"  • {job['name']} (stage: {job['stage']})")
        summary.append("")

    # Failed job logs
    if job_logs and failed_jobs:
        summary.append("📋 FAILED JOB LOGS:")
        summary.append("=" * 60)
        for job in failed_jobs:
            job_id = job["id"]
            log = job_logs.get(job_id)
            if log is None:
                continue
            summary.append(f"\n--- {job['name']} (job #{job_id}) ---")
            summary.append(log)
            summary.append("")

    # Knowledge sources
    if knowledge:
        summary.append("📚 KNOWLEDGE BASE:")
        summary.append("-" * 60)
        for kb in knowledge:
            if kb["content"].startswith("(failed"):
                summary.append(f"  ⚠️  {kb['source']} — {kb['content']}")
            else:
                preview = kb["content"][:120].replace("\n", " ").strip()
                summary.append(f"  📄 {kb['source']}")
                summary.append(f"     {preview}...")
        summary.append("")

    # Root cause analysis
    if root_cause and failed_jobs:
        summary.append("🔬 ROOT CAUSE ANALYSIS:")
        summary.append("=" * 60)
        for analysis in root_cause:
            job = analysis["job"]
            relevance = analysis["relevance"]
            error_lines = analysis["error_lines"]
            matched = analysis["matched_terms"]
            excerpts = analysis["kb_excerpts"]

            summary.append(f"\n  Job: {job['name']} (#{job['id']})")

            if error_lines:
                summary.append(f"  Error: {error_lines[0][:120]}")

            bar = "█" * (relevance // 5) + "░" * (20 - relevance // 5)
            summary.append(f"  KB relevance:  [{bar}] {relevance}%")

            if matched:
                summary.append(f"  Matched terms: {', '.join(matched[:8])}")
            if excerpts:
                summary.append(f"  KB excerpt:    {excerpts[0][:150]}")

            if relevance == 0:
                summary.append("  → Failure likely NOT related to knowledge base content")
            elif relevance < 30:
                summary.append("  → Low relevance — failure may be environmental / config")
            elif relevance < 60:
                summary.append("  → Moderate relevance — failure may involve KB content")
            else:
                summary.append("  → High relevance — failure likely related to KB content")
        summary.append("")

    # Verdict
    summary.append("🎯 VERDICT:")
    summary.append("-" * 60)
    summary.append(f"  {get_verdict(status, len(failed_jobs))}")
    summary.append("")
    summary.append("=" * 60)

    return "\n".join(summary)


def main():
    parser = argparse.ArgumentParser(
        description="Check GitLab pipeline status and generate summary",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check via direct pipeline or job URL
  python check_pipeline.py --link http://gitlab.example.com/group/project/-/pipelines/283
  python check_pipeline.py --link http://gitlab.example.com/group/project/-/jobs/794

  # With knowledge base for root cause analysis
  python check_pipeline.py --link http://gitlab.example.com/group/project/-/pipelines/283 \\
    --knowledge http://gitlab.example.com/group/project/-/blob/main/README.md \\
    --knowledge runbook.md

  # Check latest pipeline for a project on gitlab.com
  python check_pipeline.py --project 278964

  # Check specific pipeline
  python check_pipeline.py --project 278964 --pipeline 123456789

  # Use self-hosted GitLab instance with authentication
  python check_pipeline.py --url https://gitlab.example.com --project 42 --token YOUR_TOKEN
        """
    )

    parser.add_argument(
        "--link",
        help="Direct GitLab pipeline or job URL (e.g., https://gitlab.com/group/project/-/pipelines/123)"
    )

    parser.add_argument(
        "--url",
        default="https://gitlab.com",
        help="GitLab instance URL (default: https://gitlab.com)"
    )

    parser.add_argument(
        "--project",
        help="Project ID or path (e.g., '278964' or 'group/project')"
    )

    parser.add_argument(
        "--pipeline",
        help="Pipeline ID (if not specified, fetches the latest pipeline)"
    )

    parser.add_argument(
        "--token",
        help="GitLab API token (required for private projects)"
    )

    parser.add_argument(
        "--tail",
        type=int,
        default=50,
        help="Number of log lines to show per failed job (default: 50, 0=full log)"
    )

    parser.add_argument(
        "--knowledge",
        nargs="*",
        default=[],
        help="Knowledge base sources: URLs or local file paths (e.g., "
             "http://gitlab.example.com/group/project/-/blob/main/README.md "
             "or knowledge/runbook.md)"
    )

    args = parser.parse_args()

    if not args.link and not args.project:
        parser.error("either --link or --project is required")

    try:
        # Resolve --link into url/project/pipeline if provided
        if args.link:
            parsed = parse_gitlab_link(args.link)
            gitlab_url = parsed["gitlab_url"]
            project = parsed["project"]
            if parsed["type"] == "jobs":
                print(f"🔍 Resolving job {parsed['id']} to its pipeline...")
                pipeline_id = resolve_job_to_pipeline(
                    gitlab_url, project, parsed["id"], args.token
                )
            else:
                pipeline_id = parsed["id"]
        else:
            gitlab_url = args.url
            project = args.project
            pipeline_id = args.pipeline

        print(f"🔍 Fetching pipeline data from {gitlab_url}...")
        print()

        data = fetch_pipeline(gitlab_url, project, pipeline_id, args.token)

        # Fetch logs for failed jobs
        job_logs: Dict[int, str] = {}
        failed = [j for j in data["jobs"] if j["status"] == "failed"]
        if failed:
            print(f"📋 Fetching logs for {len(failed)} failed job(s)...")
            print()
            for job in failed:
                try:
                    log = fetch_job_trace(gitlab_url, project, job["id"], args.token, tail=args.tail)
                    job_logs[job["id"]] = log
                except Exception as log_err:
                    job_logs[job["id"]] = f"(could not fetch log: {log_err})"

        # Fetch knowledge base if provided
        kb_data: List[Dict[str, str]] = []
        rca: List[Dict[str, Any]] = []
        if args.knowledge:
            print(f"📚 Loading {len(args.knowledge)} knowledge source(s)...")
            kb_data = fetch_knowledge(args.knowledge, token=args.token)
            if failed and job_logs:
                failed_info = [
                    {"id": j["id"], "name": j["name"], "stage": j["stage"]}
                    for j in failed
                ]
                rca = analyze_root_cause(failed_info, job_logs, kb_data)
            print()

        summary = summarize_pipeline(
            data, job_logs=job_logs, knowledge=kb_data or None, root_cause=rca or None,
        )
        print(summary)
        
        # Exit code based on status
        status = data["pipeline"]["status"]
        if status == "success":
            sys.exit(0)
        elif status in ["failed", "canceled"]:
            sys.exit(1)
        else:
            sys.exit(2)  # Running/pending/other
            
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}", file=sys.stderr)
        if e.response.status_code == 401:
            print("💡 Hint: You may need to provide a GitLab API token with --token", file=sys.stderr)
        elif e.response.status_code == 404:
            print("💡 Hint: Check that the project ID and pipeline ID are correct", file=sys.stderr)
        sys.exit(3)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
