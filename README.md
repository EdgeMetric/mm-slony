# mm-slony
mm-slony is slonik configuration generator for PostgreSQL replication via Slony-I

## Getting Started
Create a config.ini file in slonik/config.ini with the following values:
<ol>
<li>REPLICATIONDB: name of the database to replicate </li>
<li>REPLICATIONSCHEMA: List of schemas, usually public or custom schemas</li>
<li>TABLEOWNER: Owner of table, used for connecting the nodes</li>
<li>CLUSTER: name of the replication cluster, used as internal namespace by Slony </li>
<li>MASTERHOST: Host ip address of master database cluster </li>
<li>MASTERPORT: Postgres/connection pooler port of master database cluster, usually 5432 </li>
<li>MASTERUSER: Master role for connecting to db, used for creating stored procedures by Slony</li>
<li>MASTERPWD: Master role password </li>
<li>SLAVEHOST: Host ip address of slave database cluster </li>
<li>SLAVEPORT: Postgres/connection pooler port of slave database cluster, usually 5432 </li>
<li>SLAVEUSER: Slave role for connecting to db, used for creating stored procedures by Slony </li>
<li>SLAVEPWD: Slave role password </li>
</ol>

Clone this repo in master instance. Ensure the postgresql is up and running and psql client is installed.
 

## Installation and usage
<ol>
<li> Install dependencies in virtualenv. </li>

```bash
pip install -r requirements.txt
```

<li> Generate configuration files. </li>
Become a postgres user and run

```bash
python generate_config.py
```
</ol>
Generated configuration files can be found in slonik_config folder.
There will be four files generated:
<ol>
<li> create: this configuration file can be used to create and init replication cluster </li>
<li> run: starts replication </li>
<li> switchover: switchover cluster (make master as slave and vice versa)</li>
<li> end: end replication</li>
</ol>

Run any of above configuration files by calling slonik:

As postgres user, run:

```bash
/usr/lib/postgresql/<PG_VERSION>/bin/slonik configuration_file_path
```

where configuration_file_path is the path to the configuration file.

## Verify replication
This is to be run post switchover
Become a postgres user and run

```bash
python verify_replication.py
```