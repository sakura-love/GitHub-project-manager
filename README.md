# GitHub Project Manager

A desktop GUI tool for managing local Git projects and GitHub repositories.

## Features
- Manage local Git projects
- Load your owned GitHub repositories (non-fork)
- Browse project files (local and remote)
- Publish GitHub releases with asset upload
- Windows 11 inspired light/dark UI

## Requirements
- Python 3.10+
- Git installed

## Setup
`ash
pip install -r requirements.txt
python main.py
`

## Notes
- GitHub token is stored in system keyring, not in repo files.
- Local app config is stored under user home (~/.github_project_manager).
