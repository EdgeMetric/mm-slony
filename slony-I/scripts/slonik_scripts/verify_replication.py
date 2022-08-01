from jinja2 import FileSystemLoader, Environment
import os
from const import settings, Constant
from utils import get_table_schema, get_sequences
import psycopg2


def main():

    db_name = settings.REPLICATIONDB
    
    schema_table_names = get_table_schema(db_name)
    schema_seq_names = get_sequences(db_name)
    try:
        master_conn = psycopg2.connect(dbname=db_name, user=settings.MASTERUSER, password=settings.MASTERPWD, host=settings.MASTERHOST, port=settings.MASTERPORT)
        slave_conn = psycopg2.connect(dbname=db_name, user=settings.SLAVEUSER, password=settings.SLAVEPWD, host=settings.SLAVEHOST, port=settings.SLAVEPORT)
        
        master_cur=master_conn.cursor()
        slave_cur=slave_conn.cursor()
        
        
        for schema, table in schema_table_names:
            pg_query = f"select * from {schema}.{table} limit 100000"
            
            master_cur.execute(pg_query)
            master_records = master_cur.fetchall()
            slave_cur.execute(pg_query)
            slave_records = slave_cur.fetchall()
            
            for master_record in master_records:
                if master_record not in slave_records:
                    print(f'Mismatch found for {table}, master: {master_record} is not found')
                    
        for schema, sequence in schema_seq_names:
            pg_query = f"select * from {schema}.{sequence} limit 100000"
            
            master_cur.execute(pg_query)
            master_records = master_cur.fetchall()
            slave_cur.execute(pg_query)
            slave_records = slave_cur.fetchall()
            
            for master_record in master_records:
                if master_record not in slave_records:
                    print(f'Mismatch found for {sequence}, master: {master_record} is not found')
                    
                    
        print(f'No mismatch found!')
            
            
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