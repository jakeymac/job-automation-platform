from django.urls import path

from .endpoints import DeleteJobView, EditJobView, JobDetailView, ListJobsView

urlpatterns = [
    path("", ListJobsView.as_view(), name="list-jobs"),
    path("<int:job_id>/", JobDetailView.as_view(), name="job-detail"),
    path("edit/<int:job_id>/", EditJobView.as_view(), name="edit-job"),
    path("delete/<int:job_id>/", DeleteJobView.as_view(), name="delete-job"),
]
