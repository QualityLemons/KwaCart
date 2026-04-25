from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic import DetailView, ListView

from .models import ToolInstance, ToolSession


class ArchiveDashboardView(LoginRequiredMixin, ListView):
    model = ToolInstance
    template_name = 'archive/dashboard.html'
    context_object_name = 'records'
    paginate_by = 10

    def get_queryset(self):
        return ToolInstance.objects.filter(
            user=self.request.user,
            status='archived',
            session__isnull=True,
        ).order_by('-submitted_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx['sessions'] = (
            ToolSession.objects
            .filter(Q(host=user) | Q(instances__user=user))
            .distinct()
            .order_by('-created_at')[:25]
        )
        ctx['user'] = user
        return ctx


class ArchiveDetailView(LoginRequiredMixin, DetailView):
    model = ToolInstance
    template_name = 'archive/detail.html'
    context_object_name = 'record'

    def get_queryset(self):
        return ToolInstance.objects.filter(user=self.request.user)
