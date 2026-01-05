from django.utils import timezone
from .scraper import scrape_remoteok

def scrape_jobs_task(limit=20):
    """
    Task wrapper around your existing scraper.
    """
    started = timezone.now()
    scrape_remoteok(limit=limit)  # calls your existing scraper.py function
    return f"Scrape OK {started.isoformat()} → {timezone.now().isoformat()}"