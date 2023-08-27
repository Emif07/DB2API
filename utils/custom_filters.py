def map_sqlalchemy_type(pg_type: str) -> str:
    mapping = {
        "uuid": "UUID",
        "character varying": "String",
        "varchar": "String",
        "text": "Text",
        "char": "CHAR",
        "character": "CHAR",
        "timestamp with time zone": "DateTime(timezone=True)",
        "timestamp without time zone": "DateTime",
        "date": "Date",
        "integer": "Integer",
        "bigint": "BigInteger",
        "smallint": "SmallInteger",
        "numeric": "Numeric",
        "decimal": "Numeric",
        "real": "Float",
        "double precision": "Float",
        "boolean": "Boolean",
        "bytea": "LargeBinary",
        "json": "JSON",
        "jsonb": "JSONB",
        "interval": "Interval",
        "time without time zone": "Time",
        "time with time zone": "Time(timezone=True)",
        "array": "ARRAY",  # This might require more specifics depending on the array type
        "inet": "INET",
        "cidr": "CIDR",
        "macaddr": "MACADDR",
        "tsvector": "TSVECTOR",
        # ... any other specific data types you use
    }
    return mapping.get(pg_type, "String")  # Default to String if type not found
