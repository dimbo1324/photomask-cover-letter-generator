from pathlib import Path
from utils.excel_worker import ExcelWorker


if __name__ == "__main__":
    src = Path(
        r"C:\Users\dim4d\Desktop\From git\photomask-cover-letter-generator\input data\3. Практическое задание\Исходные данные для исполнения\Template.xlsx"
    )
    prefix = "АБОБА"
    above_value = "АБОБА"
    options = {
        "search_text": "№ слоя",
        "search_col": 5,
        "source_col": 6,
        "target_col": 7,
    }
    w = ExcelWorker(src, prefix, above_value, options)
    saved, rows = w.run()
    print("Saved:", saved)
    print("Modified rows:", rows)
