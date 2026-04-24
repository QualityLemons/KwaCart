from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import ToolInstance

class ArchiveDashboardView(LoginRequiredMixin, ListView):
    model = ToolInstance
    template_name = 'archive/dashboard.html'
    context_object_name = 'records'
    paginate_by = 10

    def get_queryset(self):
        # Tactic 7: Access checks on every retrieval
        return ToolInstance.objects.filter(
            user=self.request.user, 
            status='archived'
        ).order_name('-submitted_at')

class ArchiveDetailView(LoginRequiredMixin, DetailView):
    model = ToolInstance
    template_name = 'archive/detail.html'
    context_object_name = 'record'

    def get_queryset(self):
        # Strict ownership check
        return ToolInstance.objects.filter(user=self.request.user)