# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.5.x   | :white_check_mark: |
| < 0.5   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly:

1. **Do not** open a public issue
2. Email the maintainer directly or use GitLab's confidential issue feature
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Any suggested fixes (optional)

## Security Considerations

This MCP server handles API credentials for Reclaim.ai. Please ensure:

- Never commit your `.env` file or API keys
- Use environment variables for all secrets
- Review the `.gitignore` to ensure sensitive files are excluded
- Rotate your API key if you suspect it has been exposed

## Response Timeline

- Initial response: Within 48 hours
- Status update: Within 7 days
- Fix timeline: Depends on severity (critical: ASAP, high: 2 weeks, medium/low: next release)
