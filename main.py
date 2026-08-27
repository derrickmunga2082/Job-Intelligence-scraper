# ==========================================================
# JOB INTELLIGENCE SCRAPER
# MAIN RUNNER
# ==========================================================


import json

import time



from database import (

    create_database,

    purge_stale_jobs,

    save_job,

    count_jobs

)



from cleaner import (

    clean_job,

    validate_job

)



from exporter import export_jobs



from scrapers.rss_scraper import RSSJobScraper

from scrapers.generic_web_scraper import GenericWebScraper

from scrapers.job_board_scraper import JobBoardScraper





# ==========================================================
# LOAD SOURCES
# ==========================================================


def load_sources():


    with open(

        "sources.json",

        "r",

        encoding="utf-8"

    ) as file:


        data = json.load(file)


        return data.get(

            "sources",

            []

        )







# ==========================================================
# CREATE SCRAPER
# ==========================================================


def create_scraper(source):


    source_type = source.get(

        "type"

    )



    if source_type == "rss":



        return RSSJobScraper(

            source["name"],

            source["url"]

        )





    elif source_type == "job_board":



        return JobBoardScraper(

            source["name"],

            source["url"]

        )





    else:



        return GenericWebScraper(

            source["name"],

            source["url"]

        )







# ==========================================================
# START SCRAPER
# ==========================================================


def start():


    start_time = time.time()



    print()

    print(

        "JOB SCRAPER STARTED"

    )

    print()





    create_database()

    purge_stale_jobs()



    all_jobs = []



    sources = load_sources()



    print(

        "Sources loaded:",

        len(sources)

    )







    for source in sources:



        if not source.get(

            "enabled",

            False

        ):


            continue





        print()

        print(

            "--------------------------------"

        )

        print(

            "Scraping:",

            source["name"]

        )





        try:



            scraper = create_scraper(

                source

            )



            results = scraper.scrape()



            print(

                "Jobs collected:",

                len(results)

            )



            all_jobs.extend(

                results

            )




        except Exception as e:



            print(

                "Scraper error:",

                e

            )








    print()

    print(

        "Total found:",

        len(all_jobs)

    )







    saved = 0





    for job in all_jobs:



        cleaned = clean_job(

            job

        )



        if validate_job(

            cleaned

        ):



            save_job(

                cleaned

            )


            saved += 1






    print()

    print(

        "Saved:",

        saved

    )



    print(

        "Database:",

        count_jobs()

    )





    export_jobs()





    print()

    print(

        "Completed in",

        round(

            time.time()

            -

            start_time,

            2

        ),

        "seconds"

    )







if __name__ == "__main__":


    start()