from rest_framework.permissions import BasePermission
from .auth import authenticate_job_run


class HasValidAPIToken(BasePermission):
    def has_permission(self, request, view):
        run_id = view.kwargs.get("run_id")

        if not run_id:
            return False

        try:
            run = authenticate_job_run(request, run_id)
        except Exception:
            return False

        # Attached the authenticated run to the request for use in the endpoint
        request.job_run = run

        return True
