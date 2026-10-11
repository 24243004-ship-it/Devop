from flask import Flask, request, jsonify, render_template_string
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_NAME = "sticky_notes.db"

# ---------------- DATABASE ----------------

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL DEFAULT '',
                color TEXT NOT NULL DEFAULT '#fff2a8',
                status TEXT NOT NULL DEFAULT 'To Do',
                pinned INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL
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
<title>Sticky Notes Workspace</title>

<style>
* { box-sizing: border-box; }
body {
    margin: 0;
    font-family: Arial, sans-serif;
    background: #f5f7fb;
    color: #202943;
}
header {
    background: #ffffff;
    padding: 20px 5%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #e5e8f0;
    gap: 15px;
    flex-wrap: wrap;
}
header h1 { margin: 0; font-size: 25px; }
header p { margin: 6px 0 0; color: #777f91; }
.container { max-width: 1400px; margin: auto; padding: 25px 4%; }
.toolbar {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 22px;
}
input, textarea, select {
    font: inherit;
    border: 1px solid #dce1eb;
    border-radius: 9px;
    padding: 11px;
    background: white;
}
#search { flex: 1; min-width: 180px; }
button {
    border: 0;
    border-radius: 9px;
    padding: 11px 16px;
    cursor: pointer;
    font-weight: bold;
}
.primary { background: #5b5bd6; color: white; }
.secondary { background: #e9eaf8; color: #4444a9; }
.delete { background: #ffe5e5; color: #bb3333; }
.stats {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
    margin-bottom: 25px;
}
.stat {
    background: white;
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #eceef5;
}
.stat span { color: #777f91; font-size: 13px; }
.stat h2 { margin: 10px 0 0; font-size: 28px; }
.pipeline {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 18px;
}
.lane {
    background: #edf0f7;
    border-radius: 14px;
    padding: 14px;
    min-height: 300px;
}
.lane-heading {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}
.lane-heading h3 { margin: 5px 0; font-size: 16px; }
.count {
    background: white;
    border-radius: 20px;
    padding: 5px 9px;
    font-size: 12px;
}
.notes { display: grid; gap: 13px; }
.note {
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0 3px 8px #25304b12;
    overflow-wrap: anywhere;
    border-top: 4px solid #00000010;
}
.note h4 { margin: 0 0 9px; font-size: 16px; }
.note p {
    margin: 0 0 14px;
    white-space: pre-wrap;
    line-height: 1.5;
    font-size: 14px;
}
.note small { color: #53566b; }
.note-actions {
    display: flex;
    gap: 7px;
    flex-wrap: wrap;
    margin-top: 12px;
}
.note-actions button { padding: 7px 9px; font-size: 12px; }
.empty { color: #858da0; font-size: 13px; text-align: center; padding: 25px 5px; }
dialog {
    width: min(500px, 94%);
    border: 0;
    border-radius: 16px;
    padding: 25px;
    box-shadow: 0 10px 60px #0003;
}
dialog::backdrop { background: #17203b88; }
dialog h2 { margin-top: 0; }
.form-grid { display: grid; gap: 13px; }
.form-grid input, .form-grid textarea, .form-grid select { width: 100%; }
.form-grid textarea { min-height: 130px; resize: vertical; }
.form-actions { display: flex; justify-content: flex-end; gap: 10px; }
.colors { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
.colors label { display: flex; align-items: center; gap: 5px; font-size: 13px; }
.colors input { padding: 0; width: 18px; }
@media (max-width: 800px) {
    .pipeline { grid-template-columns: 1fr; }
    .stats { grid-template-columns: 1fr; }
}
</style>
</head>

<body>
<header>
    <div>
        <h1>📝 Sticky Notes</h1>
        <p>Your personal notes and task pipeline</p>
    </div>
    <button class="primary" onclick="openNewNote()">+ New Note</button>
</header>

<main class="container">
    <div class="toolbar">
        <input id="search" placeholder="🔍 Search notes..." oninput="renderNotes()">
        <select id="statusFilter" onchange="renderNotes()">
            <option value="All">All Statuses</option>
            <option>To Do</option>
            <option>In Progress</option>
            <option>Completed</option>
        </select>
        <button class="secondary" onclick="loadNotes()">↻ Refresh</button>
    </div>

    <section class="stats">
        <div class="stat"><span>TOTAL NOTES</span><h2 id="total">0</h2></div>
        <div class="stat"><span>IN PROGRESS</span><h2 id="progress">0</h2></div>
        <div class="stat"><span>COMPLETED</span><h2 id="completed">0</h2></div>
    </section>

    <section class="pipeline">
        <div class="lane">
            <div class="lane-heading"><h3>📌 To Do</h3><span class="count" id="count-todo">0</span></div>
            <div class="notes" id="lane-todo"></div>
        </div>
        <div class="lane">
            <div class="lane-heading"><h3>⚡ In Progress</h3><span class="count" id="count-progress">0</span></div>
            <div class="notes" id="lane-progress"></div>
        </div>
        <div class="lane">
            <div class="lane-heading"><h3>✅ Completed</h3><span class="count" id="count-completed">0</span></div>
            <div class="notes" id="lane-completed"></div>
        </div>
    </section>
</main>

<dialog id="noteDialog">
    <h2 id="dialogTitle">Create a Note</h2>
    <form id="noteForm" class="form-grid">
        <input id="title" placeholder="Note title" maxlength="120" required>
        <textarea id="content" placeholder="Write your note here..."></textarea>

        <label>Pipeline status</label>
        <select id="status">
            <option>To Do</option>
            <option>In Progress</option>
            <option>Completed</option>
        </select>

        <label>Sticky note color</label>
        <div class="colors">
            <label><input type="radio" name="color" value="#fff2a8" checked> Yellow</label>
            <label><input type="radio" name="color" value="#c9f3d2"> Green</label>
            <label><input type="radio" name="color" value="#d6e8ff"> Blue</label>
            <label><input type="radio" name="color" value="#ffd9e8"> Pink</label>
            <label><input type="radio" name="color" value="#eadcff"> Purple</label>
        </div>

        <div class="form-actions">
            <button type="button" class="secondary" onclick="closeDialog()">Cancel</button>
            <button type="submit" class="primary">Save Note</button>
        </div>
    </form>
</dialog>

<script>
let notes = [];
let editingId = null;

const $ = id => document.getElementById(id);

async function api(url, options = {}) {
    const response = await fetch(url, {
        headers: {"Content-Type": "application/json"},
        ...options
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error || "Something went wrong");
    }

    return data;
}

async function loadNotes() {
    try {
        notes = await api("/api/notes");
        renderNotes();
    } catch (error) {
        alert("Unable to load notes: " + error.message);
    }
}

function openNewNote() {
    editingId = null;
    $("noteForm").reset();
    $("dialogTitle").textContent = "Create a Note";
    $("noteDialog").showModal();
}

function closeDialog() {
    $("noteDialog").close();
}

function editNote(id) {
    const note = notes.find(n => n.id === id);
    if (!note) return;

    editingId = id;
    $("title").value = note.title;
    $("content").value = note.content;
    $("status").value = note.status;

    document.querySelectorAll('input[name="color"]').forEach(input => {
        input.checked = input.value === note.color;
    });

    $("dialogTitle").textContent = "Edit Note";
    $("noteDialog").showModal();
}

$("noteForm").addEventListener("submit", async event => {
    event.preventDefault();

    const selectedColor = document.querySelector('input[name="color"]:checked');

    const payload = {
        title: $("title").value.trim(),
        content: $("content").value.trim(),
        status: $("status").value,
        color: selectedColor ? selectedColor.value : "#fff2a8"
    };

    try {
        if (editingId !== null) {
            await api("/api/notes/" + editingId, {
                method: "PUT",
                body: JSON.stringify(payload)
            });
        } else {
            await api("/api/notes", {
                method: "POST",
                body: JSON.stringify(payload)
            });
        }

        closeDialog();
        await loadNotes();
    } catch (error) {
        alert(error.message);
    }
});

async function deleteNote(id) {
    if (!confirm("Delete this note permanently?")) return;

    try {
        await api("/api/notes/" + id, {method: "DELETE"});
        await loadNotes();
    } catch (error) {
        alert(error.message);
    }
}

async function togglePin(id, pinned) {
    try {
        await api("/api/notes/" + id, {
            method: "PUT",
            body: JSON.stringify({pinned: pinned ? 0 : 1})
        });
        await loadNotes();
    } catch (error) {
        alert(error.message);
    }
}

async function moveNote(id, status) {
    try {
        await api("/api/notes/" + id, {
            method: "PUT",
            body: JSON.stringify({status})
        });
        await loadNotes();
    } catch (error) {
        alert(error.message);
    }
}

function makeButton(label, css, action) {
    const button = document.createElement("button");
    button.className = css;
    button.textContent = label;
    button.addEventListener("click", action);
    return button;
}

function createNoteCard(note) {
    const card = document.createElement("article");
    card.className = "note";
    card.style.background = note.color;

    const title = document.createElement("h4");
    title.textContent = (note.pinned ? "📌 " : "") + note.title;

    const content = document.createElement("p");
    content.textContent = note.content || "No additional details.";

    const date = document.createElement("small");
    date.textContent = "Updated: " + note.updated_at;

    const actions = document.createElement("div");
    actions.className = "note-actions";

    actions.append(
        makeButton("✏️ Edit", "secondary", () => editNote(note.id)),
        makeButton(note.pinned ? "Unpin" : "📌 Pin", "secondary",
            () => togglePin(note.id, note.pinned)),
        makeButton("🗑 Delete", "delete", () => deleteNote(note.id))
    );

    const move = document.createElement("select");
    ["To Do", "In Progress", "Completed"].forEach(status => {
        const option = document.createElement("option");
        option.value = status;
        option.textContent = "Move: " + status;
        option.selected = status === note.status;
        move.appendChild(option);
    });
    move.addEventListener("change", () => moveNote(note.id, move.value));
    actions.appendChild(move);

    card.append(title, content, date, actions);
    return card;
}

function renderNotes() {
    const query = $("search").value.toLowerCase().trim();
    const statusFilter = $("statusFilter").value;

    const filtered = notes.filter(note => {
        const matchesText =
            (note.title + " " + note.content).toLowerCase().includes(query);
        const matchesStatus =
            statusFilter === "All" || note.status === statusFilter;
        return matchesText && matchesStatus;
    }).sort((a, b) => b.pinned - a.pinned);

    const lanes = {
        "To Do": $("lane-todo"),
        "In Progress": $("lane-progress"),
        "Completed": $("lane-completed")
    };

    Object.values(lanes).forEach(lane => lane.replaceChildren());

    const counts = {"To Do": 0, "In Progress": 0, "Completed": 0};

    filtered.forEach(note => {
        const lane = lanes[note.status];
        if (!lane) return;
        lane.appendChild(createNoteCard(note));
        counts[note.status]++;
    });

    Object.entries(lanes).forEach(([status, lane]) => {
        if (counts[status] === 0) {
            const empty = document.createElement("div");
            empty.className = "empty";
            empty.textContent = "No notes here yet";
            lane.appendChild(empty);
        }
    });

    $("total").textContent = notes.length;
    $("progress").textContent = notes.filter(n => n.status === "In Progress").length;
    $("completed").textContent = notes.filter(n => n.status === "Completed").length;

    $("count-todo").textContent = counts["To Do"];
    $("count-progress").textContent = counts["In Progress"];
    $("count-completed").textContent = counts["Completed"];
}

loadNotes();
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

# ---------------- BACKEND API ----------------

@app.route("/api/notes", methods=["GET"])
def get_notes():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM notes ORDER BY pinned DESC, id DESC"
        ).fetchall()
        return jsonify([dict(row) for row in rows])

@app.route("/api/notes", methods=["POST"])
def add_note():
    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()

    if not title:
        return jsonify({"error": "Title is required"}), 400

    content = str(data.get("content", ""))
    color = str(data.get("color", "#fff2a8"))
    status = str(data.get("status", "To Do"))

    if status not in ("To Do", "In Progress", "Completed"):
        return jsonify({"error": "Invalid status"}), 400

    if color not in ("#fff2a8", "#c9f3d2", "#d6e8ff",
                     "#ffd9e8", "#eadcff"):
        color = "#fff2a8"

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    with get_db() as conn:
        cursor = conn.execute("""
            INSERT INTO notes (title, content, color, status, pinned, updated_at)
            VALUES (?, ?, ?, ?, 0, ?)
        """, (title, content, color, status, now))

        note_id = cursor.lastrowid

    return jsonify({"message": "Note created", "id": note_id}), 201

@app.route("/api/notes/<int:note_id>", methods=["PUT"])
def update_note(note_id):
    data = request.get_json(silent=True) or {}

    allowed = {"title", "content", "color", "status", "pinned"}
    updates = {key: value for key, value in data.items() if key in allowed}

    if not updates:
        return jsonify({"error": "No valid fields provided"}), 400

    if "title" in updates:
        updates["title"] = str(updates["title"]).strip()
        if not updates["title"]:
            return jsonify({"error": "Title cannot be empty"}), 400

    if "status" in updates and updates["status"] not in (
        "To Do", "In Progress", "Completed"
    ):
        return jsonify({"error": "Invalid status"}), 400

    if "color" in updates and updates["color"] not in (
        "#fff2a8", "#c9f3d2", "#d6e8ff", "#ffd9e8", "#eadcff"
    ):
        return jsonify({"error": "Invalid color"}), 400

    if "pinned" in updates:
        try:
            updates["pinned"] = int(updates["pinned"])
            if updates["pinned"] not in (0, 1):
                raise ValueError
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid pin value"}), 400

    updates["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    fields = ", ".join(f"{key} = ?" for key in updates)
    values = list(updates.values()) + [note_id]

    with get_db() as conn:
        cursor = conn.execute(
            f"UPDATE notes SET {fields} WHERE id = ?", values
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "Note not found"}), 404

    return jsonify({"message": "Note updated"})

@app.route("/api/notes/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    with get_db() as conn:
        cursor = conn.execute(
            "DELETE FROM notes WHERE id = ?", (note_id,)
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "Note not found"}), 404

    return jsonify({"message": "Note deleted"})

# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":
    app.run(debug=True, port=5000)
