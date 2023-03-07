import requests
import json

# Bitcoin node client
class Bitcoin(object):
    def __init__(self, endpoint, rid="api-server"):
        self.endpoint = endpoint
        self.rid = rid

    def dead_response(self, message="Invalid Request"):
        return {"error": {
            "code": 404, "message": message
        }, "id": self.rid}

    def response(self, result, error=None):
        return {
            "error": error, "result": result,
            "id": self.rid
        }

    def make_request(self, method, params=[]):
        headers = {"content-type": "text/plain;"}
        data = json.dumps({
            "method": method, "params": params,
            "id": self.rid
        })

        try:
            return requests.post(
                self.endpoint, headers=headers, data=data
            ).json()

        except Exception as e:
            print(e)
            return self.dead_response()
