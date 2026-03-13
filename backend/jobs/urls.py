from django.urls import path

from .endpoints import ListJobsView, JobDetailView, DeleteJobView

urlpatterns = [
    path("", ListJobsView.as_view(), name="list-jobs"),
    path("<int:job_id>/", JobDetailView.as_view(), name="job-detail"),
    path("<int:job_id>/delete/", DeleteJobView.as_view(), name="delete-job"),
]