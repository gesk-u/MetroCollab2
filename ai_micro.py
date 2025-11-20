from ollama import chat
from ollama import ChatResponse
import json

# interests = """
# I like pizza, but I'm not sure if AI can really understand that.  
# By the way, what's the weather like today?  
# Sometimes I wonder if computers dream of electric sheep.  
# Also, I enjoy watching movies on weekends, nothing to do with programming though.  
# Can you help me solve this math problem? 2+2=?
# """
# skills = """
# I enjoy working on software development projects that solve real-world problems, especially apps that improve productivity or automate tasks.
# I'm also interested in cybersecurity projects and learning how to protect systems from threats. 
# """

def clean_and_validate_response(skills_text, interests_text):
    """
    Clean and validate student responses before sending to Gemini
    """
    # Convert to lowercase
    skills_text = skills_text.lower().strip()
    interests_text = interests_text.lower().strip()
    
    return skills_text, interests_text

# response: ChatResponse = chat(model='gemma3:4b', messages=[
#   {
#     'role': 'user',
#     'content': f'''
# Analyze the following student responses and return ONLY a valid JSON object with two keys: "skills" and "interests".  
# Each key should have a list of strings as its value.

# If the student includes any text not related to skills or interests (like questions, unrelated comments, etc.), ignore that text.

# If there is no valid information about skills or interests, return an empty JSON object: {{}}.

# Do NOT include any explanation or extra text.

# Student skills: {skills}
# Student interests: {interests}
#     ''',
#   },
# ])
#print(response['message']['content'])
# or access fields directly from the response object
# print(response.message.content)

# response_text = response.message.content

# if response_text.startswith("```json"):
#   response_text = response_text[len("```json"):]
# if response_text.endswith("```"):
#   response_text = response_text[:-len("```")]

# response_text = response_text.strip() 
# data = json.loads(response_text)
# skills = data['skills']
# interests = data['interests']
# print("Skills:", skills)
# print("Interests:", interests)
# print("done")


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


