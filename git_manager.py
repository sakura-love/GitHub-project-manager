"""
Git Operations Manager
Handles local Git repository operations
"""

import os
from pathlib import Path
from git import Repo, GitCommandError
from typing import Optional, List

class GitManager:
    """Manages Git operations"""
    
    @staticmethod
    def init_repository(path: str) -> Optional[Repo]:
        """Initialize a new Git repository"""
        try:
            repo_path = Path(path)
            repo_path.mkdir(parents=True, exist_ok=True)
            repo = Repo.init(repo_path)
            return repo
        except GitCommandError as e:
            print(f"Error initializing repository: {e}")
            return None
    
    @staticmethod
    def clone_repository(url: str, path: str) -> Optional[Repo]:
        """Clone a repository"""
        try:
            repo = Repo.clone_from(url, path)
            return repo
        except GitCommandError as e:
            print(f"Error cloning repository: {e}")
            return None
    
    @staticmethod
    def open_repository(path: str) -> Optional[Repo]:
        """Open an existing repository"""
        try:
            repo = Repo(path)
            return repo
        except (GitCommandError, Exception) as e:
            print(f"Error opening repository: {e}")
            return None
    
    @staticmethod
    def add_remote(repo: Repo, name: str, url: str) -> bool:
        """Add a remote to the repository"""
        try:
            if name in [remote.name for remote in repo.remotes]:
                repo.delete_remote(name)
            repo.create_remote(name, url)
            return True
        except GitCommandError as e:
            print(f"Error adding remote: {e}")
            return False
    
    @staticmethod
    def push_to_remote(repo: Repo, remote_name: str = "origin", 
                       branch: str = "master") -> bool:
        """Push to remote repository"""
        try:
            if remote_name not in [r.name for r in repo.remotes]:
                print(f"Remote '{remote_name}' not found")
                return False
            
            repo.remotes[remote_name].push(branch)
            return True
        except GitCommandError as e:
            print(f"Error pushing to remote: {e}")
            return False
    
    @staticmethod
    def create_initial_commit(repo: Repo, message: str = "Initial commit") -> bool:
        """Create an initial commit"""
        try:
            repo.index.add(["."])
            repo.index.commit(message)
            return True
        except GitCommandError as e:
            print(f"Error creating commit: {e}")
            return False
    
    @staticmethod
    def create_tag(repo: Repo, tag_name: str, message: str = "") -> bool:
        """Create a tag"""
        try:
            repo.create_tag(tag_name, message=message)
            return True
        except GitCommandError as e:
            print(f"Error creating tag: {e}")
            return False
    
    @staticmethod
    def push_tags(repo: Repo, remote_name: str = "origin") -> bool:
        """Push tags to remote"""
        try:
            repo.remotes[remote_name].push(tags=True)
            return True
        except GitCommandError as e:
            print(f"Error pushing tags: {e}")
            return False
    
    @staticmethod
    def get_commits(repo: Repo, max_count: int = 10) -> List[dict]:
        """Get recent commits"""
        try:
            commits = []
            for commit in repo.iter_commits('HEAD', max_count=max_count):
                commits.append({
                    "hash": commit.hexsha[:7],
                    "author": commit.author.name,
                    "message": commit.message.split('\n')[0],
                    "date": commit.committed_datetime.isoformat()
                })
            return commits
        except Exception as e:
            print(f"Error getting commits: {e}")
            return []
    
    @staticmethod
    def delete_directory(path: str) -> bool:
        """Delete a repository directory"""
        try:
            import shutil
            shutil.rmtree(path)
            return True
        except Exception as e:
            print(f"Error deleting directory: {e}")
            return False