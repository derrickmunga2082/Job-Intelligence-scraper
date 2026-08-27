# ==========================================================
# JOB INTELLIGENCE SCRAPER
# KENYA + NGO PRIORITY
# PROCUREMENT + LOGISTICS FILTER ENGINE
# ==========================================================


from datetime import datetime, timedelta


from config import (

    TARGET_FUNCTIONS,

    SENIORITY_KEYWORDS,

    EXPERIENCE_KEYWORDS,

    EAST_AFRICA_LOCATIONS,

    KENYA_LOCATIONS,

    NGO_KEYWORDS,

    NGO_ORGANIZATION_KEYWORDS,

    BLOCKED_KEYWORDS,

    BLOCKED_TECHNICAL_TITLES,

    REMOTE_ONLY_KEYWORDS,

    ON_SITE_OVERRIDE_KEYWORDS,

    MAX_JOB_AGE_DAYS,

    MINIMUM_JOB_SCORE,

    NGO_SCORE,

    SENIORITY_SCORE,

    EXPERIENCE_SCORE

)


# ==========================================================
# CLEAN TEXT
# ==========================================================


def clean_text(value):

    if not value:

        return ""

    return str(value).strip()


# ==========================================================
# DATE CHECK
# ==========================================================


def is_recent_job(date):

    if not date:

        return True

    today = datetime.today().date()

    cutoff = today - timedelta(

        days=MAX_JOB_AGE_DAYS

    )

    return date >= cutoff


# ==========================================================
# CATEGORY DETECTION
# ==========================================================


def detect_category(title):

    title = title.lower()

    for category, keywords in TARGET_FUNCTIONS.items():

        for keyword in keywords:

            if keyword in title:

                return category

    return "Other"


# ==========================================================
# CHECK PROCUREMENT
# ==========================================================


def is_procurement_job(text):

    text = text.lower()

    # Was previously a second, hand-maintained copy of this list that had
    # drifted out of sync with TARGET_FUNCTIONS["Procurement"] in
    # config.py (it was missing "contract management"), which meant
    # valid_job_title()/calculate_job_score() silently rejected some
    # jobs that config.py's own category list considered Procurement.
    # Reading straight from TARGET_FUNCTIONS keeps the two in sync by
    # construction.
    procurement_keywords = TARGET_FUNCTIONS["Procurement"]

    return any(

        keyword in text

        for keyword in procurement_keywords

    )


# ==========================================================
# CHECK LOGISTICS
# ==========================================================


def is_logistics_job(text):

    text = text.lower()

    # Same fix as is_procurement_job() above: read from TARGET_FUNCTIONS
    # instead of keeping a second hand-maintained copy of the list.
    logistics_keywords = TARGET_FUNCTIONS["Logistics"]

    return any(

        keyword in text

        for keyword in logistics_keywords

    )


# ==========================================================
# CHECK FOR BLOCKED TITLE
# ==========================================================


def has_blocked_title(title):

    title = title.lower()

    for word in BLOCKED_KEYWORDS:

        if word in title:

            return True

    for word in BLOCKED_TECHNICAL_TITLES:

        if word in title:

            return True

    return False


# ==========================================================
# TITLE FILTER
# USED BY JOB BOARD SCRAPER
# ==========================================================


def valid_job_title(title):

    if not title:

        return False

    title = title.lower()

    # ------------------------------------------------------
    # REMOVE INTERN / JUNIOR / TECHNICAL ROLES
    # ------------------------------------------------------

    if has_blocked_title(title):

        return False

    # ------------------------------------------------------
    # PROCUREMENT OR LOGISTICS ONLY
    # ------------------------------------------------------

    procurement = is_procurement_job(title)

    logistics = is_logistics_job(title)

    return procurement or logistics


# ==========================================================
# CHECK KENYA
# ==========================================================


def is_kenya_job(job):

    title = clean_text(

        job.get("title")

    ).lower()

    location = clean_text(

        job.get("location")

    ).lower()

    country = clean_text(

        job.get("country")

    ).lower()

    description = clean_text(

        job.get("description")

    ).lower()

    text = (

        title

        + " "

        + location

        + " "

        + country

        + " "

        + description

    )

    return any(

        place in text

        for place in KENYA_LOCATIONS

    )


# ==========================================================
# CHECK EAST AFRICA
# ==========================================================


def is_east_africa_job(job):

    title = clean_text(

        job.get("title")

    ).lower()

    location = clean_text(

        job.get("location")

    ).lower()

    country = clean_text(

        job.get("country")

    ).lower()

    description = clean_text(

        job.get("description")

    ).lower()

    text = (

        title

        + " "

        + location

        + " "

        + country

        + " "

        + description

    )

    return any(

        place in text

        for place in EAST_AFRICA_LOCATIONS

    )


# ==========================================================
# CHECK NGO
# ==========================================================


def is_ngo_job(job):

    title = clean_text(

        job.get("title")

    ).lower()

    company = clean_text(

        job.get("company")

    ).lower()

    description = clean_text(

        job.get("description")

    ).lower()

    text = (

        title

        + " "

        + company

        + " "

        + description

    )

    # ------------------------------------------------------
    # General NGO indicators
    # ------------------------------------------------------

    for keyword in NGO_KEYWORDS:

        if keyword in text:

            return True

    # ------------------------------------------------------
    # Known organizations
    # ------------------------------------------------------

    for keyword in NGO_ORGANIZATION_KEYWORDS:

        if keyword in text:

            return True

    return False


# ==========================================================
# CHECK REMOTE-ONLY (WE WANT ON-SITE OR HYBRID ONLY)
# ==========================================================


def is_remote_only_job(job):

    title = clean_text(

        job.get("title")

    ).lower()

    description = clean_text(

        job.get("description")

    ).lower()

    employment_type = clean_text(

        job.get("employment_type")

    ).lower()

    location = clean_text(

        job.get("location")

    ).lower()

    text = (

        title

        + " "

        + description

        + " "

        + employment_type

        + " "

        + location

    )

    # No remote signal at all -> assume on-site (the common case; most
    # real postings never bother to say "on-site" explicitly).
    has_remote_signal = any(

        keyword in text

        for keyword in REMOTE_ONLY_KEYWORDS

    )

    if not has_remote_signal:

        return False

    # A remote signal is present, but so is a hybrid/on-site one (e.g.
    # "Hybrid (2 days remote)") - that's not a remote-only posting.
    has_onsite_override = any(

        keyword in text

        for keyword in ON_SITE_OVERRIDE_KEYWORDS

    )

    return not has_onsite_override


# ==========================================================
# JOB SCORE
# ==========================================================


def calculate_job_score(job):

    title = clean_text(

        job.get("title")

    ).lower()

    company = clean_text(

        job.get("company")

    ).lower()

    description = clean_text(

        job.get("description")

    ).lower()

    location = clean_text(

        job.get("location")

    ).lower()

    country = clean_text(

        job.get("country")

    ).lower()

    text = (

        title

        + " "

        + company

        + " "

        + description

        + " "

        + location

        + " "

        + country

    )

    score = 0


    # ======================================================
    # HARD REJECTION
    # ======================================================

    if has_blocked_title(title):

        return -100


    # ======================================================
    # PROCUREMENT / LOGISTICS RELEVANCE
    # ======================================================

    if is_procurement_job(title):

        score += 50

    elif is_logistics_job(title):

        score += 50

    else:

        return -100


    # ======================================================
    # KENYA REQUIRED (HARD GATE)
    # ======================================================
    # Was a +KENYA_SCORE bonus only. Since a title-keyword match alone
    # (50) already exceeds MINIMUM_JOB_SCORE (40), a bonus never
    # actually stopped a non-Kenya job from passing - only a hard
    # rejection does.

    if not is_kenya_job(job):

        return -100


    # ======================================================
    # ON-SITE OR HYBRID REQUIRED (HARD GATE)
    # ======================================================

    if is_remote_only_job(job):

        return -100


    # ======================================================
    # NGO PRIORITY
    # ======================================================

    if is_ngo_job(job):

        score += NGO_SCORE


    # ======================================================
    # SENIORITY
    # ======================================================

    for keyword in SENIORITY_KEYWORDS:

        if keyword.lower() in text:

            score += SENIORITY_SCORE


    # ======================================================
    # EXPERIENCE
    # ======================================================

    for keyword in EXPERIENCE_KEYWORDS:

        if keyword.lower() in text:

            score += EXPERIENCE_SCORE


    return score


# ==========================================================
# CLEAN JOB
# ==========================================================


def clean_job(job):

    title = clean_text(

        job.get("title")

    )

    return {

        "title": title,

        "company":

        clean_text(

            job.get("company")

        ),

        "category":

        detect_category(

            title

        ),

        "source":

        clean_text(

            job.get("source")

        ),

        "url":

        clean_text(

            job.get("url")

        ),

        "location":

        clean_text(

            job.get("location")

        ),

        "country":

        clean_text(

            job.get("country")

        ),

        "description":

        clean_text(

            job.get("description")

        ),

        "requirements":

        clean_text(

            job.get("requirements")

        ),

        "employment_type":

        clean_text(

            job.get("employment_type")

        ),

        "salary":

        clean_text(

            job.get("salary")

        ),

        "published_date":

        job.get(

            "published_date"

        ),

        "expiry_date":

        job.get(

            "expiry_date"

        )

    }


# ==========================================================
# FINAL VALIDATION
# ==========================================================


def validate_job(job):

    title = job.get(

        "title"

    )

    if not title:

        return False


    if not job.get(

        "url"

    ):

        return False


    # ------------------------------------------------------
    # Procurement / Logistics only
    # ------------------------------------------------------

    if not valid_job_title(title):

        return False


    # ------------------------------------------------------
    # Date
    # ------------------------------------------------------

    if not is_recent_job(

        job.get(

            "published_date"

        )

    ):

        return False


    # ------------------------------------------------------
    # Calculate score
    # ------------------------------------------------------

    score = calculate_job_score(

        job

    )


    # ------------------------------------------------------
    # Display intelligence information
    # ------------------------------------------------------

    priority = "GENERAL"

    if is_kenya_job(job):

        priority = "KENYA"

    if is_ngo_job(job):

        priority += " + NGO"


    print(

        "Job Score:",

        score,

        "|",

        priority,

        "|",

        title

    )


    # ------------------------------------------------------
    # Final score
    # ------------------------------------------------------

    return score >= MINIMUM_JOB_SCORE