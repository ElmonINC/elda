# locustfile.py
from locust import HttpUser, task

class WebsiteUser(HttpUser):
    @task
    def search(self):
        self.client.post("/xel/search/", {"query": "test query"})