

from os import environ
import requests
from requests.auth import HTTPBasicAuth
from typing import Dict, List

class github_stat_generator():


    def __init__(self, github_username: str = "",
                 github_password: str = ""):
        """
        :param github_username: if you want to authenticate, this will be your username
        :param github_password: if you want to authenticate, this will be your password
        Note: github only lets 60 requests per hour if you're not authenticated.
        """
        self.authentication = HTTPBasicAuth(github_username, github_password)
        self.data = None


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
    def update_data(self,
                    username_to_get_data_for: str) -> Dict:
        """
        :param username_to_get_data_for: string username
        :return: a dictionary that has the github response
        """
        data = requests.get('https://api.github.com/users/' + username_to_get_data_for)
        json_data = data.json()
        self.data = json_data
        return json_data


    def pages_to_visit_is_greater_than_pages_visited(self) -> bool:
        """Checks if a is greater than b.
        Yes, I know this looks meaningless. However, to have dynamic conditional statements running in the 'get_commits' functions,
        I need to put the conditional statements inside functions."""
        return self.number_of_pages_to_visit > self.current_page_num

    def gathered_enough_repos(self) -> bool:
        return self.commits_gathered > 30 #if there are less than 30 commits, that means we are at the last page
    def get_repos(self,
                    username_to_get_data_for: str,
                    number_of_repos: int = 30) -> List:
        """
        :param number_of_repos: Number of repos to retrieve for user. INPUT -1 TO GET ALL REPOS.
        :return: list of commits
        """
        self.commits_gathered = 0

        if self.data is None:
            self.update_data(username_to_get_data_for) #retreives

        if number_of_repos > 0:
            self.number_of_pages_to_visit = number_of_repos // 30 + 1 # this is the number of pages we need to visit since every page has 30 commits
            self.current_page_num = 1 #number of pages already visited
            conditional_statement = self.pages_to_visit_is_greater_than_pages_visited
        else:
            conditional_statement = self.gathered_enough_repos


        url = self.data['repos_url']
        repos = []

        while conditional_statement():

            response = requests.get(url,
                                    params = {"page": self.current_page_num},
                                    auth = self.authentication)

            json_response = response.json()
            repos.extend(json_response)
            self.current_page_num += 1  # moving onto the next page
            self.commits_gathered += len(json_response)
        return repos
    # def login(self, username: str, password: str):


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    import pprint
    username = environ["GITHUB_USERNAME"]
    password = environ["GITHUB_PASSWORD"]
    self = github_stat_generator(username, password)
    testing = self.get_repos("EmreCenk", 80)
    pprint.pprint(testing)
    print(len(testing))