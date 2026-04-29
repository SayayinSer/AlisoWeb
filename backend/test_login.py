import httpx

with httpx.Client(base_url="http://127.0.0.1:8002") as client:
    data = {"username": "admin", "password": "admin123"}
    r1 = client.post("/admin/login", data=data, follow_redirects=False)
    print("Login Status:", r1.status_code)
    print("Cookies set:", client.cookies)
    
    r2 = client.get("/admin/", follow_redirects=False)
    print("Admin Status:", r2.status_code)
    print("Request Headers:", r2.request.headers)
    print("Headers:", r2.headers)
