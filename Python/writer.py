# writer.py

from pathlib import Path
import shutil
import openpyxl
import pandas as pd


class WorkbookWriter:
    """
    Writer v1

    - Không sửa file gốc
    - Copy file gốc sang Output
    - Đọc BBA_Cost_Adjust_Result.xlsx
    - Ghi định mức mới vào sheet 'định mức' cột F theo dòng gốc
    - Ghi thời gian mới vào sheet 'Thời gian check' cột D theo mã hàng
    """

    def __init__(self, original_file, report_file, output_folder):
        self.original_file = Path(original_file)
        self.report_file = Path(report_file)
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(exist_ok=True)

        self.output_file = self.output_folder / "BBA_Gia_Thanh_Ap_Dung.xlsx"

    def apply(self):
        if not self.original_file.exists():
            raise FileNotFoundError(f"Không tìm thấy file gốc: {self.original_file}")

        if not self.report_file.exists():
            raise FileNotFoundError(f"Không tìm thấy file report: {self.report_file}")

        # 1. Copy file gốc sang file mới
        shutil.copy2(self.original_file, self.output_file)

        # 2. Mở file mới để sửa
        wb = openpyxl.load_workbook(self.output_file)

        ws_dm = wb["định mức"]
        ws_time = wb["Thời gian check"]

        # 3. Đọc report
        dm_df = pd.read_excel(self.report_file, sheet_name="Dinh muc sau chinh sua")
        time_df = pd.read_excel(self.report_file, sheet_name="Thoi gian sau chinh sua")

        dm_count = self.apply_dinh_muc(ws_dm, dm_df)
        time_count = self.apply_time(ws_time, time_df)

        # 4. Bật chế độ tính lại công thức khi mở Excel
        try:
            wb.calculation.fullCalcOnLoad = True
            wb.calculation.forceFullCalc = True
            wb.calculation.calcMode = "auto"
        except Exception:
            pass

        wb.save(self.output_file)

        print()
        print("=" * 60)
        print("WORKBOOK WRITER SUMMARY")
        print("=" * 60)
        print("Đã sửa định mức:", dm_count)
        print("Đã sửa thời gian:", time_count)
        print("File áp dụng:")
        print(self.output_file)

        return self.output_file

    def apply_dinh_muc(self, ws_dm, dm_df):
        count = 0

        for _, row in dm_df.iterrows():
            can_thay = str(row.get("Can thay?", "")).strip().upper()

            if can_thay != "YES":
                continue

            dong_goc = row.get("Dong DM goc")
            new_value = row.get("Dinh muc sau chinh sua")

            if pd.isna(dong_goc) or pd.isna(new_value):
                continue

            try:
                dong_goc = int(dong_goc)
                new_value = float(new_value)
            except Exception:
                continue

            # Sheet định mức: cột F là định mức
            ws_dm[f"F{dong_goc}"] = new_value
            count += 1

        return count

    def apply_time(self, ws_time, time_df):
        count = 0

        # Tạo map mã hàng -> dòng trong sheet Thời gian check
        time_row_map = {}

        for r in range(4, ws_time.max_row + 1):
            ma_hang = ws_time[f"C{r}"].value

            if ma_hang is None:
                continue

            ma_hang = str(ma_hang).strip()
            time_row_map[ma_hang] = r

        for _, row in time_df.iterrows():
            can_thay = str(row.get("Can thay?", "")).strip().upper()

            if can_thay != "YES":
                continue

            ma_hang = row.get("Ma hang")
            new_value = row.get("Thoi gian sau chinh sua")

            if pd.isna(ma_hang) or pd.isna(new_value):
                continue

            ma_hang = str(ma_hang).strip()

            if ma_hang not in time_row_map:
                continue

            try:
                new_value = float(new_value)
            except Exception:
                continue

            excel_row = time_row_map[ma_hang]

            # Sheet Thời gian check: cột D là thời gian
            ws_time[f"D{excel_row}"] = new_value
            count += 1

        return count
    