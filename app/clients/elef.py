import requests

class Elef:
    def __init__(self, url):
        self.url = url

    def post_diagnosis(self, diagnosis):
        return requests.post(f"{self.url}/diagnoses", json=diagnosis)
