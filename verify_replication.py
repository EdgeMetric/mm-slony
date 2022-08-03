import psycopg2

from slonik.const import settings
from slonik.utils import get_primary_key, get_table_schema, get_sequences


def main():

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

        mismatch_found = False
        for schema, table in schema_table_names:
            pg_query = f"select * from {schema}.{table} limit 100000"

            master_cur.execute(pg_query)
            master_records = master_cur.fetchall()
            slave_cur.execute(pg_query)
            slave_records = slave_cur.fetchall()

            for master_record in master_records:
                if master_record not in slave_records:
                    print(
                        f"Mismatch found for {table}, master: {master_record} is not found"
                    )
                    mismatch_found = True
                    break

        for schema, sequence in schema_seq_names:
            pg_query = f"select * from {schema}.{sequence} limit 100000"

            master_cur.execute(pg_query)
            master_record = master_cur.fetchall()[0]
            slave_cur.execute(pg_query)
            slave_record = slave_cur.fetchall()[0]

            (
                seq_name,
                master_last_val,
                start_val,
                inc_by,
                min_val,
                max_val,
                cache_val,
                master_log_cnt,
                is_cycled,
                master_is_called,
            ) = master_record  # schema for sequences in pg 9.6
            (
                slave_last_val,
                slave_log_cnt,
                slave_is_called,
            ) = slave_record  # schema for sequences in pg 14
            if master_last_val != slave_last_val:
                print(
                    f"Mismatch found for {sequence}, master: {master_record} is not matched by slave {slave_record}"
                )

            for tab_schema, table in schema_table_names:
                primary_key = get_primary_key(master_cur, f'{schema}.{table}')
                assumed_seq_name = f'{table}_{primary_key}_seq'
                if tab_schema == schema and assumed_seq_name == sequence:
                    master_pg_query = f"select * from {tab_schema}.{table} where {primary_key}={master_last_val}"
                    master_cur.execute(master_pg_query)
                    master_records = master_cur.fetchall()
                    slave_pg_query = f"select * from {tab_schema}.{table} where {primary_key}={slave_last_val}"
                    slave_cur.execute(slave_pg_query)
                    slave_records = slave_cur.fetchall()
                    if master_records != slave_records:
                        print(
                            f"Primary key do not match for table {table}-> \
                              \n master: {master_records}\
                              \n slave: {slave_records}"
                        )
                    break

        if not mismatch_found:
            print(f"No mismatch found!")

    except (Exception, psycopg2.Error) as error:
        print("Error fetching data from PostgreSQL table", error)

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
