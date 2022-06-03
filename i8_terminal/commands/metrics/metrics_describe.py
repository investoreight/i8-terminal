import click
from rich.console import Console
from rich.table import Table

from i8_terminal.commands.metrics import metrics
from i8_terminal.common.cli import pass_command
from i8_terminal.common.metrics import get_metric_info
from i8_terminal.types.metric_param_type import MetricParamType


def get_metric_info_table(metric: str) -> Table:
    metric_display_name, metric_unit, metric_short_desc = get_metric_info(metric)
    metric_info_table = Table.grid()
    metric_info_table.add_column(justify="left", width=18)
    metric_info_table.add_column(justify="left")
    metric_info_table.add_row("Metric Name:", metric)
    metric_info_table.add_row("Display Name:", metric_display_name)
    metric_info_table.add_row("Unit:", metric_unit)
    metric_info_table.add_row("Description:", metric_short_desc)
    return metric_info_table


@metrics.command()
@click.option("--name", "-n", type=MetricParamType(), required=True, help="Metric name.")
@pass_command
def describe(name: str) -> None:
    """Describe the metric information.

    Examples:

    `i8 metrics describe --name basic_eps`
    """
    console = Console()
    metric_info = get_metric_info_table(name)
    console.print(metric_info)
