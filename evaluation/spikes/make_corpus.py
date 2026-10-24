"""Sinh bộ PDF tổng hợp, KHÔNG nhạy cảm, có đáp án đã biết — dùng cho spike T0-06/T0-07/T0-08 và bộ câu
hỏi chuẩn phiên bản 1 (T2-13) khi chưa có tập PDF thật từ business owner (DEP-001).

    python evaluation/spikes/make_corpus.py --out evaluation/spikes/corpus

Tạo ra:
- 22 tệp PDF: 8 hợp đồng (4 trang), 6 báo giá (bảng giá), 4 đề xuất (bố cục hai cột), 1 hồ sơ đối tác tiếng
  Anh, 1 PDF mã hóa, 2 PDF dạng ảnh scan.
- `ground_truth.json`: văn bản gốc từng trang (để đo chất lượng trích xuất) và các "sự kiện" (fact) kèm
  tài liệu, trang nơi chúng xuất hiện (để sinh câu hỏi có đáp án).
Mọi tên công ty, con số là hư cấu, sinh tất định từ hạt giống cố định.
"""

from __future__ import annotations

import argparse
import io
import json
import random
from dataclasses import asdict, dataclass, field
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

FONT_PATHS = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "C:/Windows/Fonts/arial.ttf"]
SEED = 20261022

COMPANIES = [
    "An Bình", "Minh Long", "Sao Việt", "Hưng Thịnh", "Phú Gia", "Đại Dương Xanh", "Trường Sơn", "Kim Ngân",
]  # fmt: skip
SERVICES = ["Lưu kho", "Vận chuyển lạnh", "Bảo trì thiết bị", "Đào tạo nhân sự", "Phần mềm kế toán", "In ấn bao bì"]
PROJECTS = ["Mở rộng miền Trung", "Kênh bán lẻ trực tuyến", "Chuỗi cửa hàng tiện lợi", "Trung tâm phân phối Cần Thơ"]

BOILERPLATE = [
    "Các bên cam kết thực hiện đúng và đầy đủ các điều khoản đã thỏa thuận trong văn bản này.",
    "Mọi sửa đổi, bổ sung phải được lập thành văn bản và có chữ ký của đại diện hợp pháp hai bên.",
    "Trong quá trình thực hiện, nếu phát sinh vướng mắc, các bên chủ động thông báo cho nhau để cùng giải quyết.",
    "Thông tin trao đổi giữa các bên được bảo mật và chỉ sử dụng cho mục đích thực hiện thỏa thuận.",
    "Các bên tuân thủ quy định pháp luật hiện hành về thuế, kế toán và bảo vệ người tiêu dùng.",
    "Hồ sơ, chứng từ liên quan được lưu trữ đầy đủ để phục vụ đối chiếu khi cần thiết.",
    "Bên nhận có trách nhiệm kiểm tra số lượng, chất lượng hàng hóa ngay khi giao nhận.",
    "Biên bản giao nhận là căn cứ để xác định thời điểm chuyển giao rủi ro giữa các bên.",
    "Mỗi bên chỉ định một đầu mối liên hệ để phối hợp công việc hằng ngày.",
    "Các thông báo được gửi bằng văn bản tới địa chỉ đã đăng ký của mỗi bên.",
    "Văn bản này được lập thành hai bản có giá trị pháp lý như nhau, mỗi bên giữ một bản.",
    "Trường hợp bất khả kháng, bên bị ảnh hưởng được miễn trách nhiệm trong phạm vi bị ảnh hưởng.",
    "Các bên ưu tiên giải quyết tranh chấp bằng thương lượng trên tinh thần thiện chí.",
    "Kế hoạch triển khai chi tiết được hai bên thống nhất trước ngày bắt đầu thực hiện.",
    "Bên cung cấp bảo đảm nhân sự thực hiện có đủ năng lực và kinh nghiệm phù hợp.",
]


@dataclass
class Fact:
    key: str
    document: str
    page: int
    value: str
    sentence: str
    extra: dict[str, str] = field(default_factory=dict)


@dataclass
class DocInfo:
    file_name: str
    kind: str
    pages: list[str]
    note: str = ""


def register_font() -> str:
    for path in FONT_PATHS:
        if Path(path).exists():
            pdfmetrics.registerFont(TTFont("CorpusSans", path))
            return "CorpusSans"
    raise SystemExit("Không tìm thấy phông Unicode (cần DejaVuSans)")


def filler(rng: random.Random, n: int) -> list[str]:
    return [rng.choice(BOILERPLATE) for _ in range(n)]


def styles(font: str) -> tuple[ParagraphStyle, ParagraphStyle]:
    body = ParagraphStyle("body", fontName=font, fontSize=10.5, leading=15, spaceAfter=6)
    head = ParagraphStyle("head", fontName=font, fontSize=13, leading=18, spaceAfter=10)
    return body, head


def build_simple(path: Path | io.BytesIO, font: str, pages: list[list[tuple[str, str]]]) -> None:
    """Mỗi trang là danh sách (kiểu, văn bản) với kiểu 'h' (tiêu đề) hoặc 'p' (đoạn)."""
    body, head = styles(font)
    story = []
    for i, page in enumerate(pages):
        for kind, text in page:
            story.append(Paragraph(text, head if kind == "h" else body))
        if i < len(pages) - 1:
            story.append(PageBreak())
    SimpleDocTemplate(
        path if isinstance(path, io.BytesIO) else str(path), pagesize=A4, title=getattr(path, "stem", "doc")
    ).build(story)


def page_text(page: list[tuple[str, str]]) -> str:
    return "\n".join(t for _, t in page)


def make_contracts(out: Path, font: str, rng: random.Random, facts: list[Fact], docs: list[DocInfo]) -> None:
    for company in COMPANIES:
        name = ascii_name("HopDong", company)
        term = rng.choice([15, 20, 30, 45, 60])
        deposit = rng.choice([10, 20, 30, 40])
        late = rng.choice(["0,03", "0,05", "0,08", "0,1"])
        delivery_penalty = rng.choice([2, 3, 5, 8])
        months = rng.choice([12, 18, 24, 36])
        notice = rng.choice([30, 45, 60, 90])
        value = rng.choice(["1,2", "2,5", "3,8", "4,6", "6,0", "7,5"])
        title = f"Hợp đồng phân phối giữa Công ty Cổ phần Thương mại Việt Tín và Công ty {company}"
        pages = [
            [
                ("h", title),
                (
                    "p",
                    f"Điều 1. Phạm vi. Công ty {company} là nhà phân phối độc quyền sản phẩm đồ gia dụng của Việt Tín tại khu vực được giao.",
                ),
                (
                    "p",
                    f"Điều 2. Giá trị hợp đồng. Tổng giá trị ước tính của hợp đồng với Công ty {company} là {value} tỷ đồng chưa gồm thuế giá trị gia tăng.",
                ),
                *[("p", t) for t in filler(rng, 14)],
            ],
            [
                ("h", f"{title} — Điều khoản thanh toán"),
                (
                    "p",
                    f"Điều 3. Thanh toán. Thời hạn thanh toán là {term} ngày kể từ ngày Công ty {company} nhận hóa đơn hợp lệ.",
                ),
                ("p", f"Công ty {company} đặt cọc {deposit}% giá trị mỗi đơn hàng trước khi giao hàng."),
                *[("p", t) for t in filler(rng, 14)],
            ],
            [
                ("h", f"{title} — Phạt vi phạm"),
                (
                    "p",
                    f"Điều 7. Phạt chậm thanh toán. Nếu Công ty {company} thanh toán chậm, mức phạt là {late}% mỗi ngày trên số tiền chậm trả.",
                ),
                (
                    "p",
                    f"Điều 8. Phạt giao hàng trễ. Việt Tín giao hàng trễ hạn chịu phạt {delivery_penalty}% giá trị lô hàng giao trễ.",
                ),
                *[("p", t) for t in filler(rng, 13)],
            ],
            [
                ("h", f"{title} — Thời hạn và chấm dứt"),
                ("p", f"Điều 11. Thời hạn. Hợp đồng với Công ty {company} có hiệu lực {months} tháng kể từ ngày ký."),
                (
                    "p",
                    f"Điều 12. Chấm dứt. Mỗi bên được đơn phương chấm dứt hợp đồng nếu báo trước {notice} ngày bằng văn bản.",
                ),
                *[("p", t) for t in filler(rng, 13)],
            ],
        ]
        build_simple(out / name, font, pages)
        docs.append(DocInfo(name, "contract", [page_text(p) for p in pages]))
        facts += [
            Fact("contract_value", name, 1, f"{value} tỷ đồng", pages[0][2][1], {"company": company}),
            Fact("payment_term", name, 2, f"{term} ngày", pages[1][1][1], {"company": company}),
            Fact("deposit", name, 2, f"{deposit}%", pages[1][2][1], {"company": company}),
            Fact("late_fee", name, 3, f"{late}%", pages[2][1][1], {"company": company}),
            Fact("delivery_penalty", name, 3, f"{delivery_penalty}%", pages[2][2][1], {"company": company}),
            Fact("duration", name, 4, f"{months} tháng", pages[3][1][1], {"company": company}),
            Fact("notice", name, 4, f"{notice} ngày", pages[3][2][1], {"company": company}),
        ]


def ascii_name(prefix: str, label: str) -> str:
    import unicodedata

    plain = unicodedata.normalize("NFKD", label.replace("Đ", "D").replace("đ", "d"))
    plain = "".join(ch for ch in plain if ch.isalnum() and ord(ch) < 128)
    return f"{prefix}_{plain}.pdf"


def make_quotes(out: Path, font: str, rng: random.Random, facts: list[Fact], docs: list[DocInfo]) -> None:
    body, head = styles(font)
    for service in SERVICES:
        name = ascii_name("BaoGia", service)
        prices = {tier: rng.choice(range(5, 60)) for tier in ("Cơ bản", "Tiêu chuẩn", "Nâng cao")}
        prepay = rng.choice([30, 50, 70])
        validity = rng.choice([15, 30, 60])
        table_data = [["Gói dịch vụ", "Giá mỗi tháng (triệu đồng)", "Cam kết tối thiểu"]] + [
            [f"Gói {tier}", str(price), f"{rng.choice([3, 6, 12])} tháng"] for tier, price in prices.items()
        ]
        table = Table(table_data, colWidths=[150, 170, 130])
        table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), font),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ]
            )
        )
        intro = f"Bảng báo giá dịch vụ {service} năm 2026 của Công ty Dịch vụ Hoàng Hà gửi Việt Tín."
        conditions = [
            f"Điều kiện thanh toán dịch vụ {service}: khách hàng thanh toán trước {prepay}% giá trị hợp đồng.",
            f"Báo giá dịch vụ {service} có hiệu lực trong {validity} ngày kể từ ngày phát hành.",
        ]
        page2_fill = filler(rng, 12)
        story = [Paragraph(intro, head), Spacer(1, 8), table, Spacer(1, 12)]
        story += [Paragraph(t, body) for t in filler(rng, 6)]
        story += [PageBreak(), Paragraph(f"Điều kiện áp dụng báo giá {service}", head)]
        story += [Paragraph(t, body) for t in conditions + page2_fill]
        SimpleDocTemplate(str(out / name), pagesize=A4, title=name).build(story)
        table_text = "\n".join(" ".join(row) for row in table_data)
        docs.append(
            DocInfo(
                name,
                "quote",
                [
                    f"{intro}\n{table_text}",
                    "\n".join([f"Điều kiện áp dụng báo giá {service}", *conditions, *page2_fill]),
                ],
                "bảng giá",
            )
        )
        for tier, price in prices.items():
            facts.append(
                Fact("tier_price", name, 1, f"{price} triệu", f"Gói {tier} {price}", {"service": service, "tier": tier})
            )
        facts += [
            Fact("prepay", name, 2, f"{prepay}%", conditions[0], {"service": service}),
            Fact("validity", name, 2, f"{validity} ngày", conditions[1], {"service": service}),
        ]


def make_proposals(out: Path, font: str, rng: random.Random, facts: list[Fact], docs: list[DocInfo]) -> None:
    body, head = styles(font)
    for project in PROJECTS:
        name = ascii_name("DeXuat", project)
        budget = rng.choice(["850 triệu", "1,4 tỷ", "2,1 tỷ", "3,3 tỷ"])
        stores = rng.choice([12, 25, 40, 60])
        months = rng.choice([6, 9, 12])
        key_sentences = [
            f"Ngân sách đề xuất cho dự án {project} là {budget} đồng trong năm đầu.",
            f"Dự án {project} dự kiến tiếp cận {stores} điểm bán sau {months} tháng triển khai.",
        ]
        left = [f"Đề xuất dự án {project}", key_sentences[0], *filler(rng, 6)]
        right = [key_sentences[1], *filler(rng, 6)]

        doc = BaseDocTemplate(str(out / name), pagesize=A4, title=name)
        width, height = A4
        col = (width - 3 * 36) / 2
        frames = [Frame(36, 36, col, height - 72, id="left"), Frame(36 * 2 + col, 36, col, height - 72, id="right")]
        doc.addPageTemplates([PageTemplate(id="two", frames=frames)])
        from reportlab.platypus import FrameBreak

        story = [Paragraph(left[0], head)] + [Paragraph(t, body) for t in left[1:]]
        story += [FrameBreak()] + [Paragraph(t, body) for t in right]
        doc.build(story)
        docs.append(DocInfo(name, "proposal", ["\n".join(left + right)], "hai cột"))
        facts += [
            Fact("budget", name, 1, budget, key_sentences[0], {"project": project}),
            Fact(
                "stores", name, 1, f"{stores} điểm bán", key_sentences[1], {"project": project, "months": str(months)}
            ),
        ]


def make_english(out: Path, font: str, rng: random.Random, facts: list[Fact], docs: list[DocInfo]) -> None:
    name = "Partner_Profile_EN.pdf"
    lines = [
        "Partner profile: Lotus Freight International",
        "Lotus Freight International operates 14 bonded warehouses across Southeast Asia.",
        "The standard customs clearance time offered to partners is 48 hours.",
        "All shipments are insured up to 200,000 USD per container.",
        "Partners receive a dedicated account manager and quarterly performance reviews.",
    ] * 3
    build_simple(out / name, font, [[("h", lines[0])] + [("p", t) for t in lines[1:]]])
    docs.append(DocInfo(name, "english", ["\n".join(lines)], "tiếng Anh"))
    facts.append(Fact("warehouses", name, 1, "14", lines[1], {}))
    facts.append(Fact("clearance", name, 1, "48 hours", lines[2], {}))


def make_special(out: Path, font: str, rng: random.Random, docs: list[DocInfo]) -> None:
    # PDF mã hóa
    tmp = io.BytesIO()
    build_simple(tmp, font, [[("h", "Biên bản ghi nhớ nội bộ"), ("p", "Tài liệu có mật khẩu.")]])
    writer = PdfWriter(clone_from=PdfReader(io.BytesIO(tmp.getvalue())))
    writer.encrypt(user_password="khoa-123", owner_password="chu-so-huu", algorithm="AES-256")
    with (out / "BienBan_MaHoa.pdf").open("wb") as f:
        writer.write(f)
    docs.append(DocInfo("BienBan_MaHoa.pdf", "encrypted", [], "mã hóa"))
    # PDF dạng ảnh scan (chỉ có hình, không có lớp văn bản)
    from reportlab.pdfgen import canvas

    for i in (1, 2):
        name = f"Scan_HoaDon_{i}.pdf"
        c = canvas.Canvas(str(out / name), pagesize=A4)
        for _ in range(2):
            for _k in range(40):
                c.setFillGray(rng.random())
                c.rect(
                    rng.randint(30, 500),
                    rng.randint(30, 780),
                    rng.randint(20, 120),
                    rng.randint(5, 15),
                    fill=1,
                    stroke=0,
                )
            c.showPage()
        c.save()
        docs.append(DocInfo(name, "scan", [], "ảnh scan"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("evaluation/spikes/corpus"))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    font = register_font()
    rng = random.Random(SEED)
    facts: list[Fact] = []
    docs: list[DocInfo] = []
    make_contracts(args.out, font, rng, facts, docs)
    make_quotes(args.out, font, rng, facts, docs)
    make_proposals(args.out, font, rng, facts, docs)
    make_english(args.out, font, rng, facts, docs)
    make_special(args.out, font, rng, docs)
    truth = {"seed": SEED, "documents": [asdict(d) for d in docs], "facts": [asdict(f) for f in facts]}
    (args.out / "ground_truth.json").write_text(json.dumps(truth, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Đã tạo {len(docs)} PDF và {len(facts)} sự kiện trong {args.out}")


if __name__ == "__main__":
    main()
