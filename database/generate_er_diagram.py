"""Draws database/er_diagram.png from the table definitions below (needs Pillow).
Run:  python database/generate_er_diagram.py"""

import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "er_diagram.png")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(size, bold=False):
    try:
        return ImageFont.truetype(BOLD if bold else FONT, size)
    except OSError:
        return ImageFont.load_default()


TABLES = {
    "users": ("#4f46e5", [
        ("PK", "id", "SERIAL"), ("", "username", "VARCHAR(50) UNIQUE"),
        ("", "email", "VARCHAR(100) UNIQUE"), ("", "password_hash", "VARCHAR(255)"),
        ("", "full_name", "VARCHAR(100)"), ("", "created_at", "TIMESTAMP")]),
    "categories": ("#059669", [
        ("PK", "id", "SERIAL"), ("FK", "user_id", "INTEGER -> users.id"),
        ("", "name", "VARCHAR(50)  (unique per user)"), ("", "description", "TEXT"),
        ("", "color", "VARCHAR(7)"), ("", "budget_limit", "NUMERIC(10,2) >= 0"),
        ("", "created_at", "TIMESTAMP")]),
    "expenses": ("#d97706", [
        ("PK", "id", "SERIAL"), ("FK", "user_id", "INTEGER -> users.id"),
        ("FK", "category_id", "INTEGER -> categories.id"), ("", "amount", "NUMERIC(10,2) > 0"),
        ("", "expense_date", "DATE"), ("", "payment_method", "VARCHAR(30)"),
        ("", "description", "TEXT"), ("", "created_at", "TIMESTAMP"), ("", "updated_at", "TIMESTAMP")]),
}

W, H = 1500, 760
img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)
d.text((40, 24), "Expense Tracker System - ER Diagram (PostgreSQL)", font=font(28, True), fill="#111827")
d.text((40, 64), "Candidate: Prithika M  |  Monarch Softwares Final Round Task", font=font(16), fill="#6b7280")

BOX_W, ROW_H, TOP = 430, 34, 130
xs = {"users": 40, "categories": 535, "expenses": 1030}
boxes = {}
for name, (color, cols) in TABLES.items():
    x, y = xs[name], TOP
    h = 44 + ROW_H * len(cols)
    d.rounded_rectangle((x, y, x + BOX_W, y + h), 10, fill="white", outline=color, width=3)
    d.rounded_rectangle((x, y, x + BOX_W, y + 44), 10, fill=color)
    d.text((x + 16, y + 9), name, font=font(20, True), fill="white")
    for i, (key, col, typ) in enumerate(cols):
        ry = y + 44 + i * ROW_H
        if i % 2:
            d.rectangle((x + 3, ry, x + BOX_W - 3, ry + ROW_H), fill="#f3f4f6")
        if key:
            d.rounded_rectangle((x + 10, ry + 6, x + 48, ry + 28), 5, fill="#facc15" if key == "PK" else "#93c5fd")
            d.text((x + 16, ry + 8), key, font=font(12, True), fill="#111827")
        d.text((x + 58, ry + 8), col, font=font(15, key == "PK"), fill="#111827")
        d.text((x + 195, ry + 9), typ, font=font(12), fill="#4b5563")
    boxes[name] = (x, y, x + BOX_W, y + h)


def arrow(p1, p2, label, lx, ly):
    d.line([p1, p2], fill="#374151", width=3)
    d.text((lx, ly), label, font=font(15, True), fill="#374151")


# users 1 -> N categories, categories 1 -> N expenses
arrow((boxes["users"][2], TOP + 160), (boxes["categories"][0], TOP + 160), "1 : N", 478, TOP + 128)
arrow((boxes["categories"][2], TOP + 160), (boxes["expenses"][0], TOP + 160), "1 : N", 973, TOP + 128)
# users 1 -> N expenses (route under the boxes)
bottom = max(b[3] for b in boxes.values()) + 50
ux = (boxes["users"][0] + boxes["users"][2]) // 2
ex = boxes["expenses"][0] + BOX_W // 2
d.line([(ux, boxes["users"][3]), (ux, bottom), (ex, bottom), (ex, boxes["expenses"][3])], fill="#374151", width=3)
d.text((ux + 20, bottom - 26), "1 : N  (a user owns many expenses)", font=font(15, True), fill="#374151")

notes = [
    "Relationships:  users 1-N categories,  users 1-N expenses,  categories 1-N expenses.",
    "Deleting a user cascades to their data. A category that still has expenses cannot be deleted (ON DELETE RESTRICT).",
]
for i, t in enumerate(notes):
    d.text((40, H - 70 + i * 26), t, font=font(14), fill="#374151")
img.save(OUT)
print("Saved", OUT)
