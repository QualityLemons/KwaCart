from .md_gen import generate_markdown
from .rtf_gen import generate_rtf

def run_export_pipeline(instance):
    """
    Updates the instance with generated file paths.
    """
    try:
        instance.md_file = generate_markdown(instance)
        instance.rtf_file = generate_rtf(instance)
        # Note: HTML generation usually happens via a Django template view, 
        # but we can store the path here if we pre-render it.
        instance.save()
    except Exception as e:
        # Tactic 8: Audit Logging
        print(f"Export Error for Instance {instance.id}: {str(e)}")