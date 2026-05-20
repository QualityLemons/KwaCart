"""RTF export generator.

Converts ``payload_output`` from a ``ToolInstance`` or ``ToolSession`` into
a minimal ``.rtf`` file.

Storage strategy
----------------
In production (``CLOUDINARY_URL`` present) the file is uploaded directly via
the Cloudinary Python SDK with an explicit ``public_id`` so the asset path is
fully controlled regardless of the account's folder mode.  The ``secure_url``
returned by the API is stored on the model field — the download view then
redirects to that URL, avoiding any URL-reconstruction issues.

In local development the file is written to ``MEDIA_ROOT/archives/rtf/`` via
Django's ``default_storage`` (FileSystemStorage).

RTF encoding notes
------------------
- Backslashes, opening braces, and closing braces must be escaped.
- Newlines in user text are converted to ``\\line``.
- The file is written in UTF-8; the RTF header declares ``\\ansi\\ansicpg1252``.

Filename convention: ``YYYYMMDD_<tool-slug>_<instance-or-session-id>.rtf``
"""
import os

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils.text import slugify


def _rtf_escape(value):
    """Escape a string for safe inclusion in an RTF document."""
    return (
        str(value)
        .replace('\\', r'\\')
        .replace('{', r'\{')
        .replace('}', r'\}')
        .replace('\n', r' \line ')
    )


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


def generate_rtf(instance):
    """Generate an RTF file for a solo ``ToolInstance`` submission."""
    filename = (
        f"{instance.submitted_at.strftime('%Y%m%d')}"
        f"_{slugify(instance.tool_slug)}_{instance.id}.rtf"
    )
    relative_path = f"archives/rtf/{filename}"

    rtf_header = r"{\rtf1\ansi\deff0 {\fonttbl {\f0 Arial;}}\f0\fs24 "
    parts = [rtf_header]
    parts.append(r"\b " + instance.tool_slug.upper() + r"\b0 \line ")
    parts.append(f"Date: {instance.submitted_at.strftime('%Y-%m-%d')} \\line ")
    parts.append(r"\line -------------------------- \line ")

    for key, value in instance.payload_output.items():
        label = key.replace('_', ' ').title()
        parts.append(r"\b " + label + r": \b0 \line ")
        parts.append(f"{_rtf_escape(value)} \\line \\line ")

    parts.append("}")
    return _save_file(relative_path, "".join(parts).encode('utf-8'))


def generate_session_rtf(session):
    """Combine every participant's response into one RTF file."""
    closed_stamp = (session.closed_at or session.created_at).strftime('%Y%m%d')
    filename = f"{closed_stamp}_{slugify(session.tool_slug)}_session_{session.id}.rtf"
    relative_path = f"archives/rtf/{filename}"

    rtf_header = r"{\rtf1\ansi\deff0 {\fonttbl {\f0 Arial;}}\f0\fs24 "
    parts = [rtf_header]

    title = session.tool_slug.upper() + ' - COMBINED SESSION RESULTS'
    parts.append(r"\b " + title + r"\b0 \line ")
    parts.append(f"Hosted by: {_rtf_escape(session.host.email if session.host else 'Unknown')} \\line ")
    if session.closed_at:
        parts.append(f"Closed at: {session.closed_at.strftime('%Y-%m-%d %H:%M')} \\line ")
    parts.append(r"\line ========================== \line ")

    instances = session.instances.select_related('user').order_by('submitted_at', 'created_at')
    for inst in instances:
        marker = ' (host)' if inst.user_id == session.host_id else ''
        display = inst.user.email if inst.user_id else (inst.guest_name or 'Guest')
        parts.append(r"\b " + _rtf_escape(display + marker) + r"\b0 \line ")
        if inst.payload_output:
            for key, value in inst.payload_output.items():
                label = key.replace('_', ' ').title()
                parts.append(r"\b " + label + r": \b0 \line ")
                parts.append(f"{_rtf_escape(value)} \\line ")
        else:
            parts.append(r"\i No response submitted. \i0 \line ")
        parts.append(r"\line -------------------------- \line ")

    parts.append("}")
    return _save_file(relative_path, "".join(parts).encode('utf-8'))
