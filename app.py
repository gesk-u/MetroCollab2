from flask import Flask, render_template, request, flash, session, jsonify, redirect, g, url_for
from werkzeug.security import check_password_hash, generate_password_hash
#from dotenv import load_dotenv
import os
import mysql.connector
import secrets
import string
import ai_micro
import json
import jinja2

# Create the Flask app instance
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

DATABASE = 'Collab_DB'

app.config["SESSION_PERMANENT"] = False
# #app.config["SESSION_TYPE"] = "filesystem"
# Session(app)

def get_db():
    if 'db' not in g:
        conn = mysql.connector.connect(
            user="root",
            password=os.environ.get("PASSWORD"),
            host="127.0.0.1",
            port=3306,
            database=DATABASE,
            autocommit=True
        )

        g.conn = conn
        g.db = conn.cursor(dictionary=True)
    return g.db

def generate_secure_code():
    characters = string.ascii_uppercase + string.digits
    db = get_db()
    while True:
        code = ''.join(secrets.choice(characters) for _ in range(4))
        row = db.execute("SELECT 1 FROM teacher_group WHERE group_code = %s", (code,))
        row = db.fetchone()
        if not row:
            return code

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    conn = g.pop('conn', None)
    if db is not None:
        db.close()
    if conn is not None:
        conn.close()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        #Initial signup
        if session.get('user_id') is None or request.form.get("username"):

            name = request.form.get("username")
            print(name)
            lastname = request.form.get("lastname")
            print(lastname)
            user_type = request.form.get("selectedRole")
            print(user_type)

            if not name or not lastname:
                flash("Name and lastname are required.")
                return  render_template("index.html")

            if not user_type:
                flash("You must chose your type of user")
                return  render_template("index.html")

            user_type_int = 0 if user_type == "student" else 1

            db = get_db()
            db.execute(
                "INSERT INTO users (user_firstname, user_lastname, user_type) VALUES (%s, %s, %s)",
                (name, lastname, user_type_int)
            )

            user_id = db.lastrowid
    

            # Store in session
            session['user_id'] = user_id
            session['username'] = name
            session['user_type'] = user_type_int

            flash("User registered successfully!")
        
        #Group code or student code
        else:

            if session['user_type'] == 1:
                print("line 105")
                total_students = request.form.get("total_number")
                total_group = request.form.get("group_number")

                if not total_students or not total_group:
                    flash("total_students and total_group are required.")
                    return  render_template("index.html")

                code = generate_secure_code()
                session['code'] = code
                db = get_db()
                db.execute(
                    "INSERT INTO teacher_group (teacher_id, total_students, total_group, group_code) VALUES (%s, %s, %s, %s)",
                    (session['user_id'], total_students, total_group, code)
                )

                flash(f"Group registered successfully! Your group code is: {code}")
                return redirect(url_for('teacher_page', user_id=session['user_id'], user_type=session['user_type'], group_code=session['code']))

            else:
                student_code = request.form.get("st_code")
                print(f"Student code received: {student_code}")

                if not student_code:
                    flash("Code is required.")
                    return  render_template("index.html")

                db = get_db()
                row = db.execute(
                    "SELECT id from teacher_group WHERE group_code = %s", (student_code,)
                )
                row = db.fetchone()
                print(f"Group found: {row}")

                if not row:
                    flash("Code is not valid.")
                    return  render_template("index.html")
                    
                db.execute(
                    "INSERT INTO student_group (student_id, group_code) VALUES (%s, %s)", (session['user_id'], student_code)
                )

                session['student_code'] = student_code
            
                return redirect(url_for('student_form', user_id=session['user_id']))

    return render_template("index.html")


@app.route("/student_form/<int:user_id>", methods=["GET", "POST"])
def student_form(user_id):

    if request.method == "POST":

        email = request.form.get("email")

        form_skills = request.form.get("skill")

        form_interests = request.form.get("interests")

        availability = {
            "mon": request.form.getlist("availability_mon"),
            "tue": request.form.getlist("availability_tue"),
            "wed": request.form.getlist("availability_wed"),
            "thu": request.form.getlist("availability_thu"),
            "fri": request.form.getlist("availability_fri"),
            "weekend": request.form.getlist("availability_weekend")
        }

        hours_per_week = request.form.get('hours_per_week')

        db = get_db()

        db.execute("""
        INSERT INTO skills (name) VALUES (%s)
        """, (form_skills,))
        skill_id = db.lastrowid
        db.execute("""
        INSERT INTO student_skills (user_id, skill_id) VALUES (%s, %s)
        """, (user_id, skill_id))
        db.execute("""
        INSERT INTO interests (name) VALUES (%s)
        """, (form_interests,))
        interests_id = db.lastrowid
        db.execute("""
        INSERT INTO student_interests (user_id, interest_id) VALUES (%s, %s)
        """, (user_id, interests_id))

        inter_skills_json = ai_micro.get_ai_json(form_skills, form_interests)
        interests_json = json.dumps(inter_skills_json["interests"])
        skills_json = json.dumps(inter_skills_json["skills"])
        availability_json = json.dumps(availability)
        hours_per_week_json = json.dumps(hours_per_week)

        db.execute("""
            INSERT INTO student_form (student_id, email, skills, interests, availability, hours_per_week)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, email, skills_json, interests_json, availability_json, hours_per_week_json))              #TODO if availability empty - delete it from the row

        print("Form submitted successfully")
        return jsonify({"success": True, "message": "Form submitted successfully"})

    return render_template("student_form.html", user=session['user_id'])


@app.route("/api/check_submission/<int:user_id>")
def check_submission(user_id):
    db = get_db()
    cursor = db.execute("""
        SELECT COUNT(*) FROM student_form WHERE student_id = %s
    """, (user_id,))
    
    count = cursor.fetchone()[0]
    has_submitted = count > 0
    
    return jsonify({"has_submitted": has_submitted})



@app.route("/teacher/<int:user_id>", methods=["GET", "POST"])
def teacher_page(user_id):
    db = get_db()
    db.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = db.fetchone()
    db = get_db()
    db.execute("SELECT * FROM teacher_group WHERE teacher_id = %s", (user_id,))
    group = db.fetchone()

    group_code = request.args.get('group_code')

    if request.method == "POST":
        pass
    
    return render_template("teacher.html", user=user, group=group, group_code=group_code)




if __name__ == "__main__":
    print("Starting Flask app...")
    app.run(debug=True)