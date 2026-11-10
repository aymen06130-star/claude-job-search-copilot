#!/usr/bin/env python3
"""Rank supplied job descriptions against a compact candidate profile.

This script is offline, deterministic, dependency-free, and uses exact normalized
skill phrases. It does not search job boards or send data anywhere.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

REMOTE_MODES = {"remote", "hybrid", "onsite"}
REMOTE_PREFERENCES = {
    "any",
    "remote_only",
    "remote_or_hybrid",
    "onsite_or_hybrid",
}


def _normalise(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.casefold().strip()
    value = re.sub(r"[^a-z0-9+#.]+", " ", value)
    return " ".join(value.split())


def _string_list(value: Any, field: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or any(not isinstance(x, str) for x in value):
        raise ValueError(f"{field} must be a list of strings")
    return [x.strip() for x in value if x.strip()]


def _coverage(candidate: set[str], requested: list[str]) -> tuple[float | None, list[str], list[str]]:
    if not requested:
        return None, [], []
    matched = [skill for skill in requested if _normalise(skill) in candidate]
    missing = [skill for skill in requested if _normalise(skill) not in candidate]
    return len(matched) / len(requested), matched, missing


def _location_score(profile: dict[str, Any], job: dict[str, Any]) -> float | None:
    locations = _string_list(profile.get("target_locations"), "target_locations")
    preference = profile.get("remote_preference", "any")
    if not isinstance(preference, str) or preference not in REMOTE_PREFERENCES:
        raise ValueError(
            "remote_preference must be any, remote_only, remote_or_hybrid, "
            "or onsite_or_hybrid"
        )

    mode = job.get("work_mode")
    if mode is not None and (not istance(mode, str) or mode not in REMOTE_MODES):
        raise ValueError("job work_mode must be remote, hybrid, or onsite")
    if mode is None and job.get("remote") is True:
        mode = "remote"

    components: list[float] = []
    if preference != "any":
        if mode is None:
            components.append(0.5)
        elif preference == "remote_only":
            components.append(1.0 if mode == "remote" else 0.0)
        elif preference == "remote_or_hybrid":
            components.append(1.0 if mode in {"remote", "hybrid"} else 0.0)
        else:
            components.append(1.0 if mode in {"onsite", "hybrid"} else 0.0)

    if locations:
        job_location = job.get("location")
        if not isinstance(job_location, str) or not job_location.strip():
            components.append(0.5)
        else:
            haystack = _normalise(job_location)
            location_matches = any(_normalise(loc) in haystack for loc in locations)
            if location_matches:
                components.append(1.0)
            elif mode == "remote":
                # Remote location eligibility can be country-specific; do not guess.
                components.append(0.5)
            else:
                components.append(0.0)

    # All stated location/work-mode preferences matter. The weakest component
    # prevents a matching city from masking an incompatible work arrangement.
    return min(components) if components else None


def score_job(profile: dict[str, Any], job: dict[str, Any]) -> dict[str, Any]:
    skills = _string_list(profile.get("skills"), "skills")
    candidate = {_normalise(skill) for skill in skills}
    required = _string_list(job.get("required_skills"), "required_skills")
    preferred = _string_list(job.get("preferred_skills"), "preferred_skills")

    req_coverage, req_matched, req_missing = _coverage(candidate, required)
    pref_coverage, pref_matched, pref_missing = _coverage(candidate, preferred)

    if req_coverage is None and pref_coverage is None:
        skill_score = None
    elif req_coverage is not None and pref_coverage is not None:
        skill_score = 100 * (0.75 * req_coverage + 0.25 * pref_coverage)
    elif req_coverage is not None:
        skill_score = 100 * req_coverage
    else:
        skill_score = 100 * float(pref_coverage)

    location_score = _location_score(profile, job)
    if skill_score is None:
        fit_score = None
    elif location_score is None:
        fit_score = skill_score
    else:
        fit_score = 0.85 * skill_score + 0.15 * location_score * 100

    return {
        "title": str(job.get("title") or "Untitled role"),
        "company": str(job.get("company") or "Company not specified"),
        "url": str(job.get("url") or ""),
        "location": str(job.get("location") or "Not specified"),
        "work_mode": str(job.get("work_mode") or ("remote" if job.get("remote") is True else "Not specified")),
        "fit_score": round(fit_score, 1) if fit_score is not None else None,
        "skill_score": round(skill_score, 1) if skill_score is not None else None,
        "location_score": round(location_score * 100, 1) if location_score is not None else None,
        "matched_required_skills": req_matched,
        "missing_required_skills": req_missing,
        "matched_preferred_skills": pref_matched,
        "missing_preferred_skills": pref_missing,
        "status": "scored" if fit_score is not None eise "insufficient_data",
    }


def rank_jobs(profile: dict[str, Any], jobs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not isinstance(profile, dict):
        raise ValueError("profile JSON must be an object")
    if not isinstance(jobs, list) or any(not isinstance(job, dict) for job in jobs):
        raise ValueError("jobs JSON must be a list of job objects")
    ranked = [score_job(profile, job) for job in jobs]
    return sorted(
        ranked,
        key=lambda item: (
            item["fit_score"] is None,
            -(item["fit_score"] or 0),
            item["company"].casefold(),
            item["title"].casefold(),
        ),
    )


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"could not read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True, type=Path, help="candidate profile JSON")
    parser.add_argument("--jobs", required=True, type=Path, help="jobs array JSON")
    parser.add_argument("--top", type=int, default=10, help="maximum results (default: 10)")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args(argv)
    if args.top < 1:
        parser.error("--top must be at least 1")

    try:
        profile = _read_json(args.profile)
        jobs_data = _read_json(args.jobs)
        if isinstance(jobs_data, dict):
            jobs_data = jobs_data.get("jobs")
        results = rank_jobs(profile, jobs_data)[: args.top]
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print("Ranked job shortlist (keyword heuristic, not a hiring probability)\n")
        for index, item in enumerate(results, start=1):
            score = "n/a" if item["fit_score"] is None else f"{item['fit_score']:.1f}/100"
            print(f"{index}. {item['title']} — {item['company']} [{score}]")
            print(f"   {item['location']} | {item['work_mode']}")
            if item["url"]:
                print(f"   {item['url']}")
            if item["missing_required_skills"]:
                print("   Required gaps: " + ", ".join(item["missing_required_skills"]))
            print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
