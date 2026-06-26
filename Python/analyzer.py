class Analyzer:

    def analyze(self, products):

        for p in products:

            if not isinstance(p.al, (int, float)):
                continue

            if p.al >= 0:
                continue

            tong = 0

            if isinstance(p.dinh_muc, (int, float)):
                tong += p.dinh_muc

            if isinstance(p.nhan_cong, (int, float)):
                tong += p.nhan_cong

            if tong == 0:
                p.reasons.append("Không có dữ liệu")
                continue

            ty_le_nvl = p.dinh_muc / tong if p.dinh_muc else 0
            ty_le_nc = p.nhan_cong / tong if p.nhan_cong else 0

            if ty_le_nvl > 0.7:
                p.reasons.append("NVL cao")

            if ty_le_nc > 0.4:
                p.reasons.append("Nhân công cao")

            if len(p.reasons) == 0:
                p.reasons.append("Cần kiểm tra")