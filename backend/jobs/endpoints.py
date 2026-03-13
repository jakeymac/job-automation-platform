from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema

from .models import Job
from .serializers import JobSerializer


@extend_schema(
    summary="List all jobs",
    description="Returns all jobs currently."
)
class ListJobsView(APIView):
    def get(self, request):
        jobs = Job.objects.all()
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

@extend_schema(
    summary="Get job details",
    description="Returns details of a specific job by its ID."
)
class JobDetailView(APIView):
    def get(self, request, job_id):
        try:
            job = Job.objects.get(id=job_id)
            serializer = JobSerializer(job)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Job.DoesNotExist:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)
        

@extend_schema(
    summary="Delete a job",
    description="Deletes a specific job by its ID."
)
class DeleteJobView(APIView):
    def delete(self, request, job_id):
        try:
            job = Job.objects.get(id=job_id)
            job.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Job.DoesNotExist:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)
    
