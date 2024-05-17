translate_operator = {
    "=": ("filter", ""),
    ">": ("filter","__gt"),
    ">=": ("filter","__gte"),
    "<": ("filter","__lt"),
    "=<": ("filter","__lte"),
    "in": ("filter","__in"),
    "<>": ("exclude", ""),
}


def filter_queryset(queryset, filter_string):
    filters = filter_string.split(";")
    for f in filters:
        try:
            field_name, operator, clause = f.split()
            if field_name == "time":
                field_name = "date__time"
            if clause.startswith("("):
                clause = clause.strip("()").split(",")
            method, operator = translate_operator[operator]
            method = getattr(queryset, method)
            field_name__operator = f"{field_name}{operator}"
            queryset = method(**{field_name__operator: clause})
        except Exception:
            print("Error in filters!")
    return queryset