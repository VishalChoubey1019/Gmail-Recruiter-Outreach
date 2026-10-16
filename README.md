# Gmail Recruiter Outreach — Gmail API + OAuth 2.0

Sends one email per recruiter from `recruiters.csv`, with your resume PDF attached. Uses Google's Gmail API, not an SMTP password. Preview is the default; `--send` is required to send.

## Files
- `config.py`: sender name, subject, email body, paths, delay.
- `gmail_sender.py`: OAuth authorization, preview/send logic, duplicate log.
- `recruiters.csv`: email list transcribed from your screenshots; not independently verified.
- `resume.pdf`: add your own resume PDF.
- `credentials.json`: you download this from Google Cloud Console.
- `token.json`: generated after first authorization; sensitive.
- `sent_emails.txt`: created after successful sends.

## 1. Set up Google OAuth (one time)
1. Open https://console.cloud.google.com/ and create/select a project.
2. Go to **APIs & Services → Library**, find **Gmail API**, and enable it.
3. Configure **Google Auth Platform / OAuth consent screen**. If the app is External and in Testing, add your own Google account as a test user.
4. Go to **APIs & Services → Credentials → Create Credentials → OAuth client ID**.
5. Choose **Desktop app**, download the JSON, and save it in this folder as `credentials.json`.

This setup will charge Rs. 2 for setting up autopay, rest assured no more charges from google for sending mails(says on their official page), although there is a rate limiter for 500 messages I guess.

Official guides:
- Gmail API sending: https://developers.google.com/workspace/gmail/api/guides/sending
- Python OAuth quickstart: https://developers.google.com/workspace/gmail/api/quickstart/python

## 2. Install Python dependencies
Python 3.9+ is recommended. In Terminal/PowerShell, from this folder:

Install libraries:
```bash
python3 -m pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## 3. Add your resume and edit the email
- Put your resume PDF in this folder as `resume.pdf` (or edit `RESUME_PATH` in `config.py`).
- Edit `SENDER_NAME`, `EMAIL_SUBJECT`, and `EMAIL_BODY` in `config.py`.
- The addresses are generic inboxes, so the default greeting is “Hi Hiring Team”. Review `recruiters.csv` for transcription mistakes.

## 4. Preview (does not send)
```bash
python3 gmail_sender.py
```

## 5. Authorize and send
```bash
python3 gmail_sender.py --send
```

On first use, the script opens Google's official OAuth consent flow in a browser. Select the correct Gmail account and approve the `gmail.send` permission. Being logged into Chrome can help with account selection, but does not itself authorize the script. Complete any Google security challenges yourself.

The script saves `token.json` and reuses it in future runs when possible. If access is revoked or the token becomes invalid, you may need to authorize again. Do not share or commit `credentials.json` or `token.json`.

## Safety and reliability
- Test with your own email addresses first.
- The script waits 10 seconds between sends and logs successful API responses to `sent_emails.txt`; later runs skip logged addresses.
- A successful API response does not guarantee inbox delivery. Gmail quotas and anti-abuse checks still apply.
- If a connection fails at the exact moment a message is accepted, check Gmail Sent before retrying; local logging cannot guarantee exactly-once delivery.
- Verify addresses before sending. The screenshot list was transcribed, not verified.
- Use for relevant professional outreach and respect requests not to be contacted again.
- Also for emails which are incorrect, mailer-daemon will send you a mail corresponding to it which is very irritating so create a filter and that will delete the mails
