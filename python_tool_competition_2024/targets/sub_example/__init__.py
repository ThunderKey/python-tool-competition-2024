"""The sub example pacakge."""


def helper(text: str) -> str | None:
    """Add an exclamation mark if the text is not empty, `None` otherwise."""
    if text:
        return text + "!"
    return None
