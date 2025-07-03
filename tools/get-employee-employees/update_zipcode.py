import os
import requests

API_TOKEN = "866f7ce004c853ce1ff74018fa6ee510bd26546c58292f6d2fb544f6229a01c1"
BASE_URL = "https://tutorial.formatgold.de/api/employees"

def update_zipcode(employee_id, new_zipcode):
    print("🚀 Updating ZIP code...")

    if not API_TOKEN:
        print("❌ No API token found.")
        return

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = {
        "zipcode": new_zipcode
    }

    url = f"{BASE_URL}/{employee_id}"
    print(f"🔗 PATCH {url}")

    try:
        response = requests.patch(url, headers=headers, json=payload)
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return

    if response.status_code in [200, 204]:
        print(f"✅ ZIP code updated to {new_zipcode} for employee ID {employee_id}")
    else:
        print(f"❌ Failed with status {response.status_code}:")
        print(response.text)

if __name__ == "__main__":
    print("🧑 Enter the employee ID you want to update:")
    employee_id = input("➡️ ID: ").strip()

    print("🏠 Enter the new ZIP code:")
    new_zipcode = input("➡️ ZIP Code: ").strip()

    if employee_id.isdigit() and new_zipcode:
        update_zipcode(employee_id=int(employee_id), new_zipcode=new_zipcode)
    else:
        print("❌ Invalid input. Please enter numeric ID and a non-empty ZIP code.")
