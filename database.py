# ==========================================================
# JOB INTELLIGENCE SCRAPER
# DATABASE ENGINE
# ==========================================================


import sqlite3

from datetime import datetime


from config import DATABASE_PATH





# ==========================================================
# DATABASE CONNECTION
# ==========================================================


def get_connection():


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


                str(job.get("published_date")),


                str(job.get("expiry_date")),


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