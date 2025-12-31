from ..schemas.chat import ChatRequest

def build_user_context(chat_request: ChatRequest) -> str:
    parts = []

    if chat_request.majors:
        majors_str = ', '.join(chat_request.majors)
        parts.append(f"The student is majoring in {majors_str}.")

    if chat_request.minors:
        minors_str = ', '.join(chat_request.minors)
        parts.append(f"The student is also minoring in {minors_str}.")

    if chat_request.schedule_preferences:
        parts.append(f"They have the following schedule preferences: {chat_request.schedule_preferences}.")

    if chat_request.locked_classes:
        locked_str = ', '.join(chat_request.locked_classes)
        parts.append(f"The student has indicated they do not want to remove these classes from their schedule: {locked_str}.")

    if chat_request.self_description:
        parts.append(f"This is how the student describes themselves: {chat_request.self_description}")

    return " ".join(parts)