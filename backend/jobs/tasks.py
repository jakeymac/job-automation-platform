from celery import shared_task
from django.utils import timezone

from .models import JobRun

@shared_task
def run_job_task(job_run_id):
    run = JobRun.objects.get(id=job_run_id)

    run.status = JobRun.Status.RUNNING
    run.started_at = timezone.now()
    run.save()

    try:
        # Temporary placeholder execution
        import time
        time.sleep(3)

        run.status = JobRun.Status.SUCCESS
        run.exit_code = 0
        run.output = "Job completed successfully."

    except Exception as e:
        run.status = JobRun.Status.FAILED
        run.error = str(e)

    run.finished_at = timezone.now()
    run.save()