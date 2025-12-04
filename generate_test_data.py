# Import dotenv to load environment variables from .env file
from dotenv import load_dotenv
import os
import sys
# Import Flask app instance and test data generation function
from app import app, insert_test_data

# Load environment variables from .env file (database password, secret key, etc.)
load_dotenv()

if __name__ == "__main__":
    """
    Script to generate test data for the MetroCollab application.
    
    Usage:
        python script_name.py [num_students] [min_group_size] [max_group_size]
    
    Arguments (all optional):
        students (int): Number of students to create (default: 10)
        min_students (int): Minimum students per group (default: 2)
        max_students (int): Maximum students per group (default: 4)
    
    Example:
        python script_name.py 20 3 5
        Creates 20 students with group sizes between 3-5
    
    The script will:
    1. Create one fake teacher with a unique group code
    2. Generate specified number of fake students
    3. Assign AI-generated skills, interests, and availability to each student
    4. Output the teacher page URL for easy access
    """

    students = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    min_students = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    max_students = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    
    with app.app_context():
        group_code, teacher_id = insert_test_data(students, min_students, max_students)
        print(f"✓ Created {students} students")
        print(f"✓ Group code: {group_code}")
        print(f"✓ Teacher ID: {teacher_id}")
        # Print direct URL to teacher dashboard for easy access during testin
        print(f"✓ Teacher page: http://127.0.0.1:5000/teacher/{teacher_id}/{group_code}")
