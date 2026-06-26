# cost_solver.py


class CostSolver:
    """
    CostSolver v2

    Input:
    - plan: danh sách kế hoạch phân bổ từ optimizer.py
    - products: danh sách Product từ reader.py

    Output:
    - actions: danh sách hành động cuối cùng
    """

    def __init__(self, plan, products):
        self.plan = plan
        self.products = products
        self.actions = []

    def solve(self):
        self.actions = []

        for row in self.plan:
            status = row.get("status")

            ma_am = row.get("ma_am")
            ma_nhan = row.get("ma_nhan")
            amount = row.get("so_tien_chuyen", 0)
            method = row.get("method", "")

            if status == "PLANNED":
                self.actions.append({
                    "ma_am": ma_am,
                    "ma_nhan": ma_nhan,
                    "amount": amount,
                    "action": "TRANSFER",
                    "note": method
                })

            elif status == "NEED_REDUCE_COST":
                self.actions.append({
                    "ma_am": ma_am,
                    "ma_nhan": "",
                    "amount": amount,
                    "action": "REDUCE_COST",
                    "note": "Không đủ mã nhận, giảm giá thành vừa đủ"
                })

            elif status == "NO_RECEIVER":
                al_am = row.get("al_am", 0)

                self.actions.append({
                    "ma_am": ma_am,
                    "ma_nhan": "",
                    "amount": abs(al_am),
                    "action": "REDUCE_COST",
                    "note": "Không có mã nhận phù hợp"
                })

        return self.actions

    def summary(self):
        total_transfer = 0
        total_reduce = 0

        for a in self.actions:
            amount = a.get("amount", 0)

            if not isinstance(amount, (int, float)):
                amount = 0

            if a.get("action") == "TRANSFER":
                total_transfer += amount

            elif a.get("action") == "REDUCE_COST":
                total_reduce += amount

        print()
        print("=" * 60)
        print("COST SOLVER SUMMARY")
        print("=" * 60)
        print("Số hành động:", len(self.actions))
        print("Tổng chuyển phân bổ:", round(total_transfer, 2))
        print("Tổng cần giảm giá thành:", round(total_reduce, 2))