# App namespace: 'archive'
# Named URLs exposed by this module:
#   archive:knowledge_bank      — tool-index for the authenticated user
#   archive:knowledge_bank_tool — drill-in: all activity for one tool slug
#   archive:dashboard           — legacy redirect → knowledge_bank
#   archive:detail              — single ToolInstance detail page
#   archive:delete              — POST-only deletion endpoint for a ToolInstance
#   archive:download            — per-instance file download (md, rtf, html)
#   archive:session_download    — combined session export download (md, rtf)
from django.urls import path

from .views import (
    ArchiveDashboardView,
    ArchiveDetailView,
    KnowledgeBankToolView,
    KnowledgeBankView,
    archive_record_delete,
)
from .views_downloads import secure_download, secure_session_download
from .views_insights import insights_dashboard
from .views_preview import md_preview, session_md_preview

app_name = 'archive'

urlpatterns = [
    path('knowledge-bank/', KnowledgeBankView.as_view(), name='knowledge_bank'),
    path('knowledge-bank/<slug:tool_slug>/', KnowledgeBankToolView.as_view(), name='knowledge_bank_tool'),
    # Legacy redirect — old bookmarks and any templates still using archive:dashboard
    # are silently forwarded to the Knowledge Bank.
    path('dashboard/', ArchiveDashboardView.as_view(), name='dashboard'),
    path('insights/', insights_dashboard, name='insights'),
    path('detail/<int:pk>/', ArchiveDetailView.as_view(), name='detail'),
    path('delete/<int:pk>/', archive_record_delete, name='delete'),
    path('download/<int:instance_id>/<str:file_type>/', secure_download, name='download'),
    path('session-download/<uuid:session_id>/<str:file_type>/', secure_session_download, name='session_download'),
    path('md-preview/<int:instance_id>/', md_preview, name='md_preview'),
    path('session-md-preview/<uuid:session_id>/', session_md_preview, name='session_md_preview'),
]
