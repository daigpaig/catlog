from __future__ import annotations
from typing import Any, Dict, List, Optional
import json
import os
from pathlib import Path
from dataclasses import asdict
from openai import OpenAI
from dotenv import load_dotenv

from ..tools.parse_structured_query import parse_structured_query, StructuredQuery
from ..tools.shortlist_classes import shortlist_classes

load_dotenv()

def _get_openai_client() -> OpenAI:
    """Get OpenAI client instance."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        # Try loading again
        app_dir = Path(__file__).parent.parent.parent  # backend/app
        backend_dir = app_dir.parent  # backend
        env_paths = [
            app_dir / ".env",
            backend_dir / ".env",
            Path.cwd() / ".env",
            Path.cwd() / "backend" / ".env",
            Path.cwd() / "backend" / "app" / ".env",
        ]
        for env_path in env_paths:
            if env_path.exists():
                load_dotenv(env_path, override=True)
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    break
        
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
    return OpenAI(api_key=api_key)


def tool_parse_structured_query(message: str, term_hint: Optional[str] = None) -> Dict[str, Any]:
    """Tool function: Parse a natural language query into a structured query."""
    q = parse_structured_query(message, term_hint)
    # Convert dataclass to dict
    result = asdict(q)
    # Handle nested PrioritySpec
    if isinstance(result.get("priority"), dict) is False and q.priority is not None:
        result["priority"] = asdict(q.priority)
    return result


def tool_shortlist_classes(
    query: Dict[str, Any],
    plan_path: Optional[str] = None,
    schedule_path: Optional[str] = None,
    limit: int = 20,
    per_subject_cap: int = 6
) -> Dict[str, Any]:
    """Tool function: Get a shortlist of courses matching the structured query."""
    # Convert dict to StructuredQuery
    query_obj = query  # shortlist_classes can handle dict or StructuredQuery
    
    # Default paths
    if plan_path is None:
        plan_path = Path(__file__).parent.parent.parent / "data" / "plan.json"
    if schedule_path is None:
        schedule_path = Path(__file__).parent.parent.parent / "data" / "5000.json"
    
    result = shortlist_classes(query_obj, plan_path, schedule_path, limit, per_subject_cap)
    return result


# Define tool schemas for OpenAI function calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "parse_structured_query",
            "description": "STEP 1: Parse a natural language query about courses into a structured query format. ALWAYS call this first when the user asks about courses. Use this to understand what courses the user is looking for based on their natural language request. Returns a structured query object that you must then pass to shortlist_classes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The user's natural language query about courses (e.g., 'I need STAT classes after 2pm with no Friday', 'recommend consulting courses', 'find NLP classes')",
                    },
                    "term_hint": {
                        "type": "string",
                        "description": "Optional term code hint (e.g., '2025FA') if the user mentioned a specific term",
                    },
                },
                "required": ["message"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "shortlist_classes",
            "description": "STEP 2: Get a shortlist of courses that match the structured query. ALWAYS call this AFTER parse_structured_query, passing the structured query object you received. This searches through the actual course catalog database and returns relevant courses with their details (course codes, titles, descriptions, meeting times, instructors, etc.). You MUST use the courses from this result in your recommendation - do not make up course information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "object",
                        "description": "The structured query object returned from parse_structured_query",
                        "properties": {
                            "subjects": {"type": "array", "items": {"type": "string"}},
                            "catalog_numbers": {"type": "array", "items": {"type": "string"}},
                            "days_include": {"type": "array", "items": {"type": "string"}},
                            "days_exclude": {"type": "array", "items": {"type": "string"}},
                            "time_include": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                            "time_exclude": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                            "include_keywords": {"type": "array", "items": {"type": "string"}},
                            "exclude_keywords": {"type": "array", "items": {"type": "string"}},
                            "schools": {"type": "array", "items": {"type": "string"}},
                            "distros": {"type": "array", "items": {"type": "string"}},
                            "units_range": {"type": "array", "items": {"type": "array", "items": {"type": "number"}}},
                        },
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of courses to return (default: 20)",
                        "default": 20,
                    },
                    "per_subject_cap": {
                        "type": "integer",
                        "description": "Maximum number of courses per subject (default: 6)",
                        "default": 6,
                    },
                },
                "required": ["query"],
            },
        },
    },
]


def recommend_courses(user_query: str, term_hint: Optional[str] = None, max_iterations: int = 5) -> str:
    """
    Use LLM with function calling to make course recommendations.
    
    Args:
        user_query: The user's natural language query about courses
        term_hint: Optional term code hint
        max_iterations: Maximum number of tool call iterations (default: 5)
    
    Returns:
        Final recommendation text from the LLM
    """
    client = _get_openai_client()
    
    system_message = """You are an academic advisor assistant at Northwestern University helping students find courses.

CRITICAL WORKFLOW - You MUST follow these steps:
1. ALWAYS start by calling parse_structured_query with the user's message to understand their query
2. THEN call shortlist_classes with the parsed query to get actual courses from the database
3. Use the course data from shortlist_classes to make your recommendation
4. Format your response in a specific alternating structure (see below)

IMPORTANT RULES:
- You MUST call both tools in sequence - parse_structured_query first, then shortlist_classes
- Do NOT make up course names or information - only use courses from the shortlist_classes results
- If shortlist_classes returns courses, you MUST use them in your recommendation

RESPONSE FORMAT - Structure your response as follows:

1. Start with a short intro message (1-2 sentences), e.g., "Here are some STAT classes available after 2 PM that might fit your schedule:"

2. For each course from the shortlist (present 3-5 courses), alternate between:
   a) Course block: Present the course with its basic info
      Format: "SUBJECT CATALOG_NUMBER: Title"
      Include: Meeting times if available (e.g., "Meets: Monday, Wednesday 2:00-3:30 PM")
   
   b) Description: A short explanation (1-2 sentences) about why this course fits the user's query/preferences
      Be specific: mention schedule fit, requirements, interests, difficulty level, etc.

Example:
"Here are some STAT classes available after 2 PM that might fit your schedule:

STAT 303-1: Statistical Methods for Data Science
Meets: Monday, Wednesday 2:00-3:30 PM

This course fits your schedule perfectly - it's after 2 PM and avoids Friday classes. It's a core requirement for the Data Science major and covers essential statistical methods that will be useful for your career goals.

STAT 320-1: Regression Analysis
Meets: Tuesday, Thursday 3:00-4:30 PM

This advanced statistics course builds on STAT 303 and meets your time constraints. It's highly recommended for students interested in data analysis and will help you develop practical skills for internships.

..."

IMPORTANT: 
- Use actual course data from shortlist_classes results - reference the exact course codes, titles, and meeting times
- Be specific about why each course fits (schedule, requirements, interests, difficulty, etc.)
- Keep descriptions concise but informative (1-2 sentences each)
- Present 3-5 courses in this alternating format

If the shortlist is empty, explain why and suggest what they might try instead."""
    
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_query}
    ]
    
    iteration = 0
    parse_called = False
    shortlist_called = False
    
    while iteration < max_iterations:
        # Call the model with tools
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",  # Let the model decide when to use tools
            temperature=0.7
        )
        
        message = response.choices[0].message
        # Convert ChatCompletionMessage to dict format for messages list
        message_dict = {
            "role": message.role,
            "content": message.content or "",
        }
        if message.tool_calls:
            message_dict["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in message.tool_calls
            ]
        messages.append(message_dict)
        
        # Check if the model wants to call a function
        tool_calls = message_dict.get("tool_calls") or []
        if tool_calls:
            # Process each tool call
            for tool_call in tool_calls:
                function_name = tool_call["function"]["name"]
                function_args = json.loads(tool_call["function"]["arguments"])
                
                print(f"[TOOL CALL] {function_name} with args: {function_args}")
                
                # Execute the function
                try:
                    if function_name == "parse_structured_query":
                        parse_called = True
                        function_result = tool_parse_structured_query(
                            function_args.get("message"),
                            function_args.get("term_hint")
                        )
                        print(f"[TOOL RESULT] parse_structured_query returned {len(str(function_result))} chars")
                    elif function_name == "shortlist_classes":
                        shortlist_called = True
                        function_result = tool_shortlist_classes(
                            function_args.get("query"),
                            function_args.get("plan_path"),
                            function_args.get("schedule_path"),
                            function_args.get("limit", 20),
                            function_args.get("per_subject_cap", 6)
                        )
                        shortlist_count = len(function_result.get("shortlist", []))
                        print(f"[TOOL RESULT] shortlist_classes returned {shortlist_count} courses")
                        if shortlist_count == 0:
                            print(f"[WARNING] shortlist_classes returned 0 courses!")
                    else:
                        function_result = {"error": f"Unknown function: {function_name}"}
                    
                    # Truncate very large results to avoid token limits
                    result_str = json.dumps(function_result)
                    if len(result_str) > 50000:  # ~50k chars
                        print(f"[WARNING] Tool result is very large ({len(result_str)} chars), truncating...")
                        # Keep the structure but limit course details
                        if "shortlist" in function_result:
                            function_result["shortlist"] = function_result["shortlist"][:10]  # Limit to 10 courses
                            function_result["_truncated"] = True
                    
                    # Add the function result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": json.dumps(function_result)
                    })
                except Exception as e:
                    print(f"[TOOL ERROR] {function_name} failed: {e}")
                    import traceback
                    traceback.print_exc()
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": json.dumps({"error": str(e)})
                    })
            
            iteration += 1
        else:
            # Model returned a final answer, no more tool calls needed
            if not parse_called:
                print("[WARNING] LLM returned answer without calling parse_structured_query")
            if parse_called and not shortlist_called:
                print("[WARNING] LLM parsed query but didn't call shortlist_classes - this means RAG is not working!")
            break
    
    # Return the final assistant message
    final_message = messages[-1]
    final_content = final_message.get("content") if isinstance(final_message, dict) else getattr(final_message, "content", "Sorry, I couldn't generate a recommendation.")
    if not final_content:
        final_content = "Sorry, I couldn't generate a recommendation."
    
    # Try to extract structured recommendation from the final message
    structured_data = None
    try:
        import re
        
        # Get shortlist data from tool calls
        shortlist_data = None
        for msg in reversed(messages):
            if msg.get("role") == "tool" and "shortlist" in msg.get("content", ""):
                try:
                    tool_data = json.loads(msg["content"])
                    if "shortlist" in tool_data and len(tool_data.get("shortlist", [])) > 0:
                        shortlist_data = tool_data
                        break
                except:
                    pass
        
        if shortlist_data:
            # Extract intro message (first paragraph or first 200 chars)
            intro_message = final_content.split("\n\n")[0] if "\n\n" in final_content else final_content.split("\n")[0]
            if len(intro_message) > 200:
                intro_message = intro_message[:200] + "..."
            
            # Build the structure from shortlist
            structured_data = _convert_shortlist_to_recommendation(shortlist_data, intro_message)
            
            # Try to extract descriptions from the LLM's natural language response
            # Look for course codes followed by descriptions
            if structured_data and structured_data.get("items"):
                course_items = [item for item in structured_data["items"] if item["type"] == "course"]
                
                for i, course_item in enumerate(course_items):
                    course = course_item["course"]
                    course_code = f"{course['subject']} {course['catalog_number']}"
                    
                    # Try to find this course code in the response and extract the description after it
                    # Look for pattern: "COURSE_CODE" or "COURSE_CODE:" followed by text until next course or end
                    next_course_code = None
                    if i + 1 < len(course_items):
                        next_course = course_items[i + 1]["course"]
                        next_course_code = f"{next_course['subject']} {next_course['catalog_number']}"
                    
                    # Pattern: course code, optional colon/dash, then description text
                    if next_course_code:
                        pattern = rf"{re.escape(course_code)}[:\-]?\s*(.+?)(?=\s*(?:{re.escape(next_course_code)}|$))"
                    else:
                        pattern = rf"{re.escape(course_code)}[:\-]?\s*(.+?)$"
                    
                    match = re.search(pattern, final_content, re.DOTALL | re.IGNORECASE)
                    if match:
                        desc_text = match.group(1).strip()
                        # Clean up: remove course title if it's in there, keep only the explanation
                        # Remove common patterns like "Meets:", "Instructor:", etc. and keep the reasoning
                        lines = desc_text.split("\n")
                        # Find the line that explains why it fits (usually after meeting info)
                        for line in reversed(lines):
                            if len(line) > 20 and not re.match(r'^(Meets?|Instructor|Time|Days?):', line, re.I):
                                desc_text = line.strip()
                                break
                        
                        # Update the description item
                        desc_idx = structured_data["items"].index(course_item) + 1
                        if desc_idx < len(structured_data["items"]) and structured_data["items"][desc_idx]["type"] == "description":
                            structured_data["items"][desc_idx]["description"] = desc_text
                            print(f"[STRUCTURED] Extracted description for {course_code}: {desc_text[:50]}...")
                
                print(f"[STRUCTURED] Built recommendation with {len(structured_data.get('items', []))} items")
                
    except Exception as e:
        print(f"Error extracting structured data: {e}")
        import traceback
        traceback.print_exc()
    
    return {
        "content": final_content,
        "structured_data": structured_data
    }


def _convert_shortlist_to_recommendation(shortlist_data: Dict[str, Any], intro_message: str) -> Dict[str, Any]:
    """Convert shortlist_classes output to CourseRecommendation format with alternating course/description blocks."""
    courses_data = shortlist_data.get("shortlist", [])
    
    if not courses_data:
        return None
    
    # Convert courses to the format needed
    formatted_courses = []
    for course_card in courses_data[:5]:  # Limit to 5 courses max
        # Extract sections info
        sections = course_card.get("sections", [])
        meeting_days = set()
        start_end = []
        instructors = []
        
        for section in sections:
            if section.get("meeting_days"):
                meeting_days.update(section["meeting_days"])
            if section.get("start_end"):
                start_end.extend(section["start_end"])
            if section.get("instructors"):
                instructors.extend(section["instructors"])
        
        # Build tags
        tags = []
        if course_card.get("distros"):
            tags.append(f"Distro: {course_card['distros']}")
        if course_card.get("school"):
            tags.append(course_card["school"])
        
        course = {
            "id": course_card.get("key") or f"{course_card.get('subject')}-{course_card.get('catalog_number')}",
            "subject": course_card.get("subject", ""),
            "catalog_number": course_card.get("catalog_number", ""),
            "title": course_card.get("title", ""),
            "units": course_card.get("units"),
            "description": course_card.get("description"),
            "meeting_days": list(meeting_days) if meeting_days else None,
            "start_end": start_end if start_end else None,
            "instructors": list(set(instructors)) if instructors else None,
            "tags": tags if tags else None,
            "school": course_card.get("school"),
            "sections": sections,  # Include full section data
        }
        formatted_courses.append(course)
    
    # Build alternating items: course, description, course, description...
    items = []
    for i, course in enumerate(formatted_courses):
        # Add course block
        items.append({
            "type": "course",
            "course": course
        })
        # Add description (will be filled by LLM, but we provide a placeholder)
        items.append({
            "type": "description",
            "description": f"This course matches your criteria."  # LLM should replace this
        })
    
    return {
        "type": "COURSE_RECOMMENDATION",
        "intro": intro_message,
        "items": items
    }


# For backward compatibility
def tool_parse_structured_query_legacy(message: str, term_hint: str | None = None) -> Dict[str, Any]:
    """Legacy wrapper - use tool_parse_structured_query instead."""
    return tool_parse_structured_query(message, term_hint)
