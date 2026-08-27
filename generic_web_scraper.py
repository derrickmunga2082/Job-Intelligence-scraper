# ==========================================================
# JOB INTELLIGENCE SCRAPER
# ADVANCED WEBSITE SCRAPER
# ==========================================================


from bs4 import BeautifulSoup

from urllib.parse import urljoin

import re

from scrapers.base_scraper import BaseScraper





class GenericWebScraper(BaseScraper):


    """
    Generic scraper for public career pages.

    Designed to capture:
    - Job title
    - Company
    - Location
    - Employment type
    - Description
    - Dates
    """



    def __init__(self, name, url):


        super().__init__(

            name,

            url

        )





    # ======================================================
    # FIND JOB LINKS
    # ======================================================


    def find_job_links(self, html):


        soup = BeautifulSoup(

            html,

            "lxml"

        )


        links = []



        keywords = [

            "job",

            "career",

            "vacancy",

            "position",

            "opportunity",

            "apply",

            "opening"

        ]



        for link in soup.find_all(

            "a",

            href=True

        ):



            text = link.get_text(

                " ",

                strip=True

            ).lower()



            href = link["href"]



            if any(

                word in text

                for word in keywords

            ):



                full_url = urljoin(

                    self.url,

                    href

                )



                links.append(

                    full_url

                )




        return list(

            set(

                links

            )

        )





    # ======================================================
    # EXTRACT TITLE
    # ======================================================


    def extract_title(self, soup):


        possible = [


            soup.find("h1"),


            soup.find("title")

        ]



        for item in possible:


            if item:


                return item.get_text(

                    " ",

                    strip=True

                )



        return ""





    # ======================================================
    # EXTRACT LOCATION
    # ======================================================


    def extract_location(self, text):


        locations = [

            "Kenya",

            "Uganda",

            "Tanzania",

            "Rwanda",

            "Ethiopia",

            "Nigeria",

            "South Africa"

        ]



        for location in locations:


            if location.lower() in text.lower():


                return location



        return ""





    # ======================================================
    # EXTRACT EMPLOYMENT TYPE
    # ======================================================


    def extract_type(self,text):


        types = [

            "full time",

            "part time",

            "contract",

            "consultant",

            "internship",

            "temporary"

        ]



        for item in types:


            if item in text.lower():


                return item



        return ""





    # ======================================================
    # EXTRACT DATE
    # ======================================================


    def extract_date(self,text):


        patterns = [


            r"\d{1,2}\s[A-Za-z]+\s\d{4}",


            r"[A-Za-z]+\s\d{1,2},\s\d{4}",


            r"\d{4}-\d{2}-\d{2}"

        ]



        for pattern in patterns:


            match = re.search(

                pattern,

                text

            )



            if match:


                return self.convert_date(

                    match.group()

                )



        return None





    # ======================================================
    # SCRAPE WEBSITE
    # ======================================================


    def scrape(self):


        jobs = []



        print(

            "Scanning:",

            self.name

        )



        html = self.fetch_page(

            self.url

        )



        if not html:


            return jobs





        job_links = self.find_job_links(

            html

        )



        print(

            len(job_links),

            "job links found"

        )



        # SPEED CONTROL
        # Only scan first 20 jobs

        for url in job_links[:20]:


            page = self.fetch_page(

                url

            )



            if not page:


                continue



            soup = BeautifulSoup(

                page,

                "lxml"

            )



            text = soup.get_text(

                " ",

                strip=True

            )



            title = self.extract_title(

                soup

            )



            location = self.extract_location(

                text

            )



            employment_type = self.extract_type(

                text

            )



            published_date = self.extract_date(

                text

            )





            job = self.create_job(

                title=title,

                company=self.name,

                url=url,

                location=location,

                country=location,

                description=text[:3000],

                employment_type=employment_type,

                published_date=published_date

            )



            jobs.append(

                job

            )





        print(

            len(jobs),

            "jobs extracted from",

            self.name

        )



        return jobs