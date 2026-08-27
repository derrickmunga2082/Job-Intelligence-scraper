# ==========================================================
# JOB INTELLIGENCE SCRAPER
# CONFIGURATION FILE
# KENYA + NGO PRIORITY
# PROCUREMENT + LOGISTICS
# ==========================================================


# ==========================================================
# DATABASE SETTINGS
# ==========================================================

DATABASE_PATH = "database/jobs.db"


# ==========================================================
# SCRAPER SETTINGS
# ==========================================================

REQUEST_TIMEOUT = 15

REQUEST_DELAY_SECONDS = 0.5

MAX_JOBS_PER_SOURCE = 50

# Job board listing pages only used to be scraped one page deep, which
# was a real ceiling on volume - e.g. jobwebkenya.com has 264 pages of
# listings and careerpointkenya.co.ke has 58, but only page 1 was ever
# looked at. This lets job_board_scraper.py page through more of the
# archive per site (verified 2026-08-27 that all 5 job-board sources
# support either /jobs/page/N/ or ?page=N pagination).
MAX_PAGES_PER_SOURCE = 5


# ==========================================================
# TARGET JOB FUNCTIONS
# PROCUREMENT + LOGISTICS ONLY
# ==========================================================

TARGET_FUNCTIONS = {

    "Procurement": [

        "procurement",

        "purchasing",

        "strategic sourcing",

        "sourcing",

        "buyer",

        "supplier",

        "supplier management",

        "vendor management",

        "vendor",

        "contract management",

        "contract procurement",

        "tender",

        "tendering"

    ],


    "Logistics": [

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

}


# ==========================================================
# SENIORITY INDICATORS
# ==========================================================

SENIORITY_KEYWORDS = [

    "senior",

    "manager",

    "head",

    "director",

    "lead",

    "chief",

    "officer",

    "specialist",

    "coordinator",

    "strategic",

    "regional",

    "country",

    "principal"

]


# ==========================================================
# EXPERIENCE INDICATORS
# ==========================================================

EXPERIENCE_KEYWORDS = [

    "10 years",

    "10+ years",

    "11 years",

    "11+ years",

    "12 years",

    "12+ years",

    "13 years",

    "13+ years",

    "14 years",

    "14+ years",

    "15 years",

    "15+ years",

    "16 years",

    "16+ years",

    "17 years",

    "17+ years",

    "18 years",

    "18+ years",

    "19 years",

    "19+ years",

    "20 years",

    "20+ years",

    "8 years",

    "8+ years",

    "9 years",

    "9+ years",

    "extensive experience",

    "proven experience",

    "significant experience",

    "substantial experience",

    "relevant experience",

    "progressive experience",

    "professional experience"

]


# ==========================================================
# KENYA PRIORITY
# ==========================================================

KENYA_LOCATIONS = [

    "kenya",

    "nairobi",

    "mombasa",

    "kisumu",

    "nakuru",

    "eldoret",

    "thika",

    "malindi",

    "kilifi",

    "garissa",

    "kakamega",

    "machakos",

    "meru",

    "nyeri",

    "kiambu",

    "naivasha",

    "embu",

    "kitale",

    "lodwar",

    "turkana",

    "kwale",

    "lamu",

    "bungoma",

    "busia",

    "kericho",

    "nyeri",

    "narok",

    "isiolo",

    "wajir",

    "mandera"

]


# ==========================================================
# EAST AFRICA LOCATIONS
# KENYA HAS SEPARATE HIGHER PRIORITY
# ==========================================================

EAST_AFRICA_LOCATIONS = [

    "kenya",

    "uganda",

    "tanzania",

    "rwanda",

    "burundi",

    "ethiopia",

    "somalia",

    "south sudan",

    "drc",

    "democratic republic of congo"

]


# ==========================================================
# NGO / DEVELOPMENT ORGANIZATION INDICATORS
# ==========================================================

NGO_KEYWORDS = [

    "ngo",

    "non-governmental",

    "non governmental",

    "nonprofit",

    "non-profit",

    "humanitarian",

    "humanitarian organization",

    "humanitarian organisation",

    "development organization",

    "development organisation",

    "international development",

    "relief",

    "aid organization",

    "aid organisation",

    "charity",

    "foundation",

    "refugee",

    "human rights",

    "civil society",

    "international organization",

    "international organisation",

    "development agency",

    "development programme",

    "development program",

    "community development",

    "global development"

]


# ==========================================================
# WELL-KNOWN DEVELOPMENT / NGO ORGANIZATION INDICATORS
# ==========================================================

NGO_ORGANIZATION_KEYWORDS = [

    "unicef",

    "undp",

    "unhcr",

    "world food programme",

    "wfp",

    "world health organization",

    "who",

    "food and agriculture organization",

    "fao",

    "international rescue committee",

    "irc",

    "save the children",

    "care",

    "oxfam",

    "world vision",

    "mercy corps",

    "action against hunger",

    "international committee of the red cross",

    "icrc",

    "red cross",

    "amref",

    "amref health africa",

    "plan international",

    "norwegian refugee council",

    "nrc",

    "danish refugee council",

    "drc",

    "caritas",

    "world relief",

    "medecins sans frontieres",

    "doctors without borders",

    "usaid",

    "giz",

    "fhi 360",

    "clinton health access initiative",

    "path",

    "population services international",

    "psi",

    "world bank",

    "african development bank",

    "international labour organization",

    "ilo",

    "international labour organisation"

]


# ==========================================================
# BLOCKED JOB TYPES
# ==========================================================

BLOCKED_KEYWORDS = [

    "intern",

    "internship",

    "graduate trainee",

    "graduate program",

    "graduate programme",

    "trainee",

    "junior",

    "entry level",

    "entry-level",

    "entrylevel",

    "apprentice",

    "apprenticeship",

    "attachment",

    "industrial attachment",

    "engineering intern",

    "engineering internship",

    "technician",

    "research assistant",

    "volunteer"

]


# ==========================================================
# COMPLETELY UNRELATED TECHNICAL ROLES
# ==========================================================

BLOCKED_TECHNICAL_TITLES = [

    "mechanical engineer",

    "mechanical engineering",

    "civil engineer",

    "civil engineering",

    "electrical engineer",

    "electrical engineering",

    "software engineer",

    "software engineering",

    "network engineer",

    "network engineering",

    "chemical engineer",

    "chemical engineering",

    "structural engineer",

    "structural engineering",

    "technician",

    "developer",

    "software developer",

    "web developer"

]


# ==========================================================
# WORK ARRANGEMENT
# ONLY ON-SITE OR HYBRID - NO FULLY REMOTE ROLES
# ==========================================================
#
# A job is only rejected as "remote" when it contains one of the
# REMOTE_ONLY_KEYWORDS AND none of the ON_SITE_OVERRIDE_KEYWORDS.
# Postings that don't mention work arrangement at all are assumed
# on-site (the common case for Kenyan job boards) rather than requiring
# an explicit "on-site" label, which most real postings never bother to
# state. This also means "Hybrid (2 days remote)" style postings are
# correctly kept, since the override keyword outweighs the remote one.
# ==========================================================

REMOTE_ONLY_KEYWORDS = [

    "fully remote",

    "100% remote",

    "remote only",

    "remote-only",

    "remote position",

    "remote role",

    "remote job",

    "work from home",

    "work-from-home",

    "telecommute",

    "telecommuting",

    "virtual position",

    "virtual role",

    "work from anywhere",

    "home based",

    "home-based"

]

ON_SITE_OVERRIDE_KEYWORDS = [

    "hybrid",

    "on-site",

    "onsite",

    "on site",

    "in-office",

    "in office",

    "physical presence",

    "office based",

    "office-based"

]


# ==========================================================
# DATE FILTER
# ==========================================================

MAX_JOB_AGE_DAYS = 30


# ==========================================================
# MINIMUM SCORE
# ==========================================================

MINIMUM_JOB_SCORE = 40


# ==========================================================
# KENYA SCORE
# ==========================================================
#
# NOTE: Kenya location is now a hard requirement in
# calculate_job_score() (non-Kenya jobs are rejected outright), not just
# a bonus - a title-keyword match alone (50) already exceeded
# MINIMUM_JOB_SCORE (40), so leaving Kenya as a bonus meant non-Kenya
# jobs could still pass. KENYA_SCORE/EAST_AFRICA_SCORE below are kept
# in case a future version wants to rank Kenya jobs above other East
# African ones again, but neither is currently added to the score.

KENYA_SCORE = 30


# ==========================================================
# NGO SCORE
# ==========================================================

NGO_SCORE = 30


# ==========================================================
# SENIORITY SCORE
# ==========================================================

SENIORITY_SCORE = 10


# ==========================================================
# EXPERIENCE SCORE
# ==========================================================

EXPERIENCE_SCORE = 20


# ==========================================================
# EAST AFRICA SCORE
# ==========================================================

EAST_AFRICA_SCORE = 10


# ==========================================================
# EXPORT SETTINGS
# ==========================================================

EXPORT_FOLDER = "output"

EXCEL_FILE = "output/jobs.xlsx"

CSV_FILE = "output/jobs.csv"