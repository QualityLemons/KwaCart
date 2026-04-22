from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import json

from .registry import get_tool_instance
from archive.models import ToolInstance

@login_required
def draft_editor(request, tool_slug, instance_id=None):
    """
    Standard GET view to render the drafting interface.
    """
    # Fetch existing draft or provide a blank state
    instance = None
    if instance_id:
        instance = get_object_or_404(ToolInstance, id=instance_id, user=request.user, status='draft')
    
    context = {
        'tool_slug': tool_slug,
        'instance': instance,
        # In a real app, we'd pull the tool's form fields from the registry here
    }
    return render(request, 'tools/draft_editor.html', context)

@login_required
@require_POST
def autosave_endpoint(request, tool_slug):
    """
    AJAX endpoint for Tactic 4 (Autosave).
    Expects JSON data: { "instance_id": 1, "form_data": {...} }
    """
    data = json.loads(request.body)
    instance_id = data.get('instance_id')
    form_data = data.get('form_data')

    # 1. Get or Create the Draft
    if instance_id:
        instance = get_object_or_404(ToolInstance, id=instance_id, user=request.user, status='draft')
    else:
        # Tactic 3: Get version from the tool logic
        tool_class = get_tool_instance(tool_slug)
        instance = ToolInstance.objects.create(
            user=request.user,
            tool_slug=tool_slug,
            tool_version=tool_class.version,
            status='draft'
        )

    # 2. Update the Draft Data (Tactic 2)
    instance.payload_input = form_data
    instance.save()

    return JsonResponse({
        'status': 'success',
        'instance_id': instance.id,
        'last_saved': instance.updated_at.strftime("%H:%M:%S")
    })