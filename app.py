from flask import Flask, render_template, request, redirect
import json
import os
from pypdf import PdfReader

app = Flask(__name__)


def load_users():
    with open("users.json", "r") as f:
        return json.load(f)


def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        for user in load_users():
            if user["email"] == email and user["password"] == password:
                return redirect("/dashboard")

        return "Invalid email or password"

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        users = load_users()

        users.append({
            "name": request.form["name"],
            "email": request.form["email"],
            "password": request.form["password"]
        })

        save_users(users)
        return redirect("/")

    return render_template("signup.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/assistant", methods=["GET", "POST"])
def assistant():
    answer = ""

    if request.method == "POST":
        question = request.form["question"].lower()

        if "python" in question:
            answer = "Python is a simple and popular programming language."
        elif "java" in question:
            answer = "Java is an object-oriented programming language."
        elif "ai" in question or "artificial intelligence" in question:
            answer = "Artificial Intelligence helps computers perform tasks that normally require human intelligence."
        elif "machine learning" in question:
            answer = "Machine Learning allows computers to learn patterns from data."
        elif "dbms" in question:
            answer = "DBMS is software used to store, manage and organize data."
        elif "hello" in question or "hi" in question:
            answer = "Hello! 👋 How can I help you with your studies?"
        else:
            answer = "Sorry, I don't know this yet. Try asking about Python, Java, AI, Machine Learning or DBMS."

    return render_template("assistant.html", answer=answer)


@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    questions = []
    score = None

    if request.method == "POST":

        if "submit_quiz" in request.form:
            total = int(request.form["total"])
            score = 0

            for i in range(total):
                if request.form.get(f"answer_{i}") == request.form.get(f"correct_{i}"):
                    score += 1

        else:
            file = request.files["notes"]

            if file and file.filename.endswith(".pdf"):
                os.makedirs("uploads", exist_ok=True)

                file_path = os.path.join("uploads", file.filename)
                file.save(file_path)

                reader = PdfReader(file_path)
                text = ""

                for page in reader.pages:
                    text += page.extract_text() or ""

                sentences = [
                    s.strip()
                    for s in text.replace("\n", " ").split(".")
                    if len(s.strip()) > 20
                ]

                sentences = [s[:100] for s in sentences if len(s) > 20]

                for i, sentence in enumerate(sentences[:5]):
                    options = sentences[:4]

                    if sentence not in options:
                        options[-1] = sentence

                    questions.append({
                        "question": "Which statement is related to the uploaded notes?",
                        "options": options,
                        "answer": sentence
                    })

    return render_template(
        "quiz.html",
        questions=questions,
        score=score
    )

@app.route("/planner", methods=["GET", "POST"])
def planner():

    # Load existing tasks
    try:
        with open("tasks.json", "r") as f:
            tasks = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        tasks = []

    # Add a new task
    if request.method == "POST":

        action = request.form.get("action")

        # Mark task as complete / incomplete
        if action == "toggle":
            task_id = int(request.form["task_id"])

            if 0 <= task_id < len(tasks):
                tasks[task_id]["completed"] = not tasks[task_id].get(
                    "completed", False
                )

        # Add new task
        else:
            tasks.append({
                "subject": request.form["subject"],
                "task": request.form["task"],
                "due_date": request.form["due_date"],
                "completed": False
            })

        # Save tasks
        with open("tasks.json", "w") as f:
            json.dump(tasks, f, indent=4)

        return redirect("/planner")

    # Make old tasks compatible
    for task in tasks:
        if "completed" not in task:
            task["completed"] = False

    # Calculate progress
    total_tasks = len(tasks)
    completed_tasks = sum(
        1 for task in tasks if task.get("completed", False)
    )

    if total_tasks > 0:
        progress = round((completed_tasks / total_tasks) * 100)
    else:
        progress = 0

    pending_tasks = total_tasks - completed_tasks

    return render_template(
        "planner.html",
        tasks=tasks,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        progress=progress
    )
if __name__ == "__main__":
    app.run(debug=True)