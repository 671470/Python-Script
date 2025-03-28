import os
import sys
import argparse
from github import Github
import subprocess
import requests

#GitLab Role to GitHub Role Mapping
ROLE_MAP = {
    50: "admin",  # Owner (GitLab) -> Admin (GitHub)
    40: "maintain",  # Maintainer -> Maintain
    30: "push",  # Developer -> Push
    20: "pull",  # Reporter -> Read (Pull)
    10: "pull",  # Guest -> Read (Pull)
}

# Fetch GitLab Group Members
def get_gitlab_members(gitlab_token, gitlab_group_id):
    gitlab_api_url = f"https://gitlab.com/api/v4/groups/{gitlab_group_id}/members"
    headers = {"PRIVATE-TOKEN": gitlab_token}
    response = requests.get(gitlab_api_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching GitLab members: {response.text}")
        return []

# Add GitLab Users to GitHub Repository
def add_members_to_github(github_token, github_org, github_repo_name, gitlab_token, gitlab_group_id):
    members = get_gitlab_members(gitlab_token, gitlab_group_id)
    gh = Github(github_token)
    org = gh.get_organization(github_org)
    repo = org.get_repo(github_repo_name)
    for member in members:
        username = member["username"]
        access_level = member["access_level"]
        github_role = ROLE_MAP.get(access_level, "pull") # Default to pull if not mapped
        try:
            repo.add_to_collaborators(username, rithub_role)
            print(f"Added {username} to GitHub repo with '{github_role}' access.")
        except Exception as e:
            print(f"Error adding {username}: {e}")


def main(gitlab_repo, github_repo, gitlab_url, github_org, gitlab_token, github_token):
    try:
        #1. Create the github repository
        print(f"Creating GitHub repository: {github_repo}")
        g = Github(github_token)
        org = g.get_organization(github_org)
        repo = org.create_repo(github_repo)
        print(f"GitHub repository created: {repo.clone_url}")
    
        # 2. Mirror the gitlab repository
        print("Cloning GitLab repository...")
        clone_command = f"git clone --mirror https://oauth2:{gitlab_token}@{gitlab_url}/{gitlab_repo}.git"
        subprocess.run(clone_command, shell=True, check=True)
    
        # 3. Push the mirrored repository to github
        print("Pushing to GitHub")
        local_repo_name = gitlab_repo.split("/")[-1] + ".git"
        os.chdir(local_repo_name)
        push_command = f"git push --mirror https://{github_token}@github.com/{github_org}/{github_repo}.git"
        subprocess.run(push_command, shell=True, check=True)
    
        os.chdir("..")
    
        # 4. Cleanup local repo.
        print("Cleaning up local repo.")
        remove_command = f"rm -rf {local_repo_name}"
        subprocess.run(remove_command, shell=True, check=True)
    
        print("Migration siccessful!")
    
    except subprocess.CalledProcessError as e:
        print(f"Error during migration {e}")
    
    except Exception as e:
        print(f"An unexpected error occured: {e}")        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="migrate GitLab repository to GitHub.")
    parser.add_argument("--gitlab-repo", required=True, help="GitLab repository name (e.g. group/project)")
    parser.add_argument("--github-repo", required=True, help="GitHub repository name")
    parser.add_argument("--gitlab-url", required=True, help="GitLab URL")
    parser.add_argument("--github-org", required=True, help="GitHub organization")
    parser.add_argument("--gitlab-token", required=True, help="GitLab token")
    parser.add_argument("--github-token", required=True, help="GitHub token")
    parser.add_argument("--gitlab-group-id", required=True, help="GitLab Group ID")
    args = parser.parse_args()
    
    main(args.gitlab_repo, args.github_repo, args.gitlab_url, args.github_org, args.gitlab_token, args.github_token)
