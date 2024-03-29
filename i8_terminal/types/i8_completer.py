from typing import Callable, Iterable

import click
from click import Group
from click.decorators import F
from click_repl import ClickCompleter, text_type
from prompt_toolkit.completion import CompleteEvent, Completion
from prompt_toolkit.document import Document

from i8_terminal.common.utils import get_matched_params
from i8_terminal.types.auto_complete_choice import AutoCompleteChoice
from i8_terminal.types.chart_param_type import ChartParamType
from i8_terminal.types.command_parser import CommandParser
from i8_terminal.types.fin_identifier_param_type import FinancialsIdentifierParamType
from i8_terminal.types.fin_period_param_type import FinancialsPeriodParamType
from i8_terminal.types.fin_statement_param_type import FinancialStatementParamType
from i8_terminal.types.indicator_param_type import IndicatorParamType
from i8_terminal.types.market_indice_param_type import MarketIndiceParamType
from i8_terminal.types.metric_identifier_param_type import MetricIdentifierParamType
from i8_terminal.types.metric_param_type import MetricParamType
from i8_terminal.types.metric_view_param_type import MetricViewParamType
from i8_terminal.types.output_param_type import OutputParamType
from i8_terminal.types.period_type_param_type import PeriodTypeParamType
from i8_terminal.types.price_period_param_type import PricePeriodParamType
from i8_terminal.types.screening_condition_param_type import ScreeningConditionParamType
from i8_terminal.types.screening_profile_param_type import ScreeningProfileParamType
from i8_terminal.types.sort_order_param_type import SortOrderParamType
from i8_terminal.types.ticker_param_type import TickerParamType
from i8_terminal.types.user_watchlist_tickers_param_type import (
    UserWatchlistTickersParamType,
)
from i8_terminal.types.user_watchlists_param_type import UserWatchlistsParamType


class I8Completer(ClickCompleter):
    def __init__(self, cli: Callable[[F], Group]) -> None:
        self.cli = cli

    def get_completions(self, document: Document, complete_event: CompleteEvent = None) -> Iterable[Completion]:
        ctx = CommandParser(self.cli).parse(document)
        if not ctx:
            return None

        command = ctx.click_ctx.command

        choices = []
        filter_choices = True

        if ctx.last_option or not document.is_cursor_at_the_end:
            matched_params = get_matched_params(ctx, command, document)
            if matched_params and len(matched_params) > 0:
                matched_param = matched_params[0]
                if type(matched_param.type) is click.types.Choice:
                    for c in matched_param.type.choices:
                        choices.append(Completion(text_type(c), -len(ctx.incomplete)))

                elif type(matched_param.type) in [
                    AutoCompleteChoice,
                    FinancialStatementParamType,
                    PeriodTypeParamType,
                    PricePeriodParamType,
                    FinancialsPeriodParamType,
                    ChartParamType,
                    OutputParamType,
                    MarketIndiceParamType,
                    SortOrderParamType,
                ]:
                    filter_choices = False
                    parts = ctx.incomplete.split(",")
                    incomplete = parts[-1] if len(parts) > 0 else " "
                    for (ticker, name) in matched_param.type.get_suggestions(  # type: ignore
                        incomplete if incomplete else " ", True
                    ):
                        choices.append(Completion(text_type(ticker), -len(incomplete), display_meta=name))
                elif type(matched_param.type) in [TickerParamType, UserWatchlistTickersParamType]:
                    filter_choices = False
                    include_peers = matched_param.name != "ticker"
                    if matched_param.name == "ticker":
                        incomplete = ctx.incomplete
                    else:
                        parts = ctx.incomplete.split(",")
                        incomplete = parts[-1] if len(parts) > 0 else " "
                    for (ticker, name) in matched_param.type.get_suggestions(  # type: ignore
                        incomplete if incomplete else " ", True, include_peers
                    ):
                        choices.append(Completion(text_type(ticker), -len(incomplete), display_meta=name))
                elif type(matched_param.type) in [MetricParamType, IndicatorParamType]:
                    filter_choices = False
                    parts = ctx.incomplete.split(",")
                    incomplete = parts[-1] if len(parts) > 0 else " "
                    for (metric, name) in matched_param.type.get_suggestions(  # type: ignore
                        incomplete if incomplete else " ", True
                    ):
                        choices.append(Completion(text_type(metric.lower()), -len(incomplete), display_meta=name))

                elif type(matched_param.type) is FinancialsIdentifierParamType:
                    param_type = "ticker"
                    filter_choices = False
                    parts = ctx.incomplete.split(",")
                    incomplete = parts[-1] if len(parts) > 0 else " "
                    sub_parts = incomplete.split("-")
                    if len(sub_parts) > 2:
                        param_type = "quarter"
                    elif len(sub_parts) > 1:
                        param_type = "year"
                    else:
                        param_type = "ticker"
                    incomplete = sub_parts[-1] if len(sub_parts) > 0 else " "
                    for (idf, name) in matched_param.type.get_suggestions(
                        incomplete if incomplete else " ", False, param_type
                    ):
                        choices.append(Completion(text_type(idf.upper()), -len(incomplete), display_meta=name))
                elif type(matched_param.type) is UserWatchlistsParamType:
                    filter_choices = False
                    parts = ctx.incomplete.split(",")
                    incomplete = parts[-1] if len(parts) > 0 else " "
                    for (watchlist, desc) in matched_param.type.get_suggestions(
                        incomplete if incomplete else " ", True
                    ):
                        choices.append(Completion(text_type(watchlist), -len(incomplete)))
                elif type(matched_param.type) is MetricViewParamType:
                    filter_choices = False
                    parts = ctx.incomplete.split(",")
                    incomplete = parts[-1] if len(parts) > 0 else " "
                    for (metric_view, desc) in matched_param.type.get_suggestions(
                        incomplete if incomplete else " ", True
                    ):  # type: ignore
                        choices.append(Completion(text_type(metric_view), -len(incomplete), display_meta=desc))
                elif type(matched_param.type) is ScreeningProfileParamType:
                    filter_choices = False
                    parts = ctx.incomplete.split(",")
                    incomplete = parts[-1] if len(parts) > 0 else " "
                    for (profile, desc) in matched_param.type.get_suggestions(
                        incomplete if incomplete else " ", True
                    ):  # type: ignore
                        choices.append(Completion(text_type(profile), -len(incomplete), display_meta=desc))
                elif type(matched_param.type) is MetricIdentifierParamType:
                    param_type = "metric"
                    filter_choices = False
                    parts = ctx.incomplete.split(",")
                    incomplete = parts[-1] if len(parts) > 0 else " "
                    sub_parts = incomplete.split(".")
                    if len(sub_parts) > 1:
                        param_type = "period"
                    else:
                        param_type = "metric"
                    incomplete = sub_parts[-1] if len(sub_parts) > 0 else " "
                    for (idf, name) in matched_param.type.get_suggestions(
                        incomplete if incomplete else " ", False, param_type, sub_parts[0]
                    ):
                        choices.append(Completion(text_type(idf), -len(incomplete), display_meta=name))
                elif type(matched_param.type) is ScreeningConditionParamType:
                    param_type = "metric"
                    filter_choices = False
                    parts = ctx.incomplete.split(",")
                    incomplete = parts[-1] if len(parts) > 0 else " "
                    condition_sub_parts = incomplete.split(":")
                    period_sub_parts = condition_sub_parts[0].split(".")
                    period = None
                    value_field = None
                    if len(condition_sub_parts) > 2:
                        param_type = "condition"
                        if len(period_sub_parts) > 1:
                            period = period_sub_parts[1]
                        if len(period_sub_parts) > 2:
                            value_field = period_sub_parts[2]
                        incomplete = condition_sub_parts[-1] if len(condition_sub_parts) > 1 else " "
                    elif len(condition_sub_parts) > 1:
                        param_type = "operator"
                        incomplete = condition_sub_parts[-1] if len(condition_sub_parts) > 0 else " "
                    elif len(period_sub_parts) > 2:
                        param_type = "value_field"
                        incomplete = period_sub_parts[-1] if len(period_sub_parts) > 1 else " "
                    elif len(period_sub_parts) > 1:
                        param_type = "period"
                        incomplete = period_sub_parts[-1] if len(period_sub_parts) > 0 else " "
                    else:
                        param_type = "metric"

                    for (idf, name) in matched_param.type.get_suggestions(
                        incomplete if incomplete else " ", False, param_type, period_sub_parts[0], period, value_field
                    ):
                        choices.append(Completion(text_type(idf), -len(incomplete), display_meta=name))
                elif type(matched_param.type) is click.types.BoolParamType:
                    for param in command.params:
                        if isinstance(param, click.Option):
                            if not any(o in ctx.used_options for o in param.opts) or param.multiple:
                                choices.append(
                                    Completion(
                                        text_type(max(param.opts, key=len)),
                                        -len(ctx.incomplete),
                                        display_meta=f"({param.opts[-1]}) {param.help}",
                                    )
                                )
            else:
                for param in command.params:
                    if isinstance(param, click.Option):
                        if not any(o in ctx.used_options for o in param.opts) or param.multiple:
                            choices.append(
                                Completion(
                                    text_type(max(param.opts, key=len)),
                                    -len(ctx.incomplete),
                                    display_meta=f"({param.opts[-1]}) {param.help}",
                                )
                            )
        else:
            for param in command.params:
                if isinstance(param, click.Option):
                    if not any(o in ctx.used_options for o in param.opts) or param.multiple:
                        choices.append(
                            Completion(
                                text_type(max(param.opts, key=len)),
                                -len(ctx.incomplete),
                                display_meta=f"({param.opts[-1]}) {param.help}",
                            )
                        )
                elif isinstance(param, click.Argument):
                    if isinstance(param.type, click.Choice):
                        for choice in param.type.choices:
                            choices.append(Completion(text_type(choice), -len(ctx.incomplete)))

            if isinstance(command, click.MultiCommand):
                for name in command.list_commands(ctx.click_ctx):
                    sub_command = command.get_command(ctx.click_ctx, name)
                    choices.append(
                        Completion(
                            text_type(name),
                            -len(ctx.incomplete),
                            display_meta=getattr(sub_command, "short_help"),
                        )
                    )

        for item in choices:
            if not filter_choices or item.text.startswith(ctx.incomplete):
                yield item
