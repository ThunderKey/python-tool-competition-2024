def some_method(number: int) -> str:
    if number > 0:
        return f"{number * 5}"
    return f"{number - 3}"


def other_method(number: int) -> int:
    total = 0
    for i in range(number):
        total += i
    return total
