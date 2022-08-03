"""
This modules does sanity checks on replicated tables.
Note: This should ideally be run
after switching over slave as new master
"""
import traceback
from typing import Tuple
import psycopg2

from slonik.const import settings
from slonik.utils import get_primary_key, get_table_schema, get_sequences


def verify_table_data(
    master_cur, slave_cur, schema_table_names: str
) -> Tuple[int, int, int]:
    """
    Verifies if table has exactly same data.
    This should match during replication.
    Default: limit of 100k is applied

    Args:
        master_cur (cursor): cursor to connect to master
        slave_cur (cursor): cursor to connect to slave
        schema_table_names (str): list of schema/table names

    Returns:
        Tuple[int, int, int]: returns stats of comparision
    """
    total_tables = len(schema_table_names)
    matched_tables, unmatched_tables = 0, 0
    for schema, table in schema_table_names:
        pg_query = f"select * from {schema}.{table} limit 100000"

        master_cur.execute(pg_query)
        master_records = master_cur.fetchall()
        slave_cur.execute(pg_query)
        slave_records = slave_cur.fetchall()
        found_mismatch = False
        for master_record in master_records:
            if master_record not in slave_records:
                print(
                    f"Mismatch found for {table}, master: {master_record} is not found"
                )
                unmatched_tables += 1
                found_mismatch = True
                break
        if not found_mismatch:
            matched_tables += 1

    return (total_tables, matched_tables, unmatched_tables)


def verify_sequence_data(
    master_cur, slave_cur, schema_seq_names: str, schema_table_names: str
) -> Tuple[int, int, int]:
    """
    Verifies if table has exactly same data.
    This should match during replication.
    Default: limit of 100k is applied

    Args:
        master_cur (cursor): cursor to connect to master
        slave_cur (cursor): cursor to connect to slave
        schema_seq_names (str): list of schema/sequence names
        schema_table_names(str): list of schema/table names

    Returns:
        Tuple[int, int, int]: returns stats of comparision
    """
    total_seq = len(schema_seq_names)
    matched_seq, unmatched_seq = 0, 0
    for schema, sequence in schema_seq_names:
        pg_query = f"select * from {schema}.{sequence} limit 100000"

        master_cur.execute(pg_query)
        master_record = master_cur.fetchall()[0]
        slave_cur.execute(pg_query)
        slave_record = slave_cur.fetchall()[0]

        (seq_name, master_last_val, _) = master_record  # schema for sequences in pg 9.6
        (slave_last_val, _) = slave_record  # schema for sequences in pg 14
        if master_last_val != slave_last_val:
            print(
                f"Mismatch found for {sequence}, \
                    master: {master_record} is not matched by slave {slave_record}"
            )

        for tab_schema, table in schema_table_names:
            if tab_schema != schema:
                continue

            primary_key = get_primary_key(master_cur, f"{tab_schema}.{table}")
            assumed_seq_name = f"{table}_{primary_key}_seq"
            if tab_schema == schema and assumed_seq_name == sequence:
                master_pg_query = f"select * from \
                    {tab_schema}.{table} where {primary_key}={master_last_val}"
                master_cur.execute(master_pg_query)
                master_records = master_cur.fetchall()
                slave_pg_query = f"select * from \
                    {tab_schema}.{table} where {primary_key}={slave_last_val}"
                slave_cur.execute(slave_pg_query)
                slave_records = slave_cur.fetchall()
                if master_records != slave_records:
                    print(
                        f"Primary key do not match for table {table}-> \
                        \n master: {master_records}\
                        \n slave: {slave_records}"
                    )
                    unmatched_seq += 1
                else:
                    matched_seq += 1

                break

    return (total_seq, matched_seq, unmatched_seq)


def main():
    """
    Runs tests on master and slave tables and
    verifies if primary key sequence matches.
    """

    db_name = settings.REPLICATIONDB

    schema_table_names = get_table_schema(db_name)
    schema_seq_names = get_sequences(db_name)
    try:
        master_conn = psycopg2.connect(
            dbname=db_name,
            user=settings.MASTERUSER,
            password=settings.MASTERPWD,
            host=settings.MASTERHOST,
            port=settings.MASTERPORT,
        )
        slave_conn = psycopg2.connect(
            dbname=db_name,
            user=settings.SLAVEUSER,
            password=settings.SLAVEPWD,
            host=settings.SLAVEHOST,
            port=settings.SLAVEPORT,
        )

        master_cur = master_conn.cursor()
        slave_cur = slave_conn.cursor()

        total_tables, matched_tables, unmatched_tables = verify_table_data(
            master_cur, slave_cur, schema_table_names
        )
        total_seq, matched_seq, unmatched_seq = verify_sequence_data(
            master_cur, slave_cur, schema_seq_names, schema_table_names
        )

        print(
            f"Out of {total_seq} sequences, \
                {matched_seq} got matched and {unmatched_seq} got unmatched"
        )
        print(
            f"Out of {total_tables} tables, \
                {matched_tables} got matched and {unmatched_tables} got unmatched"
        )
        if total_seq == matched_seq and total_tables == matched_tables:
            print("No mismatch found!")

    except (Exception, psycopg2.Error) as error:
        print("Error fetching data from PostgreSQL table", error)
        print(traceback.format_exc())

    finally:
        if master_conn:
            master_cur.close()
            master_conn.close()

        if slave_conn:
            slave_cur.close()
            slave_conn.close()

        print("PostgreSQL connection is closed \n")


if __name__ == "__main__":
    main()
