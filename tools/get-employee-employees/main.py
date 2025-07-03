import os
import requests

# ✅ Hardcoded token (replace with your actual token)
API_TOKEN = "d616f4cc09714516ad9d1cb3a449c9020d24438ebc5ecf0a22867de0c566252e"
URL = "https://tutorial.formatgold.de/api/employees?filter[employee_visibility]=all"

def fetch_employees():
    print("🔍 Starting fetch_employees()")

    if not API_TOKEN:
        print("❌ No API token found.")
        return
    else:
        print(f"🔐 Token in use (first 10 chars): {API_TOKEN[:10]}...")

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Accept": "application/json"
    }

    print(f"🌐 Sending request to: {URL}")

    try:
        response = requests.get(URL, headers=headers)
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return

    print(f"📡 Status Code: {response.status_code}")

    if response.status_code != 200:
        print("❌ Error Response:")
        print(response.text[:300])
        return

    try:
        employees = response.json().get("data", [])
    except Exception as e:
        print("❌ Failed to parse JSON response.")
        print(f"Error: {e}")
        return

    if not employees:
        print("⚠️ No employee data returned.")
        return

    print(f"✅ Found {len(employees)} employees:\n")

    for emp in employees:
        name = emp.get("name", "Unknown")
        nationality = emp.get("nationality", "N/A")
        zipcode = emp.get("zipcode", "N/A")
        birthdate = emp.get("birthdate", "N/A")
        print(f"🧑 {name} |{zipcode}| 🌍 {nationality} | 🎂 {birthdate}")
        print("-" * 40)

if __name__ == "__main__":
    fetch_employees()

