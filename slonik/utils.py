import subprocess
import os
from typing import List, Tuple

from slonik.const import settings


def get_table_schema(db_name: str) -> List[Tuple[str, str]]:

    table_names_fp = "/tmp/table_names"

    subprocess.run(
        [
            "psql",
            "-t",
            "-d",
            db_name,
            "-c",
            f"COPY (SELECT schemaname, tablename FROM pg_catalog.pg_tables where tableowner='{settings.TABLEOWNER}') TO '{table_names_fp}'",
        ],
        capture_output=True,
    )

    table_names_read = open(table_names_fp)
    table_names = table_names_read.readlines()
    table_seq_names = []

    for table in table_names:
        seq_name = table.split("\t")[0].strip()
        table_name = table.split("\t")[1].strip()
        table_seq_names.append((seq_name, table_name))

    return table_seq_names


def get_sequences(db_name: str) -> List[Tuple[str, str]]:
    seq_names_fp = "/tmp/seq_names"

    subprocess.run(
        [
            "psql",
            "-t",
            "-d",
            db_name,
            "-c",
            f"COPY (SELECT  sequence_schema, sequence_name FROM information_schema.sequences where sequence_schema in {settings.REPLICATIONSCHEMA}) TO '{seq_names_fp}'",
        ],
        capture_output=True,
    )

    seq_names_read = open(seq_names_fp)
    seq_names = seq_names_read.readlines()
    schema_seq_names = []

    for seq in seq_names:
        sechma_name = seq.split("\t")[0].strip()
        sequence_name = seq.split("\t")[1].strip()
        schema_seq_names.append((sechma_name, sequence_name))

    return schema_seq_names


def get_primary_key(db_name: str, table_name: str) -> str:
    table_primary_key_fp = "/tmp/primary_key"

    subprocess.run(
        [
            "psql",
            "-t",
            "-d",
            db_name,
            "-c",
            f"COPY (SELECT \
                pg_attribute.attname, \
                FROM pg_index, pg_class, pg_attribute, pg_namespace \
                WHERE\
                pg_class.oid = '{table_name}'::regclass AND\
                indrelid = pg_class.oid AND\
                nspname = 'public' AND\
                pg_class.relnamespace = pg_namespace.oid AND\
                pg_attribute.attrelid = pg_class.oid AND\
                pg_attribute.attnum = any(pg_index.indkey)\
                AND indisprimary;\
                ) TO '{table_primary_key_fp}'",
        ],
        capture_output=True,
    )
    primary_key_read = open(table_primary_key_fp)
    primary_key = primary_key_read.readline()

    return primary_key
