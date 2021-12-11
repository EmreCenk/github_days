

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
        self.repos = None
        self.commits = None


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
        return self.number_of_pages_to_visit > self.current_page_num - 1

    def gathered_enough_repos(self) -> bool:
        return self.commits_gathered > 30 #if there are less than 30 commits, that means we are at the last page
    def update_repos(self,
                     username_to_get_data_for: str,
                     number_of_repos: int = 30) -> List:
        """
        :param number_of_repos: Number of repos to retrieve for user. INPUT -1 TO GET ALL REPOS.
        :return: list of commits
        """
        self.commits_gathered = 0

        if self.data is None:
            self.update_data(username_to_get_data_for) #retreives
        print("a")
        if number_of_repos > 0:
            self.number_of_pages_to_visit = (number_of_repos // 30) + 1 # this is the number of pages we need to visit since every page has 30 commits
            self.current_page_num = 1 #number of pages already visited
            conditional_statement = self.pages_to_visit_is_greater_than_pages_visited
        else:
            conditional_statement = self.gathered_enough_repos

        print("a", self.number_of_pages_to_visit)

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

        self.repos = repos
        return repos

    def update_all_commits(self,
                           username_to_get_data_for: str,
                           repo_number: int = -1,
                           ) -> List:
        """
        :param repo_number: Number of repos to get commits from. By default, it is set to -1 (-1 is used
        to indicate that all repos will be fetched).
        :param username_to_get_data_for: username
        :return:
        """
        self.update_repos(username_to_get_data_for, number_of_repos = repo_number)

        self.commits = []
        for i, repo in enumerate(self.repos):
            # ex: repo["commits_url"] = "https://api.github.com/repos/EmreCenk/smartdraw_watermark_remover/commits{/sha}"
            commit_url = repo["commits_url"].replace("{/sha}", "")
            commit = requests.get(commit_url, auth = self.authentication)
            print(commit_url, commit)
            self.commits.append(commit.json())
            if i >= repo_number:
                break
        return self.commits


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    import pprint
    username = environ["GITHUB_USERNAME"]
    password = environ["GITHUB_PASSWORD"]
    self = github_stat_generator(username, password)
    a = self.update_all_commits("EmreCenk", 1)
    print(len(a))
    for k in a:
        pprint.pprint(k)
        break
