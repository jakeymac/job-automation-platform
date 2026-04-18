import logging

from rest_framework.exceptions import PermissionDenied

from ..models import JobRun

logger = logging.getLogger(__name__)


def authenticate_job_run(request, run_id):
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise PermissionDenied("Missing token")

    token = auth_header.replace("Bearer ", "").strip()

    try:
        run = JobRun.objects.get(id=run_id)
    except JobRun.DoesNotExist:
        raise PermissionDenied("Invalid run ID")

    if run.status != JobRun.Status.RUNNING:
        raise PermissionDenied("Job run is not active")

    if not run.check_api_token(token):
        raise PermissionDenied("Invalid token")

    return run
