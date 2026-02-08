import os
import snowflake.connector
from typing import Optional

_connection: Optional[snowflake.connector.SnowflakeConnection] = None

DATABASE = "AUTOGL_YIELD_OPTIMIZATION"
SCHEMA = "AUTOGL_YIELD_OPTIMIZATION"
WAREHOUSE = "AUTOGL_YIELD_OPTIMIZATION_WH"

def get_connection() -> snowflake.connector.SnowflakeConnection:
    global _connection
    if _connection is None or _connection.is_closed():
        connection_name = os.getenv("SNOWFLAKE_CONNECTION_NAME", "demo")
        _connection = snowflake.connector.connect(connection_name=connection_name)
        _connection.cursor().execute(f"USE DATABASE {DATABASE}")
        _connection.cursor().execute(f"USE SCHEMA {SCHEMA}")
        _connection.cursor().execute(f"USE WAREHOUSE {WAREHOUSE}")
    return _connection

def close_connection():
    global _connection
    if _connection and not _connection.is_closed():
        _connection.close()
        _connection = None

def execute_query(sql: str, params: tuple = None) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(sql, params)
        columns = [desc[0].lower() for desc in cursor.description] if cursor.description else []
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    finally:
        cursor.close()

def execute_scalar(sql: str, params: tuple = None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(sql, params)
        row = cursor.fetchone()
        return row[0] if row else None
    finally:
        cursor.close()
