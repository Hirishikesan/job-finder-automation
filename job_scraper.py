import os
import datetime as dt
from pathlib import Path
import pandas as pd

# JobSpy import (pip package name is python-jobspy; module import is jobspy)
from jobspy import scrape_jobs

# ---- Config via environment variables (with safe defaults) ----
KEYWORDS       = os.getenv("JOB_KEYWORDS", "DevOps Engineer")
LOCATION       = os.getenv("JOB_LOCATION", "Bengaluru, India")
RESULTS_WANTED = int(os.getenv("RESULTS_WANTED", "50"))
HOURS_OLD      = int(os.getenv("HOURS_OLD", "24"))
SITES_RAW      = os.getenv("JOB_SITES", "linkedin,indeed,google")
SITES          = [s.strip().lower() for s in SITES_RAW.split(",") if s.strip()]

# If Google Jobs is included, JobSpy prefers a google_search_term param.
google_kwargs = {}
if "google" in SITES:
    google_kwargs["google_search_term"] = KEYWORDS

# ---- Scrape ----
print(f"Searching: '{KEYWORDS}' in '{LOCATION}' | sites={SITES} | last {HOURS_OLD}h | max {RESULTS_WANTED}")
jobs_df = scrape_jobs(
    site_name=SITES,
    search_term=KEYWORDS,
    location=LOCATION,
    results_wanted=RESULTS_WANTED,
    **google_kwargs
)

if jobs_df is None or jobs_df.empty:
    print("No jobs found. Exiting with no report.")
    # Create empty report for consistency
    Path("reports").mkdir(exist_ok=True)
    out = Path("reports") / f"job_results_{dt.date.today()}.xlsx"
    pd.DataFrame(columns=["title","company","location","job_url","via_site","date_posted"]).to_excel(out, index=False)
    print(f"Created empty report at: {out.resolve()}")
    raise SystemExit(0)

# Normalize & tidy (keep common, useful columns if present)
keep_cols = [c for c in [
    "title","company","location","job_url","job_type","via_site",
    "date_posted","salary","is_remote","description","company_industry"
] if c in jobs_df.columns]

jobs_df = jobs_df[keep_cols].drop_duplicates(subset=[c for c in ["job_url"] if c in jobs_df.columns])

# Timestamp and nice ordering
jobs_df.insert(0, "scraped_at", pd.Timestamp.now())
if "date_posted" in jobs_df.columns:
    jobs_df = jobs_df.sort_values("date_posted", ascending=False)

# ---- Save Excel report ----
reports_dir = Path("reports")
reports_dir.mkdir(exist_ok=True)
outfile = reports_dir / f"job_results_{dt.date.today()}.xlsx"
jobs_df.to_excel(outfile, index=False, engine="openpyxl")

print(f"✅ Job scraping complete. Saved: {outfile.resolve()}")
print(f"Found {len(jobs_df)} jobs.")
