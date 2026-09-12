from pathlib import Path
import pdfplumber
import re
import pandas as pd


def extract_field(text, label):
    pattern = rf"{label}[：:\s]+(.+)"
    return re.findall(pattern, text)


def extract_transfer_data(input_folder, output_folder):
    """
    人事異動申請PDFから社員番号、氏名、異動日、
    異動元部署、異動先部署を抽出し一覧化する。
    """

    result = []

    for pdf_path in input_folder.glob("*.pdf"):

        with pdfplumber.open(pdf_path) as pdf:

            for page in pdf.pages:

                text = page.extract_text()

                if not text:
                    continue

                transfer_dates = extract_field(text, "異動日")
                employee_ids = extract_field(text, "社員番号")
                names = extract_field(text, "氏名")
                from_depts = extract_field(text, "異動元部署")
                to_depts = extract_field(text, "異動先部署")

                for transfer_date, employee_id, name, from_dept, to_dept in zip(
                    transfer_dates,
                    employee_ids,
                    names,
                    from_depts,
                    to_depts
                ):
                    result.append({
                        "異動日": transfer_date.strip(),
                        "社員番号": employee_id.strip(),
                        "氏名": name.strip(),
                        "異動元部署": from_dept.strip(),
                        "異動先部署": to_dept.strip()
                    })

    result = pd.DataFrame(result)

    result["異動日"] = pd.to_datetime(
        result["異動日"],
        errors="coerce"
    )

    output_folder.mkdir(exist_ok=True)

    valid_dates = result["異動日"].dropna()

    if not valid_dates.empty:
        target_month = valid_dates.min().strftime("%Y%m")
        output_path = output_folder / f"人事異動一覧_{target_month}.xlsx"
    else:
        output_path = output_folder / "人事異動一覧.xlsx"

    result.to_excel(
        output_path,
        index=False
    )

    return output_path


if __name__ == "__main__":

    BASE_DIR = Path(__file__).parent

    input_folder = BASE_DIR / "sample_input" / "人事異動申請"
    output_folder = BASE_DIR / "sample_output"

    output_path = extract_transfer_data(
        input_folder,
        output_folder
    )

    print(f"出力完了: {output_path}")