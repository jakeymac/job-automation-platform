from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema

from .models import Job
from .serializers import JobSerializer


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

    def patch(self, request, job_id):
        breakpoint()
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
