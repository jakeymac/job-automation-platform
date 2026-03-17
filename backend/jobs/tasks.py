import os
import shutil

from celery import shared_task
import subprocess
from django.utils import timezone
import tempfile

from .models import JobRun


@shared_task
def execute_job_run(job_run_id):
    run = JobRun.objects.get(id=job_run_id)

    run.status = "RUNNING"
    run.started_at = timezone.now()
    run.save()

    job_dir = tempfile.mkdtemp(prefix=f"job_{run.id}_")

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

        os.makedirs("/logs", exist_ok=True)
        with open(f"/logs/job_run_{run.id}.log", "w") as log_file:
            for line in process.stdout:
                log_file.write(line)

        process.wait()

        if process.stdout:
            process.stdout.close()

        run.exit_code = process.returncode
        run.status = "SUCCESS" if process.returncode == 0 else "FAILED"

    except Exception as e:
        os.makedirs("/logs", exist_ok=True)
        with open(f"/logs/job_run_{run.id}.log", "a") as log_file:
            log_file.write(f"Error executing job: {str(e)}\n")
        run.status = "FAILED"

    run.finished_at = timezone.now()
    run.duration_seconds = (run.finished_at - run.started_at).total_seconds()

    run.log_file.name = f"job_logs/job_run_{run.id}.log"

    run.save()

    shutil.rmtree(job_dir, ignore_errors=True)
