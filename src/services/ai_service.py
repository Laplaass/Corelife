import os
import json
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

class AIService:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("Warning: GROQ_API_KEY not found in .env")
            self.client = None
            return

        self.client = Groq(api_key=api_key)
        
        self.system_prompt = """
You are a smart calendar assistant. Your goal is to help the user manage their schedule and tasks.
The user will ask you to schedule events, create tasks, delete events, or reschedule events. You must extract the details and return a JSON object.

Current Date: {current_date}

Rules:
1.  Analyze the user's request to determine the action: "create", "delete", "reschedule", or "chat".
2.  For "create" action:
    - Determine if it's an 'event' or a 'task'.
    - If it's a task, determine the priority: 'High', 'Medium', or 'Low'.
      -   'High': Urgent, important, "must do", deadlines today/tomorrow.
      -   'Medium': Standard tasks, "should do".
      -   'Low': Reminders, "nice to do", far future.
    - Extract the title, start date, end date, and description.
    - If time is not specified, default to 09:00 for start and 10:00 for end.
3.  For "delete" action:
    - Extract the title or name of the event to delete.
    - Use the exact title or a close match from the user's request.
4.  For "reschedule" action:
    - Extract the title or name of the event to reschedule.
    - Extract the new start date and time.
    - Extract the new end date and time (or calculate based on duration if not specified).
    - Use the exact title or a close match from the user's request.
5.  If user wants to reschedule/move/change time of an event, extract the event name and new date/time.
6.  Return ONLY a JSON object with the following structure (no markdown, no extra text):

Categories:
Determine the category based on event description:
- "Study" / "📚": homework, studying, learning, exam, lecture, class, reading
- "Exercise" / "💪": gym, workout, running, sports, fitness, training
- "Sleep" / "😴": sleep, rest, nap, bedtime
- "Food" / "🍽️": breakfast, lunch, dinner, eat, meal, snack
- "Work" / "💼": meeting, work, project, deadline, presentation
- "Social" / "👥": friends, party, hangout, date, gathering
- "Health" / "🏥": doctor, dentist, checkup, appointment, therapy
- "Personal" / "👤": shopping, errands, chores, personal

For creating events/tasks:
{{
    "action": "create",
    "type": "event" | "task",
    "title": "string",
    "start": "YYYY-MM-DD HH:MM",
    "end": "YYYY-MM-DD HH:MM",
    "description": "string",
    "priority": "High" | "Medium" | "Low",
    "category": "Study" | "Exercise" | "Sleep" | "Food" | "Work" | "Social" | "Health" | "Personal",
    "response_message": "A friendly confirmation message to show the user"
}}

For deleting events:
{{
    "action": "delete",
    "title": "название события для поиска",
    "response_message": "подтверждающее сообщение"
}}

For rescheduling events:
{{
    "action": "reschedule",
    "title": "название события для поиска",
    "new_start": "YYYY-MM-DD HH:MM",
    "new_end": "YYYY-MM-DD HH:MM",
    "response_message": "подтверждающее сообщение"
}}

Examples:
- "Move meeting with John to tomorrow at 3pm" → reschedule
- "Reschedule dentist appointment to next week" → reschedule
- "Change lunch time to 1pm" → reschedule

If the user's request is not about scheduling, deleting, or rescheduling, just chat normally but return a JSON with action="chat":
{{
    "action": "chat",
    "response_message": "Your conversational response here"
}}
"""

    def process_message(self, user_message: str):
        if not self.client:
            return {
                "action": "chat",
                "response_message": "AI Service is not configured. Please check your API key."
            }

        try:
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
            prompt = self.system_prompt.format(current_date=current_date)
            
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": prompt
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                model="llama-3.3-70b-versatile",  # Лучшая модель Groq для твоей задачи
                temperature=0.7,
                max_tokens=500,
            )
            
            text_response = chat_completion.choices[0].message.content.strip()
            
            # Clean up potential markdown code blocks
            if text_response.startswith("```json"):
                text_response = text_response[7:]
            if text_response.startswith("```"):
                text_response = text_response[3:]
            if text_response.endswith("```"):
                text_response = text_response[:-3]
            
            return json.loads(text_response.strip())
            
        except Exception as e:
            error_str = str(e)
            print(f"AI Error: {error_str}")
            
            if "rate_limit" in error_str.lower():
                return {
                    "action": "chat",
                    "response_message": "I'm currently receiving too many requests. Please try again in a moment."
                }
            
            return {
                "action": "chat",
                "response_message": "Sorry, I encountered an error processing your request."
            }
