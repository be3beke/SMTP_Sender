from flask import Flask, render_template, request, jsonify
import smtplib
import re
import time
import os
from datetime import datetime

app = Flask(__name__)

# -----------------------
# SMTP Configuration - change these
# -----------------------
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 2525
SMTP_USERNAME = os.environ.get("SMTP_USERNAME")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
USE_SSL = False  # set True if SSL required
# -----------------------

# Replace all [D=>...] tokens with the UTC formatted date
def replace_date_token(raw_email):
    pattern = re.compile(r'\[D=>(.*?)\]')
    def repl(m):
        fmt = m.group(1)
        try:
            return datetime.utcnow().strftime(fmt)
        except Exception:
            return m.group(0)
    return pattern.sub(repl, raw_email)

# Replace placeholders like [KEY] with their values
def replace_variables(raw_email, variables):
    if not variables:
        return raw_email

    for raw_key, value in variables.items():
        if raw_key is None:
            continue
        key = str(raw_key).strip().lstrip('[').rstrip(']').strip()
        if not key:
            continue
        pattern = re.compile(r'\[' + re.escape(key) + r'\]', flags=re.IGNORECASE)
        raw_email = pattern.sub(str(value), raw_email)

    return raw_email

# Replace To: [*to] and Cc: [*to] with actual recipient emails
def replace_to_cc(raw_email, recipients):
    if not recipients:
        return raw_email
    recipients_str = ", ".join(recipients)
    raw_email = re.sub(r'To:\s*\[\*to\]', f'To: {recipients_str}', raw_email, flags=re.IGNORECASE)
    raw_email = re.sub(r'Cc:\s*\[\*to\]', f'Cc: {recipients_str}', raw_email, flags=re.IGNORECASE)
    return raw_email

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/send-email', methods=['POST'])
def send_email():
    try:
        data = request.json or {}
        raw_email = data.get("raw_email", "")
        to_emails = data.get("to_emails", [])
        if isinstance(to_emails, str):
            to_emails = [e.strip() for e in re.split(r'[,\n\r]+', to_emails) if e.strip()]

        variables = data.get("variables", {}) or {}
        batch_size = int(data.get("batch_size", 1) or 1)
        delay_ms = int(data.get("delay_ms", 0) or 0)

        if not raw_email:
            return jsonify({"success": False, "message": "Missing raw email content."}), 400
        if not to_emails:
            return jsonify({"success": False, "message": "Missing recipient list."}), 400

        results = []

        # Connect once
        if USE_SSL:
            server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=30)
        else:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)
            server.ehlo()
            try:
                server.starttls()
                server.ehlo()
            except Exception:
                pass

        if SMTP_USERNAME and SMTP_PASSWORD:
            server.login(SMTP_USERNAME, SMTP_PASSWORD)

        # Send in batches
        for i in range(0, len(to_emails), batch_size):
            batch = to_emails[i:i+batch_size]
            for to_email in batch:
                prepared = raw_email
                prepared = replace_date_token(prepared)
                prepared = replace_variables(prepared, variables)
                prepared = replace_to_cc(prepared, batch)  # replace To: and Cc: placeholders

                from_email = SMTP_USERNAME
                for line in prepared.splitlines():
                    if line.lower().startswith("from:"):
                        m = re.search(r'<([^>]+)>', line)
                        if m:
                            from_email = m.group(1)
                        else:
                            m2 = re.search(r'From:\s*([^,\s]+@[^,\s]+)', line, flags=re.IGNORECASE)
                            if m2:
                                from_email = m2.group(1)
                        break

                try:
                    server.sendmail(from_email, to_email, prepared.encode('utf-8'))
                    results.append({"email": to_email, "status": "sent"})
                except Exception as e:
                    results.append({"email": to_email, "status": f"error: {str(e)}"})

            if delay_ms > 0 and i + batch_size < len(to_emails):
                time.sleep(delay_ms / 1000.0)

        server.quit()
        return jsonify({"success": True, "results": results})

    except Exception as e:
        return jsonify({"success": False, "message": f"{str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5008))
    app.run(host="0.0.0.0", port=port)
