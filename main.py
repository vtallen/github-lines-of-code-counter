import requests
import os
from git import Repo
import string
import shutil
import json

'''
TODO:

Make the program able to do multiple users in one execution
Save the user and number of lines in a json file
'''


def format_filename(s):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in s if c in valid_chars)
    filename = filename.replace(' ', '_')  # I don't like spaces in filenames.
    return filename


def get_user_repo_data(username):
    url = f"https://api.github.com/users/{username}/repos"
    data = requests.get(url)

    repo_url_list = []

    for repo in data.json():
        repo_name = repo.get("name")
        repo_url = repo.get("html_url")
        repo_url_list.append([repo_name, repo_url])

    return repo_url_list


def clone_repos(username, root_dir):
    repos_data = get_user_repo_data(username)

    for usr_repo in repos_data:
        repo_dir = root_dir + format_filename(usr_repo[0])
        Repo.clone_from(usr_repo[1], repo_dir)


def count_lines_in_repos(repos_dir, valid_file_extensions):
    #valid_file_extensions = ['.c', '.cpp', '.cs', '.java', '.py', '.rb', '.js', '.php', '.swift', '.go', '.pl', '.pm', '.vb', '.f90', '.f95', '.scala', '.jl', '.rs', '.m', '.pas', '.clj', '.coffee', '.hs', '.ml', '.erl', '.elm', '.exs', '.lisp', '.rkt']
    num_lines_in_repos = 0

    # Iterate over every subdirectory in the main directory
    for subdir, dirs, files in os.walk(repos_dir):
        # Iterate over every file in the subdirectory
        for file in files:
            has_valid_file_ext = False
            for ext in valid_file_extensions:
                if file.endswith(ext):
                    has_valid_file_ext = True
                    #print("Valid file ext found " + file)

            # Open the file and count the number of lines
            if has_valid_file_ext:
                try:
                    with open(os.path.join(subdir, file), 'r') as f:
                        lines = f.readlines()
                        num_lines = len(lines)

                    print(f'Number of lines in {file}: {num_lines}')
                    num_lines_in_repos += num_lines
                except:
                    print("Error with file " + file + " in " + subdir)

    return num_lines_in_repos


def main():

    if not os.path.exists("valid_file_exts.json"):
        default_file_extensions = ['.c', '.cpp', '.cs', '.java', '.py', '.rb', '.js', '.php', '.swift', '.go', '.pl',
                                 '.pm',
                                 '.vb', '.f90', '.f95', '.scala', '.jl', '.rs', '.m', '.pas', '.clj', '.coffee', '.hs',
                                 '.ml', '.erl', '.elm', '.exs', '.lisp', '.rkt']

        with open("valid_file_exts.json", "w") as f:
            json.dump(default_file_extensions, f)
    else:
        with open("valid_file_exts.json", "r") as f:
            valid_file_extensions = json.load(f)

    root_dir = os.getcwd() + "/cloned/"

    print("This program will count how many lines of code are within a GitHub user's repos")
    print("Only files with valid file extensions listed in the valid_file_exts.json will be counted")
    user = input("GitHub Username >> ")
    print("")

    clone_repos(user, root_dir)
    num_lines = count_lines_in_repos(root_dir, valid_file_extensions)

    print("\nNum lines in " + user + "'s " + "repos " + str(num_lines))

    shutil.rmtree(root_dir)



if __name__ == '__main__':
    main()
