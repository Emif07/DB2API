def map_sqlalchemy_type(pg_type: str) -> str:
    mapping = {
        "uuid": "UUID",
        "character varying": "String",
        "varchar": "String",
        "timestamp with time zone": "DateTime(timezone=True)",
        "integer": "Integer",
        # ... add more mappings as required
    }
    return mapping.get(pg_type, "String")  # Default to String if type not found
