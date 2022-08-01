from jinja2 import FileSystemLoader, Environment
import os
from const import settings, Constant
from utils import get_table_schema, get_sequences


def main():

    db_name = settings.REPLICATIONDB
    schema_table_names = get_table_schema(db_name)
    schema_seq_names = get_sequences(db_name)
    cwd = os.getcwd()
    templateLoader = FileSystemLoader(searchpath=f"{cwd}/templates")
    templateEnv = Environment(loader=templateLoader)

    VAR_MAP = {
        "CLUSTERNAME": settings.CLUSTER,
        "REPLICATIONDB": settings.REPLICATIONDB,
        "MASTERHOST": settings.MASTERHOST,
        "MASTERUSER": settings.MASTERUSER,
        "MASTERPWD": settings.MASTERPWD,
        "SLAVEHOST": settings.SLAVEHOST,
        "SLAVEUSER": settings.SLAVEUSER,
        "SLAVEPWD": settings.SLAVEPWD,
        "REPLICATIONTABLES": schema_table_names,
        "REPLICATIONSEQUENCE": schema_seq_names,
    }

    for template_file in Constant.all_templates:
        template = templateEnv.get_template(template_file)

        outputText = template.render(VAR_MAP)
        outputfp = f"{cwd}/slonik_config/{template_file.split('.')[0]}"
        with open(outputfp, "w") as f:
            f.write(outputText)


if __name__ == "__main__":
    main()
