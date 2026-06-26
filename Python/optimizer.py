# optimizer.py

class Optimizer:
    """
    Optimizer v3
    - Tách mã âm / mã dương
    - Loại mã TK Có 5113 khỏi mã nhận
    - Ưu tiên cùng khách hàng
    - Có theo dõi số dư AL còn lại của từng mã nhận
    - Không để một mã nhận bị dùng vượt quá AL dương
    """

    def __init__(self, products):
        self.products = products

        self.negative = []
        self.positive = []
        self.receiver_pool = {}
        self.available_al = {}

    # ==========================
    # Helpers
    # ==========================

    def is_number(self, value):
        return isinstance(value, (int, float))

    def is_negative(self, product):
        return self.is_number(product.al) and product.al < 0

    def is_positive(self, product):
        return self.is_number(product.al) and product.al > 0

    def is_customer_supply_nvl(self, product):
        return product.khach_cap_nvl is True

    def has_customer(self, product):
        return product.ma_khach not in [None, ""]

    def customer_key(self, product):
        if not self.has_customer(product):
            return "UNKNOWN"
        return str(product.ma_khach).strip()

    # ==========================
    # Split products
    # ==========================

    def split_products(self):
        self.negative = []
        self.positive = []

        for p in self.products:
            if self.is_negative(p):
                self.negative.append(p)

            elif self.is_positive(p):
                self.positive.append(p)

        self.negative.sort(key=lambda x: x.al)
        self.positive.sort(key=lambda x: x.al, reverse=True)

    # ==========================
    # Build receiver pool
    # ==========================

    def build_receiver_pool(self):
        self.receiver_pool = {}
        self.available_al = {}

        for p in self.positive:

            # TK Có 5113: khách cấp NVL, không được nhận NVL mua ngoài
            if self.is_customer_supply_nvl(p):
                continue

            key = self.customer_key(p)

            if key not in self.receiver_pool:
                self.receiver_pool[key] = []

            self.receiver_pool[key].append(p)

            # Theo dõi AL còn lại của mã nhận
            self.available_al[p.ma_hang] = float(p.al)

        for key in self.receiver_pool:
            self.receiver_pool[key].sort(
                key=lambda x: self.available_al.get(x.ma_hang, 0),
                reverse=True
            )

    # ==========================
    # Receiver search
    # ==========================

    def find_receivers_same_customer(self, negative_product):
        key = self.customer_key(negative_product)
        return self.receiver_pool.get(key, [])

    def find_receivers_toyo_sato(self, negative_product):
        name = str(negative_product.khach_hang or "").lower()

        if "toyo" not in name and "sato" not in name:
            return []

        receivers = []

        for p in self.positive:

            if self.is_customer_supply_nvl(p):
                continue

            pname = str(p.khach_hang or "").lower()

            if "toyo" in pname or "sato" in pname:
                if self.available_al.get(p.ma_hang, 0) > 0:
                    receivers.append(p)

        receivers.sort(
            key=lambda x: self.available_al.get(x.ma_hang, 0),
            reverse=True
        )

        return receivers

    def find_receivers(self, negative_product):
        receivers = self.find_receivers_same_customer(negative_product)

        receivers = [
            p for p in receivers
            if self.available_al.get(p.ma_hang, 0) > 0
        ]

        if receivers:
            return receivers, "Cùng khách hàng"

        receivers = self.find_receivers_toyo_sato(negative_product)

        if receivers:
            return receivers, "Toyo/Sato mở rộng"

        return [], "Không có mã nhận phù hợp"

    # ==========================
    # Transfer plan
    # ==========================

    def make_transfer_plan(self):
        plan = []

        for neg in self.negative:

            need = abs(float(neg.al))
            original_need = need

            receivers, method = self.find_receivers(neg)

            if not receivers:
                plan.append({
                    "ma_am": neg.ma_hang,
                    "al_am": neg.al,
                    "ma_nhan": "",
                    "al_du": 0,
                    "so_tien_chuyen": 0,
                    "method": method,
                    "status": "NO_RECEIVER"
                })
                continue

            for rec in receivers:

                if need <= 0:
                    break

                available = self.available_al.get(rec.ma_hang, 0)

                if available <= 0:
                    continue

                # để AL nhận vẫn > 0, không dùng hết 100%
                safe_available = max(available - 1, 0)

                if safe_available <= 0:
                    continue

                move = min(need, safe_available)

                if move <= 0:
                    continue

                plan.append({
                    "ma_am": neg.ma_hang,
                    "al_am": neg.al,
                    "ma_nhan": rec.ma_hang,
                    "al_du": available,
                    "so_tien_chuyen": move,
                    "method": method,
                    "status": "PLANNED"
                })

                # Trừ dần AL còn lại của mã nhận
                self.available_al[rec.ma_hang] = available - move

                need -= move

            if need > 0:
                plan.append({
                    "ma_am": neg.ma_hang,
                    "al_am": neg.al,
                    "ma_nhan": "",
                    "al_du": 0,
                    "so_tien_chuyen": need,
                    "method": "Không đủ mã nhận, cần giảm giá thành",
                    "status": "NEED_REDUCE_COST"
                })

        return plan

    # ==========================
    # Summary
    # ==========================

    def summary(self):
        print("=" * 60)
        print("OPTIMIZER v3")
        print("=" * 60)

        print("Tổng mã:", len(self.products))
        print("Mã âm:", len(self.negative))
        print("Mã dương:", len(self.positive))
        print("Nhóm khách hàng có thể nhận:", len(self.receiver_pool))
        print()

        print("Top mã âm:")
        for p in self.negative[:10]:
            print(
                f"{p.ma_hang:20}",
                f"AL={p.al:12.2f}",
                f"KH={p.ma_khach}",
                f"TK={p.tk511}"
            )

    # ==========================
    # Run
    # ==========================

    def run(self):
        self.split_products()
        self.build_receiver_pool()
        self.summary()
        return self.make_transfer_plan()