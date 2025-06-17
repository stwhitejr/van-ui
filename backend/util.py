def convert_to_float(raw_value: int | str) -> float:
    return round(int(raw_value) / 1000.0, 2)


def convert_to_percentage(raw_value: int | str) -> str:
    percent = round(int(raw_value) / 10)
    return f"{percent}%"


def convert_minutes_to_duration(_minutes: int | str) -> str:
    minutes = int(_minutes)
    days = minutes // (24 * 60)
    if days >= 1:
        return f"{days} day{'s' if days > 1 else ''}"
    hours = minutes // 60
    if hours >= 1:
        return f"{hours} hour{'s' if hours > 1 else ''}"
    return f"{minutes} minute{'s' if minutes > 1 else ''}"
