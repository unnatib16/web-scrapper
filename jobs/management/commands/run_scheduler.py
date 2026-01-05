import signal, sys, time
from django.conf import settings
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore, register_events
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.utils import timezone

from jobs.tasks import scrape_jobs_task

class Command(BaseCommand):
    help = "Starts APScheduler with Django job store (cross-platform)."

    def handle(self, *args, **options):
        scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # Run every minute (testin
        scheduler.add_job(
            scrape_jobs_task,
            trigger=CronTrigger(minute="*/1"),
            kwargs={"limit": 20},
            id="scrape_every_minute",
            max_instances=1,
            coalesce=True,
            replace_existing=True,
            misfire_grace_time=60,
            jobstore="default",
            next_run_time=timezone.now(),  # run once immediately
        )

        register_events(scheduler)
        scheduler.start()
        self.stdout.write(self.style.SUCCESS("✓ APScheduler started."))

        # Graceful shutdown
        def shutdown(*_):
            self.stdout.write("Shutting down scheduler…")
            scheduler.shutdown(wait=False)
            sys.exit(0)

        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                signal.signal(sig, shutdown)
            except Exception:
                pass

        try:
            signal.pause()  # Linux/macOS
        except Exception:
            while True:     # Windows fallback
                time.sleep(1)