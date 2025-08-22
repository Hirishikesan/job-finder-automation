import os, smtplib, glob
from email.mime.multipart import MIMEMultipart
from email.mime.text    import MIMEText
from email.mime.base    import MIMEBase
from email              import encoders
from pathlib import Path
import sys

# ---- Read env vars (set in Azure DevOps as secrets/variables) ----
SENDER_EMAIL    = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECEIVER_EMAIL  = os.getenv("RECEIVER_EMAIL")

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")       # Outlook: smtp.office365.com
SMTP_PORT   = int(os.getenv("SMTP_PORT", "587"))

SUBJECT = os.getenv("MAIL_SUBJECT", "Daily Job Report")
BODY    = os.getenv("MAIL_BODY", "Hello,\n\nPlease find attached today's job report.\n\nRegards,\nJob Finder Bot")

missing = [v for v in ["SENDER_EMAIL","SENDER_PASSWORD","RECEIVER_EMAIL"] if not os.getenv(v)]
if missing:
    print(f"Missing required env vars: {missing}")
    sys.exit(1)

# ---- Find latest .xlsx in current working dir ----
candidates = sorted(glob.glob("*.xlsx"), key=os.path.getmtime, reverse=True)
if not candidates:
    print("No .xlsx file found in current directory. Nothing to send.")
    sys.exit(0)
attachment_path = candidates[0]
print(f"Attaching: {attachment_path}")

# ---- Build & send email ----
msg = MIMEMultipart()
msg["From"] = SENDER_EMAIL
msg["To"] = RECEIVER_EMAIL
msg["Subject"] = SUBJECT
msg.attach(MIMEText(BODY, "plain"))

with open(attachment_path, "rb") as f:
    part = MIMEBase("application", "octet-stream")
    part.set_payload(f.read())
encoders.encode_base64(part)
part.add_header("Content-Disposition", f'attachment; filename="{Path(attachment_path).name}"')
msg.attach(part)

server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
server.starttls()
server.login(SENDER_EMAIL, SENDER_PASSWORD)
server.send_message(msg)
server.quit()

print(f"📧 Email sent to {RECEIVER_EMAIL} with attachment: {Path(attachment_path).name}")
