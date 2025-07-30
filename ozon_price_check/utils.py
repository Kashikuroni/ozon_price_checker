from datetime import datetime


def to_camel(s: str) -> str:
    parts = s.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


def normalize(strings: str | list[str]) -> str | list[str]:
    """Normalize string(s) by converting to lowercase and removing extra whitespace."""
    if isinstance(strings, str):
        return " ".join(strings.strip().split()).lower()
    elif isinstance(strings, list):
        return [" ".join(title.strip().split()).lower() for title in strings]
    else:
        raise TypeError("Expected a string or a list of strings")


def get_current_date() -> str:
    """Get current date in DD.MM.YYYY format."""
    current_date = datetime.now()
    formatted_date = current_date.strftime("%d.%m.%Y")
    return formatted_date
