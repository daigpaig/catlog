TOOLS = [
    {
        "type": "function",
        "name": "parse_structured_query",
        "description": "Parse free-text into a StructuredQuery dict (subjects, levels, distros, days/times, schools, instructors, negations).",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {"type": "string"},
                "term_hint": {"anyOf": [{"type": "string"}, {"type": "null"}]}
            },
            "required": ["message"]
        }
    },
    {
        "type": "function",
        "name": "shortlist_classes",
        "description": "Given a StructuredQuery and UserProfile, return a ranked shortlist: [{'course_id','score'}].",
        "parameters": {
            "type": "object",
            "properties": {
                "query":   {"type": "object"},
                "profile": {"type": "object"},
                "weights": {"type": "array", "items": {"type": "number"}}
            },
            "required": ["query", "profile"]
        }
    }
]


