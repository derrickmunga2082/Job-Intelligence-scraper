"""
Scratch verification script (not wired into any test runner).

Part 1 builds small synthetic HTML fixtures that mirror the REAL
structure of each job board, as confirmed by inspecting the live sites:

  - careerpointkenya.co.ke     : real postings inside <article> tags;
                                 category links live in a sidebar widget.
  - myjobmag.co.ke             : real postings are <a href="/job/...">,
                                 titled "<Role> at <Company>".
  - brightermonday.co.ke       : real postings carry
                                 data-cy="listing-title-link"; category
                                 links end in a bare job count.
  - fuzu.com                    : real postings' href contains /jobs/
                                 (plural); /job/<slug> (singular) is the
                                 category/industry filter.
  - jobwebkenya.com             : real postings inside <li class="job">
                                 / <li class="job-alt"> inside
                                 <ol class="jobs">. (verified 2026-08-27)
  - corporatestaffing.co.ke     : real postings inside <article> tags,
                                 each also carrying 2-3 /category/...
                                 taxonomy badge links. (verified 2026-08-27)

Each fixture includes: one real job that SHOULD match (procurement or
logistics), one real job that should NOT match (unrelated role), and the
site's actual category/nav junk that the old scraper was mistakenly
picking up.

Part 2 exercises cleaner.py's hard gates (Kenya-only, on-site/hybrid
only, blocked titles) directly.

Run with: python tests/manual_verify_job_board_scraper.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cleaner
from scrapers.job_board_scraper import JobBoardScraper


FIXTURES = {
    "https://www.careerpointkenya.co.ke/jobs/": """
    <html><body>
      <nav class="header-navigation"><ul class="menu">
        <li class="menu-item"><a href="/">Home</a></li>
      </ul></nav>
      <div class="sidebar widget">
        <nav class="wp-block-navigation"><ul>
          <li><a href="/category/procurement-jobs-in-kenya/">Procurement Jobs</a></li>
          <li><a href="/category/logistics-jobs-in-kenya/">Logistics Jobs</a></li>
        </ul></nav>
      </div>
      <article><a href="/job/sales-marketing-coordinator/">Sales & Marketing Coordinator Job Newton Educational Resources</a></article>
      <article><a href="/job/procurement-officer-amref/">Procurement Officer Job Amref Health Africa</a></article>
    </body></html>
    """,

    "https://www.myjobmag.co.ke/jobs": """
    <html><body>
      <nav><a href="/">Home</a><a href="/employers">Employers</a></nav>
      <div class="listings">
        <a href="/job/hr-assistant-team-plus-limited-1">HR Assistant at Team Plus Limited</a>
        <a href="/job/administrator-maintenance-and-transport-strathmore-university">Administrator, Maintenance and Transport at Strathmore University</a>
        <a href="/job/supply-chain-officer-save-the-children">Supply Chain Officer at Save the Children</a>
      </div>
    </body></html>
    """,

    "https://www.brightermonday.co.ke/jobs": """
    <html><body>
      <div data-cy="listing-cards-components">
        <a data-cy="listing-title-link" href="https://www.brightermonday.co.ke/listings/lead-baker-5p6jmp">LEAD BAKER</a>
        <a data-cy="listing-title-link" href="https://www.brightermonday.co.ke/listings/tendering-officer-aviation-9k2p">TENDERING OFFICER - AVIATION</a>
        <a data-cy="listing-title-link" href="https://www.brightermonday.co.ke/listings/logistics-coordinator-ngo-4x7q">Logistics Coordinator - NGO Programme</a>
      </div>
      <div class="filters"><a href="https://www.brightermonday.co.ke/jobs/supply-chain-procurement">Supply Chain & Procurement 80</a></div>
    </body></html>
    """,

    "https://www.fuzu.com/kenya/jobs": """
    <html><body>
      <div class="filters">
        <a href="https://www.fuzu.com/job/transportation-logistics-driving">Transportation, logistics, driving</a>
      </div>
      <div class="results">
        <a href="https://www.fuzu.com/kenya/jobs/sales-manager-techno-brain-limited">Sales Manager</a>
        <a href="https://www.fuzu.com/kenya/jobs/warehouse-supervisor-dhl-kenya">Warehouse Supervisor at DHL Kenya</a>
      </div>
    </body></html>
    """,

    "https://www.jobwebkenya.com/jobs/": """
    <html><body>
      <div class="filter-tabs">
        <a href="/job-type/full-time/">Full-Time</a>
        <a href="/job-type/internship/">Internship</a>
      </div>
      <ol class="jobs">
        <li class="job">
          <a href="/jobs/retail-sales-associate-st-john-ambulance/">Retail Sales Associate at St John Ambulance</a>
          <a href="/jobs/retail-sales-associate-st-john-ambulance/">Details</a>
          <a href="https://www.facebook.com/sharer.php?u=x">Facebook</a>
        </li>
        <li class="job-alt">
          <a href="/jobs/procurement-officer-danish-refugee-council/">Procurement Officer at Danish Refugee Council</a>
          <a href="/jobs/procurement-officer-danish-refugee-council/">Details</a>
          <a href="https://www.facebook.com/sharer.php?u=y">Facebook</a>
        </li>
      </ol>
    </body></html>
    """,

    "https://www.corporatestaffing.co.ke/jobs/": """
    <html><body>
      <article>
        <a href="/category/it-jobs-in-kenya/">IT Jobs In Kenya</a>
        <a href="/category/employment-type/full-time-jobs/">Full Time Jobs</a>
        <a href="/job/data-analyst-at-takataka-solutions/">Data Analyst at TakaTaka Solutions</a>
      </article>
      <article>
        <a href="/category/logistics-jobs-in-kenya/">Logistics Jobs In Kenya</a>
        <a href="/category/experience-level/mid-level-jobs/">Mid Level Jobs</a>
        <a href="/job/warehouse-manager-at-twiga-foods/">Warehouse Manager at Twiga Foods</a>
      </article>
    </body></html>
    """,
}

EXPECTED_MATCH_SUBSTRING = {
    "https://www.careerpointkenya.co.ke/jobs/": "Procurement Officer",
    "https://www.myjobmag.co.ke/jobs": "Supply Chain Officer",
    "https://www.brightermonday.co.ke/jobs": "Logistics Coordinator",
    "https://www.fuzu.com/kenya/jobs": "Warehouse Supervisor",
    "https://www.jobwebkenya.com/jobs/": "Procurement Officer",
    "https://www.corporatestaffing.co.ke/jobs/": "Warehouse Manager",
}


def run_job_board_fixtures():
    all_ok = True

    for url, html in FIXTURES.items():
        scraper = JobBoardScraper(name=url, url=url)
        links = scraper.extract_links(html)

        titles = [link["title"] for link in links]
        expected = EXPECTED_MATCH_SUBSTRING[url]

        found_expected = any(expected in t for t in titles)
        no_junk = not any(
            "Jobs" == t.split()[-1] or t.rstrip()[-1:].isdigit()
            for t in titles
        )

        status = "OK" if (found_expected and no_junk) else "FAIL"
        if status == "FAIL":
            all_ok = False

        print(f"[{status}] {url}")
        print(f"        matched titles: {titles}")
        print(f"        expected to find: {expected!r} -> {found_expected}")
        print(f"        no category/junk links leaked through -> {no_junk}")
        print()

    return all_ok


def _mk_job(title, description="", location="", country="", company="",
            employment_type="", url="https://example.com/job/1"):
    return {
        "title": title,
        "description": description,
        "location": location,
        "country": country,
        "company": company,
        "employment_type": employment_type,
        "url": url,
    }


CLEANER_CASES = [
    ("Kenya procurement job, on-site", True,
     _mk_job("Procurement Officer", "Based in our Nairobi office.",
             "Nairobi", "Kenya", "Save the Children")),
    ("Non-Kenya procurement job", False,
     _mk_job("Procurement Officer", "Based in Addis Ababa.",
             "Addis Ababa", "Ethiopia", "World Vision")),
    ("Kenya but fully remote", False,
     _mk_job("Logistics Coordinator",
             "This is a fully remote position, work from home.",
             "Remote", "Kenya", "Some NGO")),
    ("Kenya hybrid (remote mentioned but overridden)", True,
     _mk_job("Logistics Coordinator",
             "Hybrid role, 2 days remote per week, Nairobi HQ.",
             "Nairobi", "Kenya", "Some NGO")),
    ("Kenya, no work-mode text at all (default on-site)", True,
     _mk_job("Supply Chain Officer", "Manage supplier contracts.",
             "Nairobi", "Kenya", "Amref")),
    ("Engineering intern (blocked title)", False,
     _mk_job("Mechanical Engineering Intern - Field Operations", "",
             "Nairobi", "Kenya", "Some Co")),
    ("Unrelated role in Kenya (not procurement/logistics)", False,
     _mk_job("Marketing Manager", "", "Nairobi", "Kenya", "Some Co")),
    ("Tendering role in Kenya (verified real gap, now fixed)", True,
     _mk_job("Tendering Officer - Aviation", "", "Nairobi", "Kenya", "Some Co")),
]


def run_cleaner_gates():
    all_ok = True

    for label, expected_pass, job in CLEANER_CASES:
        cleaned = cleaner.clean_job(job)
        result = cleaner.validate_job(cleaned)

        status = "OK" if result == expected_pass else "FAIL"
        if status == "FAIL":
            all_ok = False

        print(f"[{status}] {label}: expected {'PASS' if expected_pass else 'REJECT'}, got {'PASS' if result else 'REJECT'}")

    return all_ok


def run():
    print("=== Job board listing-detection fixtures ===\n")
    job_board_ok = run_job_board_fixtures()

    print("\n=== cleaner.py hard-gate checks ===\n")
    cleaner_ok = run_cleaner_gates()

    all_ok = job_board_ok and cleaner_ok
    print("\n" + ("ALL OK" if all_ok else "SOME CHECKS FAILED"))
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(run())
