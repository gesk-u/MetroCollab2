# MetroCollab

AI-powered student team matching system using K-Means clustering, GloVe word embeddings, and Ollama AI integration to automatically group students based on skills, interests, and availability.

## Requirements

All project dependencies are in a single `requirements.txt` file at the root.

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/gesk-u/MetroCollab2.git
cd MetroCollab2

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install Ollama
# Download from: https://ollama.com/download

# 4. Add Ollama to PATH
# Open Start → type "Environment Variables" → Enter
# Click "Environment Variables"
# Under "System variables", find "Path" → Edit
# Press "New" and paste: C:\Users\atkac\AppData\Local\Ollama
# (Use the actual Ollama installation path if you changed the default location)
# Click OK to save

# 5. Pull the AI model
ollama pull gemma3:4b

# 6. Add MariaDB to PATH
# Open Start → type "Environment Variables" → Enter
# Click "Environment Variables"
# Under "System variables", find "Path" → Edit
# Press "New" and paste your MariaDB bin location
# Example: C:\Program Files\MariaDB 12.1\bin
# Click OK to save

# 7. Set up MySQL database
# Open cmd (Win+R → type "cmd" → Enter)
# Navigate to your project directory:
cd path\to\MetroCollab2
# Run the schema:
mysql -u root -p < schema.sql

# 8. Create .env file
echo SECRET_KEY=your-secret-key-here > .env
echo PASSWORD=your-mysql-password >> .env
echo USER=your-user-name-here >> .env

# 9. Verify .env encoding is UTF-8
# Open the .env file in a text editor
# Check encoding is UTF-8, change if necessary
# In VS Code: bottom right corner shows encoding
# In Notepad: File → Save As → Encoding dropdown → UTF-8

# 10. Run the application
python app.py
```

## System Requirements

- **Python:** 3.8 or higher
- **MySQL:** 8.0 or higher
- **RAM:** 8GB+ (for Ollama AI model)
- **Disk Space:** ~3GB (for GloVe and Gemma models)

## Dependencies

### Core Framework
- **Flask** - Web framework
- **mysql-connector-python** - Database connectivity
- **python-dotenv** - Environment variable management

### AI & Machine Learning
- **ollama** - Local LLM integration
- **gensim** - GloVe word embeddings
- **numpy** - Numerical operations
- **scikit-learn** - K-Means clustering

### Development & Testing
- **Faker** - Generate test data

## Project Structure

```
MetroCollab/
├── app.py                 # Main Flask application
├── ai_micro.py           # AI generation module (Ollama)
├── sort_alg.py           # K-Means clustering algorithm
├── generate_test_data.py # Test data generation script
├── requirements.txt      # All Python dependencies
├── schema.sql            # Database schema
├── .env                  # Environment variables (create this)
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore file
├── templates/            # HTML templates
│   ├── index.html
│   ├── student_form.html
│   ├── teacher.html
│   └── results.html
└── static/               # CSS, JS, images
```

## Usage

### For Teachers
1. Register as a teacher
2. Set group parameters (min/max students per group)
3. Share the group code with students
4. Wait for all students to submit forms
5. Click "Generate Groups" to run clustering algorithm
6. View results with optimal team assignments

### For Students
1. Register as a student
2. Enter teacher's group code
3. Fill out the form with:
   - Skills
   - Interests
   - Weekly availability
   - Hours per week commitment
4. Submit and wait for teacher to generate groups

### Generate Test Data

```bash
# Create 20 students with groups of 3-5
python generate_test_data.py 20 3 5

# Use defaults (10 students, groups of 2-4)
python generate_test_data.py
```

## Configuration

### Environment Variables (.env)
```bash
SECRET_KEY=your-flask-secret-key
PASSWORD=your-mysql-root-password
USER=your-user-name
```

### Database Setup
Create these tables in your `Collab_DB` database:
- `users` - User information (students and teachers)
- `teacher_group` - Group configuration
- `student_group` - Student-group relationships
- `student_form` - Student responses
- `skills` - Skills library
- `interests` - Interests library
- `student_skills` - Student-skill relationships
- `student_interests` - Student-interest relationships

## AI Models

### Ollama (Local LLM)
- **Model:** gemma3:4b (~2.5GB)
- **Purpose:** Generate and parse student data
- **Installation:** `ollama pull gemma3:4b`

### GloVe Embeddings
- **Model:** glove-wiki-gigaword-100 (~128MB)
- **Purpose:** Convert skills to vector embeddings
- **Installation:** Auto-downloads on first use

## Features

-  AI-powered data generation
-  K-Means clustering for team formation
-  GloVe embeddings for semantic similarity
-  Multi-factor matching (skills, interests, availability, time commitment)
-  Balanced group sizing with constraints
-  Responsive web interface

---
# ===================================
# TROUBLESHOOTING: If you get connection errors
# ===================================
# If you see errors like "ConnectionError" or "Connection refused",
# uncomment the lines below and use explicit client connection:
#
# client = Client(host="http://127.0.0.1:11434")
# 
# Then replace all instances of:
#   chat(model='gemma3:4b', messages=[...])
# With:
#   client.chat(model='gemma3:4b', messages=[...])
#
# This explicitly tells Ollama where to connect.
# ===================================

**Note:** Make sure Ollama is running before starting the Flask application!
