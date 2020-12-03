import requests
from requests import Response


class SimpleGithubClient:
    def __init__(self, token: str):
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/vnd.github.luke-cage-preview+json,application/vnd.github.v3+json",
            "Authorization": "token {}".format(token),
        }

        self.__params = {"per_page": 100}

    def post(self, url, json) -> Response:
        return requests.post(url=url, json=json, headers=self.headers)

    def put(self, url, json) -> Response:
        return requests.put(url=url, json=json, headers=self.headers)

    def patch(self, url, json) -> Response:
        return requests.patch(url=url, json=json, headers=self.headers)

    def delete(self, url, json=None) -> Response:
        return requests.delete(url=url, json=json, headers=self.headers)

    def get(self, url, params=None):
        if not params:
            params = self.__params

        response = requests.get(url=url, params=params, headers=self.headers)
        json_response = response.json()

        if type(json_response) == list:
            next_link = response.links.get("next", None)

            while next_link:
                response = requests.get(
                    url=next_link["url"], params=params, headers=self.headers
                )
                json_response.extend(response.json())
                next_link = response.links.get("next", None)

        return json_response
