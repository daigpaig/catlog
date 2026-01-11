#!/usr/bin/env python3
"""
Test script for parse_structured_query.py
Tests various question types to see how they are parsed.
"""

import json
from app.services.tools.parse_structured_query import parse_structured_query, StructuredQuery

def format_query_result(query: StructuredQuery) -> dict:
    """Convert StructuredQuery to a readable dict format."""
    return {
        "term": query.term,
        "subjects": query.subjects,
        "level_range": query.level_range,
        "distros": query.distros,
        "days": query.days,
        "time_windows": query.time_windows,
        "schools": query.schools,
        "instructors": query.instructors,
        "avoidSubjects": query.avoidSubjects,
        "avoidInstructors": query.avoidInstructors,
        "days_exclude": query.days_exclude,
        "time_exclude": query.time_exclude,
        "levels_exclude": query.levels_exclude,
        "keywords": query.keywords,
        "notes": query.notes,
        "original_message": query.original_message
    }

def print_query_result(category: str, question: str, result: dict):
    """Print a formatted query result."""
    print(f"\n{'='*80}")
    print(f"Category: {category}")
    print(f"Question: {question}")
    print(f"{'-'*80}")
    
    # Only print non-empty fields
    non_empty = {k: v for k, v in result.items() if v and k != "original_message"}
    
    if non_empty:
        print(json.dumps(non_empty, indent=2))
    else:
        print("No structured data extracted")
    
    print(f"{'='*80}")

def main():
    questions = [
        # 1. Degree progress / requirements
        ("Degree progress / requirements", "What classes should I take next quarter to stay on track for the Data Science major?"),
        ("Degree progress / requirements", "I still need two STAT electives and one CS class — what do you recommend?"),
        ("Degree progress / requirements", "Which courses can double count for my Data Science major and Italian minor?"),
        ("Degree progress / requirements", "I have AP credit for Calc BC and Statistics — what should I take next?"),
        ("Degree progress / requirements", "What's the easiest way to finish my Transportation & Logistics minor by junior year?"),
        
        # 2. Interest-driven recommendations
        ("Interest-driven recommendations", "I like machine learning and linguistics — what classes combine both?"),
        ("Interest-driven recommendations", "Recommend classes related to NLP or computational linguistics."),
        ("Interest-driven recommendations", "I'm interested in urban planning and transportation systems — any good electives?"),
        ("Interest-driven recommendations", "What classes would help me get into data analytics internships?"),
        ("Interest-driven recommendations", "I enjoyed STAT 303 and CS 211 — what should I take next?"),
        
        # 3. Difficulty / workload constraints
        ("Difficulty / workload constraints", "I want a lighter quarter — what are some low-workload electives?"),
        ("Difficulty / workload constraints", "Recommend rigorous, math-heavy classes for someone who likes theory."),
        ("Difficulty / workload constraints", "I'm taking two hard STAT classes already — what's a chill fourth class?"),
        ("Difficulty / workload constraints", "Which classes are challenging but fair (not busywork-heavy)?"),
        
        # 4. Schedule / logistics constraints
        ("Schedule / logistics constraints", "What classes fit into a Monday–Wednesday schedule with no mornings?"),
        ("Schedule / logistics constraints", "Recommend classes with no Friday sections."),
        ("Schedule / logistics constraints", "I need a class after 2pm that counts toward my major."),
        ("Schedule / logistics constraints", "What courses won't conflict with my existing schedule?"),
        
        # 5. Professor / style preferences
        ("Professor / style preferences", "Are there any Data Science classes taught by professors known for clear lectures?"),
        ("Professor / style preferences", "Which professors are best if I prefer project-based classes over exams?"),
    ]
    
    print("Testing parse_structured_query.py")
    print("="*80)
    
    for category, question in questions:
        try:
            query = parse_structured_query(question)
            result = format_query_result(query)
            print_query_result(category, question, result)
        except Exception as e:
            print(f"\n{'='*80}")
            print(f"Category: {category}")
            print(f"Question: {question}")
            print(f"ERROR: {type(e).__name__}: {e}")
            print(f"{'='*80}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()

