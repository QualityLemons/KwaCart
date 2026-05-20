"""Markdown export generator.

Converts ``payload_output`` from a ``ToolInstance`` or ``ToolSession`` into
a ``.md`` file.

Storage strategy
----------------
In production (``CLOUDINARY_URL`` present) the file is uploaded directly via
the Cloudinary Python SDK with an explicit ``public_id`` so the asset path is
fully controlled regardless of the account's folder mode.  The ``secure_url``
returned by the API is stored on the model field — the download view then
redirects to that URL, avoiding any URL-reconstruction issues.

In local development the file is written to ``MEDIA_ROOT/archives/md/`` via
Django's ``default_storage`` (FileSystemStorage).

Filename convention: ``YYYYMMDD_<tool-slug>_<instance-or-session-id>.md``
"""
import os

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils.text import slugify


def _save_file(relative_path, content_bytes):
    """Upload content to Cloudinary (production) or local storage (development).

    Returns the value to store on the model field:
    - production: the Cloudinary ``secure_url`` (starts with ``https://``)
    - development: the relative filesystem path
    """
    if os.environ.get('CLOUDINARY_URL'):
        import cloudinary.uploader
        result = cloudinary.uploader.upload(
            content_bytes,
            resource_type='raw',
            public_id=relative_path,
            overwrite=True,
            use_filename=False,
            unique_filename=False,
        )
        return result['secure_url']
    if default_storage.exists(relative_path):
        default_storage.delete(relative_path)
    return default_storage.save(relative_path, ContentFile(content_bytes))


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

    return _save_file(relative_path, "\n".join(content_lines).encode('utf-8'))


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

        # Multimedia attachments — include transcriptions as first-class text;
        # fall back to a plain hyperlink when no transcription was provided.
        for att in (inst.attachments or []):
            att_type = att.get('type', 'attachment')
            att_name = att.get('name', att_type)
            att_url  = att.get('url', '')
            transcription = (att.get('transcription') or '').strip()

            if att_type == 'image':
                label = 'Symbol board / image'
            else:
                label = 'Audio clip'

            if transcription:
                content_lines.append(f"**{label} — transcription:**\n\n> {transcription}\n")
            elif att_url:
                content_lines.append(f"**{label}:** [{att_name}]({att_url})\n")

        content_lines.append("---\n")

    return _save_file(relative_path, "\n".join(content_lines).encode('utf-8'))
