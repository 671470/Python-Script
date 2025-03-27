import os
import sys
import argparse
from github import Github
import subprocess


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
        remove_command = f"rmdir -s -q {local_repo_name}"
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
    args = parser.parse_args()
    
    main(args.gitlab_repo, args.github_repo, args.gitlab_url, args.github_org, args.gitlab_token, args.github_token)
