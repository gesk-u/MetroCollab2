from flask import (
    Flask,
    render_template,
    request,
    flash,
    session,
    jsonify,
    redirect,
    g,
    url_for,
)

import os
import sys
import random
import json
import secrets
import string

import mysql.connector
from faker import Faker

# Local / custom modules
import ai_micro     # inserting data with AI
import sort_alg     # sorting/clustering algorithm


# Create the Flask app instance
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

DATABASE = 'Collab_DB'

app.config.update({
    "SESSION_PERMANENT": False,     # session ends when browser is closed
    "SESSION_TYPE": "filesystem",   # session data is stored on disk
    "PERMANENT_SESSION_LIFETIME": 3600  # 1 hour session lifetime
})


def get_db():
    """
    Get database connection and cursor.
    Uses Flask's g object to store connection per request context.
    Connection is reused within the same request.
    
    Returns:
        cursor: MySQL cursor with dictionary=True for dict-based results
    """
    if 'db' not in g:
        conn = mysql.connector.connect(
            user=os.environ.get("USER"),
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
    """
    Generate a unique 4-character group code.
    Uses uppercase letters and digits for the code.
    Checks database to ensure uniqueness.
    
    Returns:
        str: A unique 4-character code
    """
    characters = string.ascii_uppercase + string.digits
    db = get_db()
    # Keep generating until we find a unique code
    while True:
        # Generate random 4-character code
        code = ''.join(secrets.choice(characters) for _ in range(4))

        # Check if code already exists in database
        row = db.execute("SELECT 1 FROM teacher_group WHERE group_code = %s", (code,))
        row = db.fetchone()

        # If code doesn't exist, return it
        if not row:
            return code


def insert_test_data(total_students, min_students_per_group, max_students_per_group):
    """
    Insert test data into database for testing.
    Creates one teacher and multiple students with AI-generated form data.
    
    Args:
        total_students (int): Number of students to create
        min_students_per_group (int): Minimum students per group
        max_students_per_group (int): Maximum students per group
        
    Returns:
        tuple: (group_code, teacher_id) for the created test group
        
    Raises:
        Exception: If database insertion fails
    """

    # Initialize Faker for generating test data
    fake = Faker()

    # Available hours per week options
    hours_list = ["5-10", "10-15", "15-20", "20+"]
    db = get_db()

    try:
        # Create a fake teacher
        teacher_firstname = fake.first_name()
        teacher_lastname = fake.last_name()
        group_code = generate_secure_code()

        # Insert teacher into users table
        db.execute("INSERT INTO users (user_firstname, user_lastname, user_type) VALUES (%s, %s, %s)", (teacher_firstname, teacher_lastname, 1))
        teacher_id = db.lastrowid

        # Create teacher's group with specified parameters
        db.execute("INSERT INTO teacher_group (teacher_id, total_students, group_code, min_students_per_group, max_students_per_group) VALUES (%s, %s, %s, %s, %s)",
                            (teacher_id, total_students, group_code, min_students_per_group, max_students_per_group))
        
        # Create specified number of students
        for i in range(total_students):
            student_firstname = fake.first_name()
            student_lastname = fake.last_name()

            # Insert student into users table (user_type=0 for student)
            db.execute("INSERT INTO users (user_firstname, user_lastname, user_type) VALUES (%s, %s, %s)", (student_firstname, student_lastname, 0))
            student_id = db.lastrowid

            # Generate random data
            hours_per_week = random.choice(hours_list)
            hours_per_week_json = json.dumps(hours_per_week)

            # Generate availability using AI
            avb = ai_micro.time_ai()
            avb_json = json.dumps(avb)

            # Generate skills and interests using AI
            skills = ai_micro.skills_ai()
            interests = ai_micro.interests_ai()
            data = ai_micro.get_ai_json(skills, interests)
            
            # Extract and serialize skills and interests
            skills_d = data["skills"]
            interests_d = data["interests"]
            skills_j = json.dumps(skills_d)
            interests_j = json.dumps(interests_d)

            # Add student to the group
            db.execute("INSERT INTO student_group (student_id, group_code) VALUES (%s, %s)", (student_id, group_code))

            # Insert student's form data
            sql = "INSERT INTO student_form (student_id, skills, interests, availability, hours_per_week) VALUES (%s, %s, %s, %s, %s)"
            db.execute(sql, (student_id, skills_j, interests_j, avb_json, hours_per_week_json))
        
        return group_code, teacher_id
    
    except Exception as e:
        db.rollback()
        print(f"Error inserting test data: {e}")
        raise


@app.teardown_appcontext
def close_db(exception):
    """
    Close database connection after each request.
    This is called automatically by Flask at the end of each request.
    
    Args:
        exception: Any exception that occurred during request (can be None)
    """
    db = g.pop('db', None)
    conn = g.pop('conn', None)

    # Close cursor if it exists
    if db is not None:
        db.close()

    # Close connection if it exists
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
    """
    Main landing page route.
    Handles user registration and group code entry.
    
    GET: Display the main page
    POST: Process user registration or group code submission
    
    Flow:
    1. If user not logged in: Register new user (teacher or student)
    2. If teacher logged in: Create group with parameters
    3. If student logged in: Join group using code
    
    Returns:
        Rendered template or redirect
    """
    if request.method == "POST":

        # INITIAL SIGNUP - User is registering for the first time
        if session.get('user_id') is None or request.form.get("username"):

            # Get form data
            name = request.form.get("username")
            print(name)
            lastname = request.form.get("lastname")
            print(lastname)
            user_type = request.form.get("selectedRole")
            print(user_type)

            # Validate required fields
            if not name or not lastname:
                flash("Name and lastname are required.")
                return  render_template("index.html")

            if not user_type:
                flash("You must chose your type of user")
                return  render_template("index.html")

            # Convert user type to integer (0=student, 1=teacher)
            user_type_int = 0 if user_type == "student" else 1

            # Insert new user into database
            db = get_db()
            db.execute(
                "INSERT INTO users (user_firstname, user_lastname, user_type) VALUES (%s, %s, %s)",
                (name, lastname, user_type_int)
            )

            # Get the auto-generated user ID
            user_id = db.lastrowid
    

            # Store user information in session
            session['user_id'] = user_id
            session['username'] = name
            session['user_type'] = user_type_int

            flash("User registered successfully!")
        
        # GROUP CODE ENTRY: User already registered, now entering group info
        else:

            # TEACHER: Creating a new group
            if session['user_type'] == 1:
                
                # Get group parameters from form
                total_students = request.form.get("total_number")
                min_students_per_group = request.form.get("group_min")
                max_students_per_group = request.form.get("group_max")

                # Validate required fields
                if not total_students or not min_students_per_group or not max_students_per_group:
                    flash("total_students and groups are required.")
                    return  render_template("index.html")

                # Generate unique group code
                code = generate_secure_code()
                session['code'] = code

                # Create teacher's group in database
                db = get_db()
                db.execute(
                    "INSERT INTO teacher_group (teacher_id, total_students, group_code, min_students_per_group, max_students_per_group) VALUES (%s, %s, %s, %s, %s)",
                    (session['user_id'], total_students, code, min_students_per_group, max_students_per_group)
                )

                flash(f"Group registered successfully! Your group code is: {code}")
                return redirect(url_for('teacher_page', user_id=session['user_id'], group_code=session['code']))
            
            # STUDENT: Joining existing group with code
            else:
                student_code = request.form.get("st_code")
                print(f"Student code received: {student_code}")

                # Validate code is provided
                if not student_code:
                    flash("Code is required.")
                    return  render_template("index.html")

                # Check if group code exists
                db = get_db()
                row = db.execute(
                    "SELECT id from teacher_group WHERE group_code = %s", (student_code,)
                )
                row = db.fetchone()
                
                # Validate group code
                if not row:
                    flash("Code is not valid.")
                    return  render_template("index.html")
                # Add student to the group    
                db.execute(
                    "INSERT INTO student_group (student_id, group_code) VALUES (%s, %s)", (session['user_id'], student_code)
                )

                # Store code in session
                session['student_code'] = student_code

                # Redirect to student form
                return redirect(url_for('student_form', user_id=session['user_id']))

    # GET request - display main page
    return render_template("index.html")


@app.route("/student_form/<int:user_id>", methods=["GET", "POST"])
def student_form(user_id):
    """
    Student form page for collecting skills, interests, and availability.
    
    Args:
        user_id (int): The student's user ID
    
    GET: Display the form
    POST: Process form submission and save to database
    
    Form collects:
    - Email
    - Skills (free text)
    - Interests (free text)
    - Weekly availability (checkboxes for each day/time)
    - Hours per week
    
    Returns:
        GET: Rendered form template
        POST: JSON response indicating success
    """
    if request.method == "POST":

        # Get form data
        email = request.form.get("email")
        form_skills = request.form.get("skill")
        form_interests = request.form.get("interests")

        # Collect availability for each day (can select multiple time slots)
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

        # Insert skills into skills table
        db.execute("""
        INSERT INTO skills (name) VALUES (%s)
        """, (form_skills,))
        skill_id = db.lastrowid

        # Link skills to student
        db.execute("""
        INSERT INTO student_skills (user_id, skill_id) VALUES (%s, %s)
        """, (user_id, skill_id))

        # Insert interests into interests table
        db.execute("""
        INSERT INTO interests (name) VALUES (%s)
        """, (form_interests,))
        interests_id = db.lastrowid

        # Link interests to student
        db.execute("""
        INSERT INTO student_interests (user_id, interest_id) VALUES (%s, %s)
        """, (user_id, interests_id))

        # Process skills and interests through AI to get embeddings/vectors
        inter_skills_json = ai_micro.get_ai_json(form_skills, form_interests)
        interests_json = json.dumps(inter_skills_json["interests"])
        skills_json = json.dumps(inter_skills_json["skills"])
        availability_json = json.dumps(availability)
        hours_per_week_json = json.dumps(hours_per_week)

        # Insert all form data into student_form table
        # TODO: if availability empty - delete it from the row
        db.execute("""
            INSERT INTO student_form (student_id, email, skills, interests, availability, hours_per_week)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, email, skills_json, interests_json, availability_json, hours_per_week_json))

        print("Form submitted successfully")
        return jsonify({"success": True, "message": "Form submitted successfully"})

    # GET request - display form
    return render_template("student_form.html", user=session['user_id'])


@app.route("/teacher/<int:user_id>/<string:group_code>", methods=["GET", "POST"])
def teacher_page(user_id, group_code):
    """
    Teacher dashboard page
    
    Args:
        user_id (int): Teacher's user ID
        group_code (str): The group code for this class
    
    GET: Display dashboard with group code
    POST: Trigger group generation algorithm when all students submitted
    
    Displays:
    - Number of students who have submitted forms
    - Total expected students
    - Button to generate groups (only when all students submitted)
    
    Returns:
        GET: Rendered teacher dashboard
        POST: Redirect to results page after generating groups
    """
    # Ensure user_id is in session
    if 'user_id' not in session:
        session['user_id'] = user_id

    db = get_db()
    
    # Get teacher information
    db.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = db.fetchone()
    
    # Get group information
    db.execute("SELECT * FROM teacher_group WHERE group_code = %s", (group_code,))
    group = db.fetchone()
    min_students = group["min_students_per_group"]
    max_students = group["max_students_per_group"]

    # Count how many students have submitted their forms
    querySubmitted = """
    SELECT COUNT(sf.student_id) as submitted
    FROM student_form sf 
    JOIN student_group sg 
        ON sf.student_id = sg.student_id
    WHERE sg.group_code = %s
    """
    db.execute(querySubmitted, (group_code,))
    submitted = db.fetchone()
    
    total_students = group['total_students']
    generate = False
   
    # Check if all students have submitted - enable group generation
    if submitted['submitted'] == total_students:
        generate = True
    
        # POST request - Generate groups using clustering algorithm
        if request.method == "POST":
            # Get all student data for clustering
            sql = '''
                SELECT 
                    u.id,
                    u.user_firstname,
                    u.user_lastname,
                    f.skills,
                    f.interests,
                    f.availability,
                    f.hours_per_week
                FROM 
                    users AS u
                JOIN 
                    student_form AS f 
                    ON u.id = f.student_id
                JOIN 
                    student_group g
                    ON g.student_id = u.id
                WHERE g.group_code = %s'''
            
            db.execute(sql, (group['group_code'],))
            results = db.fetchall()
            
            # Convert to JSON for processing
            data_json = json.dumps(results)
            data = json.loads(data_json)
            
            # Run clustering algorithm to sort students into groups
            # Uses min/max group size from group settings
            sorted_groups = sort_alg.sort_groups(min_students, max_students, data)

            # Update database with assigned group numbers
            for group_num, student_ids in sorted_groups.items():
                for student_id in student_ids:
        
                    # Assign group number to each student
                    db.execute("UPDATE student_group SET group_number = %s WHERE student_id = %s", (group_num, student_id))

            # Redirect to results page to view generated groups        
            return redirect(url_for('show_results', user_id=session['user_id'], group_code=group_code, generate=generate))

    # GET request - display teacher dashboard
    return render_template("teacher.html", user_id=user_id, group_code=group_code, generate=generate)


@app.route("/teacher/<int:user_id>/<string:group_code>/results", methods=["GET", "POST"])
def show_results(user_id, group_code):
    """
    Display the final group assignments after clustering algorithm runs.
    
    Args:
        user_id (int): Teacher's user ID
        group_code (str): The group code for this class
    
    Shows:
    - Each student's name
    - Their assigned group number
    - Organized by group
    
    Returns:
        Rendered results template with group assignments
    """
    db = get_db()

    # Query to get all students with their assigned group numbers
    result_sql = """SELECT u.user_firstname, u.user_lastname, g.group_number
                FROM users u
                JOIN student_group g 
                    ON u.id = g.student_id
                WHERE group_code = %s"""
    db.execute(result_sql, (group_code, ))
    group_results = db.fetchall()

    # Display results page with all group assignments
    return render_template("results.html", user_id=user_id, group_code=group_code, group_results=group_results)


if __name__ == "__main__":
    print("Starting Flask app...")
    app.run(debug=True)