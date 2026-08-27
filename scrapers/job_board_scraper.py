# ==========================================================
# JOB INTELLIGENCE SCRAPER
# JOB BOARD SCRAPER
# FINAL VERSION 2 - FIXED LISTING DETECTION
# ==========================================================
#
# BUG THIS FIXES ("pulls the wrong jobs"):
#
# The previous version scanned EVERY <a> tag on a job board's listing
# page and treated any link whose visible text happened to contain a
# procurement/logistics keyword as a real job posting. In practice this
# mostly matched category/browse widgets - e.g. "Procurement Jobs",
# "Supply Chain & Procurement 80" - not individual vacancies, and it
# then scraped the *category archive page* behind that link as if it
# were that one job's description (a page that actually lists dozens of
# unrelated roles at every seniority level). That mislabeling is why the
# scraper was surfacing "jobs" that didn't match the target profile at
# all: they usually weren't jobs, they were category pages.
#
# Verified directly against the live sites on 2026-08-27 (see chat):
#   - careerpointkenya.co.ke : real postings live inside <article> tags.
#                              The 3 "matches" the old code found were
#                              all sidebar category links (Procurement
#                              Jobs / Logistics Jobs / Supply Chain Jobs).
#   - myjobmag.co.ke         : real postings use href starting with
#                              /job/ and are titled "<Role> at <Company>".
#                              The old code found 1 real match out of 74
#                              actual listings on the page - everything
#                              else was missed because it was scanning
#                              raw link text sitewide instead of the
#                              actual listing links.
#   - brightermonday.co.ke   : real postings carry
#                              [data-cy="listing-title-link"]. The old
#                              code's 3 "matches" were category-browse
#                              links ending in a job count, e.g.
#                              "Shipping & Logistics 53".
#   - fuzu.com                : real postings' href contains /jobs/
#                              (plural). Their /job/<slug> (singular) is
#                              the industry/category filter - that's what
#                              the old code was matching instead.
#
# Fix: only look at links inside the verified listing structure for
# known sites. For any site not yet in SITE_SELECTORS, fall back to a
# more conservative scan that skips nav/menu/sidebar/footer regions and
# obvious category-widget text (e.g. a label ending in a bare job count)
# instead of trusting every link on the page.
# ==========================================================


import re

import time

import requests

from bs4 import BeautifulSoup

from urllib.parse import urljoin, urlparse

from cleaner import valid_job_title

from config import MAX_JOBS_PER_SOURCE, MAX_PAGES_PER_SOURCE, REQUEST_DELAY_SECONDS, REQUEST_TIMEOUT


# How a site's listing pages 2+ are addressed. Verified 2026-08-27:
#   "path"  -> https://site/jobs/page/2/  (WordPress-style archives)
#   "query" -> https://site/jobs?page=2
# fuzu.com is omitted - it 403s outright before pagination is even
# relevant (see get_page()'s header/retry handling below).
PAGINATION_STYLE = {
    "careerpointkenya.co.ke": "path",
    "jobwebkenya.com": "path",
    "corporatestaffing.co.ke": "path",
    "myjobmag.co.ke": "query",
    "brightermonday.co.ke": "query",
}


# Per-site CSS selector that targets ONLY the anchor tag of a real job
# posting on that site's listing page (not category links, not nav).
# Add new sites here once you've verified their listing markup the same
# way - inspect the live page and confirm the selector only grabs real
# postings, not category/browse widgets.
SITE_SELECTORS = {
    "careerpointkenya.co.ke": "article a[href]",
    "myjobmag.co.ke": "a[href^='/job/']",
    "brightermonday.co.ke": "a[data-cy='listing-title-link']",
    "fuzu.com": "a[href*='/jobs/']",
    # Verified 2026-08-27: postings live in <li class="job"> /
    # <li class="job-alt"> inside <ol class="jobs">. Each card also has a
    # same-href "Details" link and a Facebook share link, both scanned
    # too, but neither ever passes valid_job_title() so they're
    # harmless (and _looks_like_category_link/seen_urls dedup catch
    # anything else).
    "jobwebkenya.com": "li.job a[href], li.job-alt a[href]",
    # Verified 2026-08-27: postings live inside <article> tags, same as
    # careerpointkenya.co.ke, but each article also carries 2-3 taxonomy
    # badge links (e.g. "IT Jobs In Kenya", "Mid Level Jobs") under
    # /category/... - already caught by _looks_like_category_link().
    "corporatestaffing.co.ke": "article a[href]",
}


# Ancestor tag names / id-or-class hints that mean "this link lives in
# navigation, not in the job listings" - used only by the generic
# fallback for sites without a verified selector above.
NON_LISTING_ANCESTOR_HINTS = (
    "nav", "menu", "sidebar", "footer", "header", "breadcrumb",
    "widget", "category", "filter", "pagination",
)


class JobBoardScraper:

    def __init__(self, name, url):

        self.name = name
        self.url = url

        # "User-Agent": "Mozilla/5.0" alone is a strong bot fingerprint -
        # real browsers always send Accept/Accept-Language/etc alongside
        # it, and some sites (Fuzu returned a bare 403) reject requests
        # missing those. A fuller, realistic header set won't get past
        # a full Cloudflare JS challenge, but it clears simpler
        # UA-sniffing blocks.
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

    # ======================================================
    # GET PAGE
    # ======================================================

    def get_page(self, url, retries=1):

        last_error = None

        for attempt in range(retries + 1):

            try:
                # Throttle every request, not just retries - we're now
                # paging through multiple listing pages plus one request
                # per job detail page, so this matters more than before.
                time.sleep(REQUEST_DELAY_SECONDS)

                response = requests.get(
                    url,
                    headers=self.headers,
                    timeout=REQUEST_TIMEOUT
                )

                response.raise_for_status()

                return response.text

            except Exception as e:

                last_error = e

        print(self.name, "connection error:", last_error)

        return ""

    # ======================================================
    # PICK THE VERIFIED SELECTOR FOR THIS SITE, IF WE HAVE ONE
    # ======================================================

    def _site_selector(self):

        domain = urlparse(self.url).netloc.lower()

        for known_domain, selector in SITE_SELECTORS.items():
            if known_domain in domain:
                return selector

        return None

    # ======================================================
    # BUILD THE URL FOR A GIVEN LISTING PAGE NUMBER
    # ======================================================

    def _build_page_url(self, page_number):

        if page_number <= 1:
            return self.url

        domain = urlparse(self.url).netloc.lower()

        style = None
        for known_domain, known_style in PAGINATION_STYLE.items():
            if known_domain in domain:
                style = known_style
                break

        if style == "path":
            base = self.url if self.url.endswith("/") else self.url + "/"
            return f"{base}page/{page_number}/"

        if style == "query":
            separator = "&" if "?" in self.url else "?"
            return f"{self.url}{separator}page={page_number}"

        # Unknown pagination style (e.g. fuzu.com) - don't guess at a
        # URL format we haven't verified, just stick to page 1.
        return None

    # ======================================================
    # SPOT A CATEGORY/BROWSE LINK MASQUERADING AS A JOB TITLE
    # ======================================================

    def _looks_like_category_link(self, text, href):

        # Category widgets on these boards commonly show a job count
        # right after the category name, e.g. "Supply Chain & Procurement
        # 80" - a real job title never ends in a bare number like that.
        if re.search(r"\s\d+$", text):
            return True

        href_lower = (href or "").lower()
        if "/category/" in href_lower or "/tag/" in href_lower:
            return True

        return False

    def _in_non_listing_region(self, tag):

        for ancestor in tag.parents:
            name = getattr(ancestor, "name", None)
            if not name:
                continue
            if name in ("nav", "header", "footer"):
                return True
            id_and_class = " ".join(
                [ancestor.get("id") or ""] + (ancestor.get("class") or [])
            ).lower()
            if any(hint in id_and_class for hint in NON_LISTING_ANCESTOR_HINTS):
                return True

        return False

    # ======================================================
    # FIND JOB LINKS
    # ======================================================

    def extract_links(self, html):

        links = []
        seen_urls = set()

        soup = BeautifulSoup(html, "html.parser")

        selector = self._site_selector()

        if selector:
            candidates = soup.select(selector)
        else:
            # Unknown site: fall back to a conservative sitewide scan
            # that skips nav/menu/sidebar/footer regions instead of
            # trusting every link on the page.
            candidates = [
                a for a in soup.find_all("a", href=True)
                if not self._in_non_listing_region(a)
            ]

        for a in candidates:

            title = a.get_text(" ", strip=True)
            href = a.get("href")

            if not title or not href:
                continue

            if self._looks_like_category_link(title, href):
                continue

            if not valid_job_title(title):
                continue

            full_url = urljoin(self.url, href)

            if full_url in seen_urls:
                continue
            seen_urls.add(full_url)

            links.append({
                "title": title,
                "url": full_url,
            })

        return links

    # ======================================================
    # EXTRACT JOB DETAILS
    # ======================================================

    def extract_job_details(self, job_link):

        html = self.get_page(job_link["url"])

        soup = BeautifulSoup(html, "html.parser")

        description = soup.get_text(" ", strip=True)

        # The previous version set "company" to self.name (the job
        # board's own name, e.g. "MyJobMag Kenya") for every job, so
        # every posting looked like it was published by the job board
        # rather than the actual employer. Several boards (MyJobMag,
        # Fuzu) title postings as "<Role> at <Company>" - pull the real
        # employer out of that when present, and leave it blank (rather
        # than wrong) when it isn't.
        title = job_link["title"]
        company = ""

        match = re.search(r"\bat\s+(.+)$", title, re.IGNORECASE)
        if match:
            company = match.group(1).strip()
            title = title[:match.start()].strip()

        return {
            "title": title,
            "company": company,
            "url": job_link["url"],
            "description": description,
            "source": self.name,
        }

    # ======================================================
    # SCRAPE
    # ======================================================
    #
    # Previously only ever looked at page 1 of a site's listings - a
    # real ceiling on volume when e.g. jobwebkenya.com has 264 pages and
    # careerpointkenya.co.ke has 58. Now pages through up to
    # MAX_PAGES_PER_SOURCE pages (for sites with a verified pagination
    # style), stopping early once a page adds no new links (end of the
    # archive, or a site whose pagination isn't verified/doesn't apply).

    def scrape(self):

        jobs = []
        all_links = []
        seen_urls = set()

        print("Scanning job board:", self.name)

        for page_number in range(1, MAX_PAGES_PER_SOURCE + 1):

            page_url = self._build_page_url(page_number)

            if page_url is None:
                # No verified pagination style for this site - only
                # page 1 (self.url) was ever attempted, so stop here.
                break

            html = self.get_page(page_url)

            if not html:
                # Connection/HTTP failure - keep whatever earlier pages
                # already found instead of losing the whole source.
                break

            page_links = self.extract_links(html)

            new_links = [
                link for link in page_links
                if link["url"] not in seen_urls
            ]

            if not new_links and page_number > 1:
                # No new postings on this page - reached the end of the
                # archive (or a site that ignores unknown page numbers
                # and just re-serves page 1).
                break

            for link in new_links:
                seen_urls.add(link["url"])

            all_links.extend(new_links)

            if len(all_links) >= MAX_JOBS_PER_SOURCE:
                break

        print(len(all_links), "relevant job links found")

        for link in all_links[:MAX_JOBS_PER_SOURCE]:

            try:
                job = self.extract_job_details(link)
                jobs.append(job)

            except Exception:
                continue

        print(len(jobs), "jobs extracted from", self.name)

        return jobs
