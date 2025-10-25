# Security Guidelines

## 🔒 Handling Sensitive Information

This document outlines the security practices for the Poetry Video Generator project to ensure sensitive information is never exposed in the public repository.

### What NOT to Do

❌ **Never commit sensitive information to the repository:**
- API keys, secrets, tokens, passwords
- Private endpoints or URLs
- Personal account information
- Real credentials (even if they're "test" or "staging")

❌ **Never hardcode sensitive values in source code:**
- Avoid putting secrets directly in `.py` files
- Don't use placeholder values that could be mistaken for real credentials

### Environment Variables

All sensitive configuration is handled through environment variables:

1. **Copy the template:**
   ```bash
   cp env_template.txt .env
   ```

2. **Configure your environment variables:**
   Edit `.env` with your actual values (this file is gitignored)

3. **Required variables for full functionality:**
   - `AWS_ACCESS_KEY_ID` - AWS S3 access key
   - `AWS_SECRET_ACCESS_KEY` - AWS S3 secret key
   - `AZURE_OPENAI_API_KEY` - Azure OpenAI GPT API key
   - `AZURE_OPENAI_TTS_API_KEY` - Azure OpenAI TTS API key
   - `PEXELS_API_KEY` - Pexels API key for backgrounds

4. **Optional variables:**
   - `EC2_UPLOAD_URL` - Instagram upload endpoint
   - `EC2_ACCESS_TOKEN` - Instagram access token
   - `EC2_ACCOUNT_ID` - Instagram account ID

### File Structure

```
📁 Project Root
├── 📄 .gitignore           # Excludes sensitive files
├── 📄 env_template.txt     # Template with placeholder values
├── 📄 .env                 # Your local environment (gitignored)
├── 📄 production.env       # ❌ NEVER COMMIT THIS FILE
└── 📄 SECURITY.md         # This security guide
```

### Development Setup

1. **Clone the repository**
2. **Set up environment variables:**
   ```bash
   cp env_template.txt .env
   # Edit .env with your actual credentials
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the application:**
   ```bash
   python main.py
   ```

### Docker Deployment

For Docker deployments, ensure your `.env` file is properly configured before running:

```bash
docker-compose up -d
```

### API Key Acquisition

- **AWS S3:** Create an IAM user with S3 permissions
- **Azure OpenAI:** Use Azure OpenAI Studio to create deployments
- **Pexels:** Get API key from [Pexels Developer](https://www.pexels.com/api/)
- **Instagram:** Use Meta for Developers for Instagram API access

### Security Checklist

Before committing changes:

- [ ] No `.env` files are staged for commit
- [ ] No sensitive values are hardcoded in source code
- [ ] No API keys appear in logs or error messages
- [ ] Environment variables are used for all sensitive configuration
- [ ] `.gitignore` properly excludes sensitive files

### Incident Response

If sensitive information is accidentally committed:

1. **Immediately revoke the exposed credentials**
2. **Remove the sensitive data from git history:**
   ```bash
   git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch .env' --prune-empty --tag-name-filter cat -- --all
   ```
3. **Force push to remove from remote:**
   ```bash
   git push origin --force --all
   ```
4. **Update all affected services with new credentials**

### Contributing

When contributing to this project:

1. Follow the security guidelines above
2. Use environment variables for any new configuration
3. Update `env_template.txt` if adding new required variables
4. Document security considerations in your PR description

### Questions

If you have questions about security practices or need help setting up credentials, please ask a maintainer privately (don't discuss sensitive information in public issues/PRs).
