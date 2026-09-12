from pathlib import Path
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta


def get_last_month_range():
    """先月の開始日と終了日を取得する。"""

    today = date.today()
    this_month_start = today.replace(day=1)

    last_month_end = this_month_start - relativedelta(days=1)
    last_month_start = last_month_end.replace(day=1)

    return (
        pd.Timestamp(last_month_start),
        pd.Timestamp(last_month_end)
    )


def create_event_data(
    df,
    event_name,
    event_date_col,
    start_date,
    end_date,
):
    """指定した日付項目を基準に、先月分の人事イベントを作成する。"""

    df = df.copy()

    df[event_date_col] = pd.to_datetime(
        df[event_date_col],
        errors="coerce"
    )

    df = df[
        df[event_date_col].between(
            start_date,
            end_date
        )
    ].copy()

    result = pd.DataFrame({
        "項目": event_name,
        "日付": df[event_date_col],
        "社員番号": df["社員番号"],
        "氏名": df["氏名"],
        "入社日": df["入社日"] if "入社日" in df.columns else pd.NaT,
        "退職日": df["退職日"] if "退職日" in df.columns else pd.NaT,
        "休職開始日": (
            df["休職開始日"]
            if "休職開始日" in df.columns
            else pd.NaT
        ),
        "休職終了日": (
            df["休職終了日"]
            if "休職終了日" in df.columns
            else pd.NaT
        ),
        "復職日": (
            df["復職日"]
            if "復職日" in df.columns
            else pd.NaT
        )
    })

    return result


def collect_hr_events(file_path, output_folder):
    """
    入社・退職・休職シートから先月分の情報を抽出し、
    入退社・休復職一覧として統合する。
    """

    start_date, end_date = get_last_month_range()

    df_join = pd.read_excel(
        file_path,
        sheet_name="入社"
    )

    df_leave = pd.read_excel(
        file_path,
        sheet_name="退職"
    )

    df_absence = pd.read_excel(
        file_path,
        sheet_name="休職"
    )

    join_result = create_event_data(
        df_join,
        "入社",
        "入社日",
        start_date,
        end_date
    )

    leave_result = create_event_data(
        df_leave,
        "退職",
        "退職日",
        start_date,
        end_date
    )

    absence_result = create_event_data(
        df_absence,
        "休職",
        "休職開始日",
        start_date,
        end_date
    )

    return_result = create_event_data(
        df_absence,
        "復職",
        "復職日",
        start_date,
        end_date
    )

    result = pd.concat(
        [
            join_result,
            leave_result,
            absence_result,
            return_result
        ],
        ignore_index=True
    )

    result = result.sort_values(
        by=["日付", "社員番号"]
    )

    output_folder.mkdir(parents=True, exist_ok=True)

    target_month = start_date.strftime("%Y%m")

    output_path = (
        output_folder
        / f"入退社・休復職一覧_{target_month}.xlsx"
    )

    result.to_excel(
        output_path,
        index=False
    )

    return output_path


if __name__ == "__main__":

    BASE_DIR = Path(__file__).parent

    input_folder = BASE_DIR / "sample_input"
    output_folder = BASE_DIR / "sample_output"

    file_path = (
        input_folder
        / "入退社・休復職情報.xlsx"
    )

    output_path = collect_hr_events(
        file_path,
        output_folder
    )

    print(f"出力完了: {output_path}")