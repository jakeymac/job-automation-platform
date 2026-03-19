import json
import logging
import os

from django.conf import settings
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Job, JobFile, JobRun
from .serializers import JobRunSerializer, JobSerializer
from .tasks import execute_job_run

logger = logging.getLogger(__name__)


def parse_cron_schedule(cron_string):
    minute, hour, day_of_month, month_of_year, day_of_week = cron_string.split()
    return {
        "minute": minute,
        "hour": hour,
        "day_of_month": day_of_month,
        "month_of_year": month_of_year,
        "day_of_week": day_of_week,
    }


def setup_periodic_task(schedule, job):
    cron_parts = parse_cron_schedule(schedule)

    schedule, _ = CrontabSchedule.objects.get_or_create(
        minute=cron_parts["minute"],
        hour=cron_parts["hour"],
        day_of_month=cron_parts["day_of_month"],
        month_of_year=cron_parts["month_of_year"],
        day_of_week=cron_parts["day_of_week"],
    )

    PeriodicTask.objects.update_or_create(
        name=f"job-{job.id}",
        defaults={
            "crontab": schedule,
            "task": "jobs.tasks.run_scheduled_job",
            "args": json.dumps([job.id]),
            "enabled": job.is_active,
        },
    )


@extend_schema(summary="List all jobs", description="Returns all jobs currently.")
class ListJobsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_staff:
            jobs = Job.objects.all()
        else:
            jobs = Job.objects.filter(owner=request.user)

        serializer = JobSerializer(jobs, many=True)
        serializer_data = serializer.data
        for job_data in serializer_data:
            job_id = job_data["id"]
            last_run = (
                JobRun.objects.filter(job_id=job_id).order_by("-created_at").first()
            )
            if last_run:
                job_data["last_run_status"] = last_run.status
            else:
                job_data["last_run_status"] = None
        return Response(serializer_data, status=status.HTTP_200_OK)


@extend_schema(summary="Create a new job", description="Creates a new job.")
class CreateJobView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        try:
            request_data = request.POST.copy()
            request_data["owner"] = request.user.id
            serializer = JobSerializer(data=request_data)
            if serializer.is_valid():
                serializer.save()
                if serializer.data["schedule"]:
                    print(serializer.data["schedule"])
                    setup_periodic_task(
                        serializer.data["schedule"], serializer.instance
                    )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error creating job: {e}")
            return Response(
                {"error": "An error occurred while creating the job."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(
    summary="Get job details",
    description="Returns details of a specific job by its ID.",
)
class JobDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, job_id):
        try:
            if request.user.is_staff:
                job = Job.objects.get(id=job_id)
            else:
                job = Job.objects.get(id=job_id, owner=request.user)
            serializer = JobSerializer(job)

            last_run = job.runs.order_by("-created_at").first()
            serializer_data = serializer.data
            if last_run:
                serializer_data["last_run_status"] = last_run.status
            else:
                serializer_data["last_run_status"] = None

            return Response(serializer_data, status=status.HTTP_200_OK)
        except Job.DoesNotExist:
            return Response(
                {"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND
            )


@extend_schema(summary="Edit a job", description="Edits a specific job by its ID.")
class EditJobView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request, job_id):
        try:
            if request.user.is_staff:
                job = Job.objects.get(id=job_id)
            else:
                job = Job.objects.get(id=job_id, owner=request.user)
            serializer = JobSerializer(job, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                if serializer.data["schedule"]:
                    setup_periodic_task(
                        serializer.data["schedule"], serializer.instance
                    )
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Job.DoesNotExist:
            return Response(
                {"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND
            )


@extend_schema(summary="Delete a job", description="Deletes a specific job by its ID.")
class DeleteJobView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, job_id):
        try:
            if request.user.is_staff:
                job = Job.objects.get(id=job_id)
            else:
                job = Job.objects.get(id=job_id, owner=request.user)

            # Delete associated job runs, files, and logs
            logs_dir = os.path.join(settings.MEDIA_ROOT, "logs")
            runs = job.runs.all()
            for run in runs:
                log_path = os.path.join(logs_dir, f"job_run_{run.id}.log")
                if os.path.exists(log_path):
                    try:
                        os.remove(log_path)
                    except Exception as e:
                        logger.error(f"Error deleting log file {log_path}: {e}")
            job_file_directory = os.path.join(
                settings.MEDIA_ROOT, "job_files", f"job_{job.id}"
            )
            if os.path.exists(job_file_directory):
                try:
                    import shutil

                    shutil.rmtree(job_file_directory)
                except Exception as e:
                    logger.error(
                        f"Error deleting job file directory {job_file_directory}: {e}"
                    )
            job.files.all().delete()
            runs.delete()
            PeriodicTask.objects.filter(name=f"job-{job.id}").delete()
            job.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)
        except Job.DoesNotExist:
            return Response(
                {"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND
            )


@extend_schema(
    summary="List files for a job",
    description="Returns a list of files associated with a specific job.",
)
class JobFilesView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, job_id):
        try:
            if request.user.is_staff:
                job = Job.objects.get(id=job_id)
            else:
                job = Job.objects.get(id=job_id, owner=request.user)
        except Job.DoesNotExist:
            return Response(
                {"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND
            )

        files = job.files.all()
        file_data = [{"id": f.id, "filename": f.file.name} for f in files]
        return Response(file_data, status=status.HTTP_200_OK)


class UploadJobFileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        summary="Upload a file for a job",
        description="Uploads a file to be used by a specific job.",
    )
    def post(self, request, job_id):
        try:
            if request.user.is_staff:
                job = Job.objects.get(id=job_id)
            else:
                job = Job.objects.get(id=job_id, owner=request.user)
        except Job.DoesNotExist:
            return Response(
                {"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND
            )
        file = request.FILES.get("file")
        if file:
            file.name = os.path.basename(file.name)
            new_file = JobFile.objects.create(job=job, file=file)

        return Response(
            {
                "message": "File uploaded successfully",
                "id": new_file.id,
                "filename": new_file.file.name,
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(
    summary="Delete a job file",
    description="Deletes a specific file associated with a job.",
)
class DeleteJobFileView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, file_id):
        try:
            if request.user.is_staff:
                job_file = JobFile.objects.get(id=file_id)
            else:
                job_file = JobFile.objects.get(id=file_id, job__owner=request.user)
            job_file.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except JobFile.DoesNotExist:
            return Response(
                {"error": "Job file not found"}, status=status.HTTP_404_NOT_FOUND
            )


@extend_schema(
    summary="Run a job",
    description="Queues a job for execution.",
)
class RunJobView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, job_id):
        trigger_type = request.data.get("trigger_type", "manual")
        try:
            if request.user.is_staff:
                job = Job.objects.get(id=job_id)
            else:
                job = Job.objects.get(id=job_id, owner=request.user)

        except Job.DoesNotExist:
            return Response(
                {"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND
            )

        # Create a new JobRun instance with status PENDING
        job_run = JobRun.objects.create(
            job=job,
            status=JobRun.Status.PENDING,
            triggered_by=request.user,
            trigger_type=trigger_type,
        )

        execute_job_run.delay(job_run.id)

        return Response(
            {"message": "Job run started", "job_run_id": job_run.id},
            status=status.HTTP_200_OK,
        )


@extend_schema(
    summary="List job runs",
    description="Returns all runs for a specific job.",
)
class JobRunsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, job_id):
        try:
            if request.user.is_staff:
                job = Job.objects.get(id=job_id)
            else:
                job = Job.objects.get(id=job_id, owner=request.user)
        except Job.DoesNotExist:
            return Response(
                {"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND
            )

        runs = job.runs.all().order_by("-created_at")
        serializer = JobRunSerializer(runs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="Get job run details",
    description="Returns details of a specific job run by its ID.",
)
class JobRunView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, run_id):
        try:
            if request.user.is_staff:
                run = JobRun.objects.get(id=run_id)
            else:
                run = JobRun.objects.get(id=run_id, job__owner=request.user)
        except JobRun.DoesNotExist:
            return Response(
                {"error": "Job run not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = JobRunSerializer(run)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary="Get job run logs",
    description="Returns the logs of a specific job run.",
)
class JobRunLogsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, run_id):
        try:
            if request.user.is_staff:
                run = JobRun.objects.get(id=run_id)
            else:
                run = JobRun.objects.get(id=run_id, job__owner=request.user)
        except JobRun.DoesNotExist:
            return Response(
                {"error": "Job run not found"}, status=status.HTTP_404_NOT_FOUND
            )

        log_path = os.path.join(settings.MEDIA_ROOT, "logs", f"job_run_{run.id}.log")
        if os.path.exists(log_path):
            with open(log_path, "r") as log_file:
                logs = log_file.read()
            return Response({"logs": logs}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Log file not found"}, status=status.HTTP_404_NOT_FOUND
            )
