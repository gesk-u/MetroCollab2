from ollama import chat
from ollama import ChatResponse
import json

interests = """
I like pizza, but I'm not sure if AI can really understand that.  
By the way, what's the weather like today?  
Sometimes I wonder if computers dream of electric sheep.  
Also, I enjoy watching movies on weekends, nothing to do with programming though.  
Can you help me solve this math problem? 2+2=?
"""
skills = """
I enjoy working on software development projects that solve real-world problems, especially apps that improve productivity or automate tasks.
I'm also interested in cybersecurity projects and learning how to protect systems from threats. 
"""

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
  response: ChatResponse = chat(model='gemma3:4b', messages=[
    {
      'role': 'user',
      'content': f'''
  Analyze the following student responses and return ONLY a valid JSON object with two keys: "skills" and "interests".  
  Each key should have a list of strings as its value. Read carefully each response.

  If the student includes any text not related to skills or interests (like questions, unrelated comments, etc.), ignore that text.

  If there is no valid information about skills or interests, return an empty JSON object: {{}}.

  Do NOT include any explanation or extra text.

  Student skills: {skills}
  Student interests: {interests}
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




data = get_ai_json(skills, interests)

print(data["skills"])