from flask import Flask, render_template, request, redirect, url_for, flash
import csv
import os

app = Flask(__name__)
app.secret_key = "placement_tracker_secret"

DATA_FILE = "placement_data.csv"

FIELDS = ["Name", "Department", "Company", "Package", "Status"]


def load_students():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()

    with open(DATA_FILE, "r", newline="") as f:
        return list(csv.DictReader(f))


def save_student(student):
    with open(DATA_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writerow(student)


@app.route("/")
def home():

    students = load_students()

    total = len(students)

    placed = sum(
        1 for s in students
        if s["Status"].strip().lower() == "placed"
    )

    not_placed = total - placed

    percentage = (
        round((placed / total) * 100, 2)
        if total > 0 else 0
    )

    search = request.args.get("search", "").strip()

    if search:
        students = [
            s for s in students
            if search.lower() in s["Name"].lower()
        ]

    return render_template(
        "index.html",
        students=students,
        total=total,
        placed=placed,
        not_placed=not_placed,
        percentage=percentage,
        search=search
    )


@app.route("/add", methods=["POST"])
def add_student():

    name = request.form["name"].strip()
    department = request.form["department"].strip()
    company = request.form["company"].strip()
    package = request.form["package"].strip()
    status = request.form["status"]

    if not name or not department:
        flash("Please enter student name and department.")
        return redirect(url_for("home"))

    if package:
        try:
            if float(package) < 0:
                raise ValueError
        except ValueError:
            flash("Enter a valid package.")
            return redirect(url_for("home"))

    student = {
        "Name": name,
        "Department": department,
        "Company": company if company else "-",
        "Package": package if package else "-",
        "Status": status
    }

    save_student(student)

    flash("Student added successfully!")

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)