# Job Search Copilot — Claude Skill

A privacy-first Claude Skill that turns a CV into a compact candidate profile, finds relevant job openings when web search is available, ranks opportunities transparently, and helps tailor honest applications.

**Designed to save tokens:** progressive disclosure keeps the initial Skill instructions concise. Detailed search, scoring, and privacy references load only when needed, so Claude avoids repeatedly carrying the full CV or long instructions in context.

## Features

- Builds an evidence-based candidate profile from a CV.
- Searches public job listings when the current Claude environment has web or browser access.
- Uses generic role, skills, location, and work-mode terms — never the full CV or contact details as search queries.
- Verifies source links and separates confirmed details from unknowns.
- Ranks relevant roles and explains matching skills and gaps.
- Tailors CVs and cover letters without inventing experience.
- Includes an optional offline Python keyword-ranking helper (standard library only).

## Important limitation

A Claude Skill is an instruction package, not a job-board API or web-search connector. Live job discovery depends on tools available in the Claude environment. When browsing is unavailable or a site requires login, provide job links or paste vacancy text.

## Install

**Claude Code:** open this repository as a Claude Code project. The Skill is in `.claude/skills/job-search-copilot/`. To install it for your user account:

```bash
mkdir -p ~/.claude/skills
cp -R .claude/skills/job-search-copilot ~/.claude/skills/
```

**Claude.ai:** zip the `job-search-copilot` Skill folder with `SKILL.md` at the folder root, then use **Customize → Skills → Create skill → Upload a skill**. Enable Code execution and file creation if required by Claude.

## Offline ranking helper

Run the bundled helper with the example profile and jobs:

```bash
python .claude/skills/job-search-copilot/scripts/rank_jobs.py \
  --profile .claude/skills/job-search-copilot/assets/candidate-profile.example.json \
  --jobs examples/jobs.example.json \
  --top 5
```

The score is a keyword heuristic, not semantic matching or a hiring probability. No third-party Python packages are required.

## Privacy and safety

- Do not commit real CVs, candidate profiles, contact details, or application documents to this public repository.
- The Skill does not send CV contents to external services or upload CVs to job boards.
- It never submits applications or contacts employers without explicit approval.
- Verify the original job listing and requirements before applying.

See the [privacy checklist](.claude/skills/job-search-copilot/references/privacy.md) and [scoring guide](.claude/skills/job-search-copilot/references/scoring.md).

## Tests

```bash
python -m unittest discover -s tests -v
```

## License

MIT. See [LICENSE](LICENSE).
