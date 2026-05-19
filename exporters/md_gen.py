"""Markdown export generator.

Converts ``payload_output`` from a ``ToolInstance`` or ``ToolSession`` into
a ``.md`` file.  In production the file is stored via Django's
DEFAULT_FILE_STORAGE backend (Cloudinary); locally it is written to
``MEDIA_ROOT/archives/md/``.

Filename convention: ``YYYYMMDD_<tool-slug>_<instance-or-session-id>.md``
"""
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils.text import slugify


def generate_markdown(instance):
    """Generate a Markdown file for a solo ``ToolInstance`` submission."""
    filename = (
        f"{instance.submitted_at.strftime('%Y%m%d')}"
        f"_{slugify(instance.tool_slug)}_{instance.id}.md"
    )
    relative_path = f"archives/md/{filename}"

    content_lines = [
        f"# {instance.tool_slug.replace('-', ' ').title()}",
        f"**Date:** {instance.submitted_at.strftime('%Y-%m-%d %H:%M')}",
        f"**Tool Version:** {instance.tool_version}",
        "\n--- \n",
        "## Results",
    ]
    for key, value in instance.payload_output.items():
        label = key.replace('_', ' ').title()
        content_lines.append(f"### {label}\n{value}\n")

    content_bytes = "\n".join(content_lines).encode('utf-8')

    if default_storage.exists(relative_path):
        default_storage.delete(relative_path)
    default_storage.save(relative_path, ContentFile(content_bytes))

    return relative_path


def generate_session_markdown(session):
    """Combine every participant's response into one Markdown file."""
    closed_stamp = (session.closed_at or session.created_at).strftime('%Y%m%d')
    filename = f"{closed_stamp}_{slugify(session.tool_slug)}_session_{session.id}.md"
    relative_path = f"archives/md/{filename}"

    title = session.tool_slug.replace('-', ' ').title()
    closed_at_str = session.closed_at.strftime('%Y-%m-%d %H:%M') if session.closed_at else '-'
    content_lines = [
        f"# {title} — Combined Session Results",
        f"**Hosted by:** {session.host.email if session.host else 'Unknown'}",
        f"**Closed at:** {closed_at_str}",
        f"**Tool version:** {session.tool_version}",
        "\n---\n",
    ]

    instances = session.instances.select_related('user').order_by('submitted_at', 'created_at')
    for inst in instances:
        marker = ' (host)' if inst.user_id == session.host_id else ''
        display = inst.user.email if inst.user_id else (inst.guest_name or 'Guest')
        content_lines.append(f"## {display}{marker}")
        if inst.payload_output:
            for key, value in inst.payload_output.items():
                label = key.replace('_', ' ').title()
                content_lines.append(f"### {label}\n{value}\n")
        else:
            content_lines.append("*No response submitted.*\n")
        content_lines.append("---\n")

    content_bytes = "\n".join(content_lines).encode('utf-8')

    if default_storage.exists(relative_path):
        default_storage.delete(relative_path)
    default_storage.save(relative_path, ContentFile(content_bytes))

    return relative_path
