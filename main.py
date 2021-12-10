

from os import environ
import requests
from requests.auth import HTTPBasicAuth

class github_stat_generator():


    def __init__(self, github_username: str = "",
                 github_password: str = ""):
        """
        :param github_username: if you want to authenticate, this will be your username
        :param github_password: if you want to authenticate, this will be your password
        Note: github only lets 60 requests per hour if you're not authenticated.
        """
        self.authentication = HTTPBasicAuth(github_username, github_password)


    def login(self, github_username: str, github_password: str):
        """
        :param github_username: username to log in
        :param github_password: password to log in
        return: None

        If you run out of requests, use this function to authenticate requests.
        If this function is ran once, every request after that will be authenticated with these credentials.
        Note: github only lets 60 requests per hour if you're not authenticated.
        """
        self.authentication = HTTPBasicAuth(github_username, github_password)


    # def login(self, username: str, password: str):


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    username = environ["GITHUB_USERNAME"]
    password = environ["GITHUB_PASSWORD"]
    self = github_stat_generator(username, password)
