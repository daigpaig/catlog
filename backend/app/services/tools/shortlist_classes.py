# shortlist_classes.py
from __future__ import annotations

import json
import re
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Iterable

# Import your types
from .parse_structured_query import StructuredQuery, DayCode

DAY_DIGIT_TO_CODE = {
    "0": "M",
    "1": "T",
    "2": "W",
    "3": "R",
    "4": "F",
    # sometimes sched may include weekend; map if it appears
    "5": "S",
    "6": "U",
}
CODE_TO_MINUTES = {"M": 0, "T": 1, "W": 2, "R": 3, "F": 4, "S": 5, "U": 6}


# -----------------------------
# Helpers: normalization & parsing
# -----------------------------
_ws = re.compile(r"\s+")
_non_alnum = re.compile(r"[^a-z0-9]+")

def norm(s: str) -> str:
    return _ws.sub(" ", s.strip().lower())

def norm_compact(s: str) -> str:
    return _non_alnum.sub("", s.strip().lower())

def parse_float_units(u: Any) -> Optional[float]:
    """
    plan.json uses string units like "1.00" (NU units).
    Keep as float for range filtering.
    """
    if u is None:
        return None
    try:
        return float(str(u))
    except Exception:
        return None

def hhmm_to_minutes(hhmm: str) -> int:
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)

def time_obj_to_minutes(t: Dict[str, Any]) -> Optional[int]:
    # schedule section start time/end time: {"h":10,"m":0}
    if not t:
        return None
    h = t.get("h")
    m = t.get("m")
    if h is None or m is None:
        return None
    return int(h) * 60 + int(m)

def overlaps(a0: int, a1: int, b0: int, b1: int) -> bool:
    return max(a0, b0) < min(a1, b1)

def within_window(start: int, end: int, win0: int, win1: int) -> bool:
    return start >= win0 and end <= win1

def any_window_contains(start: int, end: int, windows: List[Tuple[int, int]]) -> bool:
    return any(within_window(start, end, w0, w1) for w0, w1 in windows)

def any_window_overlaps(start: int, end: int, windows: List[Tuple[int, int]]) -> bool:
    return any(overlaps(start, end, w0, w1) for w0, w1 in windows)

def distro_contains(distro_string: Optional[str], wanted: List[str]) -> bool:
    """
    DistroString: each char is a distro category "1"-"7"
    Return True if ALL wanted distros appear somewhere.
    """
    if not wanted:
        return True
    if not distro_string:
        return False
    s = str(distro_string)
    return all(d in s for d in wanted)

def disciplines_contains(disc_string: Optional[str], wanted: List[str]) -> bool:
    # DisciplinesString works the same (characters).
    if not wanted:
        return True
    if not disc_string:
        return False
    s = str(disc_string)
    return all(d in s for d in wanted)


# -----------------------------
# Loading & indexing
# -----------------------------
def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))

def plan_course_key(plan_id: str) -> str:
    """
    plan.json PlanCourse.i is "SUBJECT 210-0" or "AF_AM_ST 101-6", etc.
    Use that as canonical join key.
    """
    return _ws.sub(" ", plan_id.strip())

def sched_course_key(subject: str, catalog: str) -> str:
    """
    schedule course: subject is ScheduleCourse.u, catalog is ScheduleCourse.n
    key like "CONDUCT 326-0"
    """
    return f"{subject.strip()} {catalog.strip()}"

def build_plan_index(plan_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    idx: Dict[str, Dict[str, Any]] = {}
    for c in plan_data.get("courses", []) + plan_data.get("legacy", []):
        pid = c.get("i")
        if not pid:
            continue
        idx[plan_course_key(pid)] = c
    return idx

def iter_schedule_courses(schedule_data: Any) -> Iterable[Dict[str, Any]]:
    # schedule data is array of ScheduleCourse
    if isinstance(schedule_data, list):
        for c in schedule_data:
            if isinstance(c, dict):
                yield c


# -----------------------------
# Extract section info needed for filtering
# -----------------------------
def section_meeting_days(section: Dict[str, Any]) -> List[str]:
    """
    ScheduleSection.m is list of MeetingDaysString|null
    MeetingDaysString: digits where 0=Mon,1=Tue,2=Wed,3=Thu,4=Fri
    Example: "024" -> MWF
    """
    days: List[str] = []
    m_list = section.get("m")  # list
    if not isinstance(m_list, list):
        return days
    for m in m_list:
        if not m:
            continue
        for ch in str(m):
            code = DAY_DIGIT_TO_CODE.get(ch)
            if code:
                days.append(code)
    # unique, stable order
    seen = set()
    out = []
    for d in days:
        if d not in seen:
            out.append(d)
            seen.add(d)
    return out

def section_time_ranges(section: Dict[str, Any]) -> List[Tuple[int, int]]:
    """
    x: start time array, y: end time array; entries can be null
    """
    out: List[Tuple[int, int]] = []
    x_list = section.get("x")
    y_list = section.get("y")
    if not isinstance(x_list, list) or not isinstance(y_list, list):
        return out
    for x, y in zip(x_list, y_list):
        if not x or not y:
            continue
        xs = time_obj_to_minutes(x)
        ys = time_obj_to_minutes(y)
        if xs is None or ys is None:
            continue
        if ys <= xs:
            continue
        out.append((xs, ys))
    return out

def section_instructors(section: Dict[str, Any]) -> List[Dict[str, Any]]:
    r = section.get("r")
    if isinstance(r, list):
        return [x for x in r if isinstance(x, dict)]
    return []

def section_text_blob(section: Dict[str, Any]) -> str:
    parts: List[str] = []
    # topic
    if section.get("k"):
        parts.append(str(section["k"]))
    # descriptions: SectionDescription[] where each element is ["Title","Value"]
    descs = section.get("p")
    if isinstance(descs, list):
        for d in descs:
            if isinstance(d, list) and len(d) >= 2:
                parts.append(str(d[0]))
                parts.append(str(d[1]))
    # instructors: name + bio
    for inst in section_instructors(section):
        if inst.get("n"):
            parts.append(str(inst["n"]))
        if inst.get("b"):
            parts.append(str(inst["b"]))
    return norm(" ".join(parts))


def plan_text_blob(plan_course: Optional[Dict[str, Any]]) -> str:
    if not plan_course:
        return ""
    parts: List[str] = []
    for k in ("n", "d", "p"):  # name, description, prerequisites
        v = plan_course.get(k)
        if v:
            parts.append(str(v))
    # options/offering titles sometimes include keywordy stuff
    o = plan_course.get("o")
    if isinstance(o, list):
        for row in o:
            if isinstance(row, list) and row:
                parts.append(str(row[0]))
    return norm(" ".join(parts))


# -----------------------------
# Hard filter checks
# -----------------------------
def matches_subject(query: Dict[str, Any], subject: str) -> bool:
    subjects = query.get("subjects") or []
    if not subjects:
        return True
    return subject in subjects

def matches_catalog_numbers(query: Dict[str, Any], catalog: str) -> bool:
    nums = query.get("catalog_numbers") or []
    if not nums:
        return True
    # catalog like "326-0" -> match "326" too
    base = str(catalog).split("-")[0]
    return any(str(n) == base or str(n) == str(catalog) for n in nums)

def matches_school(query: Dict[str, Any], school: Optional[str]) -> bool:
    schools = query.get("schools") or []
    if not schools:
        return True
    return (school or "") in schools

def matches_units_range(query: Dict[str, Any], units: Optional[float]) -> bool:
    ranges = query.get("units_range") or []
    if not ranges:
        return True
    if units is None:
        return False
    for r in ranges:
        if not r or len(r) != 2:
            continue
        lo, hi = float(r[0]), float(r[1])
        if units >= lo and units <= hi:
            return True
    return False

def matches_repeatable(query: Dict[str, Any], repeatable: Optional[bool]) -> bool:
    want = query.get("repeatable")
    if want is None:
        return True
    # if we don't know, treat as fail for strict
    if repeatable is None:
        return False
    return bool(repeatable) == bool(want)

def matches_placeholder(query: Dict[str, Any], is_placeholder: Optional[bool]) -> bool:
    # default: exclude placeholders
    exclude_placeholder = query.get("exclude_placeholder", True)
    if not exclude_placeholder:
        return True
    return not bool(is_placeholder)

def section_matches_days(query: Dict[str, Any], days: List[str]) -> bool:
    inc = set(query.get("days_include") or [])
    exc = set(query.get("days_exclude") or [])
    dayset = set(days)

    if inc and not inc.issubset(dayset):
        return False
    if exc and (exc & dayset):
        return False
    return True

def section_matches_time(query: Dict[str, Any], ranges: List[Tuple[int, int]]) -> bool:
    inc_raw = query.get("time_include") or []
    exc_raw = query.get("time_exclude") or []

    inc = [(hhmm_to_minutes(a), hhmm_to_minutes(b)) for a, b in inc_raw]
    exc = [(hhmm_to_minutes(a), hhmm_to_minutes(b)) for a, b in exc_raw]

    # If no meeting times, don't pass schedule filters (conservative)
    if (inc or exc) and not ranges:
        return False

    # include: ALL meetings must be contained in at least one include window
    if inc:
        for (s, e) in ranges:
            if not any_window_contains(s, e, inc):
                return False

    # exclude: NO meeting may overlap excluded windows
    if exc:
        for (s, e) in ranges:
            if any_window_overlaps(s, e, exc):
                return False

    return True

def section_matches_components(query: Dict[str, Any], component: Optional[str]) -> bool:
    inc = set(query.get("components") or [])
    exc = set(query.get("components_exclude") or [])
    comp = (component or "").strip()
    if inc and comp not in inc:
        return False
    if exc and comp in exc:
        return False
    return True

def section_matches_instructors(query: Dict[str, Any], instructors: List[Dict[str, Any]]) -> bool:
    inc = [norm(x) for x in (query.get("instructors_include") or [])]
    exc = [norm(x) for x in (query.get("instructors_exclude") or [])]
    if not inc and not exc:
        return True

    names = [norm(i.get("n", "")) for i in instructors]

    if inc:
        # require at least one included instructor to appear
        if not any(any(inc_name in nm for nm in names) for inc_name in inc):
            return False
    if exc:
        if any(any(exc_name in nm for nm in names) for exc_name in exc):
            return False
    return True


# -----------------------------
# Scoring
# -----------------------------
def keyword_score(text: str, include: List[str], exclude: List[str]) -> Tuple[float, List[str], List[str]]:
    """
    Very simple lexical scoring:
    - each include keyword matched -> +1 (multi-word allowed; substring match on normalized text)
    - each exclude keyword matched -> -1.5
    Returns (score, matched_includes, matched_excludes)
    """
    if not text:
        return 0.0, [], []
    t = " " + text + " "  # padding helps naive substring a bit

    matched_inc = []
    for kw in include:
        k = norm(str(kw))
        if k and k in t:
            matched_inc.append(kw)

    matched_exc = []
    for kw in exclude:
        k = norm(str(kw))
        if k and k in t:
            matched_exc.append(kw)

    score = 1.0 * len(matched_inc) - 1.5 * len(matched_exc)
    return score, matched_inc, matched_exc

def default_weights(priority: Dict[str, Any]) -> Dict[str, float]:
    """
    Let your LLM set weights, but keep sane defaults.
    You can rename keys later; this is internal.
    """
    w = {
        "keyword": 1.0,
        "subject": 0.3,
        "distro": 0.4,
        "discipline": 0.25,
        "schedule": 0.35,
        "term_signal": 0.15,
    }
    user = (priority or {}).get("weights") or {}
    for k, v in user.items():
        try:
            w[k] = float(v)
        except Exception:
            pass
    return w

def compute_score(
    query: Dict[str, Any],
    subject: str,
    catalog: str,
    plan_course: Optional[Dict[str, Any]],
    sections: List[Dict[str, Any]],
) -> Tuple[float, Dict[str, Any]]:
    """
    Score course-level candidate by:
    - keywords over (plan + top sections)
    - matching signals (subject/distro/discipline)
    - schedule feasibility signal (has at least one section that passes schedule filters)
    """
    inc_kws = query.get("include_keywords") or []
    exc_kws = query.get("exclude_keywords") or []

    plan_blob = plan_text_blob(plan_course)
    # take up to 3 sections' text (best effort)
    sec_blobs = [section_text_blob(s) for s in sections[:3]]
    text = norm(" ".join([plan_blob] + sec_blobs))

    kw_s, kw_inc, kw_exc = keyword_score(text, inc_kws, exc_kws)

    # subject match bonus (already filtered, but helps ranking when subjects empty)
    subj_bonus = 0.0
    if query.get("subjects"):
        subj_bonus = 1.0 if subject in query["subjects"] else 0.0

    # distro / discipline signals (course-level OR section-level)
    want_d = query.get("distros") or []
    want_f = query.get("disciplines") or []

    plan_d = plan_course.get("s") if plan_course else None
    plan_f = plan_course.get("f") if plan_course else None

    sec_d_any = any(distro_contains(s.get("o"), want_d) for s in sections) if want_d else True
    sec_f_any = any(disciplines_contains(s.get("f"), want_f) for s in sections) if want_f else True

    distro_sig = 0.0
    if want_d:
        distro_sig = 1.0 if (distro_contains(plan_d, want_d) or sec_d_any) else 0.0

    disc_sig = 0.0
    if want_f:
        disc_sig = 1.0 if (disciplines_contains(plan_f, want_f) or sec_f_any) else 0.0

    # schedule signal: at least one section passes schedule constraints
    schedule_ok = False
    for s in sections:
        if (
            section_matches_days(query, section_meeting_days(s))
            and section_matches_time(query, section_time_ranges(s))
            and section_matches_components(query, s.get("c"))
            and section_matches_instructors(query, section_instructors(s))
        ):
            schedule_ok = True
            break
    schedule_sig = 1.0 if schedule_ok else 0.0

    # term/offered_in_terms signal: plan.t is list of term ids ("4800"...)
    term_sig = 0.0
    offered = set(query.get("offered_in_terms") or [])
    if offered and plan_course and isinstance(plan_course.get("t"), list):
        term_sig = 1.0 if offered.intersection(set(plan_course["t"])) else 0.0

    weights = default_weights(query.get("priority") or {})
    score = (
        weights.get("keyword", 1.0) * kw_s
        + weights.get("subject", 0.0) * subj_bonus
        + weights.get("distro", 0.0) * distro_sig
        + weights.get("discipline", 0.0) * disc_sig
        + weights.get("schedule", 0.0) * schedule_sig
        + weights.get("term_signal", 0.0) * term_sig
    )

    debug = {
        "kw_score": kw_s,
        "kw_includes": kw_inc,
        "kw_excludes": kw_exc,
        "subject_bonus": subj_bonus,
        "distro_sig": distro_sig,
        "discipline_sig": disc_sig,
        "schedule_sig": schedule_sig,
        "term_sig": term_sig,
        "weights": weights,
    }
    return score, debug


# -----------------------------
# Main shortlist function
# -----------------------------
def shortlist_classes(
    query_obj: Any,
    plan_path: str | Path = None,
    schedule_path: str | Path = None,
    limit: int = 20,
    per_subject_cap: int = 6,
) -> Dict[str, Any]:
    """
    Returns:
      {
        "query": <query dict>,
        "shortlist": [ {course_card}, ... ],
      }

    Course card includes enough text + schedule snippets for downstream LLM.
    """
    
    # Default paths if not provided
    if plan_path is None:
        plan_path = Path(__file__).parent.parent.parent / "data" / "plan.json"
    if schedule_path is None:
        schedule_path = Path(__file__).parent.parent.parent / "data" / "5000.json"

    # Allow passing StructuredQuery dataclass or plain dict
    if hasattr(query_obj, "__dict__") and not isinstance(query_obj, dict):
        # StructuredQuery / dataclass
        q = asdict(query_obj)
        # priority is nested dataclass; ensure dict-ish
        if isinstance(q.get("priority"), dict) is False and getattr(query_obj, "priority", None) is not None:
            q["priority"] = asdict(query_obj.priority)
    else:
        q = dict(query_obj or {})

    try:
        plan_data = load_json(plan_path)
        print(f"[SHORTLIST] Loaded plan.json: {len(plan_data.get('courses', []))} courses, {len(plan_data.get('legacy', []))} legacy")
    except Exception as e:
        print(f"[SHORTLIST ERROR] Failed to load plan.json: {e}")
        return {
            "query": q,
            "shortlist": [],
            "stats": {"error": f"Failed to load plan.json: {e}"},
        }
    
    try:
        sched_data = load_json(schedule_path)
        sched_count = len(list(iter_schedule_courses(sched_data))) if isinstance(sched_data, list) else 0
        print(f"[SHORTLIST] Loaded schedule data: {sched_count} courses")
    except Exception as e:
        print(f"[SHORTLIST ERROR] Failed to load schedule data: {e}")
        return {
            "query": q,
            "shortlist": [],
            "stats": {"error": f"Failed to load schedule data: {e}"},
        }

    plan_idx = build_plan_index(plan_data)
    print(f"[SHORTLIST] Built plan index with {len(plan_idx)} courses")

    candidates: List[Tuple[float, str, Dict[str, Any]]] = []
    
    print(f"[SHORTLIST] Starting to process schedule courses with query: subjects={q.get('subjects')}, keywords={q.get('include_keywords')}")

    processed_count = 0
    for sc in iter_schedule_courses(sched_data):
        processed_count += 1
        if processed_count % 1000 == 0:
            print(f"[SHORTLIST] Processed {processed_count} courses, found {len(candidates)} candidates so far")
        subject = sc.get("u") or ""
        catalog = sc.get("n") or ""
        school = sc.get("c")  # schedule-level school
        title = sc.get("t") or ""
        sections = sc.get("s") if isinstance(sc.get("s"), list) else []

        # Join plan metadata (optional)
        key = sched_course_key(subject, catalog)
        pc = plan_idx.get(key)

        # --------- Course-level hard filters (from plan+schedule) ----------
        if not matches_subject(q, subject):
            continue
        if not matches_catalog_numbers(q, catalog):
            continue
        if not matches_school(q, school or (pc.get("c") if pc else None)):
            continue

        units = parse_float_units(pc.get("u")) if pc else None
        if not matches_units_range(q, units):
            continue

        repeatable = pc.get("r") if pc else None
        if not matches_repeatable(q, repeatable):
            continue

        is_placeholder = pc.get("l") if pc else None
        if not matches_placeholder(q, is_placeholder):
            continue

        # distro / discipline hard filter: allow either plan or any section to satisfy
        want_d = q.get("distros") or []
        want_f = q.get("disciplines") or []

        if want_d:
            plan_ok = distro_contains(pc.get("s") if pc else None, want_d)
            sec_ok = any(distro_contains(s.get("o"), want_d) for s in sections)
            if not (plan_ok or sec_ok):
                continue

        if want_f:
            plan_ok = disciplines_contains(pc.get("f") if pc else None, want_f)
            sec_ok = any(disciplines_contains(s.get("f"), want_f) for s in sections)
            if not (plan_ok or sec_ok):
                continue

        # Schedule hard filters: require at least one section passes (if any schedule constraints exist)
        schedule_constraints_present = any(
            q.get(k) for k in ("days_include", "days_exclude", "time_include", "time_exclude", "components", "components_exclude", "instructors_include", "instructors_exclude")
        )
        if schedule_constraints_present:
            ok_any = False
            for s in sections:
                if (
                    section_matches_days(q, section_meeting_days(s))
                    and section_matches_time(q, section_time_ranges(s))
                    and section_matches_components(q, s.get("c"))
                    and section_matches_instructors(q, section_instructors(s))
                ):
                    ok_any = True
                    break
            if not ok_any:
                continue

        # --------- Scoring ----------
        score, debug = compute_score(q, subject, catalog, pc, sections)

        # Build a compact card for downstream LLM (ignore capacity/enrollment/rooms)
        card = {
            "key": key,
            "subject": subject,
            "catalog_number": catalog,
            "title": title,
            "school": school or (pc.get("c") if pc else None),
            "units": pc.get("u") if pc else None,
            "repeatable": pc.get("r") if pc else None,
            "distros": pc.get("s") if pc else None,
            "disciplines": pc.get("f") if pc else None,
            "description": pc.get("d") if pc else None,
            "prerequisites": pc.get("p") if pc else None,
            "plan_terms": pc.get("t") if pc else None,
            # pick up to 2 "best" sections that pass schedule constraints if present; else first 2
            "sections": [],
            "retrieval_debug": debug,
        }

        def section_compact(s: Dict[str, Any]) -> Dict[str, Any]:
            return {
                "section_id": s.get("i"),
                "section_number": s.get("n"),
                "component": s.get("c"),
                "instructors": [i.get("n") for i in section_instructors(s) if i.get("n")],
                "meeting_days": section_meeting_days(s),
                "start_end": [
                    (f"{st//60:02d}:{st%60:02d}", f"{en//60:02d}:{en%60:02d}")
                    for (st, en) in section_time_ranges(s)
                ],
                "topic": s.get("k"),
                # keep small subset of descriptions to avoid token bloat
                "descriptions": (s.get("p") or [])[:2] if isinstance(s.get("p"), list) else [],
                "distribution_areas": s.get("o"),
                "foundational_disciplines": s.get("f"),
                # intentionally NOT including: room(l), capacity(a), enrollment requirements(q)
            }

        picked: List[Dict[str, Any]] = []
        if schedule_constraints_present:
            for s in sections:
                if (
                    section_matches_days(q, section_meeting_days(s))
                    and section_matches_time(q, section_time_ranges(s))
                    and section_matches_components(q, s.get("c"))
                    and section_matches_instructors(q, section_instructors(s))
                ):
                    picked.append(section_compact(s))
                if len(picked) >= 2:
                    break
        if not picked:
            for s in sections[:2]:
                picked.append(section_compact(s))

        card["sections"] = picked

        candidates.append((score, key, card))

    # Sort descending by score
    candidates.sort(key=lambda x: x[0], reverse=True)

    # Diversity cap per subject
    out: List[Dict[str, Any]] = []
    per_subj: Dict[str, int] = {}
    for score, key, card in candidates:
        subj = card.get("subject") or ""
        per_subj.setdefault(subj, 0)
        if per_subj[subj] >= per_subject_cap:
            continue
        out.append(card)
        per_subj[subj] += 1
        if len(out) >= limit:
            break

    print(f"[SHORTLIST] Final result: {len(out)} courses returned from {processed_count} processed")
    
    return {
        "query": q,
        "shortlist": out,
        "stats": {
            "returned": len(out),
            "scanned_schedule_courses": processed_count,
            "candidates_found": len(candidates),
        },
    }


# -----------------------------
# CLI for quick testing
# -----------------------------
if __name__ == "__main__":
    import argparse
    import sys
    from pathlib import Path

    # Add parent directory to path for imports
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

    ap = argparse.ArgumentParser()
    ap.add_argument("--query_json", required=True, help="Path to a JSON file containing the StructuredQuery dict")
    ap.add_argument("--plan", help="Path to plan.json (default: app/data/plan.json)")
    ap.add_argument("--schedule", help="Path to schedule term json (default: app/data/5000.json)")
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--per_subject_cap", type=int, default=6)
    args = ap.parse_args()

    from app.services.tools.parse_structured_query import parse_structured_query
    
    # Load query
    query_data = load_json(args.query_json)
    # If it's a StructuredQuery dict, use it; otherwise try to parse if it's a message string
    if isinstance(query_data, dict) and ("original_message" in query_data or "subjects" in query_data or "include_keywords" in query_data):
        query_obj = query_data
    elif isinstance(query_data, str):
        # Assume it's a message string
        query_obj = parse_structured_query(query_data)
    else:
        # Try to use as-is (might already be a dict)
        query_obj = query_data
    
    plan_path = Path(args.plan) if args.plan else None
    schedule_path = Path(args.schedule) if args.schedule else None
    
    result = shortlist_classes(query_obj, plan_path, schedule_path, limit=args.limit, per_subject_cap=args.per_subject_cap)
    print(json.dumps(result, indent=2))
