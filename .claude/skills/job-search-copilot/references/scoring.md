# Scoring guide

## Purpose and limits

The bundled script produces a reproducible keyword-overlap indicator. It is not an assessment of employability, a hiring probability, or a substitute for reading the full vacancy. It does not understand synonyms, context, transferable skills, seniority, or legal work eligibility. Claude should add a qualitative review of those dimensions separately.

## Inputs

A candidate profile JSON file contains:

- `skills`: a list of skills explicitly supported by the CV.
- Optional `target_locations`: locations the candidate is open to.
- Optional `remote_preference`: `any`, `remote_only`, `remote_or_hybrid`, or `onsite_or_hybrid`.

A job list JSON file contains an array of jobs. Each job may have `title`, `company`, `url`, `location`, `work_mode` (`remote`, `hybrid`, or `onsite`), `required_skills`, and `preferred_skills`.

## Formula

- If required and preferred skills are both provided: skill score = 75% required-skill coverage + 25% preferred-skill coverage.
- If only one list is provided: skill score = coverage of that list.
- If neither list is provided: the job is not scored; the output uses `null` and explains that skills data is missing.
- If the profile contains location/work-mode preferences, a location score is calculated. When both are specified, both must be compatible; the weaker/unknown component controls the location score. Unknown information is neutral (50%), not assumed to be a match. The combined score is 85% skill score + 15% location score. If no location/work-mode preference exists, the skill score is used as the overall score.

Coverage is based on normalized exact phrase matching. Punctuation and case differences are normalized, but synonyms are not inferred. Missing required skills are listed separately.

## Interpretation

- 80–100: strong keyword alignment; still verify the role's actual requirements.
- 60–79: plausible match; inspect missing requirements and transferable experience.
- Below 60: weaker keyword match; may still be relevant where skills are transferable.

No score guarantees an interview. A vacancy with missing or unclear fields should be marked `insufficient data`, not treated as a zero-quality employer.
