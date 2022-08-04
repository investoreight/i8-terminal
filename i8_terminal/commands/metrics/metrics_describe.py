import click
from rich.console import Console
from rich.table import Table

from i8_terminal.commands.metrics import metrics
from i8_terminal.common.cli import pass_command
from i8_terminal.common.formatting import styling_markdown_text
from i8_terminal.common.metrics import get_metric_info
from i8_terminal.types.metric_param_type import MetricParamType


def get_metric_info_table(metric: str) -> Table:
    h_color = "cyan"
    metric_info = get_metric_info(metric)
    metric_info_table = Table(padding=(0, 0, 1, 1), box=None)
    metric_info_table.add_column(justify="right", width=25)
    metric_info_table.add_column(justify="left")
    metric_info_table.add_row(f"[{h_color}]Metric Name[/{h_color}]", metric)
    metric_info_table.add_row(f"[{h_color}]Display Name[/{h_color}]", metric_info["display_name"])
    metric_info_table.add_row(f"[{h_color}]Unit[/{h_color}]", metric_info["unit"])
    metric_info_table.add_row(f"[{h_color}]Type[/{h_color}]", metric_info["type"])
    metric_info_table.add_row(f"[{h_color}]Display Format[/{h_color}]", metric_info["display_format"])
    metric_info_table.add_row(f"[{h_color}]Default Period type[/{h_color}]", metric_info["default_period_type"])
    metric_info_table.add_row(
        f"[{h_color}]Url[/{h_color}]", f"[blue]https://docs.i8terminal.io/metrics/{metric}/[/blue]"
    )
    metric_info_table.add_row(f"[{h_color}]Description[/{h_color}]", styling_markdown_text(metric_info["description"]))
    if metric_info["remarks"]:
        metric_info_table.add_row(f"[{h_color}]Remarks[/{h_color}]", styling_markdown_text(metric_info["remarks"]))
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
