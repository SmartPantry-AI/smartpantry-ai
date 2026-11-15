def group_pantry_items(items):
    """Group pantry records by ingredient name without merging them."""
    grouped = {}

    for item in items:
        name = item["name"].strip().casefold()

        if name not in grouped:
            grouped[name] = []

        grouped[name].append(item)

    return grouped