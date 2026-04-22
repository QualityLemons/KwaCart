import os
from django.conf import settings
from django.utils.text import slugify

def generate_markdown(instance):
    """
    Tactic 6: Transforms payload_output into a .md file.
    """
    # Define file naming convention (Tactic 6)
    filename = f"{instance.submitted_at.strftime('%Y%m%d')}_{slugify(instance.tool_slug)}_{instance.id}.md"
    relative_path = os.path.join('archives/md/', filename)
    full_path = os.path.join(settings.MEDIA_ROOT, relative_path)

    # Ensure directory exists
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    # Build Content
    content = [
        f"# {instance.tool_slug.replace('-', ' ').title()}",
        f"**Date:** {instance.submitted_at.strftime('%Y-%m-%d %H:%M')}",
        f"**Tool Version:** {instance.tool_version}",
        "\n--- \n",
        "## Results",
    ]

    # Dynamically iterate through structured output (Tactic 2)
    for key, value in instance.payload_output.items():
        label = key.replace('_', ' ').title()
        content.append(f"### {label}\n{value}\n")

    # Write file
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(content))

    return relative_path