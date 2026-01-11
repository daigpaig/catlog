from __future__ import annotations
import json

def _typ(x): return getattr(x, "type", None) or (x.get("type") if isinstance(x, dict) else None)
def _get(x, name): return getattr(x, name, None) if not isinstance(x, dict) else x.get(name)

def iter_tool_calls(resp):
    for item in (getattr(resp, "output", None) or []):
        if _typ(item) in ("tool_use","tool_call"):
            yield {"id": _get(item,"id"), "name": _get(item,"name"), "arguments": _get(item,"arguments")}

def extract_output_text(resp) -> str:
    chunks = []
    for item in (getattr(resp, "output", None) or []):
        if _typ(item) == "output_text":
            chunks.append(_get(item,"text") or "")
    if not chunks and getattr(resp,"output_text",None):
        return resp.output_text.strip()
    return "".join(chunks).strip()

def normalize_arguments(args):
    if args is None: return {}
    if isinstance(args, str):
        try: return json.loads(args)
        except Exception: return {}
    if hasattr(args, "model_dump"): return args.model_dump()
    if hasattr(args, "dict"): return args.dict()
    if hasattr(args, "__dict__"): return {k:v for k,v in vars(args).items() if not k.startswith("_")}
    return args if isinstance(args, dict) else {}


