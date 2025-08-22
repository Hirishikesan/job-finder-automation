# job_scraper.py
from jobspy import scrape_jobs
import pandas as pd

# -------- CONFIG --------
SITES = ["linkedin", "indeed", "google"]   # job sites to scrape
KEYWORDS = "Azure Devops, Security"        # search keywords
LOCATION = "India"                         # job location
RESULTS_WANTED = 10                        # number of job results
TIMEFRAME = "24h"                          # last 24 hours
OUTPUT_FILE = "jobs.csv"                   # output file name
# ------------------------

print(f"Searching: '{KEYWORDS}' in '{LOCATION}' | sites={SITES} | last {TIMEFRAME} | max {RESULTS_WANTED}")

# Call scrape_jobs with correct parameters (no google_search_term)
jobs_df = scrape_jobs(
    site_name=SITES,
    search_term=KEYWORDS,
    location=LOCATION,
    results_wanted=RESULTS_WANTED,
    hours_old=24  # instead of TIMEFRAME string
)

# Save results
if not jobs_df.empty:
    jobs_df.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ Scraping completed! Results saved to {OUTPUT_FILE}")
else:
    print("⚠️ No jobs found.")
