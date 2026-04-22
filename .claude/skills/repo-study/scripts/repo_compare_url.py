#!/usr/bin/env python3
"""
Generate revision comparison URLs for GitHub and GitLab repositories.

Given a repo URL, this script helps figure out the URL for comparing two revisions/commits/branches.

Usage:
    python repo_compare_url.py <repo_url> [--base <base_ref>] [--head <head_ref>]
    
Examples:
    python repo_compare_url.py https://github.com/ly2xxx/DevOps-labs.git
    python repo_compare_url.py https://github.com/ly2xxx/DevOps-labs.git --base main --head feature-branch
    python repo_compare_url.py https://gitlab.com/some-group/some-repo.git --base v1.0.0 --head v2.0.0
"""

import argparse
import re
import sys
from urllib.parse import urlparse


def detect_provider(repo_url: str) -> str:
    """Detect if the repo is GitHub, GitLab, or unsupported."""
    parsed = urlparse(repo_url)
    host = parsed.netloc.lower()
    
    if "github.com" in host or "github" in host:
        return "github"
    elif "gitlab.com" in host or "gitlab" in host:
        return "gitlab"
    else:
        # Check for self-hosted GitLab
        if "gitlab" in host:
            return "gitlab"
        return "unknown"


def extract_repo_info(repo_url: str, provider: str) -> dict:
    """Extract owner and repo name from the URL."""
    parsed = urlparse(repo_url)
    path = parsed.path.strip("/")
    
    # Remove .git suffix if present
    if path.endswith(".git"):
        path = path[:-4]
    
    parts = path.split("/")
    
    if len(parts) >= 2:
        owner = parts[0]
        repo = parts[1]
        return {"owner": owner, "repo": repo}
    else:
        raise ValueError(f"Could not extract owner/repo from URL: {repo_url}")


def generate_github_compare_url(repo_info: dict, base: str = None, head: str = None) -> str:
    """Generate GitHub comparison URL."""
    owner = repo_info["owner"]
    repo = repo_info["repo"]
    
    if base and head:
        # Compare two refs
        comparison = f"{base}...{head}"
    elif base:
        # Compare base to default branch
        comparison = f"{base}..."
    elif head:
        # Compare default branch to head
        comparison = f"...{head}"
    else:
        # Just show compare page
        return f"https://github.com/{owner}/{repo}/compare"
    
    return f"https://github.com/{owner}/{repo}/compare/{comparison}"


def generate_gitlab_compare_url(repo_info: dict, base: str = None, head: str = None) -> str:
    """Generate GitLab comparison URL."""
    owner = repo_info["owner"]
    repo = repo_info["repo"]
    
    if base and head:
        # Compare two refs
        return f"https://gitlab.com/{owner}/{repo}/-/compare/{base}...{head}"
    elif base:
        # Compare base to default branch
        return f"https://gitlab.com/{owner}/{repo}/-/compare/{base}..."
    elif head:
        # Compare default branch to head
        return f"https://gitlab.com/{owner}/{repo}/-/compare/...{head}"
    else:
        # Just show compare page
        return f"https://gitlab.com/{owner}/{repo}/-/compare"


def main():
    parser = argparse.ArgumentParser(
        description="Generate revision comparison URLs for GitHub and GitLab repos"
    )
    parser.add_argument("repo_url", help="Repository URL (e.g., https://github.com/owner/repo.git)")
    parser.add_argument("--base", "-b", help="Base revision/branch/tag (e.g., main, v1.0.0)")
    parser.add_argument("--head", help="Head revision/branch/tag (e.g., feature-branch, v2.0.0)")
    parser.add_argument("--print", "-p", action="store_true", help="Print just the URL (no explanations)")
    
    args = parser.parse_args()
    
    try:
        # Detect provider
        provider = detect_provider(args.repo_url)
        
        if provider == "unknown":
            print(f"Error: Unsupported repository provider. Only GitHub and GitLab are supported.")
            sys.exit(1)
        
        # Extract repo info
        repo_info = extract_repo_info(args.repo_url, provider)
        
        # Generate comparison URL
        if provider == "github":
            url = generate_github_compare_url(repo_info, args.base, args.head)
        elif provider == "gitlab":
            url = generate_gitlab_compare_url(repo_info, args.base, args.head)
        else:
            url = None
        
        if args.print:
            print(url)
        else:
            print(f"\nRepository: {repo_info['owner']}/{repo_info['repo']}")
            print(f"Provider: {provider.capitalize()}")
            print(f"\nComparison URL:")
            print(f"  {url}")
            
            if args.base and args.head:
                print(f"\nThis compares {args.base} to {args.head}")
            elif args.base:
                print(f"\nThis compares {args.base} against default branch")
            elif args.head:
                print(f"\nThis compares default branch to {args.head}")
            else:
                print(f"\nThis is the general compare page - you can select revisions interactively")
        
        return url
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
