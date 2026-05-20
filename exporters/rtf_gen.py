"""RTF export generator.

Converts ``payload_output`` from a ``ToolInstance`` or ``ToolSession`` into
a minimal ``.rtf`` file.  In production the file is stored via Django's
DEFAULT_FILE_STORAGE backend (Cloudinary); locally it is written to
``MEDIA_ROOT/archives/rtf/``.

RTF encoding notes
------------------
- Backslashes, opening braces, and closing braces must be escaped because
  RTF uses them as control character delimiters.
- Newlines in user text are converted to the RTF line-break sequence
  ``\\line`` so paragraph structure is preserved.
- The file is written in UTF-8; the RTF header declares ``\\ansi\\ansicpg1252``
  for broad reader compatibility.

Filename convention: ``YYYYMMDD_<tool-slug>_<instance-or-session-id>.rtf``
"""
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

    content_bytes = "".join(parts).encode('utf-8')

    if default_storage.exists(relative_path):
        default_storage.delete(relative_path)
    saved_path = default_storage.save(relative_path, ContentFile(content_bytes))

    return saved_path


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

    content_bytes = "".join(parts).encode('utf-8')

    if default_storage.exists(relative_path):
        default_storage.delete(relative_path)
    saved_path = default_storage.save(relative_path, ContentFile(content_bytes))

    return saved_path
