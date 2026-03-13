# SMTP Setup (Brevo / SendGrid)

## 1) Brevo (recommended)
1. Create account on Brevo and verify sender email/domain.
2. Open SMTP settings and copy:
   - SMTP login email
   - SMTP key/password
3. Update `.env`:
   - `SMTP_HOST=smtp-relay.brevo.com`
   - `SMTP_PORT=587`
   - `SMTP_USER=<brevo_login_email>`
   - `SMTP_PASSWORD=<brevo_smtp_key>`
   - `SMTP_FROM_EMAIL=<verified_sender_email>`
   - `SMTP_USE_TLS=true`
   - `SMTP_USE_SSL=false`
4. Restart app: `python app.py`

## 2) SendGrid (alternative)
1. Create SendGrid account and verify sender.
2. Create API key with Mail Send permission.
3. Update `.env`:
   - `SMTP_HOST=smtp.sendgrid.net`
   - `SMTP_PORT=587`
   - `SMTP_USER=apikey`
   - `SMTP_PASSWORD=<sendgrid_api_key>`
   - `SMTP_FROM_EMAIL=<verified_sender_email>`
   - `SMTP_USE_TLS=true`
   - `SMTP_USE_SSL=false`
4. Restart app: `python app.py`

## Common checks
- `SMTP_FROM_EMAIL` must be verified by provider.
- Keep `SMTP_CONSOLE_FALLBACK=false` in production.
- If mail fails, check server terminal logs for exact SMTP error.
