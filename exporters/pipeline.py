from .md_gen import generate_markdown, generate_session_markdown
from .rtf_gen import generate_rtf, generate_session_rtf


def run_export_pipeline(instance):
    """Generate per-instance MD and RTF exports for a solo submission."""
    try:
        instance.md_file = generate_markdown(instance)
        instance.rtf_file = generate_rtf(instance)
        instance.save()
    except Exception as e:
        print(f"Export Error for Instance {instance.id}: {str(e)}")


def run_session_export_pipeline(session):
    """Generate combined MD and RTF exports for a closed collaborative session."""
    try:
        session.md_file = generate_session_markdown(session)
        session.rtf_file = generate_session_rtf(session)
        session.save()
    except Exception as e:
        print(f"Export Error for Session {session.id}: {str(e)}")
