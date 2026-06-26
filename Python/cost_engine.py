from pathlib import Path

from reader import WorkbookReader
from optimizer import Optimizer
from cost_solver import CostSolver
from report import ReportWriter
from writer import WorkbookWriter
from validator import WorkbookValidator


PROJECT = Path(__file__).resolve().parent.parent

INPUT = PROJECT / "Input"
OUTPUT = PROJECT / "Output"

files = list(INPUT.glob("*.xlsx"))

if not files:
    print("Không tìm thấy file Excel trong Input.")
    exit()

original_file = files[0]

# 1. Đọc workbook
reader = WorkbookReader(original_file)
products = reader.read_products()

# 2. Lập kế hoạch phân bổ
optimizer = Optimizer(products)
plan = optimizer.run()

# 3. Tổng hợp hành động xử lý
solver = CostSolver(plan, products)
actions = solver.solve()
solver.summary()

# 4. Xuất report kiểm soát
report = ReportWriter(OUTPUT)
report_file = report.export_transfer_plan(plan, products)

print()
print("=" * 60)
print("ĐÃ XUẤT REPORT")
print("=" * 60)
print(report_file)

# 5. Tạo file Excel áp dụng
writer = WorkbookWriter(
    original_file=original_file,
    report_file=report_file,
    output_folder=OUTPUT
)

applied_file = writer.apply()

# 6. Kiểm tra lại AL sau áp dụng
validator = WorkbookValidator(applied_file)
negatives = validator.summary()

print()
print("=" * 60)
print("HOÀN THÀNH")
print("=" * 60)
print("File report:")
print(report_file)
print("File áp dụng:")
print(applied_file)

if negatives:
    print()
    print("CẢNH BÁO: File áp dụng vẫn còn mã AL âm.")
    print("Cần xử lý tiếp writer v3 để ép hết âm.")
else:
    print()
    print("OK: Không còn mã AL âm.")