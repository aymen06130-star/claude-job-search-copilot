# Security policy

## Supported version

The latest version on the default branch is supported.

## Reporting

Please do not publish credentials, CVs, personal data, or suspected vulnerabilities in a public issue. Use GitHub private vulnerability reporting if enabled, or contact the maintainers through the repository profile.

## Security design

- The Skill contains instructions and a local helper; it does not include a web API client or external service integration.
- The ranking helper reads user-supplied JSON files locally and uses only the Python standard library.
- The helper has no network code and does not execute job descriptions or CV content.
- Real CVs, personal profiles, contact details, API keys, and application documents must not be committed.
- Claude's web search/browser features, when available, receive only generic job-search terms, not the user's full CV. Users must review any external action before data is shared.
