from flask import Flask, request, jsonify, render_template
import os
import socket

app = Flask(__name__)

todos = []
counter = 0

@app.route("/")
def index():
    cloud = os.getenv("CLOUD_NAME", "local")
    return render_template("index.html", todos=todos, cloud=cloud)

@app.route("/add", methods=["POST"])
def add():
    global counter
    task = request.form.get("task", "").strip()
    if task:
        counter += 1
        todos.append({"id": counter, "task": task, "done": False})
    return index()

@app.route("/toggle/<int:todo_id>", methods=["POST"])
def toggle(todo_id):
    for todo in todos:
        if todo["id"] == todo_id:
            todo["done"] = not todo["done"]
    return index()

@app.route("/delete/<int:todo_id>", methods=["POST"])
def delete(todo_id):
    global todos
    todos = [t for t in todos if t["id"] != todo_id]
    return index()

@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "cloud": os.getenv("CLOUD_NAME", "local"),
        "hostname": socket.gethostname()
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)