class CostSolver:

    def __init__(self, positive, negative):

        self.positive = sorted(
            positive,
            key=lambda x: x.al,
            reverse=True
        )

        self.negative = sorted(
            negative,
            key=lambda x: x.al
        )

        self.logs = []

    def solve(self):

        for neg in self.negative:

            need = abs(neg.al)

            for pos in self.positive:

                if pos.al <= 0:
                    continue

                # TODO:
                # Sau này thêm:
                # - cùng khách hàng
                # - loại TK5113
                # - ĐVT
                # - Toyo/Sato

                move = min(need, pos.al)

                if move <= 0:
                    continue

                pos.al -= move
                neg.al += move

                self.logs.append(
                    (
                        neg.ma_hang,
                        pos.ma_hang,
                        move
                    )
                )

                need = abs(neg.al)

                if neg.al >= 0:
                    break

    def report(self):

        print()
        print("=" * 60)
        print("TRANSFER LOG")
        print("=" * 60)

        for x in self.logs[:50]:

            print(
                f"{x[0]}  <=  {x[1]}   {x[2]:,.2f}"
            )

        print()

        print("Âm còn lại:")

        for p in self.negative:

            if p.al < 0:

                print(
                    p.ma_hang,
                    round(p.al,2)
                )