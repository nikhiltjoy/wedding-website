from pathlib import Path
from typing import List

import pandas as pd
import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe


class GSheetClient:
    def __init__(self, creds_json_path: Path):
        self.client = gspread.service_account(filename=str(creds_json_path.resolve()))

    def get_dataframe_from_sheet(
        self, sheet_id: str, sheet_num: int = 0
    ) -> pd.DataFrame:
        sh = self.client.open_by_key(sheet_id)
        worksheet = sh.get_worksheet(sheet_num)
        df = get_as_dataframe(worksheet, evaluate_formulas=False)
        columns_to_select = self._get_named_columns(df)
        return df.loc[df[columns_to_select[0]].notnull(), columns_to_select].copy()

    def set_sheet_from_dataframe(
        self, df: pd.DataFrame, sheet_id: str, sheet_num: int = 0
    ) -> None:
        sh = self.client.open_by_key(sheet_id)
        worksheet = sh.get_worksheet(sheet_num)
        set_with_dataframe(worksheet, df, allow_formulas=False, string_escaping="full")

    @staticmethod
    def _get_named_columns(df: pd.DataFrame) -> List[str]:
        columns_to_select = []
        for col in df:
            if col.startswith("Unnamed:"):
                break
            columns_to_select.append(col)
        return columns_to_select
