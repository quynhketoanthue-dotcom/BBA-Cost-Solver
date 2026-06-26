# report.py

from pathlib import Path
import pandas as pd


class ReportWriter:
    """
    ReportWriter v4 - BOM aware

    Xuất file:
    Output/BBA_Cost_Adjust_Result.xlsx

    Sheet:
    - Doc truoc
    - Thoi gian sau chinh sua
    - Dinh muc sau chinh sua
    - Can soat BOM
    - Can giam gia thanh
    - Thong ke
    - Transfer Plan
    """

    def __init__(self, output_folder):
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(exist_ok=True)

    # =====================================================
    # Helpers
    # =====================================================

    def _to_number(self, value, default=0):
        if isinstance(value, (int, float)):
            return float(value)

        try:
            return float(value)
        except Exception:
            return default

    def _safe_text(self, value):
        if value is None:
            return ""
        return str(value)

    def _build_maps(self, plan):
        """
        transfer_map:
            mã âm -> tổng tiền đã xử lý bằng chuyển phân bổ

        reduce_map:
            mã âm -> tổng tiền còn phải giảm giá thành

        receiver_map:
            mã nhận -> tổng tiền nhận thêm
        """

        transfer_map = {}
        reduce_map = {}
        receiver_map = {}

        for row in plan:
            ma_am = row.get("ma_am")
            ma_nhan = row.get("ma_nhan")
            amount = self._to_number(row.get("so_tien_chuyen"))
            status = row.get("status")

            if not ma_am:
                continue

            if status == "PLANNED":
                transfer_map[ma_am] = transfer_map.get(ma_am, 0) + amount

                if ma_nhan:
                    receiver_map[ma_nhan] = receiver_map.get(ma_nhan, 0) + amount

            elif status in ["NEED_REDUCE_COST", "NO_RECEIVER"]:
                reduce_map[ma_am] = reduce_map.get(ma_am, 0) + amount

        return transfer_map, reduce_map, receiver_map

    # =====================================================
    # Transfer Plan
    # =====================================================

    def _make_transfer_plan_df(self, plan):
        rows = []

        for item in plan:
            rows.append({
                "Mã âm": item.get("ma_am"),
                "AL âm": item.get("al_am"),
                "Mã nhận": item.get("ma_nhan"),
                "AL dư tại thời điểm xét": item.get("al_du"),
                "Số tiền chuyển": item.get("so_tien_chuyen"),
                "Phương pháp": item.get("method"),
                "Trạng thái": item.get("status"),
            })

        return pd.DataFrame(rows)

    # =====================================================
    # Doc truoc
    # =====================================================

    def _make_before_df(self, products):
        rows = []

        for p in products:
            rows.append({
                "Dong GT": p.row,
                "Ma hang": p.ma_hang,
                "Ma khach": p.ma_khach,
                "Khach hang": p.khach_hang,
                "TK Co": p.tk511,
                "Khach cap NVL": p.khach_cap_nvl,
                "So dong BOM": len(p.bom_lines),
                "Tong dinh muc": p.dinh_muc,
                "Thoi gian": p.thoi_gian,
                "Nhan cong": p.nhan_cong,
                "Gia ban": p.gia_ban,
                "Gia thanh": p.gia_thanh,
                "AL": p.al,
            })

        return pd.DataFrame(rows)

    # =====================================================
    # Thoi gian sau chinh sua
    # =====================================================

    def _make_time_df(self, products, plan):
        transfer_map, reduce_map, receiver_map = self._build_maps(plan)

        rows = []

        for p in products:
            before = self._to_number(p.thoi_gian)
            after = before

            note = "GIU NGUYEN"
            need_change = "NO"

            if p.ma_hang in reduce_map and reduce_map[p.ma_hang] > 0:
                note = "CAN SOAT LAI NEU GIAM DINH MUC KHONG DU"
                need_change = "YES"

            if before > 0 and after <= 0:
                after = before * 0.01
                note = "KHONG DUOC VE 0"
                need_change = "YES"

            rows.append({
                "Dong TG/GT": p.row,
                "Ma hang": p.ma_hang,
                "Ma khach": p.ma_khach,
                "Khach hang": p.khach_hang,
                "TK Co": p.tk511,
                "Thoi gian truoc": before,
                "Thoi gian sau chinh sua": after,
                "Tang/Giam": after - before,
                "Can thay?": need_change,
                "Ghi chu": note,
            })

        return pd.DataFrame(rows)

    # =====================================================
    # Dinh muc sau chinh sua
    # =====================================================

    def _make_dinh_muc_df(self, products, plan):
        """
        Chỉ xuất các dòng có BOM thật.
        Mã không có BOM sẽ đưa sang sheet Can soat BOM.
        """

        transfer_map, reduce_map, receiver_map = self._build_maps(plan)

        rows = []

        for p in products:
            if not p.bom_lines:
                continue

            gia_thanh = self._to_number(p.gia_thanh)

            transfer_amount = transfer_map.get(p.ma_hang, 0)
            reduce_amount = reduce_map.get(p.ma_hang, 0)
            receive_amount = receiver_map.get(p.ma_hang, 0)

            for line in p.bom_lines:
                before = self._to_number(line.dinh_muc)
                after = before

                need_change = "NO"
                note = "GIU NGUYEN"

                if p.khach_cap_nvl:
                    after = 0
                    need_change = "YES"
                    note = "5113 - KHACH CAP NVL - DINH MUC = 0"

                elif gia_thanh > 0 and transfer_amount > 0 and before > 0:
                    ratio = min(transfer_amount / gia_thanh, 0.95)
                    after = before * (1 - ratio)

                    if after <= 0:
                        after = before * 0.01

                    need_change = "YES"
                    note = "GIAM MA AM DO DA CHUYEN PHAN BO"

                elif gia_thanh > 0 and reduce_amount > 0 and before > 0:
                    ratio = min(reduce_amount / gia_thanh, 0.95)
                    after = before * (1 - ratio)

                    if after <= 0:
                        after = before * 0.01

                    need_change = "YES"
                    note = "GIAM MA AM DO KHONG DU MA NHAN"

                elif gia_thanh > 0 and receive_amount > 0 and before > 0:
                    ratio = min(receive_amount / gia_thanh, 0.95)
                    after = before * (1 + ratio)

                    need_change = "YES"
                    note = "TANG MA NHAN PHAN BO"

                warning = ""
                dvt = self._safe_text(line.dvt).lower()

                if "kg" in dvt and after >= 1:
                    warning = "CAN SOAT: DINH MUC KG >= 1/SP"

                rows.append({
                    "Dong DM goc": line.row,
                    "Ma NVL": line.ma_nvl,
                    "DVT": line.dvt,
                    "Ma hang": p.ma_hang,
                    "Ma khach": p.ma_khach,
                    "Khach hang": p.khach_hang,
                    "TK Co": p.tk511,
                    "Khach cap NVL": p.khach_cap_nvl,
                    "Dinh muc truoc": before,
                    "Dinh muc sau chinh sua": after,
                    "Tang/Giam": after - before,
                    "Can thay?": need_change,
                    "Ghi chu": note,
                    "Canh bao": warning,
                })

        return pd.DataFrame(rows)

    # =====================================================
    # Can soat BOM
    # =====================================================

    def _make_missing_bom_df(self, products):
        rows = []

        for p in products:
            if p.bom_lines:
                continue

            rows.append({
                "Dong GT": p.row,
                "Ma hang": p.ma_hang,
                "Ma khach": p.ma_khach,
                "Khach hang": p.khach_hang,
                "TK Co": p.tk511,
                "Khach cap NVL": p.khach_cap_nvl,
                "Gia ban": p.gia_ban,
                "Gia thanh": p.gia_thanh,
                "AL": p.al,
                "Ghi chu": "KHONG CO BOM TRONG SHEET DINH MUC",
            })

        return pd.DataFrame(rows)

    # =====================================================
    # Can giam gia thanh
    # =====================================================

    def _make_reduce_cost_df(self, plan):
        rows = []

        for row in plan:
            status = row.get("status")

            if status not in ["NEED_REDUCE_COST", "NO_RECEIVER"]:
                continue

            amount = self._to_number(row.get("so_tien_chuyen"))

            if amount == 0:
                amount = abs(self._to_number(row.get("al_am")))

            rows.append({
                "Ma hang": row.get("ma_am"),
                "AL am": row.get("al_am"),
                "So tien can giam": amount,
                "Trang thai": status,
                "Ly do": row.get("method"),
                "Ghi chu": "CAN GIAM GIA THANH VUA DU DE AL > 0",
            })

        return pd.DataFrame(rows)

    # =====================================================
    # Thong ke
    # =====================================================

    def _make_summary_df(self, products, plan):
        transfer_map, reduce_map, receiver_map = self._build_maps(plan)

        total_products = len(products)
        negative_count = 0
        khach_cap_nvl_count = 0
        bom_line_count = 0
        missing_bom_count = 0

        for p in products:
            if isinstance(p.al, (int, float)) and p.al < 0:
                negative_count += 1

            if p.khach_cap_nvl:
                khach_cap_nvl_count += 1

            if p.bom_lines:
                bom_line_count += len(p.bom_lines)
            else:
                missing_bom_count += 1

        planned = len([x for x in plan if x.get("status") == "PLANNED"])
        no_receiver = len([x for x in plan if x.get("status") == "NO_RECEIVER"])
        need_reduce = len([x for x in plan if x.get("status") == "NEED_REDUCE_COST"])

        rows = [
            {"Chi tieu": "Tong so ma", "Gia tri": total_products},
            {"Chi tieu": "So ma AL am", "Gia tri": negative_count},
            {"Chi tieu": "Tong so dong BOM", "Gia tri": bom_line_count},
            {"Chi tieu": "So ma khong co BOM", "Gia tri": missing_bom_count},
            {"Chi tieu": "So ma khach cap NVL 5113", "Gia tri": khach_cap_nvl_count},
            {"Chi tieu": "So dong PLANNED", "Gia tri": planned},
            {"Chi tieu": "So dong NO_RECEIVER", "Gia tri": no_receiver},
            {"Chi tieu": "So dong NEED_REDUCE_COST", "Gia tri": need_reduce},
            {"Chi tieu": "Tong tien chuyen phan bo", "Gia tri": sum(transfer_map.values())},
            {"Chi tieu": "Tong tien ma nhan tang", "Gia tri": sum(receiver_map.values())},
            {"Chi tieu": "Tong tien can giam gia thanh", "Gia tri": sum(reduce_map.values())},
        ]

        return pd.DataFrame(rows)

    # =====================================================
    # Public export
    # =====================================================

    def export_transfer_plan(self, plan, products=None):
        output_file = self.output_folder / "BBA_Cost_Adjust_Result.xlsx"

        transfer_df = self._make_transfer_plan_df(plan)

        if products is None:
            old_file = self.output_folder / "BBA_Transfer_Plan.xlsx"
            transfer_df.to_excel(old_file, index=False)
            return old_file

        before_df = self._make_before_df(products)
        time_df = self._make_time_df(products, plan)
        dm_df = self._make_dinh_muc_df(products, plan)
        missing_bom_df = self._make_missing_bom_df(products)
        reduce_cost_df = self._make_reduce_cost_df(plan)
        summary_df = self._make_summary_df(products, plan)

        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
            before_df.to_excel(writer, sheet_name="Doc truoc", index=False)
            time_df.to_excel(writer, sheet_name="Thoi gian sau chinh sua", index=False)
            dm_df.to_excel(writer, sheet_name="Dinh muc sau chinh sua", index=False)
            missing_bom_df.to_excel(writer, sheet_name="Can soat BOM", index=False)
            reduce_cost_df.to_excel(writer, sheet_name="Can giam gia thanh", index=False)
            summary_df.to_excel(writer, sheet_name="Thong ke", index=False)
            transfer_df.to_excel(writer, sheet_name="Transfer Plan", index=False)

        return output_file