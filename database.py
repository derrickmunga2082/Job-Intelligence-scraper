# ==========================================================
# JOB INTELLIGENCE SCRAPER
# DATABASE ENGINE
# ==========================================================


import os

import sqlite3

from datetime import datetime, timedelta


from config import DATABASE_PATH, MAX_JOB_AGE_DAYS


def _serialize_date(value):

    # save_job() used to do str(job.get("published_date")) unconditionally,
    # which turned a real None into the literal 4-character string "None"
    # instead of a SQL NULL - that broke any later query (like the purge
    # below) that compares published_date against a cutoff date, since
    # "None" sorts as a string, not as "no date". date objects get their
    # clean ISO form (YYYY-MM-DD) so date comparisons/sorts work correctly.
    if value is None:
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)





# ==========================================================
# DATABASE CONNECTION
# ==========================================================


def get_connection():

    # DATABASE_PATH is "database/jobs.db" but the "database" folder is
    # never committed to git (it's runtime-generated), so on a fresh
    # clone sqlite3.connect() fails with "unable to open database file"
    # before a single job can be scraped. Make sure the folder exists
    # first.
    db_dir = os.path.dirname(DATABASE_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    return sqlite3.connect(

        DATABASE_PATH

    )






# ==========================================================
# CREATE DATABASE
# ==========================================================


def create_database():


    connection = get_connection()


    cursor = connection.cursor()



    cursor.execute(

        """

        CREATE TABLE IF NOT EXISTS jobs (

            id INTEGER PRIMARY KEY AUTOINCREMENT,


            title TEXT,


            company TEXT,


            category TEXT,


            source TEXT,


            url TEXT UNIQUE,


            location TEXT,


            country TEXT,


            description TEXT,


            requirements TEXT,


            employment_type TEXT,


            salary TEXT,


            published_date TEXT,


            expiry_date TEXT,


            status TEXT,


            date_added TEXT,


            last_updated TEXT


        )

        """

    )



    connection.commit()


    connection.close()







# ==========================================================
# SAVE JOB
# ==========================================================


def save_job(job):


    connection = get_connection()


    cursor = connection.cursor()



    try:



        cursor.execute(

            """

            INSERT INTO jobs (

                title,

                company,

                category,

                source,

                url,

                location,

                country,

                description,

                requirements,

                employment_type,

                salary,

                published_date,

                expiry_date,

                status,

                date_added,

                last_updated


            )


            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)

            """,



            (

                job.get("title"),


                job.get("company"),


                job.get("category"),


                job.get("source"),


                job.get("url"),


                job.get("location"),


                job.get("country"),


                job.get("description"),


                job.get("requirements"),


                job.get("employment_type"),


                job.get("salary"),


                _serialize_date(job.get("published_date")),


                _serialize_date(job.get("expiry_date")),


                "Active",


                datetime.now().strftime(

                    "%Y-%m-%d"

                ),


                datetime.now().strftime(

                    "%Y-%m-%d"

                )

            )

        )



        connection.commit()



        print(

            "Saved:",

            job.get("title")

        )



    except sqlite3.IntegrityError:



        print(

            "Duplicate skipped:",

            job.get("title")

        )



    finally:



        connection.close()







# ==========================================================
# PURGE STALE JOBS
# ==========================================================
#
# exporter.py dumps the whole "jobs" table on every run, and save_job()
# never removes anything - so once a job passed validate_job() on some
# earlier, looser version of the filtering rules (or just aged past
# MAX_JOB_AGE_DAYS since it was posted), it stayed in the export forever.
# Call this once per run (main.py does, right after create_database())
# so exports only ever reflect jobs that are still fresh under today's
# rules, not an accumulating pile of history.


def purge_stale_jobs():

    connection = get_connection()

    cursor = connection.cursor()

    cutoff = (

        datetime.today().date()
        - timedelta(days=MAX_JOB_AGE_DAYS)

    ).isoformat()

    cursor.execute(

        """

        DELETE FROM jobs

        WHERE

            (published_date IS NOT NULL AND published_date < ?)

            OR

            (published_date IS NULL AND date_added < ?)

        """,

        (cutoff, cutoff)

    )

    deleted = cursor.rowcount

    connection.commit()

    connection.close()

    if deleted:

        print(

            "Purged",
            deleted,
            "stale job(s) older than",
            MAX_JOB_AGE_DAYS,
            "days"

        )

    return deleted


# ==========================================================
# COUNT JOBS
# ==========================================================


def count_jobs():


    connection = get_connection()


    cursor = connection.cursor()



    cursor.execute(

        "SELECT COUNT(*) FROM jobs"

    )



    result = cursor.fetchone()[0]



    connection.close()



    return result







# ==========================================================
# GET JOBS
# ==========================================================


def get_jobs():


    connection = get_connection()


    cursor = connection.cursor()



    cursor.execute(

        """

        SELECT *

        FROM jobs

        ORDER BY id DESC

        """

    )


    jobs = cursor.fetchall()


    connection.close()



    return jobs