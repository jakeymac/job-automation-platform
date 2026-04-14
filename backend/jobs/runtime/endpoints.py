from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import JobState
from .permissions import HasValidAPIToken


class SetJobRunStateView(APIView):
    authentication_classes = []  # Disable default authentication
    permission_classes = [HasValidAPIToken]

    def post(self, request, run_id):

        run = (
            request.job_run
        )  # This is set by the permission class after authentication
        current_job_state = JobState.objects.get(job=run.job)
        if current_job_state.data is None:
            current_data = {}
        else:
            current_data = current_job_state.data.copy()

        run.output_data = request.data.get("output_data", {})
        for key, value in request.data.get("updated_values", {}).items():
            current_data[key] = value

        run.state_snapshot = current_job_state.data  # Store the state before updating
        run.updated_state = current_data
        run.save()

        return Response(
            {
                "status": "ok",
                "message": "Updated job run's updated state successfully",
                "run_id": run.id,
                "job_id": run.job.id,
            }
        )


class SetJobRunEmailContentView(APIView):
    authentication_classes = []  # Disable default authentication
    permission_classes = [HasValidAPIToken]

    def post(self, request, run_id):
        run = (
            request.job_run
        )  # This is set by the permission class after authentication
        custom_content = request.data.get("custom_email_content", "")
        run.custom_email_content = custom_content
        run.save()

        return Response(
            {
                "status": "ok",
                "message": "Updated job run's custom email content successfully",
                "run_id": run.id,
                "job_id": run.job.id,
            }
        )
