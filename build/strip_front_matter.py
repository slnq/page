def strip_front_matter(text: str) -> str:
    lines = text.splitlines()
    if len(lines) > 0 and lines[0].strip() == "---":
        try:
            end_idx = lines[1:].index("---") + 1
            return "\n".join(lines[end_idx+1:])
        except ValueError:
            return text
    return text