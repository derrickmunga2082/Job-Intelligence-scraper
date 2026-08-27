# ==========================================================
# JOB INTELLIGENCE SCRAPER
# ADVANCED RSS JOB SCRAPER
# ==========================================================


import feedparser

import re

from datetime import datetime

from scrapers.base_scraper import BaseScraper





class RSSJobScraper(BaseScraper):


    """
    RSS scraper designed for job feeds.

    Extracts:
    - title
    - company
    - location
    - country
    - employment type
    - description
    - dates
    """



    def __init__(self, name, url):


        super().__init__(

            name,

            url

        )





    # ======================================================
    # DATE EXTRACTION
    # ======================================================


    def extract_date(self, entry):


        try:


            if entry.published_parsed:


                return datetime(

                    entry.published_parsed.tm_year,

                    entry.published_parsed.tm_mon,

                    entry.published_parsed.tm_mday

                ).date()



        except Exception:


            pass



        return None





    # ======================================================
    # TEXT CLEANING
    # ======================================================


    def clean_text(self, text):


        if not text:


            return ""



        return (

            re.sub(

                "<.*?>",

                "",

                text

            )

            .replace(

                "\n",

                " "

            )

            .strip()

        )





    # ======================================================
    # FIND LOCATION
    # ======================================================


    def extract_location(self, text):


        countries = [

            "Kenya",

            "Uganda",

            "Tanzania",

            "Rwanda",

            "Ethiopia",

            "Somalia",

            "Nigeria",

            "South Africa"

        ]



        for country in countries:


            if country.lower() in text.lower():


                return country



        return ""





    # ======================================================
    # FIND EMPLOYMENT TYPE
    # ======================================================


    def extract_employment_type(self, text):


        types = [

            "Full time",

            "Part time",

            "Contract",

            "Consultancy",

            "Internship",

            "Temporary"

        ]



        for item in types:


            if item.lower() in text.lower():


                return item



        return ""





    # ======================================================
    # EXTRACT COMPANY
    # ======================================================


    def extract_company(self, entry):


        possible_fields = [

            "author",

            "creator",

            "publisher"

        ]



        for field in possible_fields:


            value = getattr(

                entry,

                field,

                ""

            )



            if value:


                return value



        return ""





    # ======================================================
    # SCRAPE RSS
    # ======================================================


    def scrape(self):


        jobs = []



        try:



            print(

                f"Scanning RSS source: {self.name}"

            )



            feed = feedparser.parse(

                self.url

            )



            if not feed.entries:


                print(

                    "No RSS jobs found"

                )


                return jobs





            for item in feed.entries:



                title = getattr(

                    item,

                    "title",

                    ""

                )



                link = getattr(

                    item,

                    "link",

                    ""

                )



                description = self.clean_text(

                    getattr(

                        item,

                        "description",

                        ""

                    )

                )



                company = self.extract_company(

                    item

                )



                location = self.extract_location(

                    description

                )



                employment_type = self.extract_employment_type(

                    description

                )



                published_date = self.extract_date(

                    item

                )





                job = self.create_job(

                    title=title,

                    company=company,

                    url=link,

                    location=location,

                    country=location,

                    description=description,

                    employment_type=employment_type,

                    published_date=published_date

                )



                jobs.append(

                    job

                )






        except Exception as e:


            print(

                "RSS error:",

                e

            )





        print(

            len(jobs),

            "jobs extracted from",

            self.name

        )



        return jobs