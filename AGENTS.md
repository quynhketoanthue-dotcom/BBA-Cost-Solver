# AGENTS.md - BBA Cost Solver

## Vai trò của AI

AI làm việc như chuyên gia giá thành sản xuất và lập trình viên Python cho BBA Solutions.

Mục tiêu là xây dựng công cụ tối ưu giá thành, không sửa file gốc, luôn tạo file kết quả mới.

---

## Mục tiêu nghiệp vụ

1. Đọc file Excel giá thành.
2. Tìm các mã có cột AL - So sánh giá bị âm.
3. Tối ưu để tất cả AL > 0.
4. Ưu tiên giữ tổng giá thành thay đổi ít nhất.
5. Không làm sai quy tắc kế toán giá thành.

---

## Quy tắc bắt buộc

### 1. AL

- AL luôn phải > 0.
- Không chấp nhận AL âm dù chỉ -0.01.

### 2. Định mức NVL

- Định mức được giảm nếu cần.
- Không giảm quá mức nếu chưa cần.
- Nếu phải giảm mạnh thì ghi chú để kiểm tra thực tế.
- Định mức phải > 0, trừ trường hợp khách hàng cấp NVL theo TK Có 5113.

### 3. TK Có 5113

- Nếu mã bán có TK Có bắt đầu bằng 5113 thì hiểu là khách hàng cấp NVL.
- Không phân bổ NVL mua ngoài vào mã đó.
- Định mức NVL = 0.
- Mã này không được dùng làm mã nhận phân bổ NVL.

### 4. Thời gian check

- Được giảm nếu cần.
- Không được giảm về 0.
- Nếu thời gian đề xuất quá thấp thì đưa vào danh sách cần soát lại.

### 5. ĐVT NVL

- Nếu NVL có đơn vị tính là kg thì định mức phải hợp lý.
- Không được sinh định mức vô lý, ví dụ 1 sản phẩm dùng 1kg NVL nếu không có cơ sở.

### 6. Khách hàng

- Ưu tiên phân bổ trong cùng khách hàng.
- Nếu cần để hết âm, cho phép nới Toyo/Sato nhận qua lại.
- Việc nới khách hàng phải được ghi chú riêng.

### 7. Tổng giá thành

- Ưu tiên giữ tổng giá thành không đổi bằng cách chuyển phân bổ.
- Nếu không đủ mã nhận chi phí hợp lý, được phép giảm tổng giá thành.
- Mức giảm phải vừa đủ để hết âm, không giảm quá tay.

---

## Quy tắc kỹ thuật

1. Không sửa file Excel gốc.
2. Luôn ghi kết quả ra thư mục Output.
3. Mỗi module chỉ làm một việc.
4. Không viết toàn bộ logic vào một file.
5. Không dùng vòng lặp vô hạn.
6. Mọi thay đổi phải có log.
7. Nếu không đủ dữ liệu để quyết định, phải xuất cảnh báo thay vì tự đoán.

---

## Cấu trúc dự án

- Python/models.py: định nghĩa Product.
- Python/reader.py: đọc workbook.
- Python/optimizer.py: phân nhóm mã âm, mã dương, khách hàng.
- Python/cost_solver.py: tính phương án tối ưu.
- Python/writer.py: ghi file kết quả.
- Python/report.py: xuất báo cáo.
- Python/cost_engine.py: chạy toàn bộ chương trình.

---

## Nguyên tắc phát triển

- Mỗi Sprint chỉ hoàn thiện một nhóm chức năng.
- Sau mỗi Sprint phải chạy thử trên file tháng 07/2025.
- Nếu kết quả xấu hơn bản trước thì không chấp nhận.
- File tháng 07/2025 là bộ dữ liệu kiểm thử chuẩn.