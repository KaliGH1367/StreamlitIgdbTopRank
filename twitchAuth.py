import requests
import pickle
import pathlib
import os
from datetime import datetime, timedelta


class Auth:
    def __init__(self, client_id:str, client_secret:str):
        self.AUTH_COOKIE = "auth.pkl"
        self.client_id = client_id
        self.client_secret = client_secret
        self.authenticated = self.__Authenticate()

    def __SetAuthData(self, auth_data:str) -> bool:
        try:
            self.expires_in = auth_data['expires_in']
            self.expiry_date = auth_data['expiry_date']
            self.access_token = auth_data['access_token']
            self.token_type = auth_data['token_type']
            return True
        except:
            self.expires_in = None
            self.expiry_date = None
            self.access_token = None
            self.token_type = None
            return False

    def __CreateAuthCookie(self, auth_data:str):
        expiry_date = datetime.now() + timedelta(seconds=auth_data["expires_in"])
        auth_data['expiry_date'] = expiry_date.strftime("%Y-%m-%d %H:%M:%S")
        with open(self.AUTH_COOKIE, "wb") as file:
            pickle.dump(auth_data, file)
        self.__SetAuthData(auth_data)
    
    def __LoadAuthCookie(self) -> bool:
        if pathlib.Path(self.AUTH_COOKIE).is_file():
            print("Loading authentication cookie")
            try:
                with open(self.AUTH_COOKIE, "rb") as file:
                    now = datetime.now()
                    cookie = pickle.load(file)
                    expiry_date = datetime.strptime(cookie['expiry_date'], "%Y-%m-%d %H:%M:%S")
                if expiry_date > now:
                    print("Cookie is valid")
                    self.__SetAuthData(cookie)
                    return True
                else:
                    print("Cookie has expired")
                    os.remove(self.AUTH_COOKIE)
                    self.__SetAuthData(None)
                    return False
            except:
                print("Cookie is invalid")
                os.remove(self.AUTH_COOKIE)
                self.__SetAuthData(None)
                return False
        else:
            print("Authentication cookie not found")
            self.__SetAuthData(None)
            return False

    def __Authenticate(self) -> bool:
        if self.__LoadAuthCookie():
            return True
        else:
            print("Authenticating")
            resp = requests.post(f"https://id.twitch.tv/oauth2/token?client_id={self.client_id}&client_secret={self.client_secret}&grant_type=client_credentials")
            if resp.status_code == 200:
                self.__CreateAuthCookie(resp.json())
                print("Authentication Successful")
                print(f"Cookie valid until: {self.expiry_date}")
                return True
            else:
                print("Authentication failed")
                return False
