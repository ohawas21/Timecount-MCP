from mcp.server.fastmcp import FastMCP
import httpx
import requests

app = FastMCP()

# Your API tokens and endpoints
API_TOKEN = "d616f4cc09714516ad9d1cb3a449c9020d24438ebc5ecf0a22867de0c566252e"
API_TOKEN_2 = "866f7ce004c853ce1ff74018fa6ee510bd26546c58292f6d2fb544f6229a01c1"
URL = "https://tutorial.formatgold.de/api/employees?filter[employee_visibility]=all"
BASE_URL_2 = "https://tutorial.formatgold.de/api/employees"

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
                "birth_date": emp.get("birth_date", "N/A")
            }
            for emp in employees
        ]
    except Exception as e:
        return [{"error": str(e)}]

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

if __name__ == "__main__":
    app.run()
