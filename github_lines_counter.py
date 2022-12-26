import requests
import os
from git import Repo
import string
import shutil
import json
import threading
from tqdm import tqdm

'''
TODO:
Save the output of the program into a text file
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

    try:
        for repo in data.json():
            repo_name = repo.get("name")
            repo_url = repo.get("html_url")
            repo_url_list.append([repo_name, repo_url])
    except:
        repo_url_list = []

    return repo_url_list


# TTB 64 sec
max_threads = 1
thread_semaphore = threading.Semaphore(max_threads)


def clone_repos(username, root_dir):
    global max_threads
    global thread_semaphore

    repos_data = get_user_repo_data(username)

    if len(repos_data) != 0:
        threads = []
        thread_repos = []  # Contains the url of the repo being downloaded by the thread
        for usr_repo in repos_data:
            repo_dir = root_dir + format_filename(usr_repo[0])

            # Acquire the semaphore to obtain a thread from the pool
            thread_semaphore.acquire()

            # Create a new thread to run the function
            t = threading.Thread(target=clone_repo_helper, args=(usr_repo[1], repo_dir))
            threads.append(t)
            thread_repos.append(usr_repo[1])
            t.start()

        # Wait for all threads to complete
        threads = tqdm(threads)
        for thread_num, t in enumerate(threads):
            threads.set_description(thread_repos[thread_num])
            t.join()

        return True
    else:
        print("Invalid Username")
        return False


def clone_repo_helper(url, repo_dir):
    try:
        Repo.clone_from(url, repo_dir)
    finally:
        # Release the semaphore when the thread is done, so that it can be used by another thread
        thread_semaphore.release()

def count_lines_in_repos(repos_dir, valid_file_extensions):
    num_lines_in_repos = 0

    # Iterate over every subdirectory in the main directory
    for subdir, dirs, files in os.walk(repos_dir):
        # Iterate over every file in the subdirectory
        for file in files:
            has_valid_file_ext = False
            for ext in valid_file_extensions:
                if file.endswith(ext):
                    has_valid_file_ext = True
                    # print("Valid file ext found " + file)

            # Open the file and count the number of lines
            if has_valid_file_ext:
                try:
                    with open(os.path.join(subdir, file), 'r', errors='ignore') as f:
                        lines = f.readlines()
                        num_lines = len(lines)

                    # print(f'Number of lines in {file}: {num_lines}')
                    num_lines_in_repos += num_lines
                except DeprecationWarning:
                    print("Error with file " + file + " in " + subdir)

    return num_lines_in_repos


def main():
    # Check if the valid extensions file exists, if not create it and put the default values into it
    if not os.path.exists("valid_file_exts.json"):
        default_file_extensions = ['.c', '.cpp', '.cs', '.java', '.py', '.rb', '.js', '.php', '.swift', '.go', '.pl',
                                   '.pm',
                                   '.vb', '.f90', '.f95', '.scala', '.jl', '.rs', '.m', '.pas', '.clj', '.coffee',
                                   '.hs',
                                   '.ml', '.erl', '.elm', '.exs', '.lisp', '.rkt']

        with open("valid_file_exts.json", "w") as f:
            json.dump(default_file_extensions, f)
            f.close()
    else:
        with open("valid_file_exts.json", "r") as f:
            valid_file_extensions = json.load(f)
            f.close()

    # This is a temporary directory where the cloned repos will be stored
    root_dir = os.getcwd() + "/cloned/"
    programRunning = True

    print("This program will count how many lines of code are within a GitHub user's repos")
    print("Only files with valid file extensions listed in the valid_file_exts.json will be counted")
    print("Enter exit to exit")

    while programRunning:
        user = input("GitHub Username >> ")
        print("")

        if user.lower() != "exit":
            is_clone_successful = clone_repos(user, root_dir)

            if is_clone_successful:
                num_lines = count_lines_in_repos(root_dir, valid_file_extensions)

                print("\nNum lines in " + user + "'s " + "repos " + str(num_lines))

                print("\nDeleting temp files")
                try:
                    shutil.rmtree(root_dir)
                except FileExistsError:
                    print("There was nothing to remove")
        else:
            programRunning = False
            break


if __name__ == '__main__':
    main()
