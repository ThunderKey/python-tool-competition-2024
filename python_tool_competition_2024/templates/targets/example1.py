"""First example file."""


def some_method(number: int) -> str:
    """Return a string of the manipulated number."""
    if number > 0:
        return f"{number * 5}"
    return f"{number - 3}"


def other_method(number: int) -> int:
    """Return the number calculated by a for loop."""
    total = 0
    for i in range(number):
        total += i
    return total
