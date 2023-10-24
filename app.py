from connector import snowflake_login
from snowflake import connector
import streamlit as st


def title(s):
    st.text("")
    st.title(s)
    st.text("")


@st.cache_resource
def show_databases() -> list:
    return [
        database["name"]
        for database in conn.cursor(connector.DictCursor)
        .execute("SHOW TERSE DATABASES;")
        .fetchall()
    ]


@st.cache_resource
def show_schemas(database: str) -> list:
    return [
        schema["name"]
        for schema in conn.cursor(connector.DictCursor)
        .execute(f'SHOW TERSE SCHEMAS IN DATABASE "{database}";')
        .fetchall()
    ]


@st.cache_resource
def show_tables(database: str, schema: str) -> list:
    return [
        table["name"]
        for table in conn.cursor(connector.DictCursor)
        .execute(f'SHOW TERSE TABLES IN SCHEMA "{database}"."{schema}";')
        .fetchall()
    ]


@st.cache_resource
def show_columns(database: str, schema: str, table: str) -> list:
    return [
        column["column_name"]
        for column in conn.cursor(connector.DictCursor)
        .execute(f'SHOW TERSE COLUMNS IN TABLE "{database}"."{schema}"."{table}";')
        .fetchall()
    ]


@st.cache_resource
def show_warehouses():
    return [
        warehouse["name"]
        for warehouse in conn.cursor(connector.DictCursor)
        .execute(f"SHOW TERSE WAREHOUSES;")
        .fetchall()
    ]


st.title("Streamlit Log in Test with Customer")


with st.sidebar:
    conn = snowflake_login()

with st.sidebar:
    if conn:
        database = st.selectbox("Pick your database", [""] + show_databases())
        if database != "":
            schema = st.selectbox(
                "Pick your Schema", [""] + show_schemas(database=database)
            )
            if schema != "":
                table = st.selectbox(
                    "Pick your table",
                    [""] + show_tables(database=database, schema=schema),
                )
                if table != "":
                    st.write("You selected", database, schema, table)


with st.expander(label="Expand", expanded=True):
    if conn and database != "" and schema != "" and table != "":
        warehouse = st.selectbox("Pick your Warehouse", [""] + show_warehouses())
        if warehouse != "":
            conn.cursor(connector.DictCursor).execute(
                f"use warehouse {warehouse};"
            ).fetchall()