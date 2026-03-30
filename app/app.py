from flask import Flask, request, jsonify, render_template, redirect, url_for
import os
import socket
from datetime import datetime

app = Flask(__name__)

todos = []
counter = 0

def get_info():
    return {
        "cloud": os.getenv("CLOUD_NAME", "local"),
        "hostname": socket.gethostname(),
        "version": os.getenv("APP_VERSION", "1.0.0")
    }

@app.route("/")
def index():
    info = get_info()
    total = len(todos)
    done_count = sum(1 for t in todos if t["done"])
    pending = total - done_count
    return render_template(
        "index.html",
        todos=todos,
        cloud=info["cloud"],
        hostname=info["hostname"],
        version=info["version"],
        total=total,
        done_count=done_count,
        pending=pending
    )

@app.route("/add", methods=["POST"])
def add():
    global counter
    task = request.form.get("task", "").strip()
    if task:
        counter += 1
        todos.append({
            "id": counter,
            "task": task,
            "done": False,
            "created_at": datetime.now().strftime("%d %b, %H:%M")
        })
    return redirect(url_for("index"))

@app.route("/toggle/<int:todo_id>", methods=["POST"])
def toggle(todo_id):
    for todo in todos:
        if todo["id"] == todo_id:
            todo["done"] = not todo["done"]
            break
    return redirect(url_for("index"))

@app.route("/delete/<int:todo_id>", methods=["POST"])
def delete(todo_id):
    global todos
    todos = [t for t in todos if t["id"] != todo_id]
    return redirect(url_for("index"))

@app.route("/health")
def health():
    info = get_info()
    return jsonify({
        "status": "ok",
        "cloud": info["cloud"],
        "hostname": info["hostname"],
        "version": info["version"],
        "todos": {
            "total": len(todos),
            "done": sum(1 for t in todos if t["done"]),
            "pending": sum(1 for t in todos if not t["done"])
        }
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)