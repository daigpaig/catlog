import os
from openai import OpenAI
from dotenv import load_dotenv
from ..services.prompt_builder import build_user_context
from ..schemas.chat import ChatRequest

load_dotenv()
client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

def get_chat_response(chat_request: ChatRequest) -> str:
    user_context = build_user_context(chat_request)
    full_prompt = (
        "You are an academic assistant helping a student at Northwestern University pick their classes for a given quarter.\n"
        "Here is some information about the student:\n\n"
        f"{user_context}"
    )
    try:
        response = client.chat.completions.create(
            model = "gpt-4o",
            messages = [
                {"role": "system", "content": full_prompt},
                {"role": "user", "content": chat_request.message}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print("OpenAI error:", e)
        return "Sorry, something went wrong with the AI. Please try again."
    
def categorize_request(chat_request: ChatRequest) -> str:
    prompt = (
        "You are a helpful assistant. Your job is to classify the user's intent into one of the following categories: recommend_courses, course_description, major_requirements, prerequisite_check, schedule_conflict, add_course, remove_course, class_times, professor_info, distribution_requirements, gen_ai, greeting, goodbye. \n"
        "Respond with ONLY the category name."
    )
    try:
        response = client.chat.completions.create(
            model = "gpt4o",
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": chat_request.message}
            ]
        )
    except Exception as e:
        print("OpenAI error:", e)
        return "error"