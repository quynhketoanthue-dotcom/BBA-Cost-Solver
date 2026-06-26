# writer.py

from pathlib import Path
import shutil
import pandas as pd
import win32com.client as win32


class WorkbookWriter:
    """
    Writer v2 - dùng Microsoft Excel thật để ghi file.

    Ưu điểm:
    - Không dùng openpyxl để save workbook gốc phức tạp
    - Excel tự mở file
    - Excel tự ghi giá trị
    - Excel tự tính lại công thức
    - Excel tự save
    - Hạn chế lỗi recover file
    """

    def __init__(self, original_file, report_file, output_folder):
        self.original_file = Path(original_file).resolve()
        self.report_file = Path(report_file).resolve()
        self.output_folder = Path(output_folder).resolve()
        self.output_folder.mkdir(exist_ok=True)

        self.output_file = self.output_folder / "BBA_Gia_Thanh_Ap_Dung.xlsx"

    def apply(self):
        if not self.original_file.exists():
            raise FileNotFoundError(f"Không tìm thấy file gốc: {self.original_file}")

        if not self.report_file.exists():
            raise FileNotFoundError(f"Không tìm thấy file report: {self.report_file}")

        # 1. Copy file gốc sang file mới
        if self.output_file.exists():
            self.output_file.unlink()

        shutil.copy2(self.original_file, self.output_file)

        # 2. Đọc report
        dm_df = pd.read_excel(self.report_file, sheet_name="Dinh muc sau chinh sua")
        time_df = pd.read_excel(self.report_file, sheet_name="Thoi gian sau chinh sua")

        excel = None
        wb = None

        try:
            excel = win32.DispatchEx("Excel.Application")
            excel.Visible = False
            excel.DisplayAlerts = False
            excel.AskToUpdateLinks = False

            wb = excel.Workbooks.Open(str(self.output_file))

            ws_dm = wb.Worksheets("định mức")
            ws_time = wb.Worksheets("Thời gian check")

            dm_count = self.apply_dinh_muc(ws_dm, dm_df)
            time_count = self.apply_time(ws_time, time_df)

            # 3. Tính lại toàn bộ file
            excel.CalculateFullRebuild()

            # 4. Save bằng chính Excel
            wb.Save()

            print()
            print("=" * 60)
            print("WORKBOOK WRITER v2 SUMMARY")
            print("=" * 60)
            print("Đã sửa định mức:", dm_count)
            print("Đã sửa thời gian:", time_count)
            print("File áp dụng:")
            print(self.output_file)

            return self.output_file

        finally:
            if wb is not None:
                wb.Close(SaveChanges=True)

            if excel is not None:
                excel.Quit()

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
            ws_dm.Range(f"F{dong_goc}").Value = new_value
            count += 1

        return count

    def apply_time(self, ws_time, time_df):
        count = 0

        # Tạo map mã hàng -> dòng trong sheet Thời gian check
        time_row_map = {}

        max_row = ws_time.UsedRange.Rows.Count

        for r in range(4, max_row + 1):
            ma_hang = ws_time.Range(f"C{r}").Value

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
            ws_time.Range(f"D{excel_row}").Value = new_value
            count += 1

        return count