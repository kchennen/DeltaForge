"""Sample data for demonstration — text, image, and PDF examples."""

from __future__ import annotations

import base64
import io

# Duplicates sample #####################################################################
SAMPLE_DUPLICATES = "\n".join(
    [
        "apple",
        "banana",
        "apple",
        "cherry",
        "banana",
        "apple",
        "date",
        "cherry",
        "elderberry",
        "banana",
        "fig",
        "apple",
        "grape",
        "banana",
        "cherry",
        "apple",
        "date",
        "elderberry",
        "honeydew",
        "kiwi",
        "lemon",
        "mango",
        "banana",
        "nectarine",
    ]
)

# Text samples ##########################################################################
SAMPLE_TEXT_A = """\
#!/usr/bin/env python3
\"\"\"
E-commerce order processing service — v1.2.0
Handles discounts, tax calculation, inventory checks, and order fulfilment.
\"\"\"

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

TAX_RATES: dict[str, float] = {
    "US": 0.08,
    "CA": 0.13,
    "GB": 0.20,
    "AU": 0.10,
}

DISCOUNT_TIERS: dict[str, float] = {
    "vip":    0.20,
    "member": 0.10,
    "new":    0.05,
    "guest":  0.00,
}


@dataclass
class OrderItem:
    sku: str
    name: str
    price: float
    qty: int
    weight_kg: float = 0.5

    @property
    def subtotal(self) -> float:
        return round(self.price * self.qty, 2)


@dataclass
class OrderResult:
    order_id: str
    items: list[OrderItem]
    customer_type: str
    country: str
    subtotal: float
    discount_amount: float
    tax_amount: float
    shipping_cost: float
    total: float
    created_at: datetime = field(default_factory=datetime.utcnow)
    notes: list[str] = field(default_factory=list)


def calculate_discount(subtotal: float, customer_type: str) -> float:
    \"\"\"Return discount amount based on customer tier.\"\"\"
    rate = DISCOUNT_TIERS.get(customer_type, 0.0)
    return round(subtotal * rate, 2)


def calculate_tax(amount: float, country: str) -> float:
    \"\"\"Return tax amount for the given country code.\"\"\"
    rate = TAX_RATES.get(country.upper(), 0.08)
    return round(amount * rate, 2)


def calculate_shipping(items: list[OrderItem], country: str) -> float:
    \"\"\"Flat-rate shipping with a free threshold.\"\"\"
    total_weight = sum(item.weight_kg * item.qty for item in items)
    base_rate = 5.99 if country == "US" else 14.99
    if total_weight > 10:
        base_rate += (total_weight - 10) * 0.75
    return round(base_rate, 2)


def check_inventory(items: list[OrderItem]) -> list[str]:
    \"\"\"Stub: returns SKUs that are out of stock.\"\"\"
    # Real implementation would query the warehouse DB
    return []


def process_order(
    items: list[OrderItem],
    customer_type: str = "guest",
    country: str = "US",
    order_id: Optional[str] = None,
) -> OrderResult:
    \"\"\"
    Process a customer order end-to-end.

    1. Validate inventory
    2. Apply tier discount
    3. Calculate tax on discounted amount
    4. Compute shipping
    5. Return a structured OrderResult
    \"\"\"
    if not items:
        raise ValueError("Order must contain at least one item.")

    out_of_stock = check_inventory(items)
    if out_of_stock:
        raise RuntimeError(f"Items out of stock: {', '.join(out_of_stock)}")

    if order_id is None:
        order_id = f"ORD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    subtotal = round(sum(item.subtotal for item in items), 2)
    discount = calculate_discount(subtotal, customer_type)
    discounted = round(subtotal - discount, 2)
    tax = calculate_tax(discounted, country)
    shipping = calculate_shipping(items, country)
    total = round(discounted + tax + shipping, 2)

    notes: list[str] = []
    if discount > 0:
        notes.append(f"Tier discount ({customer_type}): -${discount:.2f}")
    if shipping == 0:
        notes.append("Free shipping applied.")

    logger.info("Order %s processed: total=$%.2f", order_id, total)

    return OrderResult(
        order_id=order_id,
        items=items,
        customer_type=customer_type,
        country=country,
        subtotal=subtotal,
        discount_amount=discount,
        tax_amount=tax,
        shipping_cost=shipping,
        total=total,
        notes=notes,
    )
"""

SAMPLE_TEXT_B = """\
#!/usr/bin/env python3
\"\"\"
E-commerce order processing service — v2.0.0
Handles discounts, promo codes, tax calculation, inventory checks,
loyalty points, and order fulfilment across multiple currencies.
\"\"\"

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

TAX_RATES: dict[str, float] = {
    "US": 0.09,
    "CA": 0.13,
    "GB": 0.20,
    "AU": 0.10,
    "DE": 0.19,
    "FR": 0.20,
}

DISCOUNT_TIERS: dict[str, float] = {
    "vip":      0.25,
    "member":   0.15,
    "new":      0.10,
    "guest":    0.00,
    "employee": 0.40,
}

PROMO_CODES: dict[str, float] = {
    "SAVE10":   0.10,
    "WELCOME20": 0.20,
    "FLASH30":  0.30,
}

LOYALTY_RATE = 0.01  # 1 point per $1 spent


@dataclass
class OrderItem:
    sku: str
    name: str
    price: float
    qty: int
    weight_kg: float = 0.5
    category: str = "general"

    @property
    def subtotal(self) -> float:
        return round(self.price * self.qty, 2)


@dataclass
class OrderResult:
    order_id: str
    items: list[OrderItem]
    customer_type: str
    country: str
    subtotal: float
    discount_amount: float
    promo_discount: float
    tax_amount: float
    shipping_cost: float
    loyalty_points: int
    total: float
    currency: str = "USD"
    created_at: datetime = field(default_factory=datetime.utcnow)
    notes: list[str] = field(default_factory=list)


def calculate_discount(subtotal: float, customer_type: str) -> float:
    \"\"\"Return discount amount based on customer tier.\"\"\"
    rate = DISCOUNT_TIERS.get(customer_type, 0.0)
    return round(subtotal * rate, 2)


def apply_promo_code(amount: float, promo_code: str) -> float:
    \"\"\"Apply a promotional code and return the additional discount.\"\"\"
    rate = PROMO_CODES.get(promo_code.upper(), 0.0)
    return round(amount * rate, 2)


def calculate_tax(amount: float, country: str) -> float:
    \"\"\"Return tax amount for the given country code.\"\"\"
    rate = TAX_RATES.get(country.upper(), 0.09)
    return round(amount * rate, 2)


def calculate_shipping(items: list[OrderItem], country: str) -> float:
    \"\"\"Weight-based shipping with a free threshold above $75 subtotal.\"\"\"
    subtotal = sum(i.subtotal for i in items)
    if subtotal >= 75.0 and country == "US":
        return 0.0
    total_weight = sum(item.weight_kg * item.qty for item in items)
    base_rate = 5.99 if country == "US" else 19.99
    if total_weight > 10:
        base_rate += (total_weight - 10) * 0.65
    return round(base_rate, 2)


def award_loyalty_points(total: float) -> int:
    \"\"\"Return loyalty points earned for this order.\"\"\"
    return int(total * LOYALTY_RATE * 100)


def check_inventory(items: list[OrderItem]) -> list[str]:
    \"\"\"Stub: returns SKUs that are out of stock.\"\"\"
    # Real implementation would query the warehouse DB
    return []


def process_order(
    items: list[OrderItem],
    customer_type: str = "guest",
    country: str = "US",
    promo_code: str = "",
    order_id: Optional[str] = None,
    currency: str = "USD",
) -> OrderResult:
    \"\"\"
    Process a customer order end-to-end.

    1. Validate inventory
    2. Apply tier discount
    3. Apply promo code (stacked, capped at 50 %% combined)
    4. Calculate tax on discounted amount
    5. Compute shipping (free above $75 in the US)
    6. Award loyalty points
    7. Return a structured OrderResult
    \"\"\"
    if not items:
        raise ValueError("Order must contain at least one item.")

    out_of_stock = check_inventory(items)
    if out_of_stock:
        raise RuntimeError(f"Items out of stock: {', '.join(out_of_stock)}")

    if order_id is None:
        order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"

    subtotal = round(sum(item.subtotal for item in items), 2)

    # Tier discount
    discount = calculate_discount(subtotal, customer_type)
    after_tier = round(subtotal - discount, 2)

    # Promo code (cannot push combined discount above 50 %%)
    promo_discount = 0.0
    if promo_code:
        promo_discount = apply_promo_code(after_tier, promo_code)
        combined_rate = (discount + promo_discount) / subtotal if subtotal else 0
        if combined_rate > 0.50:
            promo_discount = round(subtotal * 0.50 - discount, 2)

    discounted = round(after_tier - promo_discount, 2)
    tax = calculate_tax(discounted, country)
    shipping = calculate_shipping(items, country)
    total = round(discounted + tax + shipping, 2)
    loyalty_points = award_loyalty_points(total)

    notes: list[str] = []
    if discount > 0:
        notes.append(f"Tier discount ({customer_type}): -${discount:.2f}")
    if promo_discount > 0:
        notes.append(f"Promo '{promo_code}': -${promo_discount:.2f}")
    if shipping == 0:
        notes.append("Free shipping applied.")
    notes.append(f"Loyalty points earned: {loyalty_points}")

    logger.info("Order %s processed: total=$%.2f (%s)", order_id, total, currency)

    return OrderResult(
        order_id=order_id,
        items=items,
        customer_type=customer_type,
        country=country,
        subtotal=subtotal,
        discount_amount=discount,
        promo_discount=promo_discount,
        tax_amount=tax,
        shipping_cost=shipping,
        loyalty_points=loyalty_points,
        total=total,
        currency=currency,
        notes=notes,
    )
"""


# Image samples #########################################################################
def _make_sample_image(
    width: int = 400,
    height: int = 300,
    bg_color: tuple[int, int, int] = (240, 248, 255),
    header_color: tuple[int, int, int] = (70, 130, 180),
    text_lines: list[str] | None = None,
) -> bytes:
    """Generate a simple sample PNG image."""
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Header bar
    draw.rectangle([0, 0, width, 50], fill=header_color)

    # Horizontal rule below header
    draw.rectangle([20, 60, width - 20, 62], fill=(180, 200, 220))

    # Content lines
    y = 75
    for line in text_lines or []:
        draw.text((20, y), line, fill=(40, 40, 40))
        y += 22

    # Footer bar
    draw.rectangle([0, height - 30, width, height], fill=(200, 210, 220))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def sample_image_a_uri() -> str:
    """Return sample image A as a base64 data URI."""
    raw = _make_sample_image(
        bg_color=(240, 248, 255),
        header_color=(70, 130, 180),
        text_lines=[
            "Product: Laptop Pro X1",
            "Price:   $1,299.00",
            "Stock:   42 units",
            "Status:  Available",
            "",
            "Rating:  4.5 / 5.0",
            "Reviews: 128",
        ],
    )
    b64 = base64.b64encode(raw).decode()
    return f"data:image/png;base64,{b64}"


def sample_image_b_uri() -> str:
    """Return sample image B as a base64 data URI."""
    raw = _make_sample_image(
        bg_color=(255, 248, 240),
        header_color=(180, 100, 60),
        text_lines=[
            "Product: Laptop Pro X2",
            "Price:   $1,499.00",
            "Stock:   17 units",
            "Status:  Low Stock",
            "",
            "Rating:  4.7 / 5.0",
            "Reviews: 256",
        ],
    )
    b64 = base64.b64encode(raw).decode()
    return f"data:image/png;base64,{b64}"


# PDF samples ###########################################################################
def _make_sample_pdf(pages: list[list[str]]) -> bytes:
    """Generate a simple multi-page PDF with the given lines per page."""
    import fitz

    doc = fitz.open()
    for page_lines in pages:
        page = doc.new_page(width=595, height=842)  # A4
        y = 72
        for line in page_lines:
            if line.startswith("##"):
                page.insert_text((50, y), line[2:].strip(), fontsize=14)  # type: ignore[attr-defined,union-attr]
                y += 24
            elif line.startswith("---"):
                page.draw_line((50, y), (545, y))  # type: ignore[attr-defined,union-attr]
                y += 16
            else:
                page.insert_text((50, y), line, fontsize=11)  # type: ignore[attr-defined,union-attr]
                y += 18
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def sample_pdf_a_uri() -> str:
    """Return sample PDF A (original contract) as a base64 data URI."""
    pages = [
        [
            "## Software License Agreement",
            "---",
            "Version: 1.0   Date: January 15, 2025",
            "",
            "## 1. Grant of License",
            "",
            "Subject to the terms of this Agreement, Licensor hereby",
            "grants Licensee a non-exclusive, non-transferable license",
            "to use the Software for internal business purposes only.",
            "",
            "## 2. Payment Terms",
            "",
            "Licensee agrees to pay the annual fee of $5,000 USD.",
            "Payment is due within 30 days of invoice.",
            "Late payments incur a 2% monthly penalty.",
            "",
            "## 3. Support",
            "",
            "Licensor will provide email support during business hours.",
            "Response time: 48 hours for standard requests.",
        ],
        [
            "## 4. Termination",
            "---",
            "Either party may terminate with 60 days written notice.",
            "Upon termination, Licensee must destroy all copies.",
            "",
            "## 5. Limitation of Liability",
            "",
            "In no event shall Licensor be liable for indirect,",
            "incidental, or consequential damages.",
            "Total liability shall not exceed the fees paid in the",
            "prior 12 months.",
            "",
            "## Signatures",
            "",
            "Licensor: _____________________  Date: ___________",
            "Licensee: _____________________  Date: ___________",
        ],
    ]
    raw = _make_sample_pdf(pages)
    b64 = base64.b64encode(raw).decode()
    return f"data:application/pdf;base64,{b64}"


def sample_pdf_b_uri() -> str:
    """Return sample PDF B (revised contract) as a base64 data URI."""
    pages = [
        [
            "## Software License Agreement",
            "---",
            "Version: 2.0   Date: March 1, 2025",
            "",
            "## 1. Grant of License",
            "",
            "Subject to the terms of this Agreement, Licensor hereby",
            "grants Licensee a non-exclusive, non-transferable license",
            "to use the Software for internal and external purposes.",
            "",
            "## 2. Payment Terms",
            "",
            "Licensee agrees to pay the annual fee of $7,500 USD.",
            "Payment is due within 15 days of invoice.",
            "Late payments incur a 1.5% monthly penalty.",
            "",
            "## 3. Support",
            "",
            "Licensor will provide email and phone support 24/7.",
            "Response time: 24 hours for all requests.",
        ],
        [
            "## 4. Termination",
            "---",
            "Either party may terminate with 90 days written notice.",
            "Upon termination, Licensee must destroy all copies.",
            "",
            "## 5. Limitation of Liability",
            "",
            "In no event shall Licensor be liable for indirect,",
            "incidental, or consequential damages.",
            "Total liability shall not exceed twice the fees paid in",
            "the prior 12 months.",
            "",
            "## Signatures",
            "",
            "Licensor: _____________________  Date: ___________",
            "Licensee: _____________________  Date: ___________",
        ],
    ]
    raw = _make_sample_pdf(pages)
    b64 = base64.b64encode(raw).decode()
    return f"data:application/pdf;base64,{b64}"


# Excel samples #########################################################################
def _make_sample_xlsx(sheets: dict[str, list[list[str]]]) -> bytes:
    """Generate a simple xlsx workbook from a dict of sheet_name → rows (first row = header)."""
    from openpyxl import Workbook

    wb = Workbook()
    wb.remove(wb.active)  # type: ignore[arg-type]
    for sheet_name, rows in sheets.items():
        ws = wb.create_sheet(title=sheet_name)
        for row in rows:
            ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def sample_excel_a_uri() -> str:
    """Return sample Excel A (Q1 sales report) as a base64 data URI."""
    raw = _make_sample_xlsx(
        {
            "Q1 Sales": [
                ["Product", "Region", "Units", "Revenue", "Cost"],
                ["Laptop Pro X1", "North", "142", "184418", "91000"],
                ["Laptop Pro X1", "South", "98", "127302", "62720"],
                ["Tablet Z9", "North", "210", "104790", "63000"],
                ["Tablet Z9", "South", "175", "87325", "52500"],
                ["Phone S22", "North", "450", "202500", "135000"],
                ["Phone S22", "South", "320", "144000", "96000"],
                ["Headset X1", "North", "580", "81200", "29000"],
                ["Headset X1", "South", "410", "57400", "20500"],
            ],
            "Summary": [
                ["Metric", "Value"],
                ["Total Revenue", "988935"],
                ["Total Cost", "549720"],
                ["Gross Profit", "439215"],
                ["Top Product", "Laptop Pro X1"],
                ["Top Region", "North"],
            ],
        }
    )
    b64 = base64.b64encode(raw).decode()
    return f"data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}"


def sample_excel_b_uri() -> str:
    """Return sample Excel B (Q1 sales report — updated figures) as a base64 data URI."""
    raw = _make_sample_xlsx(
        {
            "Q1 Sales": [
                ["Product", "Region", "Units", "Revenue", "Cost", "Discount"],
                ["Laptop Pro X1", "North", "155", "201450", "99200", "5%"],
                ["Laptop Pro X1", "South", "110", "143000", "70400", "5%"],
                ["Tablet Z9", "North", "198", "98802", "59400", "0%"],
                ["Tablet Z9", "South", "190", "94810", "57000", "0%"],
                ["Phone S22", "North", "490", "220500", "147000", "2%"],
                ["Phone S22", "South", "355", "159750", "106500", "2%"],
                ["Headset X1", "North", "600", "84000", "30000", "0%"],
                ["Headset X1", "South", "425", "59500", "21250", "0%"],
                ["Smart Watch W1", "North", "280", "139720", "84000", "3%"],
            ],
            "Summary": [
                ["Metric", "Value"],
                ["Total Revenue", "1201532"],
                ["Total Cost", "674750"],
                ["Gross Profit", "526782"],
                ["Top Product", "Phone S22"],
                ["Top Region", "North"],
                ["New Products", "1"],
            ],
        }
    )
    b64 = base64.b64encode(raw).decode()
    return f"data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}"
