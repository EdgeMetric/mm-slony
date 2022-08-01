from typing import List
from pydantic import BaseSettings
import os
class Settings(BaseSettings):
    REPLICATIONDB: str 
    REPLICATIONSCHEMA: List[str]
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
        env_file: str = 'config.ini'
        env_file_encoding: str = 'utf-8'
        
settings = Settings()

class Constant:
    TEMPLATE_PATH = f'{os.path.dirname(os.path.realpath(__file__))}/templates'
    all_templates = [
        'create.jinja2',
        'end.jinja2',
        'replication.jinja2',
        'switchover.jinja2'
    ]