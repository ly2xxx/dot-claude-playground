#!/usr/bin/env python3
"""
Job Description Scraper
Extracts job requirements from web pages (LinkedIn, Indeed, company career sites)

Usage:
    python job_scraper.py <URL>
    python job_scraper.py https://www.linkedin.com/jobs/view/12345

Returns JSON with:
    - job_title
    - company_name
    - required_skills
    - preferred_qualifications
    - job_description (full text)
    - keywords (extracted via NLP)
"""

import sys
import json
import re
from urllib.parse import urlparse
from typing import Dict, List, Optional

# Try to import optional dependencies
try:
    import requests
    from bs4 import BeautifulSoup
    SCRAPING_AVAILABLE = True
except ImportError:
    SCRAPING_AVAILABLE = False
    print("Warning: requests and beautifulsoup4 not installed", file=sys.stderr)
    print("Install with: pip install requests beautifulsoup4", file=sys.stderr)


def extract_keywords(text: str) -> List[str]:
    """
    Extract potential keywords from job description using simple heuristics.
    For production, consider using spaCy or similar NLP library.
    """
    # Common skill patterns
    skill_patterns = [
        # Programming languages
        r'\b(Python|Java|JavaScript|TypeScript|C\+\+|C#|Go|Rust|Ruby|PHP|Swift|Kotlin|R|MATLAB)\b',
        # Frameworks/Libraries
        r'\b(React|Angular|Vue|Django|Flask|FastAPI|Spring|Node\.?js|Express|jQuery)\b',
        # Databases
        r'\b(MySQL|PostgreSQL|MongoDB|Redis|Cassandra|Oracle|SQL Server|DynamoDB)\b',
        # Cloud/DevOps
        r'\b(AWS|Azure|GCP|Docker|Kubernetes|Terraform|Ansible|Jenkins|GitLab CI|CircleCI)\b',
        # Data Science/ML
        r'\b(TensorFlow|PyTorch|scikit-learn|Pandas|NumPy|Spark|Hadoop|Tableau|Power BI)\b',
        # Methodologies
        r'\b(Agile|Scrum|Kanban|DevOps|CI/CD|TDD|Microservices|REST|GraphQL)\b',
        # Soft skills
        r'\b(leadership|communication|collaboration|problem[\- ]solving|analytical|strategic)\b',
    ]
    
    keywords = set()
    for pattern in skill_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        keywords.update(match.lower() if isinstance(match, str) else match[0].lower() for match in matches)
    
    # Extract years of experience mentions
    exp_pattern = r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s+)?(?:experience|exp)?'
    exp_matches = re.findall(exp_pattern, text, re.IGNORECASE)
    if exp_matches:
        keywords.add(f"{max(map(int, exp_matches))}+ years experience")
    
    return sorted(list(keywords))


def extract_requirements(text: str) -> Dict[str, List[str]]:
    """
    Split job description into required vs preferred qualifications.
    """
    required = []
    preferred = []
    
    # Look for sections
    required_section = re.search(
        r'(?:required|qualifications|minimum qualifications|must have)[:\s]+(.*?)(?=\n\n|preferred|nice to have|$)',
        text,
        re.IGNORECASE | re.DOTALL
    )
    
    preferred_section = re.search(
        r'(?:preferred|nice to have|bonus|plus)[:\s]+(.*?)(?=\n\n|$)',
        text,
        re.IGNORECASE | re.DOTALL
    )
    
    if required_section:
        # Extract bullet points or sentences
        req_text = required_section.group(1)
        required = [line.strip('• -–') for line in req_text.split('\n') if line.strip()]
    
    if preferred_section:
        pref_text = preferred_section.group(1)
        preferred = [line.strip('• -–') for line in pref_text.split('\n') if line.strip()]
    
    return {
        "required": [r for r in required if len(r) > 10],  # Filter out noise
        "preferred": [p for p in preferred if len(p) > 10]
    }


def scrape_generic_page(url: str) -> Dict:
    """
    Generic scraper for most job posting pages.
    Tries to extract common patterns.
    """
    if not SCRAPING_AVAILABLE:
        return {
            "error": "Scraping dependencies not installed",
            "url": url,
            "instructions": "pip install requests beautifulsoup4"
        }
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try to find job title
        job_title = None
        for selector in ['h1', '.job-title', '[class*="title"]', '[itemprop="title"]']:
            element = soup.select_one(selector)
            if element:
                job_title = element.get_text(strip=True)
                break
        
        # Try to find company name
        company_name = None
        for selector in ['.company-name', '[class*="company"]', '[itemprop="hiringOrganization"]']:
            element = soup.select_one(selector)
            if element:
                company_name = element.get_text(strip=True)
                break
        
        # Extract all text (job description)
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text(separator='\n')
        
        # Clean up text
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        job_description = '\n'.join(lines)
        
        # Extract requirements
        requirements = extract_requirements(job_description)
        
        # Extract keywords
        keywords = extract_keywords(job_description)
        
        return {
            "success": True,
            "url": url,
            "job_title": job_title or "Unknown Title",
            "company_name": company_name or "Unknown Company",
            "job_description": job_description[:2000],  # Truncate to reasonable length
            "required_skills": requirements["required"],
            "preferred_qualifications": requirements["preferred"],
            "keywords": keywords,
            "extraction_method": "generic_scraper"
        }
    
    except requests.RequestException as e:
        return {
            "success": False,
            "error": f"Failed to fetch URL: {str(e)}",
            "url": url
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Scraping error: {str(e)}",
            "url": url
        }


def scrape_linkedin(url: str) -> Dict:
    """
    LinkedIn-specific scraper.
    Note: LinkedIn has anti-scraping measures. This is a basic implementation.
    For production, consider LinkedIn API or manual copy-paste.
    """
    return {
        "success": False,
        "url": url,
        "error": "LinkedIn scraping requires authentication",
        "recommendation": "Please copy and paste the job description directly instead of providing URL"
    }


def scrape_indeed(url: str) -> Dict:
    """Indeed-specific scraper."""
    # Indeed is more scraper-friendly than LinkedIn
    return scrape_generic_page(url)


def scrape_job_posting(url: str) -> Dict:
    """
    Main entry point. Routes to appropriate scraper based on URL.
    """
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    
    if 'linkedin.com' in domain:
        return scrape_linkedin(url)
    elif 'indeed.com' in domain:
        return scrape_indeed(url)
    else:
        # Try generic scraper
        return scrape_generic_page(url)


def main():
    if len(sys.argv) < 2:
        print("Usage: python job_scraper.py <URL>", file=sys.stderr)
        print("Example: python job_scraper.py https://example.com/careers/senior-engineer", file=sys.stderr)
        sys.exit(1)
    
    url = sys.argv[1]
    
    # Validate URL
    if not url.startswith(('http://', 'https://')):
        print(f"Error: Invalid URL. Must start with http:// or https://", file=sys.stderr)
        sys.exit(1)
    
    result = scrape_job_posting(url)
    
    # Pretty print JSON
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Exit with error code if scraping failed
    if not result.get("success", False):
        sys.exit(1)


if __name__ == "__main__":
    main()
