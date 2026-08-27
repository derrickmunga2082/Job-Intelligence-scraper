# ==========================================================
# JOB INTELLIGENCE SCRAPER
# JOB BOARD SCRAPER
# FINAL VERSION 1 FILTERING
# ==========================================================


import requests

from bs4 import BeautifulSoup

from urllib.parse import urljoin

from cleaner import valid_job_title





class JobBoardScraper:


    def __init__(

        self,

        name,

        url

    ):


        self.name = name

        self.url = url



        self.headers = {


            "User-Agent":

            "Mozilla/5.0"

        }







    # ======================================================
    # GET PAGE
    # ======================================================


    def get_page(self, url):


        try:


            response = requests.get(

                url,

                headers=self.headers,

                timeout=15

            )


            return response.text



        except Exception as e:


            print(

                self.name,

                "connection error:",

                e

            )


            return ""







    # ======================================================
    # FIND JOB LINKS
    # ======================================================


    def extract_links(self, html):


        links = []



        soup = BeautifulSoup(

            html,

            "html.parser"

        )



        for a in soup.find_all(

            "a",

            href=True

        ):


            title = a.get_text(

                " ",

                strip=True

            )



            href = a["href"]




            if valid_job_title(title):


                full_url = urljoin(

                    self.url,

                    href

                )


                links.append(

                    {

                    "title": title,

                    "url": full_url

                    }

                )



        return links







    # ======================================================
    # EXTRACT JOB DETAILS
    # ======================================================


    def extract_job_details(

        self,

        job_link

    ):


        html = self.get_page(

            job_link["url"]

        )



        soup = BeautifulSoup(

            html,

            "html.parser"

        )



        description = soup.get_text(

            " ",

            strip=True

        )



        return {


            "title":

            job_link["title"],


            "company":

            self.name,


            "url":

            job_link["url"],


            "description":

            description,


            "source":

            self.name


        }







    # ======================================================
    # SCRAPE
    # ======================================================


    def scrape(self):


        jobs = []



        print(

            "Scanning job board:",

            self.name

        )



        html = self.get_page(

            self.url

        )



        if not html:


            return jobs





        links = self.extract_links(

            html

        )



        print(

            len(links),

            "relevant job links found"

        )






        for link in links:


            try:


                job = self.extract_job_details(

                    link

                )


                jobs.append(

                    job

                )



            except Exception:


                continue






        print(

            len(jobs),

            "jobs extracted from",

            self.name

        )



        return jobs