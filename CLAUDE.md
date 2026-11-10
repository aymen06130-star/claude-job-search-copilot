# Repository development notes

- This repository packages a privacy-first Claude Skill under `.claude/skills/job-search-copilot/`.
- Keep `SKILL.md` compact. Put detailed workflows in `references/` so they are read only when needed.
- The `scripts/rank_jobs.py` helper must remain offline and use only the Python standard library.
- Never add real CVs, candidate profiles, personal contact details, API keys, or application documents to the repository.
- Never claim live job search unless a web/browser tool actually searched and verified a source.
- Run `python -m unittest discover -s tests -v` before committing.
