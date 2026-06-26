from dataclasses import dataclass, field


@dataclass
class BomLine:
    row: int = 0

    ma_hang: str = ""

    ma_nvl: str = ""
    ten_nvl: str = ""
    dvt: str = ""

    dinh_muc: float = 0


@dataclass
class Product:
    row: int = 0

    ma_hang: str = ""
    ten_hang: str = ""

    ma_khach: str = ""
    khach_hang: str = ""

    tk511: str = ""
    khach_cap_nvl: bool = False

    # BOM nhiều dòng NVL
    bom_lines: list = field(default_factory=list)

    # Dữ liệu tổng hợp để tương thích code cũ
    ma_nvl: str = ""
    dvt: str = ""
    dinh_muc: float = 0

    thoi_gian: float = 0
    nhan_cong: float = 0

    gia_ban: float = 0
    gia_thanh: float = 0
    al: float = 0

    reasons: list = field(default_factory=list)
    suggestions: list = field(default_factory=list)