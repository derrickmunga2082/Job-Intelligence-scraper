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

    MAX_JOB_AGE_DAYS,

    MINIMUM_JOB_SCORE,

    KENYA_SCORE,

    NGO_SCORE,

    SENIORITY_SCORE,

    EXPERIENCE_SCORE,

    EAST_AFRICA_SCORE

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

    procurement_keywords = [

        "procurement",

        "purchasing",

        "strategic sourcing",

        "sourcing",

        "buyer",

        "supplier",

        "supplier management",

        "vendor management",

        "vendor",

        "contract procurement"

    ]

    return any(

        keyword in text

        for keyword in procurement_keywords

    )


# ==========================================================
# CHECK LOGISTICS
# ==========================================================


def is_logistics_job(text):

    text = text.lower()

    logistics_keywords = [

        "logistics",

        "supply chain",

        "distribution",

        "transport",

        "warehouse",

        "inventory",

        "fleet",

        "shipping",

        "freight",

        "transportation",

        "materials management",

        "materials logistics"

    ]

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
    # KENYA PRIORITY
    # ======================================================

    if is_kenya_job(job):

        score += KENYA_SCORE


    # ======================================================
    # NGO PRIORITY
    # ======================================================

    if is_ngo_job(job):

        score += NGO_SCORE


    # ======================================================
    # EAST AFRICA
    # ======================================================

    elif is_east_africa_job(job):

        score += EAST_AFRICA_SCORE


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