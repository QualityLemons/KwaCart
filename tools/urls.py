from django.urls import path

from . import views

app_name = 'tools'

urlpatterns = [
    path('', views.tool_catalog, name='catalog'),

    # Solo drafting flow
    path('<slug:tool_slug>/draft/', views.draft_editor, name='draft_new'),
    path('<slug:tool_slug>/draft/<int:instance_id>/', views.draft_editor, name='draft_edit'),
    path('<slug:tool_slug>/autosave/', views.autosave_endpoint, name='autosave'),
    path('submit/<int:instance_id>/', views.submit_tool, name='submit'),

    # Collaborative session flow
    path('<slug:tool_slug>/session/start/', views.session_create, name='session_create'),
    path('session/<uuid:session_id>/', views.session_detail, name='session_detail'),
    path('session/<uuid:session_id>/close/', views.session_close, name='session_close'),
]
