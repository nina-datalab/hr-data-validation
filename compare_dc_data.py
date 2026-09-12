from pathlib import Path
import pandas as pd


def compare_dc_data(previous_file, current_file, output_folder):
    """
    前月・当月のDC加入者情報を比較し、
    新規加入、喪失済、項目変更を一覧化する。
    """

    previous_df = pd.read_excel(previous_file)
    current_df = pd.read_excel(current_file)

    # 社員番号を文字列に統一
    previous_df["社員番号"] = previous_df["社員番号"].astype(str)
    current_df["社員番号"] = current_df["社員番号"].astype(str)

    # 前月・当月データを社員番号で結合
    merged = previous_df.merge(
        current_df,
        on="社員番号",
        how="outer",
        suffixes=("_前月", "_当月"),
        indicator=True
    )

    result = []

    for _, row in merged.iterrows():

        employee_id = row["社員番号"]

        # 当月のみ存在する社員
        if row["_merge"] == "right_only":

            result.append({
                "社員番号": employee_id,
                "氏名": row.get("氏名_当月"),
                "差分区分": "新規",
                "変更項目": "",
                "前月": "",
                "当月": row.get("拠出状況_当月")
            })

        # 前月のみ存在する社員
        elif row["_merge"] == "left_only":

            result.append({
                "社員番号": employee_id,
                "氏名": row.get("氏名_前月"),
                "差分区分": "喪失済",
                "変更項目": "",
                "前月": row.get("拠出状況_前月"),
                "当月": ""
            })

        # 両月に存在する社員の変更項目を確認
        else:

            check_columns = [
                "氏名",
                "部署名",
                "入社日",
                "雇用区分",
                "拠出状況"
            ]

            for column in check_columns:

                previous_value = row.get(f"{column}_前月")
                current_value = row.get(f"{column}_当月")

                if pd.isna(previous_value) and pd.isna(current_value):
                    continue

                if previous_value != current_value:

                    result.append({
                        "社員番号": employee_id,
                        "氏名": row.get("氏名_当月"),
                        "差分区分": "変更",
                        "変更項目": column,
                        "前月": previous_value,
                        "当月": current_value
                    })

    result = pd.DataFrame(result)

    output_folder.mkdir(exist_ok=True)

    # 当月ファイル名から対象年月を取得
    target_month = current_file.stem.split("_")[-1]

    output_path = (
        output_folder
        / f"DC加入者差分一覧_{target_month}.xlsx"
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

    previous_file = (
        input_folder
        / "DC加入者情報_202608.xlsx"
    )

    current_file = (
        input_folder
        / "DC加入者情報_202609.xlsx"
    )

    output_path = compare_dc_data(
        previous_file,
        current_file,
        output_folder
    )

    print(f"出力完了: {output_path}")