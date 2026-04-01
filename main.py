#!/usr/bin/env python3
"""
GitHub Project Manager - Main Entry Point
A GUI tool for managing local Git projects and GitHub integration
"""

import sys
from pathlib import Path
from gui.main_window import GitHubProjectManager

def main():
    """Initialize and run the application"""
    app = GitHubProjectManager()
    app.run()

if __name__ == "__main__":
    main()