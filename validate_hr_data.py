from pathlib import Path
import pandas as pd


def validate_hr_data(
    dc_file,
    transfer_file,
    event_file,
    output_folder
):
    """
    人事異動・入退社・休復職情報とDC加入者情報を照合し、
    部署および拠出状況を確認する。
    """

    dc_df = pd.read_excel(dc_file)
    transfer_df = pd.read_excel(transfer_file)
    event_df = pd.read_excel(event_file)

    # 社員番号を文字列に統一
    dc_df["社員番号"] = dc_df["社員番号"].astype(str)
    transfer_df["社員番号"] = transfer_df["社員番号"].astype(str)
    event_df["社員番号"] = event_df["社員番号"].astype(str)

    result = []

    # =========================
    # 人事異動情報との照合
    # =========================
    transfer_check = transfer_df.merge(
        dc_df[
            [
                "社員番号",
                "氏名",
                "部署名"
            ]
        ],
        on="社員番号",
        how="left",
        suffixes=("_人事", "_DC")
    )

    for _, row in transfer_check.iterrows():

        hr_dept = row.get("異動先部署")
        dc_dept = row.get("部署名")

        result.append({
            "社員番号": row["社員番号"],
            "氏名": row.get("氏名_人事"),
            "確認項目": "部署",
            "人事情報": hr_dept,
            "DC情報": dc_dept,
            "確認結果": (
                "一致"
                if hr_dept == dc_dept
                else "要確認"
            )
        })

    # =========================
    # 入退社・休復職情報との照合
    # =========================
    event_check = event_df.merge(
        dc_df[
            [
                "社員番号",
                "氏名",
                "拠出状況"
            ]
        ],
        on="社員番号",
        how="left",
        suffixes=("_人事", "_DC")
    )

    for _, row in event_check.iterrows():

        event = row.get("項目")
        event_date = row.get("日付")
        dc_status = row.get("拠出状況")

        result.append({
            "社員番号": row["社員番号"],
            "氏名": row.get("氏名_人事"),
            "確認項目": event,
            "人事情報": event_date,
            "DC情報": dc_status,
            "確認結果": ""
        })

    result = pd.DataFrame(result)

    output_folder.mkdir(exist_ok=True)

    # DC加入者情報の対象年月をファイル名から取得
    target_month = dc_file.stem.split("_")[-1]

    output_path = (
        output_folder
        / f"人事データ照合結果_{target_month}.xlsx"
    )

    result.to_excel(
        output_path,
        index=False
    )

    return output_path


if __name__ == "__main__":
    print(__name__)
    BASE_DIR = Path(__file__).parent

    input_folder = BASE_DIR / "sample_input"
    output_folder = BASE_DIR / "sample_output"

    dc_file = (
        input_folder
        / "DC加入者情報_202609.xlsx"
    )

    transfer_file = (
        output_folder
        / "人事異動一覧_202608.xlsx"
    )

    event_file = (
        output_folder
        / "入退社・休復職一覧_202608.xlsx"
    )

    output_path = validate_hr_data(
        dc_file,
        transfer_file,
        event_file,
        output_folder
    )

    print(f"出力完了: {output_path}")