import os
import shutil

from celery import shared_task
import subprocess
import tempfile
from django.utils import timezone
from django.conf import settings

from .models import JobRun


@shared_task
def execute_job_run(job_run_id):
    run = JobRun.objects.get(id=job_run_id)

    run.status = "RUNNING"
    run.started_at = timezone.now()
    run.save()

    job_dir = os.path.join(settings.MEDIA_ROOT, f"job_files/job_{run.job.id}")

    for job_file in run.job.files.all():
        shutil.copy(job_file.file.path, job_dir)

    try:
        process = subprocess.Popen(
            [
                "docker",
                "run",
                "--rm",
                "-v",
                f"{job_dir}:/workspace",
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



        logs_dir = os.path.join(settings.BASE_DIR, "logs")
        os.makedirs(logs_dir, exist_ok=True)

        log_path = os.path.join(logs_dir, f"job_run_{run.id}.log")
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
        os.makedirs(logs_dir, exist_ok=True)
        with open(log_path, "a") as log_file:
            log_file.write(f"Error executing job: {str(e)}\n")
        run.status = "FAILED"

    run.finished_at = timezone.now()
    run.duration_seconds = (run.finished_at - run.started_at).total_seconds()

    run.log_file.name = f"job_logs/job_run_{run.id}.log"

    run.save()

    shutil.rmtree(job_dir, ignore_errors=True)
