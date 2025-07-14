from mcp.server.fastmcp import FastMCP
import httpx
import requests
import re
import smtplib
from email.message import EmailMessage

app = FastMCP()

# API tokens and base URLs
API_TOKEN = "d616f4cc09714516ad9d1cb3a449c9020d24438ebc5ecf0a22867de0c566252e"
API_TOKEN_2 = "866f7ce004c853ce1ff74018fa6ee510bd26546c58292f6d2fb544f6229a01c1"
URL = "https://tutorial.formatgold.de/api/employees?filter[employee_visibility]=all"
BASE_URL_2 = "https://tutorial.formatgold.de/api/employees"

# ✅ Tax ID validation: 11 digits, first digit not zero
def is_valid_tax_id(tax_id: str) -> bool:
    return bool(re.fullmatch(r"[1-9]\d{10}", tax_id))

# ✅ Email sending function
def send_email(to_email: str, employee_name: str) -> bool:
    msg = EmailMessage()
    msg['Subject'] = "Fehlerhafte Steuer-ID in Ihrem Profil"
    msg['From'] = "noreply@timecount.com"
    msg['To'] = to_email
    msg.set_content(f"""\
Hallo {employee_name},

wir haben festgestellt, dass Ihre hinterlegte Steuer-Identifikationsnummer nicht korrekt ist.
Bitte aktualisieren Sie diese in Ihrem Mitarbeiterprofil.

Viele Grüße,
Ihr Timecount-Team
""")

    try:
        # 🧪 For testing: run a local SMTP server with `python -m smtpd -c DebuggingServer -n localhost:1025`
        with smtplib.SMTP('localhost', 1025) as server:
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Fehler beim Senden der E-Mail an {to_email}: {e}")
        return False
    
def validate_iban(iban: str) -> bool:
    iban = iban.replace(' ', '').upper()
    if not iban.startswith("DE") or len(iban) != 22:
        return False

    rearranged = iban[4:] + iban[:4]

    numeric_iban = ''
    for ch in rearranged:
        if ch.isdigit():
            numeric_iban += ch
        else:
            numeric_iban += str(ord(ch) - 55)  # A=10, B=11, ..., Z=35

    try:
        return int(numeric_iban) % 97 == 1
    except:
        return False


# ✅ Tool: Fetch all employees
@app.tool(name="fetch-employees", description="Fetches a list of all employees.")
def fetch_employees() -> list[dict]:
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json"
    }

    try:
        response = requests.get(URL, headers=headers)
        response.raise_for_status()
        employees = response.json().get("data", [])
        return [
            {
                "name": emp.get("name", "Unknown"),
                "zipcode": emp.get("zipcode", "N/A"),
                "birth_date": emp.get("birth_date", "N/A"),
                "mobile": emp.get("mobile", "N/A"),
                "email": emp.get("email", "N/A"),
                "tax_identification_number": emp.get("tax_identification_number", "N/A"),
                "account_number": emp.get("account_number", "N/A")
            }
            for emp in employees
        ]
    except Exception as e:
        return [{"error": str(e)}]

# ✅ Tool: Update employee ZIP code
@app.tool(name="update-zipcode", description="Update an employee's ZIP code.")
def update_zipcode(employee_id_or_name: str, zip_code: str) -> dict:
    headers = {
        "Authorization": f"Bearer {API_TOKEN_2}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "zipcode": zip_code
    }

    try:
        url = f"{BASE_URL_2}/{employee_id_or_name}"
        response = requests.patch(url, headers=headers, json=payload)
        if response.status_code in [200, 204]:
            return {"success": True, "updated_zipcode": zip_code, "employee_id": employee_id_or_name}
        else:
            return {"success": False, "status_code": response.status_code, "error": response.text}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ✅ Tool: Validate tax IDs and notify if invalid
@app.tool(name="validate-tax-id", description="Validates employee tax IDs and notifies the employee via email if incorrect.")
def validate_tax_ids() -> list[dict]:
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json"
    }

    try:
        response = requests.get(URL, headers=headers)
        response.raise_for_status()
        employees = response.json().get("data", [])

        report = []
        for emp in employees:
            name = emp.get("name", "Unknown")
            email = emp.get("email", "")
            tax_id = emp.get("tax_identification_number", "")

            if not tax_id:
                report.append({"name": name, "status": "Keine Steuer-ID vorhanden"})
                continue

            if is_valid_tax_id(tax_id):
                report.append({"name": name, "status": "Steuer-ID gültig"})
            else:
                email_sent = send_email(email, name) if email else False
                report.append({
                    "name": name,
                    "status": "Steuer-ID ungültig",
                    "email": email,
                    "email_sent": email_sent
                    
                })

        return report
    except Exception as e:
        return [{"error": str(e)}]
    
@app.tool(name="validate-iban", description="Validates the IBAN of employees and notifies them if it is invalid.")
def validate_iban_tool() -> list[dict]:
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json"
    }

    try:
        response = requests.get(URL, headers=headers)
        response.raise_for_status()
        employees = response.json().get("data", [])

        report = []
        for emp in employees:
            name = emp.get("name", "Unknown")
            email = emp.get("email", "")
            iban = emp.get("account_number", "")

            if not iban:
                report.append({"name": name, "status": "Keine IBAN vorhanden"})
                continue

            if validate_iban(iban):
                report.append({"name": name, "status": "IBAN gültig"})
            else:
                email_sent = send_email_iban_invalid(email, name) if email else False
                report.append({
                    "name": name,
                    "status": "IBAN ungültig",
                    "email": email,
                    "email_sent": email_sent
                })

        return report
    except Exception as e:
        return [{"error": str(e)}]


# ✅ Start server
if __name__ == "__main__":
    app.run()
