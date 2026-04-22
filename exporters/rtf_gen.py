def generate_rtf(instance):
    """
    Tactic 6: Transforms payload_output into a basic .rtf file.
    """
    filename = f"{instance.submitted_at.strftime('%Y%m%d')}_{slugify(instance.tool_slug)}_{instance.id}.rtf"
    relative_path = os.path.join('archives/rtf/', filename)
    full_path = os.path.join(settings.MEDIA_ROOT, relative_path)

    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    # RTF Header and basic styling
    rtf_header = r"{\rtf1\ansi\deff0 {\fonttbl {\f0 Arial;}}\f0\fs24 "
    content = [rtf_header]
    
    content.append(r"\b " + instance.tool_slug.upper() + r"\b0 \line ")
    content.append(f"Date: {instance.submitted_at.strftime('%Y-%m-%d')} \line ")
    content.append(r"\line -------------------------- \line ")

    for key, value in instance.payload_output.items():
        label = key.replace('_', ' ').title()
        content.append(r"\b " + label + r": \b0 \line ")
        # Escape special RTF characters in the value if necessary
        clean_value = str(value).replace('\n', r' \line ')
        content.append(f"{clean_value} \line \line ")

    content.append("}")

    with open(full_path, 'w') as f:
        f.write("".join(content))

    return relative_path