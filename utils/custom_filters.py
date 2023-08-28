from typing import Dict

def map_sqlalchemy_type(column_name: str, pg_type: str, enums: Dict[str, Dict[str, str]]) -> str:
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
    
    # If the PostgreSQL type is 'USER-DEFINED', check if the column_name is one of the enums
    if pg_type == 'USER-DEFINED' and column_name in enums:
        enum_name = enums[column_name]["name"]
        return f"Enum({enum_name})"
    
    return mapping.get(pg_type, "String")  # Default to String if type not found
