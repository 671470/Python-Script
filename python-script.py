import subprocess
import time
import os
import requests
import shutil
from github import Github

# 🔹 Step 1: Define Variables
GITLAB_REPO_URL = "https://gitlab.com/bachelor-vizrt/unit-testing-class-2023-java.git"

GITHUB_ORG = "Bachelor-Vizrt-Test"  
GITHUB_REPO_NAME = "permission-test"

GITLAB_GROUP_ID = "103838318"

GITHUB_API_URL = "https://api.github.com"
GITLAB_API_URL = f"https://gitlab.com/api/v4/groups/{GITLAB_GROUP_ID}/members"

# 🔹 Step 2: Set Environment Variables for Tokens
os.environ['GITHUB_TOKEN'] = GITHUB_TOKEN
os.environ['GITLAB_TOKEN'] = GITLAB_TOKEN

# GitLab Role to GitHub Role Mapping
ROLE_MAP = {
    50: "admin",     # Owner (GitLab) -> Admin (GitHub)
    40: "maintain",  # Maintainer -> Maintain
    30: "push",      # Developer -> Push
    20: "pull",      # Reporter -> Read (Pull)
    10: "pull",      # Guest -> Read (Pull)
}

# 🔹 Step 3: Fetch GitLab Group Members
def get_gitlab_members():
    headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}
    response = requests.get(GITLAB_API_URL, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Error fetching GitLab members: {response.text}")
        return []

# 🔹 Step 4: Add GitLab Users to GitHub Repository
def add_members_to_github():
    members = get_gitlab_members()
    gh = Github(GITHUB_TOKEN)
    org = gh.get_organization(GITHUB_ORG)
    repo = org.get_repo(GITHUB_REPO_NAME)

    for member in members:
        username = member["username"]
        access_level = member["access_level"]
        github_role = ROLE_MAP.get(access_level, "pull")  # Default to "pull" if not mapped

        try:
            repo.add_to_collaborators(username, github_role)
            print(f"✅ Added {username} to GitHub repo with '{github_role}' access.")
        except Exception as e:
            print(f"❌ Error adding {username}: {e}")

def clone_gitlab_repo():
    repo_dir = "unit-testing-class-2023-java.git"

    # Ensure the directory is deleted before cloning
    if os.path.exists(repo_dir):
        print(f"⚠️ Removing existing directory: {repo_dir}")
        shutil.rmtree(repo_dir)  # Forcefully remove the directory

    subprocess.run("git config --global core.fileMode false", shell=True)

    clone_command = f"git clone --mirror https://oauth2:{GITLAB_TOKEN}@gitlab.com/bachelor-vizrt/unit-testing-class-2023-java.git"
    result = subprocess.run(clone_command, shell=True)

    if result.returncode == 0 and os.path.exists(repo_dir):
        os.chdir(repo_dir)
    else:
        print("❌ Error: Directory 'unit-testing-class-2023-java.git' was not created!")
        exit(1)

# 🔹 Step 6: Create GitHub Repository
def create_github_repo():
    gh = Github(GITHUB_TOKEN)
    org = gh.get_organization(GITHUB_ORG)
    repo = org.create_repo(GITHUB_REPO_NAME, private=True)
    print(f"✅ Created GitHub repo: {repo.full_name}")

# 🔹 Step 7: Push to GitHub
def push_to_github():
    subprocess.run("git remote remove origin", shell=True)
    subprocess.run(f"git remote add origin https://{GITHUB_TOKEN}:x-oauth-basic@github.com/{GITHUB_ORG}/{GITHUB_REPO_NAME}.git", shell=True)
    subprocess.run("git push --mirror origin", shell=True)
    print("✅ Repository migrated successfully to GitHub!")

# 🔹 Step 8: Run GitHub Actions Importer
def run_actions_importer():
    time.sleep(5)  # Sleep before running GitHub Actions Importer

    migrate_command = f"""
    gh actions-importer migrate gitlab --target-url https://github.com/{GITHUB_ORG}/{GITHUB_REPO_NAME} --output-dir tmp/migrate --namespace bachelor-vizrt --project unit-testing-class-2023-java --github-access-token {GITHUB_TOKEN} --gitlab-access-token {GITLAB_TOKEN}
    """
    subprocess.run(migrate_command, shell=True, check=True)
    print("✅ GitHub Actions Importer completed.")

# 🔹 Main Execution
if __name__ == "__main__":
    clone_gitlab_repo()
    create_github_repo()
    push_to_github()
    add_members_to_github()
    run_actions_importer()
