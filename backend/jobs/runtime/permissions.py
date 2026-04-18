import logging

from rest_framework.permissions import BasePermission

from .auth import authenticate_job_run

logger = logging.getLogger(__name__)


class HasValidAPIToken(BasePermission):
    def has_permission(self, request, view):
        run_id = view.kwargs.get("run_id")

        if not run_id:
            logger.warning("No run_id found in view kwargs: %s", view.kwargs)
            return False

        try:
            run = authenticate_job_run(request, run_id)
        except Exception as e:
            logger.warning(
                f"Failed to authenticate job run with run_id: {run_id}, error: {e}"
            )
            return False

        # Attached the authenticated run to the request for use in the endpoint
        request.job_run = run

        return True
