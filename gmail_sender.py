import argparse, base64, csv, time
from email.message import EmailMessage
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from config import *

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def get_service():
    creds = None
    if Path(TOKEN_FILE).is_file():
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds or not creds.valid:
        if not Path(OAUTH_CLIENT_FILE).is_file():
            raise FileNotFoundError("Missing credentials.json. Follow README.md to create a Google OAuth Desktop app client.")
        flow = InstalledAppFlow.from_client_secrets_file(OAUTH_CLIENT_FILE, SCOPES)
        creds = flow.run_local_server(port=0, open_browser=True)
        Path(TOKEN_FILE).write_text(creds.to_json(), encoding="utf-8")
        try: Path(TOKEN_FILE).chmod(0o600)
        except OSError: pass
    return build("gmail", "v1", credentials=creds, cache_discovery=False)

def recipients():
    with open(RECRUITERS_CSV, newline="", encoding="utf-8-sig") as f:
        seen, out = set(), []
        for row in csv.DictReader(f):
            e = row.get("email", "").strip()
            if e and e.lower() not in seen:
                seen.add(e.lower()); out.append(e)
        return out

def raw_message(to_email):
    msg = EmailMessage()
    msg["To"] = to_email
    msg["Subject"] = EMAIL_SUBJECT
    msg.set_content(EMAIL_BODY.format(sender_name=SENDER_NAME))
    resume = Path(RESUME_PATH)
    if not resume.is_file():
        raise FileNotFoundError(f"Resume not found: {resume.resolve()}")
    with resume.open("rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename=resume.name)
    return base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--send", action="store_true", help="Actually send emails; without this flag, preview only")
    args = p.parse_args()
    all_emails = recipients()
    sent = set(Path(SENT_LOG_FILE).read_text(encoding="utf-8").lower().splitlines()) if Path(SENT_LOG_FILE).exists() else set()
    pending = [e for e in all_emails if e.lower() not in sent]
    print(f"Recipients: {len(all_emails)} | Already logged: {len(all_emails)-len(pending)} | Pending: {len(pending)}")
    if not args.send:
        print("PREVIEW ONLY — no emails sent.")
        print("\n".join(pending))
        print("\nTo send after setup/review: python gmail_sender.py --send")
        return
    if not Path(RESUME_PATH).is_file():
        raise FileNotFoundError(f"Resume not found: {Path(RESUME_PATH).resolve()}")
    service = get_service()
    for i, email in enumerate(pending):
        try:
            service.users().messages().send(userId="me", body={"raw": raw_message(email)}).execute()
            with open(SENT_LOG_FILE, "a", encoding="utf-8") as log: log.write(email.lower() + "\n")
            print(f"[{i+1}/{len(pending)}] Sent to {email}")
        except Exception as exc:
            print(f"[{i+1}/{len(pending)}] FAILED for {email}: {exc}")
        if i < len(pending)-1: time.sleep(EMAIL_DELAY_SECONDS)

if __name__ == "__main__":
    main()
