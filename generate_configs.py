"""
This module generates slonik configurations.
This requires access to both master and slave db clusters.
"""
import os

from jinja2 import FileSystemLoader, Environment
from slonik.const import settings, Constant
from slonik.utils import get_master_connection, get_table_schema, get_sequences


def main():
    """
    Generate slonik configurations
    """

    master_conn = get_master_connection()
    master_cur = master_conn.cursor()

    schema_table_names = get_table_schema(master_cur)
    schema_seq_names = get_sequences(master_cur)

    template_loader = FileSystemLoader(
        searchpath=f"{os.path.dirname(os.path.realpath(__file__))}/slonik/templates"
    )
    template_env = Environment(loader=template_loader)

    var_map = {
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
        template = template_env.get_template(template_file)

        output_text = template.render(var_map)
        outputfp = Constant.CONFIG_TEMPLATE_PATH.substitute(
            filename=template_file.split(".", maxsplit=1)[0]
        )
        with open(outputfp, "w", encoding="utf-8") as output_file_fp:
            output_file_fp.write(output_text)


if __name__ == "__main__":
    main()
