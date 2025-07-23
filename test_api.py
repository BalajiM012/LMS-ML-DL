import requests

BASE_URL = "http://127.0.0.1:5000"

def test_signup():
    url = f"{BASE_URL}/api/student_login/signup"
    data = {
        "fullname": "Test User",
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "TestPass123"
    }
    response = requests.post(url, json=data)
    print("Signup response:", response.status_code, response.json())

def test_login():
    url = f"{BASE_URL}/api/student_login/login"
    data = {
        "username": "testuser",
        "password": "TestPass123"
    }
    response = requests.post(url, json=data)
    print("Login response:", response.status_code, response.json())
    if response.status_code == 200:
        token = response.json().get("access_token")
        return token
    return None

def test_get_books():
    token = test_login()
    url = f"{BASE_URL}/api/book_management/books"
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = requests.get(url, headers=headers)
    print("Get books response:", response.status_code, response.json())

def test_logout():
    token = test_login()
    url = f"{BASE_URL}/api/student_login/logout"
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    response = requests.post(url, headers=headers)
    print("Logout response:", response.status_code, response.json())

if __name__ == "__main__":
    test_signup()
    token = test_login()
    if token:
        test_get_books(token)
        test_logout(token)
