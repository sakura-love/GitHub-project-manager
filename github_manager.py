"""
GitHub API Manager
Handles all GitHub API interactions
"""

from github import Github, GithubException
from typing import Optional, List, Dict, Any
from datetime import datetime

class GitHubManager:
    """Manages GitHub API operations"""
    
    def __init__(self, token: str):
        """Initialize with GitHub token"""
        self.token = token
        self.client = Github(token)
        self.user = None
        
    def authenticate(self) -> bool:
        """Verify authentication with GitHub"""
        try:
            self.user = self.client.get_user()
            self.user.login  # Trigger API call to verify token
            return True
        except GithubException as e:
            print(f"Authentication failed: {e}")
            return False
    
    def get_username(self) -> Optional[str]:
        """Get authenticated user's username"""
        try:
            if not self.user:
                self.user = self.client.get_user()
            return self.user.login
        except GithubException:
            return None

    def get_owned_repositories(self) -> List[Dict[str, Any]]:
        """Get repositories owned by the authenticated user"""
        try:
            if not self.user:
                self.user = self.client.get_user()

            repositories = []
            for repo in self.user.get_repos(type="owner", sort="created", direction="desc"):
                # Extra filtering rule:
                # 1) Must be owned by current authenticated user
                # 2) Must not be a fork repository
                if repo.owner.login != self.user.login:
                    continue
                if repo.fork:
                    continue

                repositories.append({
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "description": repo.description or "",
                    "private": repo.private,
                    "html_url": repo.html_url,
                    "clone_url": repo.clone_url,
                    "ssh_url": repo.ssh_url,
                    "fork": repo.fork,
                    "created_at": repo.created_at.isoformat() if repo.created_at else None,
                    "updated_at": repo.updated_at.isoformat() if repo.updated_at else None
                })

            return repositories
        except GithubException as e:
            print(f"Error getting owned repositories: {e}")
            return []
    
    def create_repository(self, repo_name: str, description: str = "", 
                         private: bool = False, auto_init: bool = False) -> Optional[Dict[str, Any]]:
        """Create a new repository on GitHub"""
        try:
            if not self.user:
                self.user = self.client.get_user()
            
            repo = self.user.create_repo(
                name=repo_name,
                description=description,
                private=private,
                auto_init=auto_init
            )
            
            return {
                "name": repo.name,
                "url": repo.clone_url,
                "html_url": repo.html_url,
                "ssh_url": repo.ssh_url,
                "full_name": repo.full_name
            }
        except GithubException as e:
            print(f"Error creating repository: {e}")
            return None
    
    def repository_exists(self, repo_name: str) -> bool:
        """Check if repository already exists"""
        try:
            if not self.user:
                self.user = self.client.get_user()
            
            self.user.get_repo(repo_name)
            return True
        except GithubException:
            return False
    
    def get_repository(self, repo_name: str):
        """Get repository object"""
        try:
            if not self.user:
                self.user = self.client.get_user()
            
            return self.user.get_repo(repo_name)
        except GithubException as e:
            print(f"Error getting repository: {e}")
            return None

    def get_repository_files(self, repo_name: str) -> List[str]:
        """Get all file paths from a repository"""
        try:
            repo = self.get_repository(repo_name)
            if not repo:
                return []

            file_paths = []
            stack = repo.get_contents("")

            while stack:
                item = stack.pop(0)
                if item.type == "dir":
                    stack.extend(repo.get_contents(item.path))
                elif item.type == "file":
                    file_paths.append(item.path)

            return sorted(file_paths, key=str.lower)
        except GithubException as e:
            print(f"Error getting repository files: {e}")
            return []

    def get_repository_file_content(self, repo_name: str, file_path: str) -> Optional[str]:
        """Get file content from a repository"""
        try:
            repo = self.get_repository(repo_name)
            if not repo:
                return None

            content_file = repo.get_contents(file_path)
            if isinstance(content_file, list):
                return None

            decoded = content_file.decoded_content
            return decoded.decode("utf-8")
        except UnicodeDecodeError:
            return "[Binary or non-UTF8 file, preview not supported]"
        except GithubException as e:
            print(f"Error getting repository file content: {e}")
            return None
    
    def create_release(self, repo_name: str, tag_name: str,
                      release_name: str = "", body: str = "",
                      draft: bool = False, prerelease: bool = False,
                      asset_paths: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Create a new release"""
        try:
            repo = self.get_repository(repo_name)
            if not repo:
                return None
            
            release = repo.create_git_release(
                tag=tag_name,
                name=release_name or tag_name,
                message=body,
                draft=draft,
                prerelease=prerelease
            )

            uploaded_assets = []
            failed_assets = []
            for asset_path in (asset_paths or []):
                try:
                    asset = release.upload_asset(asset_path)
                    uploaded_assets.append({
                        "name": asset.name,
                        "url": asset.browser_download_url
                    })
                except GithubException as asset_error:
                    failed_assets.append({
                        "path": asset_path,
                        "error": str(asset_error)
                    })
            
            return {
                "tag": release.tag_name,
                "name": release.title,
                "url": release.html_url,
                "created_at": release.created_at.isoformat(),
                "uploaded_assets": uploaded_assets,
                "failed_assets": failed_assets
            }
        except GithubException as e:
            print(f"Error creating release: {e}")
            return None
    
    def get_releases(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get all releases for a repository"""
        try:
            repo = self.get_repository(repo_name)
            if not repo:
                return []
            
            releases = []
            for release in repo.get_releases():
                releases.append({
                    "tag": release.tag_name,
                    "name": release.title,
                    "body": release.body,
                    "url": release.html_url,
                    "created_at": release.created_at.isoformat(),
                    "draft": release.draft,
                    "prerelease": release.prerelease
                })
            
            return releases
        except GithubException as e:
            print(f"Error getting releases: {e}")
            return []
    
    def delete_repository(self, repo_name: str) -> bool:
        """Delete a repository"""
        try:
            repo = self.get_repository(repo_name)
            if repo:
                repo.delete()
                return True
            return False
        except GithubException as e:
            print(f"Error deleting repository: {e}")
            return False
