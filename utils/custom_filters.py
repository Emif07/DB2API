def sql_to_python(data_type: str) -> str:
    mapping = {
        "integer": "int",
        "text": "str",
        "timestamp without time zone": "datetime.datetime",
        # ... add other mappings as needed
    }
    return mapping.get(data_type, "Any")  # Default to 'Any' if type is not recognized
