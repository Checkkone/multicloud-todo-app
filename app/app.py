from flask import Flask, request, jsonify, render_template, redirect, url_for
import os
import socket
from datetime import datetime

app = Flask(__name__)

todos = []
counter = 0

PRIORITIES = ["haute", "moyenne", "basse"]
CATEGORIES = ["Travail", "Personnel", "Étude", "Réunion", "Urgent", "Autre"]

def get_info():
    return {
        "cloud":    os.getenv("CLOUD_NAME", "local"),
        "hostname": socket.gethostname(),
        "version":  os.getenv("APP_VERSION", "1.0.0")
    }

def compute_stats():
    total    = len(todos)
    done     = sum(1 for t in todos if t["done"])
    pending  = total - done
    progress = round((done / total) * 100) if total > 0 else 0
    overdue  = sum(
        1 for t in todos
        if not t["done"] and t.get("due_date") and
           datetime.strptime(t["due_date"], "%Y-%m-%d") < datetime.now()
    )
    return dict(total=total, done=done, pending=pending,
                progress=progress, overdue=overdue)

@app.route("/")
def index():
    search   = request.args.get("q", "").strip()
    filter_s = request.args.get("filter", "all")
    cat_f    = request.args.get("category", "all")
    prio_f   = request.args.get("priority", "all")

    filtered = todos[:]

    # Filtre statut
    if filter_s == "active":
        filtered = [t for t in filtered if not t["done"]]
    elif filter_s == "done":
        filtered = [t for t in filtered if t["done"]]

    # Filtre catégorie
    if cat_f != "all":
        filtered = [t for t in filtered if t.get("category") == cat_f]

    # Filtre priorité
    if prio_f != "all":
        filtered = [t for t in filtered if t.get("priority") == prio_f]

    # Recherche
    if search:
        filtered = [t for t in filtered if search.lower() in t["task"].lower()]

    # Marquer les tâches en retard
    now = datetime.now()
    for t in filtered:
        if t.get("due_date"):
            due = datetime.strptime(t["due_date"], "%Y-%m-%d")
            t["overdue"] = not t["done"] and due < now
            t["due_display"] = due.strftime("%d %b %Y")
        else:
            t["overdue"] = False
            t["due_display"] = None

    return render_template(
        "index.html",
        todos=filtered,
        search=search,
        filter_s=filter_s,
        cat_filter=cat_f,
        prio_filter=prio_f,
        categories=CATEGORIES,
        priorities=PRIORITIES,
        **get_info(),
        **compute_stats()
    )

@app.route("/add", methods=["POST"])
def add():
    global counter
    task     = request.form.get("task", "").strip()
    priority = request.form.get("priority", "moyenne")
    category = request.form.get("category", "Autre")
    due_date = request.form.get("due_date", "").strip()

    if task:
        counter += 1
        todos.append({
            "id":         counter,
            "task":       task,
            "done":       False,
            "priority":   priority if priority in PRIORITIES else "moyenne",
            "category":   category if category in CATEGORIES else "Autre",
            "due_date":   due_date if due_date else None,
            "created_at": datetime.now().strftime("%d %b %Y, %H:%M")
        })
    return redirect(url_for("index"))

@app.route("/toggle/<int:todo_id>", methods=["POST"])
def toggle(todo_id):
    for t in todos:
        if t["id"] == todo_id:
            t["done"] = not t["done"]
            break
    return redirect(url_for("index"))

@app.route("/delete/<int:todo_id>", methods=["POST"])
def delete(todo_id):
    global todos
    todos = [t for t in todos if t["id"] != todo_id]
    return redirect(url_for("index"))

@app.route("/health")
def health():
    return jsonify({"status": "ok", **get_info(), **compute_stats()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)