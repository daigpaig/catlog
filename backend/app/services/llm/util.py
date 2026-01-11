from __future__ import annotations
from dataclasses import is_dataclass, asdict
from pydantic import BaseModel
from datetime import date, datetime
import numpy as np

def to_plain(x):
    if x is None or isinstance(x, (str,int,float,bool)): return x
    if isinstance(x, (date, datetime)): return x.isoformat()
    if isinstance(x, np.generic): return x.item()
    if isinstance(x, np.ndarray): return [to_plain(v) for v in x.tolist()]
    if isinstance(x, BaseModel):
        try: d = x.model_dump()
        except Exception: d = x.dict()
        return to_plain(d)
    if is_dataclass(x): return to_plain(asdict(x))
    if isinstance(x, dict): return {str(k): to_plain(v) for k,v in x.items()}
    if isinstance(x, (list,tuple,set)): return [to_plain(v) for v in x]
    return str(x)


