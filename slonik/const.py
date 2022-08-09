"""
This modules exposes commonly used constants
and configurations settings
"""
import os
from string import Template
from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    Contains settings read from
    config.ini file
    """
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
        """
        Specifies location of configuration file
        """
        env_file: str = f"{os.path.dirname(os.path.realpath(__file__))}/config.ini"
        env_file_encoding: str = "utf-8"


settings = Settings()


class Constant:
    """
    Contains hardcoded constants
    """
    TEMPLATE_PATH = f"{os.path.dirname(os.path.realpath(__file__))}/templates"
    all_templates = [
        "create.jinja2",
        "end.jinja2",
        "replication.jinja2",
        "switchover.jinja2",
    ]
    CONFIG_TEMPLATE_PATH = Template(
        f"{os.path.dirname(os.path.realpath(__file__))}/../slonik_config/$filename"
    )
