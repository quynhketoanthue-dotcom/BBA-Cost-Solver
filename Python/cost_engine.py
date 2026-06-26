from pathlib import Path

from reader import WorkbookReader
from optimizer import Optimizer
from cost_solver import CostSolver

PROJECT = Path(__file__).resolve().parent.parent

INPUT = PROJECT / "Input"

files = list(INPUT.glob("*.xlsx"))

reader = WorkbookReader(files[0])

products = reader.read_products()

opt = Optimizer(products)

opt.split_products()

solver = CostSolver(
    opt.positive,
    opt.negative
)

solver.solve()

solver.report()