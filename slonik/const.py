import os
from pydantic import BaseSettings


class Settings(BaseSettings):
    REPLICATIONDB: str
    REPLICATIONSCHEMA: str
    TABLEOWNER: str
    CLUSTER: str

    MASTERHOST: str
    MASTERPORT: str
    MASTERUSER: str
    MASTERPWD: str

    SLAVEHOST: str
    SLAVEPORT: str
    SLAVEUSER: str
    SLAVEPWD: str

    class Config:
        env_file: str = f"{os.path.dirname(os.path.realpath(__file__))}/config.ini"
        env_file_encoding: str = "utf-8"


settings = Settings()


class Constant:
    TEMPLATE_PATH = f"{os.path.dirname(os.path.realpath(__file__))}/templates"
    all_templates = [
        "create.jinja2",
        "end.jinja2",
        "replication.jinja2",
        "switchover.jinja2",
    ]
