"""
This module contains commonly used function accross the repo.
"""
from typing import List, Tuple
import psycopg2

from slonik.const import settings

def get_table_schema(cursor) -> List[Tuple[str, str]]:
    """
    returns list of schema and table names

    Args:
        cursor (cursor object): used for pg connection

    Returns:
        List[Tuple[str, str]]: list of tuple with data
    """

    pg_query = f"SELECT schemaname, tablename \
                FROM pg_catalog.pg_tables \
                where tableowner='{settings.TABLEOWNER}'"
    cursor.execute(pg_query)
    return cursor.fetchall()


def get_sequences(cursor) -> List[Tuple[str, str]]:
    """
    returns list of schema and sequence names

    Args:
        cursor (cursor object): used for pg connection

    Returns:
        List[Tuple[str, str]]: list of tuple with data
    """

    pg_query = f"SELECT  sequence_schema, sequence_name \
                FROM information_schema.sequences \
                where sequence_schema in {settings.REPLICATIONSCHEMA}"
    cursor.execute(pg_query)
    return cursor.fetchall()


def get_primary_key(cursor, table_name) -> str:
    """
    Returns primary key of given table
    """

    pg_query = f"SELECT pg_attribute.attname \
                FROM pg_index, pg_class, pg_attribute, pg_namespace \
                WHERE \
                pg_class.oid = '{table_name}'::regclass AND \
                indrelid = pg_class.oid AND \
                nspname = 'public' AND \
                pg_class.relnamespace = pg_namespace.oid AND \
                pg_attribute.attrelid = pg_class.oid AND \
                pg_attribute.attnum = any(pg_index.indkey) \
                AND indisprimary"

    cursor.execute(pg_query)
    records = cursor.fetchall()
    if len(records):
        (primary_key,) = records[0]
    else:
        primary_key = None

    return primary_key


def get_master_connection():
    """
    Returns psycopg2 connection object
    to master database

    Returns:
        connection: connection to database
    """
    master_conn = psycopg2.connect(
        dbname=settings.REPLICATIONDB,
        user=settings.MASTERUSER,
        password=settings.MASTERPWD,
        host=settings.MASTERHOST,
        port=settings.MASTERPORT,
    )

    return master_conn


def get_slave_connection():
    """
    Returns psycopg2 connection object
    to slave database

    Returns:
        connection: connection to database
    """

    slave_conn = psycopg2.connect(
        dbname=settings.REPLICATIONDB,
        user=settings.SLAVEUSER,
        password=settings.SLAVEPWD,
        host=settings.SLAVEHOST,
        port=settings.SLAVEPORT,
    )

    return slave_conn
