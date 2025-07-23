# locustfile.py
from locust import HttpUser, task, between, events

class WebsiteUser(HttpUser):
    wait_time = between(1, 5) # Simulate a wait time between tasks
    
    def on_start(self):
        """Called when a Locust user starts before any task is scheduled."""
        self.client.post("/accounts/login/", {"username": "testuser", "password": "password"})

    @task(3) # Search for Narration Entries
    def search(self):
        self.client.post("/xel/search/", {"query": "IREDIA"})

    @task(1) # Weighted less than search
    def upload(self):
        with open("test.xlsx", "rb") as f:
            self.client.post("/xel/admin/", {"file": f}, headers={"Content-Type": "multipart/form-data"})