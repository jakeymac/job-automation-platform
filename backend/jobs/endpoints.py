from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Job, JobRun, JobFile
from .serializers import JobSerializer, JobRunSerializer
from .tasks import execute_job_run


@extend_schema(summary="List all jobs", description="Returns all jobs currently.")
class ListJobsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_staff:
            jobs = Job.objects.all()
        else:
            jobs = Job.objects.filter(owner=request.user)
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
            return Response(serializer.data, status=status.HTTP_200_OK)
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
