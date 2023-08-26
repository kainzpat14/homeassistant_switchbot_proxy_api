
import requests

class SwitchbotProxyClient:
    def __init__(self, url, token) -> None:
        """Proxy client class"""
        self.url = url
        self.token = token

    def listDevices(self):
        response = requests.get(self.url + "/devices", headers={"x-api-key": self.token})
        if(response.status_code >= 300):
            raise Exception("Error "+response.status_code+": " + response.text)
        return response.json()
    
    def status(self, deviceId):
        response = requests.get(self.url + "/"+deviceId, headers={"x-api-key": self.token})
        if(response.status_code >= 300):
            raise Exception("Error "+response.status_code+": " + response.text)
        return response.json()
