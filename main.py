from pathlib import Path

from extract_transfer_data import extract_transfer_data
from collect_hr_events import collect_hr_events
from compare_dc_data import compare_dc_data
from validate_hr_data import validate_hr_data


BASE_DIR = Path(__file__).parent
input_folder = BASE_DIR / "sample_input"
output_folder = BASE_DIR / "sample_output"


def main():

    # 1. 人事異動申請PDF → 一覧化
    transfer_output = extract_transfer_data(
        input_folder / "人事異動申請",
        output_folder
    )

    # 2. 入退社・休復職情報 → 一覧化
    event_output = collect_hr_events(
        input_folder / "入退社・休復職情報.xlsx",
        output_folder
    )

    # 3. DC加入者情報の月次差分
    compare_dc_data(
        input_folder / "DC加入者情報_202608.xlsx",
        input_folder / "DC加入者情報_202609.xlsx",
        output_folder
    )

    # 4. 前工程の出力結果とDC加入者情報を照合
    validate_hr_data(
        input_folder / "DC加入者情報_202609.xlsx",
        transfer_output,
        event_output,
        output_folder
    )


if __name__ == "__main__":
    main()