from typing import Any, Dict, Optional
import investor8_sdk

from i8_terminal.common.financials import prepare_financials_df

from i8_terminal.api.financials.financials_list_result import FinancialsListResult



        

def get_financials_list(
    identifiers_dict: Dict[str, str],
    statement: str,
    period_type: Optional[str],
    period_size: int = 4,
    exportize: Optional[bool] = False,
) -> Optional[Dict[str, Any]]:
    fins = []
    if identifiers_dict.get("fiscal_period"):
        fins = [
            investor8_sdk.FinancialsApi().get_financials_single(
                ticker=identifiers_dict["ticker"],
                stat_code=statement,
                fiscal_year=identifiers_dict.get("fiscal_year"),
                fiscal_period=identifiers_dict.get("fiscal_period"),
            )
        ]
    else:
        period_type = "FY" if not period_type else period_type
        fins = investor8_sdk.FinancialsApi().get_list_standardized_financials(
            ticker=identifiers_dict["ticker"],
            stat_code=statement,
            period_type=period_type,
            end_year=identifiers_dict.get("fiscal_year", ""),
        )
    if not fins:
        return None
    df = prepare_financials_df(fins, period_size, include_ticker=False, exportize=exportize)
    
    return FinancialsListResult(df)
