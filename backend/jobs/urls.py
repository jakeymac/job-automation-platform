from django.urls import path

from .endpoints import (
    DeleteJobView,
    EditJobView,
    CreateJobView,
    JobDetailView,
    JobFilesView,
    UploadJobFileView,
    DeleteJobFileView,
    ListJobsView,
    RunJobView,
    JobRunsView,
    JobRunView,
    JobRunLogsView,
)

urlpatterns = [
    path("", ListJobsView.as_view(), name="list-jobs"),
    path("new/", CreateJobView.as_view(), name="create-job"),
    path("<int:job_id>/", JobDetailView.as_view(), name="job-detail"),
    path("<int:job_id>/edit/", EditJobView.as_view(), name="edit-job"),
    path("<int:job_id>/delete/", DeleteJobView.as_view(), name="delete-job"),
    path("<int:job_id>/run/", RunJobView.as_view(), name="run-job"),
    path("<int:job_id>/runs/", JobRunsView.as_view(), name="job-runs"),
    path("runs/<int:run_id>/", JobRunView.as_view(), name="job-run-detail"),
    path("<int:job_id>/files/", JobFilesView.as_view(), name="job-files"),
    path(
        "<int:job_id>/files/upload/",
        UploadJobFileView.as_view(),
        name="upload-job-file",
    ),
    path(
        "files/<int:file_id>/delete/",
        DeleteJobFileView.as_view(),
        name="delete-job-file",
    ),
    path(
        "runs/<int:run_id>/logs/",
        JobRunLogsView.as_view(),
        name="job-run-logs",
    ),
]
