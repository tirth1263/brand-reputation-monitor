# Security policy

Please report security issues privately through GitHub's **Security → Report a vulnerability** flow instead of opening a public issue.

## Credential handling

- API keys entered in the Streamlit sidebar are held only in the active server session.
- `.env`, Streamlit secrets, SQLite databases, and common secret-bearing files are excluded from Git.
- Production secrets should be configured in the hosting provider's encrypted environment settings.
- Visitors to the public demo should use their own restricted API keys and rotate any key they believe was exposed.

## Data and scraping

Use Bright Data and this application only for websites and data you are authorized to access. Respect applicable terms, laws, robots policies, privacy requirements, and retention obligations.

