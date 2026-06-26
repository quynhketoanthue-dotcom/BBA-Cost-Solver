import openpyxl

from models import Product


class WorkbookReader:

    def __init__(self, workbook):

        self.workbook = workbook

        self.wb = openpyxl.load_workbook(workbook, data_only=True)

        self.ws_cost = self.wb["Giá thành 2025.07"]
        self.ws_dm = self.wb["định mức"]
        self.ws_time = self.wb["Thời gian check"]
        self.ws_sale = self.wb["Sổ chi tiết bán hàng"]
        self.ws_dvt = self.wb["ĐVT của NVL"]

    # ===========================
    # Đọc ĐVT NVL
    # ===========================

    def load_dvt(self):

        data = {}

        for r in range(3, self.ws_dvt.max_row + 1):

            ma = self.ws_dvt[f"B{r}"].value

            if not ma:
                continue

            data[str(ma).strip()] = self.ws_dvt[f"D{r}"].value

        return data

    # ===========================
    # Định mức
    # ===========================

    def load_dinh_muc(self):

        data = {}

        for r in range(3, self.ws_dm.max_row + 1):

            ma = self.ws_dm[f"C{r}"].value

            if not ma:
                continue

            ma = str(ma).strip()

            data[ma] = {

                "ma_nvl": self.ws_dm[f"B{r}"].value,

                "dinh_muc": self.ws_dm[f"F{r}"].value

            }

        return data

    # ===========================
    # Thời gian
    # ===========================

    def load_time(self):

        data = {}

        for r in range(4, self.ws_time.max_row + 1):

            ma = self.ws_time[f"C{r}"].value

            if not ma:
                continue

            data[str(ma).strip()] = self.ws_time[f"D{r}"].value

        return data

    # ===========================
    # Bán hàng
    # ===========================

    def load_sale(self):

        data = {}

        for r in range(5, self.ws_sale.max_row + 1):

            ma = self.ws_sale[f"P{r}"].value

            if not ma:
                continue

            ma = str(ma).strip()

            tk = self.ws_sale[f"AO{r}"].value

            data[ma] = {

                "ma_khach": self.ws_sale[f"H{r}"].value,

                "khach_hang": self.ws_sale[f"I{r}"].value,

                "tk511": tk,

                "khach_cap_nvl": str(tk).startswith("5113")

            }

        return data

    # ===========================
    # Đọc Product
    # ===========================

    def read_products(self):

        dm = self.load_dinh_muc()

        tg = self.load_time()

        sale = self.load_sale()

        dvt = self.load_dvt()

        products = []

        for r in range(12, self.ws_cost.max_row + 1):

            ma = self.ws_cost[f"C{r}"].value

            if not ma:
                continue

            ma = str(ma).strip()

            p = Product()

            p.row = r

            p.ma_hang = ma

            p.gia_ban = self.ws_cost[f"D{r}"].value

            p.gia_thanh = self.ws_cost[f"AK{r}"].value

            p.al = self.ws_cost[f"AL{r}"].value

            p.nhan_cong = self.ws_cost[f"AE{r}"].value

            # -------------------------

            if ma in dm:

                p.ma_nvl = dm[ma]["ma_nvl"]

                p.dinh_muc = dm[ma]["dinh_muc"]

                if p.ma_nvl in dvt:

                    p.dvt = dvt[p.ma_nvl]

            # -------------------------

            if ma in tg:

                p.thoi_gian = tg[ma]

            # -------------------------

            if ma in sale:

                p.ma_khach = sale[ma]["ma_khach"]

                p.khach_hang = sale[ma]["khach_hang"]

                p.tk511 = sale[ma]["tk511"]

                p.khach_cap_nvl = sale[ma]["khach_cap_nvl"]

            products.append(p)

        return products