# ==========================================================
# JOB INTELLIGENCE SCRAPER
# BASE SCRAPER ENGINE
# ==========================================================


import requests

import time

from datetime import datetime

from config import (
    REQUEST_DELAY_SECONDS,
    REQUEST_TIMEOUT
)




class BaseScraper:



    """
    Parent class for all job scrapers.

    Every website scraper will extend this class.
    """



    def __init__(self, name, url):


        self.name = name

        self.url = url



        self.headers = {


            "User-Agent":

            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "Chrome/120 Safari/537.36"

        }




    # ======================================================
    # DOWNLOAD PAGE
    # ======================================================


    def fetch_page(self, url):


        try:


            response = requests.get(

                url,

                headers=self.headers,

                timeout=REQUEST_TIMEOUT

            )


            response.raise_for_status()



            time.sleep(

                REQUEST_DELAY_SECONDS

            )



            return response.text



        except Exception as e:


            print(

                f"{self.name} error:",

                e

            )


            return None





    # ======================================================
    # STANDARD JOB FORMAT
    # ======================================================


    def create_job(

        self,

        title="",

        company="",

        url="",

        location="",

        country="",

        description="",

        requirements="",

        published_date=None,

        expiry_date=None,

        salary="",

        employment_type=""


    ):



        return {


            "title": title,


            "company": company,


            "source": self.name,


            "url": url,


            "location": location,


            "country": country,


            "description": description,


            "requirements": requirements,


            "published_date": published_date,


            "expiry_date": expiry_date,


            "salary": salary,


            "employment_type": employment_type


        }




    # ======================================================
    # DATE CONVERSION
    # ======================================================


    def convert_date(self, date_string):


        """
        Converts different website dates
        into standard format.

        Example:

        Aug 20, 2026

        becomes:

        2026-08-20

        """



        if not date_string:

            return None



        formats = [


            "%b %d, %Y",

            "%B %d, %Y",

            "%Y-%m-%d",

            "%d %B %Y"

        ]



        for fmt in formats:


            try:


                return datetime.strptime(

                    date_string,

                    fmt

                ).date()



            except ValueError:


                continue



        return None





    # ======================================================
    # SCRAPE FUNCTION
    # ======================================================


    def scrape(self):


        """
        Each website scraper
        must override this.
        """


        raise NotImplementedError(

            "Scraper must implement scrape()"

        )