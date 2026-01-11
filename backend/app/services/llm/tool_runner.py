from __future__ import annotations
import json
from typing import Any, Dict, List
from .client import get_client
from .tools_schema import TOOLS
from .tools_impl import tool_parse_structured_query, tool_shortlist_classes
from .util import to_plain
from .resp_utils import iter_tool_calls, extract_output_text, normalize_arguments

MODEL = "gpt-4o-mini"  # Updated to available model name

def _dispatch_tool(name: str, arguments: Dict[str, Any]) -> str:
    if name == "parse_structured_query":
        out = tool_parse_structured_query(**arguments)
    elif name == "shortlist_classes":
        out = tool_shortlist_classes(**arguments)
    else:
        out = {"error": f"unknown tool {name}"}
    return json.dumps(out, ensure_ascii=False)

def run_pipeline_with_tools(user_message: str, profile: Dict[str, Any], term_hint: str | None = None) -> Dict[str, Any]:
    client = get_client()
    payload = {"message": user_message, "profile": to_plain(profile)}
    if term_hint is not None: payload["term_hint"] = term_hint

    messages = [
        {"role": "system", "content":
         "You are Course AI for Northwestern. Always use tools to: (1) parse to StructuredQuery, (2) shortlist. Be concise and never invent catalog data."},
        {"role": "user", "content": json.dumps(to_plain(payload))}
    ]

    # Note: OpenAI Responses API may have different method names
    # Adjust based on actual SDK version
    try:
        resp = client.responses.create(model=MODEL, input=messages, tools=TOOLS, max_output_tokens=700)
    except AttributeError:
        # Fallback if responses API doesn't exist - use chat completions with function calling
        resp = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=[{"type": "function", "function": tool} for tool in TOOLS],
            tool_choice="auto"
        )
        # Convert to compatible format
        class ResponseWrapper:
            def __init__(self, resp):
                self.id = getattr(resp, "id", None)
                self.output = []
                if hasattr(resp, "choices") and resp.choices:
                    choice = resp.choices[0]
                    if hasattr(choice, "message"):
                        if hasattr(choice.message, "tool_calls") and choice.message.tool_calls:
                            for tc in choice.message.tool_calls:
                                self.output.append({
                                    "type": "tool_use",
                                    "id": tc.id,
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments
                                })
                        elif hasattr(choice.message, "content"):
                            self.output.append({
                                "type": "output_text",
                                "text": choice.message.content or ""
                            })
        resp = ResponseWrapper(resp)

    while True:
        calls = list(iter_tool_calls(resp))
        if not calls: break
        outs = []
        for tc in calls:
            args = normalize_arguments(tc["arguments"])
            if "profile" in args: args["profile"] = to_plain(args["profile"])
            if "query" in args:   args["query"]   = to_plain(args["query"])
            outs.append({"tool_call_id": tc["id"], "output": _dispatch_tool(tc["name"], args)})
        
        try:
            resp = client.responses.submit_tool_outputs(response_id=resp.id, tool_outputs=outs)
        except AttributeError:
            # Fallback for chat completions API
            messages.append({
                "role": "tool",
                "tool_call_id": tc["id"],
                "content": _dispatch_tool(tc["name"], args)
            })
            resp = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=[{"type": "function", "function": tool} for tool in TOOLS],
                tool_choice="auto"
            )
            # Wrap again
            class ResponseWrapper:
                def __init__(self, resp):
                    self.id = getattr(resp, "id", None)
                    self.output = []
                    if hasattr(resp, "choices") and resp.choices:
                        choice = resp.choices[0]
                        if hasattr(choice, "message"):
                            if hasattr(choice.message, "tool_calls") and choice.message.tool_calls:
                                for tc in choice.message.tool_calls:
                                    self.output.append({
                                        "type": "tool_use",
                                        "id": tc.id,
                                        "name": tc.function.name,
                                        "arguments": tc.function.arguments
                                    })
                            elif hasattr(choice.message, "content"):
                                self.output.append({
                                    "type": "output_text",
                                    "text": choice.message.content or ""
                                })
            resp = ResponseWrapper(resp)

    return {"text": extract_output_text(resp)}


