import click
from rich.console import Console
from rich.table import Table

from i8_terminal.commands.metrics import metrics
from i8_terminal.common.cli import pass_command
from i8_terminal.common.metrics import get_metric_info
from i8_terminal.types.metric_param_type import MetricParamType


def get_metric_info_table(metric: str) -> Table:
    header_color = "cyan"
    metric_info = get_metric_info(metric)
    metric_info_table = Table(padding=(0, 1), box=None)
    metric_info_table.add_column(justify="right", width=25)
    metric_info_table.add_column(justify="left")
    metric_info_table.add_row(f"[{header_color}]Metric Name[/{header_color}]", metric)
    metric_info_table.add_row(f"[{header_color}]Display Name[/{header_color}]", metric_info["display_name"])
    metric_info_table.add_row(f"[{header_color}]Unit[/{header_color}]", metric_info["unit"])
    metric_info_table.add_row(f"[{header_color}]Type[/{header_color}]", metric_info["type"])
    metric_info_table.add_row(f"[{header_color}]Display Format[/{header_color}]", metric_info["display_format"])
    metric_info_table.add_row(f"[{header_color}]Url[/{header_color}]", f"https://docs.i8terminal.io/metrics/{metric}/")
    metric_info_table.add_row(f"[{header_color}]Description[/{header_color}]", metric_info["description"])
    metric_info_table.add_row(f"[{header_color}]Remarks[/{header_color}]", "")
    return metric_info_table


@metrics.command()
@click.option("--name", "-n", type=MetricParamType(), required=True, help="Metric name.")
@pass_command
def describe(name: str) -> None:
    """
    Describe the metric information.

    Examples:

    `i8 metrics describe --name basic_eps`
    """
    console = Console()
    metric_info = get_metric_info_table(name)
    console.print(metric_info)
