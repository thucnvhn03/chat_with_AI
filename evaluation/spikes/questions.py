"""Sinh câu hỏi có đáp án đã biết từ `ground_truth.json` của bộ PDF tổng hợp.

Dùng chung cho spike truy xuất (T0-07) và để dựng bản nháp bộ câu hỏi chuẩn v1 (T2-13). Bộ câu hỏi chính
thức phải được business owner duyệt và bổ sung trên tài liệu thật (DEP-001, ASM-005).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

TEMPLATES: dict[str, list[str]] = {
    "contract_value": ["Tổng giá trị ước tính của hợp đồng với Công ty {company} là bao nhiêu?"],
    "payment_term": [
        "Thời hạn thanh toán trong hợp đồng với Công ty {company} là bao nhiêu ngày?",
        "Công ty {company} phải thanh toán trong vòng bao lâu sau khi nhận hóa đơn?",
    ],
    "deposit": ["Công ty {company} phải đặt cọc bao nhiêu phần trăm mỗi đơn hàng?"],
    "late_fee": [
        "Nếu Công ty {company} thanh toán chậm thì bị phạt bao nhiêu mỗi ngày?",
        "Mức phạt chậm thanh toán áp dụng cho Công ty {company} là bao nhiêu?",
    ],
    "delivery_penalty": ["Việt Tín bị phạt bao nhiêu nếu giao hàng trễ cho Công ty {company}?"],
    "duration": ["Hợp đồng với Công ty {company} có hiệu lực trong bao lâu?"],
    "notice": ["Muốn chấm dứt hợp đồng với Công ty {company} thì phải báo trước bao nhiêu ngày?"],
    "tier_price": ["Gói {tier} của dịch vụ {service} có giá bao nhiêu mỗi tháng?"],
    "prepay": ["Khách hàng dịch vụ {service} phải thanh toán trước bao nhiêu phần trăm?"],
    "validity": ["Báo giá dịch vụ {service} có hiệu lực trong bao nhiêu ngày?"],
    "budget": ["Ngân sách đề xuất cho dự án {project} là bao nhiêu?"],
    "stores": ["Dự án {project} dự kiến tiếp cận bao nhiêu điểm bán?"],
    "warehouses": ["How many bonded warehouses does Lotus Freight International operate?"],
    "clearance": ["What is the standard customs clearance time offered by Lotus Freight International?"],
}

# Câu hỏi không có đáp án trong bộ tài liệu (để đo tỷ lệ bịa)
OUT_OF_SCOPE = [
    "Thủ đô của nước Úc là thành phố nào?",
    "Hợp đồng với Công ty Bắc Hải có thời hạn thanh toán bao nhiêu ngày?",
    "Giá gói dịch vụ bảo hiểm sức khỏe nhân viên là bao nhiêu?",
    "Ai là tổng giám đốc của Công ty Việt Tín?",
    "Dự án mở rộng sang thị trường Campuchia có ngân sách bao nhiêu?",
    "Tỷ giá đô la Mỹ hôm nay là bao nhiêu?",
    "Công ty Hoàng Hà thành lập năm nào?",
    "Mức lương tối thiểu vùng năm 2026 là bao nhiêu?",
    "Báo giá dịch vụ vệ sinh công nghiệp có hiệu lực bao lâu?",
    "Hợp đồng với Công ty Minh Long có điều khoản về quyền sở hữu trí tuệ phần mềm không?",
    "What is the annual revenue of Lotus Freight International?",
    "Số điện thoại liên hệ của đầu mối bên Phú Gia là gì?",
]


@dataclass
class GeneratedQuestion:
    id: str
    type: str
    question: str
    lang: str
    expected_answer: str | None = None
    expected_keywords: list[str] = field(default_factory=list)
    expected_sources: list[dict[str, Any]] = field(default_factory=list)
    history: list[str] = field(default_factory=list)

    def to_json(self) -> dict[str, Any]:
        data: dict[str, Any] = {"id": self.id, "lang": self.lang, "type": self.type, "question": self.question}
        if self.history:
            data["history"] = self.history
        if self.expected_answer:
            data["expected_answer"] = self.expected_answer
        if self.expected_keywords:
            data["expected_keywords"] = self.expected_keywords
        if self.expected_sources:
            data["expected_sources"] = self.expected_sources
        return data


def load_truth(corpus: Path) -> dict[str, Any]:
    data: dict[str, Any] = json.loads((corpus / "ground_truth.json").read_text(encoding="utf-8"))
    return data


def in_scope_questions(truth: dict[str, Any], variant: int = 0) -> list[GeneratedQuestion]:
    result: list[GeneratedQuestion] = []
    for i, fact in enumerate(truth["facts"]):
        templates = TEMPLATES[fact["key"]]
        template = templates[variant % len(templates)]
        lang = "en" if fact["document"].endswith("_EN.pdf") else "vi"
        result.append(
            GeneratedQuestion(
                id=f"in{i:03d}",
                type="in_scope",
                question=template.format(**fact["extra"]),
                lang=lang,
                expected_answer=fact["sentence"],
                expected_keywords=[fact["value"].split()[0]],
                expected_sources=[{"document": fact["document"], "page": fact["page"]}],
            )
        )
    return result


def multi_doc_questions(truth: dict[str, Any]) -> list[GeneratedQuestion]:
    """Câu hỏi so sánh giữa hai hợp đồng / hai báo giá: đáp án nằm ở hai tài liệu khác nhau."""
    facts = truth["facts"]
    by_key: dict[str, list[dict[str, Any]]] = {}
    for f in facts:
        by_key.setdefault(f["key"], []).append(f)
    result: list[GeneratedQuestion] = []

    def add(a: dict[str, Any], b: dict[str, Any], text: str) -> None:
        result.append(
            GeneratedQuestion(
                id=f"md{len(result):03d}",
                type="multi_doc",
                question=text,
                lang="vi",
                expected_answer=f"{a['sentence']} {b['sentence']}",
                expected_keywords=[a["value"].split()[0], b["value"].split()[0]],
                expected_sources=[
                    {"document": a["document"], "page": a["page"]},
                    {"document": b["document"], "page": b["page"]},
                ],
            )
        )

    terms = by_key["payment_term"]
    for a, b in zip(terms[0::2], terms[1::2], strict=False):
        add(
            a,
            b,
            f"So sánh thời hạn thanh toán trong hợp đồng với Công ty {a['extra']['company']} và Công ty {b['extra']['company']}.",
        )
    fees = by_key["late_fee"]
    for a, b in zip(fees[0::2], fees[1::2], strict=False):
        add(
            a,
            b,
            f"Mức phạt chậm thanh toán của Công ty {a['extra']['company']} và Công ty {b['extra']['company']} khác nhau thế nào?",
        )
    prepay = by_key["prepay"]
    for a, b in zip(prepay[0::2], prepay[1::2], strict=False):
        add(
            a,
            b,
            f"Tỷ lệ thanh toán trước của dịch vụ {a['extra']['service']} và dịch vụ {b['extra']['service']} là bao nhiêu?",
        )
    return result


def follow_up_questions(truth: dict[str, Any]) -> list[GeneratedQuestion]:
    """Câu hỏi tiếp theo dùng đại từ, cần ngữ cảnh câu trước (US-010, AC-008)."""
    result: list[GeneratedQuestion] = []
    for f in truth["facts"]:
        company = f["extra"].get("company")
        if not company:
            continue
        if f["key"] == "late_fee":
            first = f"Hợp đồng với Công ty {company} có điều khoản phạt chậm thanh toán không?"
            follow = "Mức phạt đó là bao nhiêu mỗi ngày?"
        elif f["key"] == "notice":
            first = f"Hợp đồng với Công ty {company} có cho phép đơn phương chấm dứt không?"
            follow = "Phải báo trước bao nhiêu ngày?"
        else:
            continue
        result.append(
            GeneratedQuestion(
                id=f"fu{len(result):03d}",
                type="follow_up",
                question=follow,
                lang="vi",
                history=[first],
                expected_answer=f["sentence"],
                expected_keywords=[f["value"].split()[0]],
                expected_sources=[{"document": f["document"], "page": f["page"]}],
            )
        )
    return result


def out_of_scope_questions() -> list[GeneratedQuestion]:
    return [
        GeneratedQuestion(id=f"oo{i:03d}", type="out_of_scope", question=q, lang="en" if q.isascii() else "vi")
        for i, q in enumerate(OUT_OF_SCOPE)
    ]
