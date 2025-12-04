from ollama import chat
from ollama import ChatResponse
import json
import random

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

def clean_and_validate_response(skills_text, interests_text):
    """
    Clean and validate student responses before sending to Gemini
    """
    # Convert to lowercase
    skills_text = skills_text.lower().strip()
    interests_text = interests_text.lower().strip()
    
    return skills_text, interests_text


def get_ai_json(skills, interests):
  skills, interests = clean_and_validate_response(skills, interests)
  response: ChatResponse = chat(model='gemma3:4b', messages=[
    {
      'role': 'user',
      'content': f'''
  You are analyzing student responses for a project team-matching system. Your task is to extract ONLY project-relevant skills and interests.

STRICT RULES:
1. Extract only technical skills, academic subjects, and project-related capabilities from skills
2. Extract only project-related interests (e.g., "web development", "machine learning", "game design")
3. IGNORE personal hobbies unrelated to projects (e.g., "hiking", "cooking", "sports")
4. Convert all items to lowercase
5. Remove duplicates
6. If a student mentions many technical items but adds 1-2 unrelated hobbies, exclude those hobbies
7. Focus on what indicates PROJECT preferences, not lifestyle preferences

Student skills input: {skills}
Student interests input: {interests}

Respond ONLY with valid JSON in this exact format:
{{"skills": ["skill1", "skill2"], "interests": ["interest1", "interest2"]}}

If no valid project-related information exists, return: {{}}

DO NOT include explanations, markdown, or any text outside the JSON object.
      ''',
    },
  ])
  response_text = response.message.content

  if response_text.startswith("```json"):
    response_text = response_text[len("```json"):]
  if response_text.endswith("```"):
    response_text = response_text[:-len("```")]

  response_text = response_text.strip() 

  data = json.loads(response_text)
  return data

#TODO add error handling

interest_levels = ["beginner", "enthusiastic", "passionate", "curious"]
interest_fields = [
    "Artificial Intelligence",
    "Open Source Projects",
    "Cloud Technologies",
    "Cybersecurity",
    "Mobile App Development",
    "Game Development",
    "Data Science",
    "Machine Learning",
    "DevOps Practices",
    "Web Development",
    "Internet of Things",
    "Virtual Reality",
    "Blockchain Technology"
]


def interests_ai():

  level = random.choice(interest_levels)
  word_count = random.randint(10, 50)
  num_interests = random.randint(2, 4)
  chosen_interests = random.sample(interest_fields, k=num_interests)
  interests_str = ", ".join(chosen_interests[:-1]) + " and " + chosen_interests[-1] if num_interests > 1 else chosen_interests[0]
  response: ChatResponse = chat(model='gemma3:4b', messages=[

    {
      'role': 'user',
      'content': f'''
      You are a university student. You have a {level} interest in programming and technology. Write a brief statement {word_count} words about your programming and technology interests.

      Be specific about what you enjoy working with or want to learn. Mention the most important {num_interests} areas.

      You are especially fascinated by {interests_str}.

      IMPORTANT: Do not include phrases like "My interests:", "I am interested in:", or any labels. Write ONLY the direct description. Start immediately with the content.

      Student interests:''',
    },
  ])

  response_text = response.message.content
  return response_text 

level = ["medium", "high", "low"]
talents = [
    "Software Development",
    "Data Science and Analytics",
    "Cybersecurity",
    "Cloud Computing",
    "DevOps and Automation",
    "Web Development",
    "Mobile Application Development",
    "Database Management",
    "Artificial Intelligence and Machine Learning",
    "Network Administration"
]



def skills_ai():
  response: ChatResponse = chat(model='gemma3:4b', messages=[
    {
      'role': 'user',
    'content': f'''
    You are a university student. You have {random.choice(level)} level of skills. Write a brief statement {random.randint(8, 30)} words about your programming and technical skills.

    Be specific about technologies, languages, and tools you know. Give the most {random.randint(3, 5)} skills. You are talanted at {random.choice(talents)}

    IMPORTANT: Do not include phrases like "My skills:", "I have skills in:", or any labels. Write ONLY the direct description. Start immediately with the content.
    

    Student skills:''',
      },
    ],
    options={
      'temperature': 0.9,  # Increased from 0.7 for more variety
      'top_p': 0.95,       # Adds more diversity
    }
  )

  response_text = response.message.content
  return response_text 



def time_ai():
  response: ChatResponse = chat(model='gemma3:4b', messages=[
    {
      'role': 'user',
      'content': f'''
      You are a university student. Generate your weekly availability for project work as a JSON object.
      Use this exact format: {{"mon": [], "tue": [], "wed": [], "thu": [], "fri": [], "weekend": []}}

      For each day, include zero or more time slots from: "morning", "afternoon", "evening"
      Make it realistic - students typically have 2-5 available slots across the week.

      IMPORTANT: Return ONLY the JSON object, no explanations, no labels, no additional text.
      Student availability:''',
    },
  ])

  response_text = response.message.content

  if response_text.startswith("```json"):
    response_text = response_text[len("```json"):]
  if response_text.endswith("```"):
    response_text = response_text[:-len("```")]

  response_text = response_text.strip() 

  data = json.loads(response_text)
  return data

