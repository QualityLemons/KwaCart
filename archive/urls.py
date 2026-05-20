# App namespace: 'archive'
# Named URLs exposed by this module:
#   archive:dashboard        — paginated list of solo submissions and sessions
#   archive:detail           — single ToolInstance detail page
#   archive:delete           — POST-only deletion endpoint for a ToolInstance
#   archive:download         — per-instance file download (md, rtf, html)
#   archive:session_download — combined session export download (md, rtf)
from django.urls import path

from .views import ArchiveDashboardView, ArchiveDetailView, archive_record_delete
from .views_downloads import secure_download, secure_session_download
from .views_preview import md_preview, session_md_preview

app_name = 'archive'

urlpatterns = [
    path('dashboard/', ArchiveDashboardView.as_view(), name='dashboard'),
    path('detail/<int:pk>/', ArchiveDetailView.as_view(), name='detail'),
    path('delete/<int:pk>/', archive_record_delete, name='delete'),
    path('download/<int:instance_id>/<str:file_type>/', secure_download, name='download'),
    path('session-download/<uuid:session_id>/<str:file_type>/', secure_session_download, name='session_download'),
    # Inline Markdown preview — returns raw text as JSON for the modal viewer.
    path('md-preview/<int:instance_id>/', md_preview, name='md_preview'),
    path('session-md-preview/<uuid:session_id>/', session_md_preview, name='session_md_preview'),
]
