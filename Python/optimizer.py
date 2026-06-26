class Optimizer:

    def __init__(self, products):

        self.products = products

        self.negative = []
        self.positive = []

    def split_products(self):

        self.negative.clear()
        self.positive.clear()

        for p in self.products:

            if not isinstance(p.al, (int, float)):
                continue

            if p.al < 0:
                self.negative.append(p)

            elif p.al > 0:
                self.positive.append(p)

    def summary(self):

        print()
        print("=" * 60)
        print("OPTIMIZER")
        print("=" * 60)

        print("Negative :", len(self.negative))
        print("Positive :", len(self.positive))

        print()

        print("Top 10 Negative")

        for p in sorted(self.negative, key=lambda x: x.al):

            print(f"{p.ma_hang:20} {p.al:12.2f}")

        print()

        print("Top 10 Positive")

        for p in sorted(self.positive,
                        key=lambda x: x.al,
                        reverse=True)[:10]:

            print(f"{p.ma_hang:20} {p.al:12.2f}")

    def run(self):

        self.split_products()

        self.summary()