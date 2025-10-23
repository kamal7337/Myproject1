from locust import HttpUser, between, task
import uuid  

class UserBehavior(HttpUser):
    wait_time = between(1, 3)
    token = None
    created_user_id = None

    def on_start(self):
        """Authenticate and create an initial user."""
        self.authenticate()
        self.create_user()

    def authenticate(self):
        """Obtain JWT token"""
        response = self.client.post("/api/token/", json={
            "username": "admin", 
            "password": "admin123"  
        })

        if response.status_code == 200:
            self.token = response.json().get("access")
            print("[Auth] Token obtained.")
        else:
            print(f"[Auth] Failed. Status code: {response.status_code}")

    def auth_headers(self):
        """Return authorization header"""
        return {"Authorization": f"Bearer {self.token}"}

    def create_user(self):
        """Create a new user and store its ID"""
        if not self.token:
            return

        unique_email = f"{uuid.uuid4().hex[:6]}@example.com"
        payload = {
            "name": "Locust User",
            "email": unique_email,
            "Batch": 1,
            "weight": 70,
            "role": "viewer"
        }

        response = self.client.post("/api/users/", json=payload, headers=self.auth_headers(), catch_response=True)
        if response.status_code == 201:
            self.created_user_id = response.json().get("id")
            print(f"[Create] User created with ID: {self.created_user_id}")
        else:
            response.failure(f"[Create FAIL] {response.status_code} - {response.text}")

    @task(3)
    def get_user_list(self):
        """GET /api/users/"""
        if self.token:
            self.client.get("/api/users/", headers=self.auth_headers(), name="/api/users/")

    @task(2)
    def get_user_detail(self):
        """GET /api/users/{id}/"""
        if self.created_user_id:
            with self.client.get(f"/api/users/{self.created_user_id}/", headers=self.auth_headers(), name="/api/users/:id", catch_response=True) as response:
                if response.status_code == 404:
                    print(f"[DETAIL FAIL] User ID {self.created_user_id} not found.")
                    self.created_user_id = None
                    response.failure(f"[DETAIL GET FAIL] {response.status_code} - {response.text}")

    @task(1)
    def put_update_user(self):
        """PUT /api/users/{id}/"""
        if self.created_user_id:
            payload = {
                "name": "Updated Locust User",
                "email": f"{uuid.uuid4().hex[:6]}@example.com",
                "Batch": 2,
                "weight": 75,
                "role": "manager"
            }
            with self.client.put(f"/api/users/{self.created_user_id}/", json=payload, headers=self.auth_headers(), name="/api/users/:id", catch_response=True) as response:
                if response.status_code == 404:
                    print(f"[UPDATE FAIL] User ID {self.created_user_id} not found.")
                    self.created_user_id = None
                    response.failure(f"[PUT FAIL] {response.status_code} - {response.text}")

    @task(1)
    def delete_user(self):
        """DELETE /api/users/{id}/"""
        if self.created_user_id:
            with self.client.delete(f"/api/users/{self.created_user_id}/", headers=self.auth_headers(), name="/api/users/:id", catch_response=True) as response:
                if response.status_code not in [200, 204]:
                    response.failure(f"[DELETE FAIL] {response.status_code} - {response.text}")
                else:
                    print(f"[DELETE] User {self.created_user_id} deleted.")
                    self.created_user_id = None
                    # Optionally, create a new user right away
                    self.create_user()

    @task(1)
    def post_create_user(self):
        """POST /api/users/ - create additional user"""
        if self.token:
            payload = {
                "name": "Another User",
                "email": f"{uuid.uuid4().hex[:6]}@example.com",
                "Batch": 1,
                "weight": 70,
                "role": "viewer"
            }
            with self.client.post("/api/users/", json=payload, headers=self.auth_headers(), name="/api/users/", catch_response=True) as response:
                if response.status_code != 201:
                    response.failure(f"[POST FAIL] {response.status_code} - {response.text}")
