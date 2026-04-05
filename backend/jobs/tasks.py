import logging
import os
import shutil
import subprocess

from celery import shared_task
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail

from .models import JobRun

logger = logging.getLogger(__name__)


@shared_task
def run_scheduled_job(job_id):
    from .models import Job, JobRun

    job = Job.objects.get(id=job_id)

    run = JobRun.objects.create(job=job, status="PENDING")

    execute_job_run.delay(run.id)

@shared_task(bind=True, max_retries=3)
def send_job_notification(self, job_run_id):
    try:
        run = JobRun.objects.select_related("job", "job__owner").get(id=job_run_id)
    except JobRun.DoesNotExist:
        logger.warning(f"JobRun with id {job_run_id} does not exist")
        return
    
    if run.email_status == "SENT":
        logger.info(f"Email already sent for JobRun {run.id}, skipping.")
        return

    run.email_status = "PENDING"
    run.save(update_fields=["email_status"])
    
    if run.status == "SUCCESS":
        subject = f"Job '{run.job.name}' Completed Successfully"
        message = f"The job '{run.job.name}' has completed successfully.\n\nDuration: {run.duration_seconds:.2f} seconds.\n\nYou can view the logs for this run at: {settings.SITE_URL}/jobs/runs/{run.id}"
        recipient_list = [run.job.owner.email]
    else:
        subject = f"Job '{run.job.name}' Failed"
        message = f"The job '{run.job.name}' has failed.\n\nDuration: {run.duration_seconds:.2f} seconds.\n\nYou can view the logs for this run at: {settings.SITE_URL}/jobs/runs/{run.id}"
        try:
            with run.log_file.open() as f:
                last_lines = f.readlines()[-10:]
                message += "\n\nLast log output:\n" + "".join(last_lines)
        except Exception:
            pass
    email = run.job.owner.email
    if not email:
        logger.warning(f"No email found for user {run.job.owner.username}, cannot send notification for JobRun {run.id}")
        run.email_status = "FAILED"
        run.email_error = "No email address found for user"
        run.save(update_fields=["email_status", "email_error"])
        return
    recipient_list = [run.job.owner.email]

    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
        run.email_status = "SENT"
        run.email_sent_at = timezone.now()
        run.save(update_fields=["email_status", "email_sent_at"])
        logger.info(f"Notification email sent for JobRun {run.id}")
    except Exception as e:
        run.email_status = "FAILED"
        run.email_error = str(e)
        run.save(update_fields=["email_status", "email_error"])
        logger.error(f"Error sending notification email for JobRun {run.id}: {e}")
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))

@shared_task
def execute_job_run(job_run_id):
    try:
        run = JobRun.objects.get(id=job_run_id)
    except JobRun.DoesNotExist:
        logger.warning(f"JobRun with id {job_run_id} does not exist")
        return

    run.status = "RUNNING"
    run.started_at = timezone.now()
    run.save()

    container_media_root = os.environ.get("HOST_MEDIA_ROOT", settings.MEDIA_ROOT)
    host_media_root_real = os.environ.get("HOST_MEDIA_ROOT_REAL", container_media_root)

    job_dir_container = os.path.join(container_media_root, "tmp_jobs", f"job_{run.id}")
    job_dir_host = os.path.join(host_media_root_real, "tmp_jobs", f"job_{run.id}")
    os.makedirs(job_dir_container, exist_ok=True)

    for job_file in run.job.files.all():
        src = job_file.file.path
        destination = os.path.join(job_dir_container, os.path.basename(src))
        if os.path.abspath(src) != os.path.abspath(destination):
            shutil.copy(src, destination)
    logger.info(f"Container job dir: {job_dir_container}")
    logger.info(f"Host job dir: {job_dir_host}")
    logger.info(f"Job dir contents: {os.listdir(job_dir_container)}")
    try:
        logs_dir = os.path.join(settings.MEDIA_ROOT, "job_logs")
        os.makedirs(logs_dir, exist_ok=True)
        log_path = os.path.join(logs_dir, f"job_run_{run.id}.log")
    except Exception as e:
        logger.error(f"Error setting up log file for JobRun {run.id}: {e}")
        run.status = "FAILED"
        run.finished_at = timezone.now()
        run.duration_seconds = (run.finished_at - run.started_at).total_seconds()
        run.save()
        shutil.rmtree(job_dir_container, ignore_errors=True)
        return

    try:
        process = subprocess.Popen(
            [
                "docker",
                "run",
                "--rm",
                "--network",
                "none",
                "--memory",
                "512m",
                "--cpus",
                "1.0",
                "--pids-limit",
                "100",
                "--read-only",
                "--tmpfs",
                "/tmp",
                "-v",
                f"{job_dir_host}:/workspace",
                "-w",
                "/workspace",
                run.job.image,
                "bash",
                "-c",
                run.job.command or "echo 'No command specified'",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        with open(log_path, "w") as log_file:
            for line in process.stdout:
                log_file.write(line)
                log_file.flush()

        process.wait()

        if process.stdout:
            process.stdout.close()

        run.exit_code = process.returncode
        run.status = "SUCCESS" if process.returncode == 0 else "FAILED"

    except Exception as e:
        with open(log_path, "a") as log_file:
            log_file.write(f"Error executing job: {str(e)}\n")
        run.status = "FAILED"

    run.finished_at = timezone.now()
    run.duration_seconds = (run.finished_at - run.started_at).total_seconds()

    run.log_file.name = f"job_logs/job_run_{run.id}.log"

    run.save()

    shutil.rmtree(job_dir_container, ignore_errors=True)

    send_job_notification.delay(run.id)
