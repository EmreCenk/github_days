

from os import environ
import requests
from requests.auth import HTTPBasicAuth
from typing import Dict, List, Set

class github_stat_generator():

    def __init__(self, github_username: str = "",
                 github_password: str = "",
                 import_data: bool = False):
        """
        :param github_username: if you want to authenticate, this will be your username
        :param github_password: if you want to authenticate, this will be your password
        Note: github only lets 60 requests per hour if you're not authenticated.
        """
        self.authentication = HTTPBasicAuth(github_username, github_password)

        self.data = None
        self.repos = None
        self.commits = None
        self.import_data = import_data

    def get_exported_commit_file_name(self, username: str):
        return username + "_exported_commits.py"

    def login(self, github_username: str,
              github_password: str,
              ):
        """
        :param github_username: username to log in
        :param github_password: password to log in
        return: None

        If you run out of requests, use this function to authenticate requests.
        If this function is ran once, every request after that will be authenticated with these credentials.
        Note: github only lets 60 requests per hour if you're not authenticated.
        """
        self.authentication = HTTPBasicAuth(github_username, github_password)

    def export_data(self, user: str) -> None:
        self.update_data(user)
        i = 0
        while True:
            try:
                file_name = user + "_export_data" + str(i)
                file = open(file_name, "w+")
                file.write(str(self.data))
                file.close()
                break
            except:
                i+=1


    def update_data(self,
                    username_to_get_data_for: str):
        if not (self.data is None):
            return self.request_data(username_to_get_data_for)


    def request_data(self,
                     username_to_get_data_for: str) -> Dict:
        """
        :param username_to_get_data_for: string username
        :return: a dictionary that has the github response
        """
        data = requests.get('https://api.github.com/users/' + username_to_get_data_for, auth=self.authentication)

        json_data = data.json()

        if json_data == {'message': "API rate limit exceeded for 72.53.192.5. (But here's the good news: Authenticated requests get a higher rate limit."
                               " Check out the documentation for more details.)",
                    'documentation_url': 'https://docs.github.com/rest/overview/resources-in-the-rest-api#rate-limiting'}:
            raise RuntimeError(
                               "Unauthenticated users can make up to 60 requests per hour to the github api. "
                               "It appears you have reached your maximum request limit. "
                               "\nPlease authenticate to keep using this service. To do so, input your password and "
                               "username when initializing the github_stat_generator class. \n\n"
                               "Here is the message github gave:\n" + \
                               "'message': 'API rate limit exceeded for 72.53.192.5. (But here's the good news: Authenticated requests get a higher rate limit."
                               " Check out the documentation for more details.)'"
            )

        self.data = json_data
        return json_data


    def pages_to_visit_is_greater_than_pages_visited(self) -> bool:
        """Checks if a is greater than b.
        Yes, I know this looks meaningless. However, to have dynamic conditional statements running in the 'get_commits' functions,
        I need to put the conditional statements inside functions."""
        return self.number_of_pages_to_visit > self.current_page_num - 1

    def gathered_enough_repos(self) -> bool:
        return self.repos_gathered < 30 #if there are less than 30 commits, that means we are at the last page
    def update_repos(self,
                     username_to_get_data_for: str,
                     number_of_repos: int = 30) -> List:
        """
        :param number_of_repos: Number of repos to retrieve for user. INPUT -1 TO GET ALL REPOS.
        :return: list of commits
        """

        if not (self.repos is None): #if cached, don't require again
            return self.repos
        self.repos_gathered = 0
        self.current_page_num = 1  # number of pages already visited

        self.update_data(username_to_get_data_for) #retreives

        if number_of_repos > 0:
            self.number_of_pages_to_visit = (number_of_repos // 30) + 1 # this is the number of pages we need to visit since every page has 30 commits
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
            self.repos_gathered += len(json_response)

        self.repos = repos
        return repos

    def get_all_commits(self, commit_url: str) -> List:
        page_number = 1
        commits = []
        current_commits = [0]*30
        while len(current_commits) == 30:
            current_commits = requests.get(commit_url, auth=self.authentication).json()
            commits.extend(current_commits)
        return commits

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
        if self.commits is not None:
            return self.commits

        self.update_repos(username_to_get_data_for, number_of_repos = repo_number)

        self.commits = []
        for i, repo in enumerate(self.repos):
            # ex: repo["commits_url"] = "https://api.github.com/repos/EmreCenk/smartdraw_watermark_remover/commits{/sha}"

            commit_url = repo["commits_url"].replace("{/sha}", "")
            commits = self.get_all_commits(commit_url)

            self.commits.extend(commits)
            if i >= repo_number:
                break
        return self.commits

    def find_how_many_distinct_days(self,
                                    username_to_get_data_for: str,
                                    repo_number: int = -1,) -> Set:
        self.update_all_commits(username_to_get_data_for,
                                repo_number)
        dates = set()
        print(len(self.commits))
        for commit in self.commits:

            try:
                date = commit["commit"]["author"]["date"]
                # alternate way of accessing date:
                # date = commit["commit"]["committer"]["date"]
                dates.add(date)
            except:
                pass

        return dates

    def export_all_commits(self, username: str):
        self.update_all_commits(username)

        file_name = self.get_exported_commit_file_name(username)
        file = open(file_name, "w+")
        file.write("commits = " + str(self.commits))
        file.close()
    def import_all_commits(self, username: str) -> List[Dict]:
        try:
            imported = __import__(self.get_exported_commit_file_name(username).replace(".py", ""))
            self.commits = imported.commits[:-2]
            return self.commits
        except:
            raise ImportError(f"Username {username} has never exported data in current working directory.")

if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    import pprint
    username = environ["GITHUB_USERNAME"]
    password = environ["GITHUB_PASSWORD"]
    self = github_stat_generator(username, password)
    self.import_all_commits("EmreCenk")
    a = self.find_how_many_distinct_days("EmreCenk")
    print(a)
    print(len(a))
    # print(self.commits)

    # with open("EmreCenk_export_0.py", "r") as file:
    #     a = file.read()

    # self.export_data("EmreCenk")
