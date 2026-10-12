
from flask import Flask, request, jsonify, render_template_string
import sqlite3
from datetime import date, datetime

app = Flask(__name__)
DB = "expenses.db"

CATEGORIES = [
    "Food", "Travel", "Shopping", "Education",
    "Bills", "Health", "Entertainment", "Other"
]
STATUSES = ["Planned", "Paid", "Reimbursed"]


# ---------------- DATABASE ----------------

def connect_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with connect_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                expense_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Paid',
                note TEXT DEFAULT '',
                created_at TEXT NOT NULL
            )
        """)


init_db()


# ---------------- FRONTEND ----------------

HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PennyWise | Expense Tracker</title>

<style>
* { box-sizing: border-box; }
body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #f5f7fb;
    color: #202943;
}
header {
    background: white;
    border-bottom: 1px solid #e5e8f0;
    padding: 20px 5%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
}
header h1 { margin: 0; font-size: 25px; }
header p { color: #7b8395; margin: 7px 0 0; }
.container { max-width: 1400px; margin: auto; padding: 25px 4%; }
button {
    border: 0;
    border-radius: 9px;
    padding: 11px 15px;
    cursor: pointer;
    font-weight: bold;
}
.primary { background: #4f46e5; color: white; }
.secondary { background: #e8eaff; color: #3730a3; }
.danger { background: #fee2e2; color: #b91c1c; }
.toolbar {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-bottom: 22px;
}
input, select, textarea {
    padding: 11px;
    border: 1px solid #dce1eb;
    border-radius: 9px;
    background: white;
    font: inherit;
    min-width: 0;
}
#search { flex: 1; min-width: 180px; }
.cards {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-bottom: 25px;
}
.card {
    background: white;
    border: 1px solid #eceef5;
    padding: 22px;
    border-radius: 14px;
}
.card span { color: #7b8395; font-size: 13px; }
.card h2 { margin: 12px 0 0; font-size: 27px; }
.section-title {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    margin: 25px 0 15px;
    flex-wrap: wrap;
}
.section-title h2 { font-size: 20px; margin: 0; }
.pipeline {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 16px;
}
.lane {
    background: #eceff6;
    border-radius: 13px;
    padding: 14px;
    min-height: 190px;
}
.lane h3 { margin: 5px 0 15px; font-size: 16px; }
.lane-count {
    background: white;
    padding: 4px 9px;
    border-radius: 15px;
    font-size: 12px;
}
.lane-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.expense-card {
    background: white;
    padding: 15px;
    border-radius: 11px;
    margin-bottom: 12px;
    border-left: 4px solid #6366f1;
    overflow-wrap: anywhere;
}
.expense-card h4 { margin: 0 0 8px; font-size: 15px; }
.amount { font-size: 20px; font-weight: bold; margin: 8px 0; }
.meta { color: #7b8395; font-size: 12px; line-height: 1.8; }
.card-actions { display: flex; flex-wrap: wrap; gap: 7px; margin-top: 12px; }
.card-actions button { padding: 7px 9px; font-size: 12px; }
.card-actions select { width: 100%; font-size: 12px; }
.list-wrap {
    background: white;
    border-radius: 14px;
    padding: 15px;
    overflow-x: auto;
}
table { width: 100%; border-collapse: collapse; min-width: 750px; }
th, td {
    padding: 14px 12px;
    text-align: left;
    border-bottom: 1px solid #edf0f5;
    font-size: 13px;
}
th { color: #777f91; background: #fafbfe; }
.badge {
    display: inline-block;
    border-radius: 20px;
    padding: 5px 9px;
    background: #e0e7ff;
    color: #3730a3;
    font-size: 12px;
}
dialog {
    border: 0;
    border-radius: 16px;
    padding: 25px;
    width: min(500px, 94%);
    box-shadow: 0 15px 60px #0003;
}
dialog::backdrop { background: #18213b88; }
.form-grid { display: grid; gap: 12px; }
.form-grid input, .form-grid select, .form-grid textarea { width: 100%; }
.form-grid textarea { min-height: 70px; resize: vertical; }
.form-actions { display: flex; justify-content: flex-end; gap: 10px; }
.empty { color: #8a91a2; padding: 20px 5px; font-size: 13px; text-align: center; }
@media(max-width: 800px) {
    .cards { grid-template-columns: 1fr; }
    .pipeline { grid-template-columns: 1fr; }
}
</style>
</head>

<body>
<header>
    <div>
        <h1>💰 PennyWise</h1>
        <p>Expense Tracker · Manage your money clearly</p>
    </div>
    <button class="primary" onclick="openNew()">+ Add Expense</button>
</header>

<main class="container">
    <div class="toolbar">
        <input id="search" placeholder="🔍 Search expenses..." oninput="render()">
        <select id="categoryFilter" onchange="render()">
            <option value="All">All Categories</option>
            <option>Food</option><option>Travel</option>
            <option>Shopping</option><option>Education</option>
            <option>Bills</option><option>Health</option>
            <option>Entertainment</option><option>Other</option>
        </select>
        <select id="statusFilter" onchange="render()">
            <option value="All">All Statuses</option>
            <option>Planned</option><option>Paid</option>
            <option>Reimbursed</option>
        </select>
        <button class="secondary" onclick="loadExpenses()">↻ Refresh</button>
    </div>

    <section class="cards">
        <div class="card">
            <span>TOTAL EXPENSES</span>
            <h2 id="total">₹0.00</h2>
        </div>
        <div class="card">
            <span>THIS MONTH · PAID</span>
            <h2 id="monthly">₹0.00</h2>
        </div>
        <div class="card">
            <span>TRANSACTIONS</span>
            <h2 id="transactions">0</h2>
        </div>
    </section>

    <div class="section-title">
        <h2>Expense Pipeline</h2>
        <span class="meta">Move expenses between stages</span>
    </div>

    <section class="pipeline">
        <div class="lane">
            <div class="lane-head">
                <h3>🗓 Planned</h3><span class="lane-count" id="count-Planned">0</span>
            </div>
            <div id="lane-Planned"></div>
        </div>
        <div class="lane">
            <div class="lane-head">
                <h3>💳 Paid</h3><span class="lane-count" id="count-Paid">0</span>
            </div>
            <div id="lane-Paid"></div>
        </div>
        <div class="lane">
            <div class="lane-head">
                <h3>↩ Reimbursed</h3><span class="lane-count" id="count-Reimbursed">0</span>
            </div>
            <div id="lane-Reimbursed"></div>
        </div>
    </section>

    <div class="section-title">
        <h2>Expense List</h2>
        <span class="meta" id="listCount">0 expenses</span>
    </div>

    <div class="list-wrap">
        <table>
            <thead>
                <tr>
                    <th>Expense</th><th>Category</th><th>Date</th>
                    <th>Amount</th><th>Status</th><th>Actions</th>
                </tr>
            </thead>
            <tbody id="expenseRows"></tbody>
        </table>
        <div id="emptyList" class="empty" hidden>No expenses found.</div>
    </div>
</main>

<dialog id="expenseDialog">
    <h2 id="dialogTitle">Add Expense</h2>
    <form id="expenseForm" class="form-grid">
        <label>Expense Name</label>
        <input id="title" maxlength="120" placeholder="e.g. Lunch" required>

        <label>Amount (₹)</label>
        <input id="amount" type="number" min="0.01" max="1000000000"
               step="0.01" placeholder="e.g. 250" required>

        <label>Category</label>
        <select id="category">
            <option>Food</option><option>Travel</option>
            <option>Shopping</option><option>Education</option>
            <option>Bills</option><option>Health</option>
            <option>Entertainment</option><option>Other</option>
        </select>

        <label>Expense Date</label>
        <input id="expenseDate" type="date" required>

        <label>Pipeline Status</label>
        <select id="status">
            <option>Planned</option><option selected>Paid</option>
            <option>Reimbursed</option>
        </select>

        <label>Notes (optional)</label>
        <textarea id="note" maxlength="1000" placeholder="Add details..."></textarea>

        <div class="form-actions">
            <button type="button" class="secondary" onclick="closeDialog()">Cancel</button>
            <button type="submit" class="primary">Save Expense</button>
        </div>
    </form>
</dialog>

<script>
let expenses = [];
let editingId = null;
const $ = id => document.getElementById(id);
const money = n => "₹" + Number(n).toLocaleString("en-IN", {
    minimumFractionDigits: 2, maximumFractionDigits: 2
});

async function api(url, options = {}) {
    const response = await fetch(url, {
        headers: {"Content-Type": "application/json"},
        ...options
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Request failed");
    return data;
}

async function loadExpenses() {
    try {
        expenses = await api("/api/expenses");
        render();
    } catch (error) {
        alert("Could not load expenses: " + error.message);
    }
}

function openNew() {
    editingId = null;
    $("expenseForm").reset();
    $("expenseDate").value = new Date().toLocaleDateString("en-CA");
    $("status").value = "Paid";
    $("dialogTitle").textContent = "Add Expense";
    $("expenseDialog").showModal();
}

function closeDialog() {
    $("expenseDialog").close();
}

function editExpense(id) {
    const e = expenses.find(item => item.id === id);
    if (!e) return;

    editingId = id;
    $("title").value = e.title;
    $("amount").value = e.amount;
    $("category").value = e.category;
    $("expenseDate").value = e.expense_date;
    $("status").value = e.status;
    $("note").value = e.note || "";
    $("dialogTitle").textContent = "Edit Expense";
    $("expenseDialog").showModal();
}

$("expenseForm").addEventListener("submit", async event => {
    event.preventDefault();

    const payload = {
        title: $("title").value.trim(),
        amount: Number($("amount").value),
        category: $("category").value,
        expense_date: $("expenseDate").value,
        status: $("status").value,
        note: $("note").value.trim()
    };

    try {
        if (editingId !== null) {
            await api("/api/expenses/" + editingId, {
                method: "PUT", body: JSON.stringify(payload)
            });
        } else {
            await api("/api/expenses", {
                method: "POST", body: JSON.stringify(payload)
            });
        }
        closeDialog();
        await loadExpenses();
    } catch (error) {
        alert(error.message);
    }
});

async function deleteExpense(id) {
    if (!confirm("Delete this expense permanently?")) return;

    try {
        await api("/api/expenses/" + id, {method: "DELETE"});
        await loadExpenses();
    } catch (error) {
        alert(error.message);
    }
}

async function moveExpense(id, status) {
    try {
        await api("/api/expenses/" + id, {
            method: "PUT", body: JSON.stringify({status})
        });
        await loadExpenses();
    } catch (error) {
        alert(error.message);
    }
}

function el(tag, text, className) {
    const node = document.createElement(tag);
    node.textContent = text;
    if (className) node.className = className;
    return node;
}

function createExpenseCard(e) {
    const card = el("article", "", "expense-card");
    const title = el("h4", e.title);
    const amount = el("div", money(e.amount), "amount");
    const meta = el("div",
        e.category + " · " + e.expense_date, "meta");
    const note = e.note ? el("div", e.note, "meta") : null;
    const actions = el("div", "", "card-actions");

    const edit = el("button", "Edit", "secondary");
    edit.onclick = () => editExpense(e.id);

    const del = el("button", "Delete", "danger");
    del.onclick = () => deleteExpense(e.id);

    const move = document.createElement("select");
    ["Planned", "Paid", "Reimbursed"].forEach(s => {
        const option = el("option", s);
        option.value = s;
        option.selected = s === e.status;
        move.appendChild(option);
    });
    move.setAttribute("aria-label", "Change expense status");
    move.onchange = () => moveExpense(e.id, move.value);

    actions.append(edit, del);
    card.append(title, amount, meta);
    if (note) card.append(note);
    actions.appendChild(move);
    card.appendChild(actions);
    return card;
}

function render() {
    const query = $("search").value.toLowerCase().trim();
    const category = $("categoryFilter").value;
    const status = $("statusFilter").value;

    const filtered = expenses.filter(e =>
        (e.title + " " + e.category + " " + (e.note || ""))
            .toLowerCase().includes(query) &&
        (category === "All" || e.category === category) &&
        (status === "All" || e.status === status)
    );

    const lanes = ["Planned", "Paid", "Reimbursed"];
    lanes.forEach(s => {
        $("lane-" + s).replaceChildren();
        $("count-" + s).textContent =
            filtered.filter(e => e.status === s).length;
    });

    filtered.forEach(e => {
        $("lane-" + e.status).appendChild(createExpenseCard(e));
    });

    lanes.forEach(s => {
        if (!$("lane-" + s).children.length) {
            $("lane-" + s).appendChild(el("div", "No expenses here", "empty"));
        }
    });

    $("total").textContent = money(
        expenses.reduce((sum, e) => sum + Number(e.amount), 0)
    );

    const today = new Date();
    const month = today.getMonth();
    const year = today.getFullYear();

    const monthlyTotal = expenses
        .filter(e => {
            const d = new Date(e.expense_date + "T12:00:00");
            return e.status === "Paid" &&
                   d.getMonth() === month &&
                   d.getFullYear() === year;
        })
        .reduce((sum, e) => sum + Number(e.amount), 0);

    $("monthly").textContent = money(monthlyTotal);
    $("transactions").textContent = expenses.length;
    $("listCount").textContent = filtered.length + " expenses";

    const tbody = $("expenseRows");
    tbody.replaceChildren();

    filtered.forEach(e => {
        const tr = document.createElement("tr");
        const values = [
            e.title, e.category, e.expense_date,
            money(e.amount), e.status
        ];

        values.forEach((value, i) => {
            const td = document.createElement("td");
            if (i === 4) td.appendChild(el("span", value, "badge"));
            else td.textContent = value;
            tr.appendChild(td);
        });

        const actionCell = document.createElement("td");
        const edit = el("button", "Edit", "secondary");
        edit.onclick = () => editExpense(e.id);
        const del = el("button", "Delete", "danger");
        del.onclick = () => deleteExpense(e.id);

        actionCell.append(edit, document.createTextNode(" "), del);
        tr.appendChild(actionCell);
        tbody.appendChild(tr);
    });

    $("emptyList").hidden = filtered.length > 0;
}

loadExpenses();
</script>
</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HTML)


# ---------------- BACKEND API ----------------

@app.route("/api/expenses", methods=["GET"])
def get_expenses():
    with connect_db() as conn:
        rows = conn.execute(
            "SELECT * FROM expenses ORDER BY expense_date DESC, id DESC"
        ).fetchall()
        return jsonify([dict(row) for row in rows])


def validate_expense(data, partial=False):
    result = {}

    if "title" in data or not partial:
        title = str(data.get("title", "")).strip()
        if not title or len(title) > 120:
            return None, "Enter a title (maximum 120 characters)"
        result["title"] = title

    if "amount" in data or not partial:
        try:
            amount = float(data.get("amount"))
            if not (0 < amount <= 1_000_000_000):
                raise ValueError
        except (ValueError, TypeError):
            return None, "Amount must be greater than zero"
        result["amount"] = amount

    if "category" in data or not partial:
        category = data.get("category", "Other")
        if category not in CATEGORIES:
            return None, "Invalid category"
        result["category"] = category

    if "expense_date" in data or not partial:
        try:
            d = date.fromisoformat(str(data.get("expense_date", "")))
            result["expense_date"] = d.isoformat()
        except ValueError:
            return None, "Enter a valid date"

    if "status" in data or not partial:
        status = data.get("status", "Paid")
        if status not in STATUSES:
            return None, "Invalid expense status"
        result["status"] = status

    if "note" in data or not partial:
        note = str(data.get("note", ""))
        if len(note) > 1000:
            return None, "Notes must be under 1000 characters"
        result["note"] = note

    return result, None


@app.route("/api/expenses", methods=["POST"])
def add_expense():
    data = request.get_json(silent=True) or {}
    values, error = validate_expense(data)

    if error:
        return jsonify({"error": error}), 400

    values["created_at"] = datetime.now().isoformat(timespec="seconds")

    with connect_db() as conn:
        cursor = conn.execute("""
            INSERT INTO expenses
            (title, amount, category, expense_date, status, note, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            values["title"], values["amount"], values["category"],
            values["expense_date"], values["status"], values["note"],
            values["created_at"]
        ))

        new_id = cursor.lastrowid

    return jsonify({"message": "Expense added", "id": new_id}), 201


@app.route("/api/expenses/<int:expense_id>", methods=["PUT"])
def update_expense(expense_id):
    data = request.get_json(silent=True) or {}
    allowed = {"title", "amount", "category", "expense_date", "status", "note"}
    data = {key: value for key, value in data.items() if key in allowed}

    if not data:
        return jsonify({"error": "No valid fields provided"}), 400

    values, error = validate_expense(data, partial=True)

    if error:
        return jsonify({"error": error}), 400

    if not values:
        return jsonify({"error": "No valid fields provided"}), 400

    assignments = ", ".join(f"{key} = ?" for key in values)
    parameters = list(values.values()) + [expense_id]

    with connect_db() as conn:
        cursor = conn.execute(
            f"UPDATE expenses SET {assignments} WHERE id = ?",
            parameters
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "Expense not found"}), 404

    return jsonify({"message": "Expense updated"})


@app.route("/api/expenses/<int:expense_id>", methods=["DELETE"])
def delete_expense(expense_id):
    with connect_db() as conn:
        cursor = conn.execute(
            "DELETE FROM expenses WHERE id = ?", (expense_id,)
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "Expense not found"}), 404

    return jsonify({"message": "Expense deleted"})


# ---------------- START APPLICATION ----------------

if __name__ == "__main__":
    app.run(debug=True, port=5000)
