import os
from dotenv import load_dotenv
from github import Github
from gitlab import Gitlab
import subprocess

load_dotenv()

# Load API tokens and configurations from .env
gitlab_url = os.environ.get("GITLAB_URL")
gitlab_token = os.environ.get("GITLAB_TOKEN")
gitlab_project_id = os.environ.get("GITLAB_PROJECT_ID")
github_token = os.environ.get("GITHUB_TOKEN")
github_repo_name = os.environ.get("GITLAB_PROJECT_ID")
github_org = os.environ.get("GITHUB_ORG")

try:
    #1. Create the github repository
    print(f"Creating GitHub repository: {github_repo_name}")
    g = Github(github_token)
    org = g.get_organization(github_org)
    repo = org.create_repo(github_repo_name)
    print(f"GitHub repository created: {repo.clone_url}")
    
    # 2. Mirror the gitlab repository
    print("Cloning GitLab repository...")
    clone_command = f"git clone --mirror {gitlab_url}/{gitlab_project_id}.git"
    subprocess.run(clone_command, shell=True, check=True)
    
    # 3. Push the mirrored repository to github
    print("Pushing to GitHub")
    local_repo_name = gitlab_project_id.split("/")[-1] + ".git" #get the repo name from the clone command.
    os.chdir(local_repo_name) #Add this line to change the directory.
    push_command = f"git push --mirror https://{github_token}@github.com/{github_org}/{github_repo_name}.git"
    subprocess.run(push_command, shell=True, check=True)
    
    os.chdir("..") #move back up one directory.
    
    # 4. Cleanup local repo.
    print("Cleaning up local repo.")
    remove_command = f"rmdir /s /q {local_repo_name}"
    subprocess.run(remove_command, shell=True, check=True)
    
    print("Migration siccessful!")
    
except subprocess.CalledProcessError as e:
    print(f"Error during migration {e}")
    
except Exception as e:
    print(f"An unexpected error occured: {e}")