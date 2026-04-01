"""
Main GUI Window for GitHub Project Manager
"""

import sys
import os
import tempfile
import subprocess
import platform
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QListWidgetItem, QLabel, QLineEdit,
    QMessageBox, QFileDialog, QTabWidget, QScrollArea, QGroupBox, QFormLayout,
    QStyleFactory, QCheckBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QPixmap, QPainter, QColor, QLinearGradient, QPen

from config_manager import ConfigManager
from github_manager import GitHubManager
from git_manager import GitManager
from gui.dialogs import (
    LoginDialog, CreateProjectDialog, ReleaseDialog, ProjectContentDialog
)

class WorkerThread(QThread):
    """Worker thread for long-running operations"""
    finished = pyqtSignal()
    error = pyqtSignal(str)
    success = pyqtSignal(str)

class GitHubProjectManager(QApplication):
    """Main application class"""
    
    def __init__(self):
        super().__init__(sys.argv)
        self.config_manager = ConfigManager()
        self.theme_mode = self.config_manager.get_theme_mode()
        self.app_icon = self.create_app_icon()
        self.setWindowIcon(self.app_icon)
        self.apply_windows11_theme(self.theme_mode)
        self.github_manager = None
        self.current_repo_path = None
        self.project_items = {}
        self.setup_ui()
        self.check_authentication()

    def create_app_icon(self) -> QIcon:
        """Create a simple built-in app icon"""
        size = 256
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing, True)

        gradient = QLinearGradient(0, 0, size, size)
        gradient.setColorAt(0.0, QColor("#1a73e8"))
        gradient.setColorAt(1.0, QColor("#0b57d0"))
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(8, 8, size - 16, size - 16, 48, 48)

        # Draw a white "project branch" glyph.
        pen = QPen(QColor("#ffffff"))
        pen.setWidth(18)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.drawLine(70, 80, 185, 80)
        painter.drawLine(70, 80, 70, 176)
        painter.drawLine(70, 176, 185, 176)

        painter.setBrush(QColor("#ffffff"))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(50, 60, 40, 40)
        painter.drawEllipse(165, 60, 40, 40)
        painter.drawEllipse(165, 156, 40, 40)
        painter.end()

        return QIcon(pixmap)

    def apply_windows11_theme(self, mode: str = "light"):
        """Apply a Windows 11-inspired global UI theme"""
        self.setStyle(QStyleFactory.create("Fusion"))
        self.setFont(QFont("Segoe UI", 10))
        if mode == "dark":
            self.setStyleSheet("""
                QWidget {
                    background-color: #1f2329;
                    color: #e6e8eb;
                    font-family: "Segoe UI";
                    font-size: 10pt;
                }
                QMainWindow, QDialog {
                    background-color: #1f2329;
                }
                QLabel {
                    background: transparent;
                    color: #e6e8eb;
                }
                QTabWidget::pane {
                    border: none;
                    border-radius: 0px;
                    background: transparent;
                    top: 0px;
                }
                QTabBar::tab {
                    background: transparent;
                    color: #c8d0da;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 16px;
                    margin-right: 6px;
                }
                QTabBar::tab:selected {
                    background: #2f3742;
                    color: #6ea8ff;
                }
                QLineEdit, QTextEdit, QListWidget, QTreeWidget {
                    background: #2a313a;
                    border: 1px solid #3b4452;
                    border-radius: 8px;
                    padding: 6px 8px;
                    selection-background-color: #1f4fa3;
                    selection-color: #f5f7fa;
                }
                QLineEdit:focus, QTextEdit:focus, QListWidget:focus, QTreeWidget:focus {
                    border: 1px solid #6ea8ff;
                }
                QGroupBox {
                    border: 1px solid #3b4452;
                    border-radius: 10px;
                    margin-top: 10px;
                    padding-top: 12px;
                    background: #252b33;
                    font-weight: 600;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 12px;
                    padding: 0 6px;
                    color: #c8d0da;
                }
                QPushButton {
                    background: #2a313a;
                    color: #e6e8eb;
                    border: 1px solid #465264;
                    border-radius: 9px;
                    padding: 7px 14px;
                    min-height: 18px;
                }
                QPushButton:hover {
                    background: #333b46;
                    border-color: #5a677b;
                }
                QPushButton:pressed {
                    background: #3a4452;
                }
                QPushButton:disabled {
                    color: #8f99a6;
                    background: #2a313a;
                    border-color: #3a4350;
                }
                QPushButton#primaryButton {
                    background: #0b57d0;
                    color: #ffffff;
                    border: 1px solid #0b57d0;
                }
                QPushButton#primaryButton:hover {
                    background: #0a4db7;
                    border-color: #0a4db7;
                }
                QPushButton#dangerButton {
                    background: #d92d20;
                    color: #ffffff;
                    border: 1px solid #d92d20;
                }
                QPushButton#dangerButton:hover {
                    background: #b42318;
                    border-color: #b42318;
                }
                QScrollBar:vertical {
                    background: transparent;
                    width: 12px;
                    margin: 2px;
                }
                QScrollBar::handle:vertical {
                    background: #5a677b;
                    border-radius: 6px;
                    min-height: 32px;
                }
                QScrollBar::handle:vertical:hover {
                    background: #6a7890;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
                QMessageBox QLabel {
                    min-width: 320px;
                }
            """)
            return

        self.setStyleSheet("""
            QWidget {
                background-color: #f5f6f8;
                color: #1f2328;
                font-family: "Segoe UI";
                font-size: 10pt;
            }
            QMainWindow, QDialog {
                background-color: #f5f6f8;
            }
            QLabel {
                background: transparent;
                color: #1f2328;
            }
            QTabWidget::pane {
                border: none;
                border-radius: 0px;
                background: transparent;
                top: 0px;
            }
            QTabBar::tab {
                background: transparent;
                color: #3b4350;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                margin-right: 6px;
            }
            QTabBar::tab:selected {
                background: #e9edf3;
                color: #0b57d0;
            }
            QLineEdit, QTextEdit, QListWidget, QTreeWidget {
                background: #ffffff;
                border: 1px solid #d7dce2;
                border-radius: 8px;
                padding: 6px 8px;
                selection-background-color: #dbe9ff;
                selection-color: #0f172a;
            }
            QLineEdit:focus, QTextEdit:focus, QListWidget:focus, QTreeWidget:focus {
                border: 1px solid #0b57d0;
            }
            QGroupBox {
                border: 1px solid #dfe3e8;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 12px;
                background: #ffffff;
                font-weight: 600;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
                color: #3b4350;
            }
            QPushButton {
                background: #ffffff;
                color: #1f2328;
                border: 1px solid #cfd6de;
                border-radius: 9px;
                padding: 7px 14px;
                min-height: 18px;
            }
            QPushButton:hover {
                background: #f1f5fb;
                border-color: #b8c3d0;
            }
            QPushButton:pressed {
                background: #e8eef8;
            }
            QPushButton:disabled {
                color: #9aa4b2;
                background: #f3f4f6;
                border-color: #e1e5ea;
            }
            QPushButton#primaryButton {
                background: #0b57d0;
                color: #ffffff;
                border: 1px solid #0b57d0;
            }
            QPushButton#primaryButton:hover {
                background: #0a4db7;
                border-color: #0a4db7;
            }
            QPushButton#dangerButton {
                background: #d92d20;
                color: #ffffff;
                border: 1px solid #d92d20;
            }
            QPushButton#dangerButton:hover {
                background: #b42318;
                border-color: #b42318;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 12px;
                margin: 2px;
            }
            QScrollBar::handle:vertical {
                background: #c6ced8;
                border-radius: 6px;
                min-height: 32px;
            }
            QScrollBar::handle:vertical:hover {
                background: #b4beca;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QMessageBox QLabel {
                min-width: 320px;
            }
        """)
    
    def setup_ui(self):
        """Set up the main window UI"""
        self.main_window = QMainWindow()
        self.main_window.setWindowTitle("GitHub Project Manager")
        self.main_window.setGeometry(100, 100, 1000, 700)
        self.main_window.setWindowIcon(self.app_icon)
        
        central_widget = QWidget()
        self.main_window.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # User info bar
        user_layout = QHBoxLayout()
        self.user_label = QLabel("Not logged in")
        self.user_label.setFont(QFont("Segoe UI", 10))
        self.login_btn = QPushButton("Login")
        self.login_btn.setObjectName("primaryButton")
        self.login_btn.clicked.connect(self.show_login_dialog)
        self.logout_btn = QPushButton("Logout")
        self.logout_btn.clicked.connect(self.logout)
        self.logout_btn.setEnabled(False)
        
        user_layout.addWidget(self.user_label)
        user_layout.addStretch()
        user_layout.addWidget(self.login_btn)
        user_layout.addWidget(self.logout_btn)
        layout.addLayout(user_layout)
        
        # Tab widget
        tabs = QTabWidget()
        tabs.setDocumentMode(True)
        
        # Projects Tab
        projects_widget = self.create_projects_tab()
        tabs.addTab(projects_widget, "Projects")
        
        # Settings Tab
        settings_widget = self.create_settings_tab()
        tabs.addTab(settings_widget, "Settings")
        
        layout.addWidget(tabs)
        
        central_widget.setLayout(layout)
        self.main_window.show()
    
    def create_projects_tab(self) -> QWidget:
        """Create the projects management tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Projects list
        list_label = QLabel("Your Projects:")
        layout.addWidget(list_label)
        
        self.projects_list = QListWidget()
        self.projects_list.itemDoubleClicked.connect(self.on_project_item_double_clicked)
        layout.addWidget(self.projects_list)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        create_btn = QPushButton("Create New Project")
        create_btn.clicked.connect(self.show_create_project_dialog)
        
        upload_btn = QPushButton("Upload to GitHub")
        upload_btn.clicked.connect(self.upload_project)
        
        release_btn = QPushButton("Publish Release")
        release_btn.setObjectName("primaryButton")
        release_btn.clicked.connect(self.show_release_dialog)
        
        delete_btn = QPushButton("Delete Project")
        delete_btn.clicked.connect(self.delete_project)
        delete_btn.setObjectName("dangerButton")
        
        open_btn = QPushButton("Open Project")
        open_btn.clicked.connect(self.open_project)

        view_content_btn = QPushButton("View Content")
        view_content_btn.clicked.connect(self.show_project_content)
        
        buttons_layout.addWidget(create_btn)
        buttons_layout.addWidget(upload_btn)
        buttons_layout.addWidget(release_btn)
        buttons_layout.addWidget(open_btn)
        buttons_layout.addWidget(view_content_btn)
        buttons_layout.addWidget(delete_btn)
        
        layout.addLayout(buttons_layout)
        
        # Refresh projects list
        self.refresh_projects_list()
        
        widget.setLayout(layout)
        return widget
    
    def create_settings_tab(self) -> QWidget:
        """Create the settings tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Projects directory settings
        dir_group = QGroupBox("Projects Directory")
        dir_layout = QFormLayout()
        
        self.projects_dir_label = QLineEdit()
        self.projects_dir_label.setText(str(self.config_manager.get_projects_directory()))
        self.projects_dir_label.setReadOnly(True)
        
        choose_dir_btn = QPushButton("Change Directory")
        choose_dir_btn.clicked.connect(self.choose_projects_directory)
        
        dir_layout.addRow("Current Directory:", self.projects_dir_label)
        dir_layout.addRow(choose_dir_btn)
        dir_group.setLayout(dir_layout)
        layout.addWidget(dir_group)

        # Appearance settings
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QFormLayout()
        self.dark_mode_check = QCheckBox("Enable Windows 11 Dark Mode")
        self.dark_mode_check.setChecked(self.theme_mode == "dark")
        self.dark_mode_check.toggled.connect(self.toggle_theme_mode)
        appearance_layout.addRow("Theme:", self.dark_mode_check)
        appearance_group.setLayout(appearance_layout)
        layout.addWidget(appearance_group)
        
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget

    def toggle_theme_mode(self, enabled: bool):
        """Toggle app theme mode and persist preference"""
        self.theme_mode = "dark" if enabled else "light"
        self.config_manager.set_theme_mode(self.theme_mode)
        self.apply_windows11_theme(self.theme_mode)
    
    def check_authentication(self):
        """Check if user is authenticated"""
        token = self.config_manager.get_github_token()
        username = self.config_manager.get_github_username()
        
        if token:
            self.github_manager = GitHubManager(token)
            if self.github_manager.authenticate():
                self.user_label.setText(f"Logged in as: {username}")
                self.login_btn.setEnabled(False)
                self.logout_btn.setEnabled(True)
                self.refresh_projects_list()
            else:
                self.config_manager.clear_credentials()
                self.show_error("Authentication failed", "Your token has expired. Please login again.")
    
    def show_login_dialog(self):
        """Show login dialog"""
        if not self.login_btn.isEnabled():
            return
        
        dialog = LoginDialog(self.main_window)
        if dialog.exec_():
            token = dialog.get_token()
            self.github_manager = GitHubManager(token)
            
            if self.github_manager.authenticate():
                username = self.github_manager.get_username()
                self.config_manager.save_github_token(token)
                self.config_manager.save_github_username(username)
                self.user_label.setText(f"Logged in as: {username}")
                self.login_btn.setEnabled(False)
                self.logout_btn.setEnabled(True)
                self.refresh_projects_list()
                self.show_success("Login successful", f"Welcome, {username}!")
            else:
                self.show_error("Authentication failed", "Invalid token. Please check and try again.")
    
    def logout(self):
        """Logout user"""
        reply = QMessageBox.question(
            self.main_window,
            "Confirm Logout",
            "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.config_manager.clear_credentials()
            self.github_manager = None
            self.user_label.setText("Not logged in")
            self.login_btn.setEnabled(True)
            self.logout_btn.setEnabled(False)
            self.refresh_projects_list()
            self.show_success("Logout", "You have been logged out.")
    
    def show_create_project_dialog(self):
        """Show create project dialog"""
        if not self.github_manager:
            self.show_error("Not logged in", "Please login to GitHub first.")
            return
        
        dialog = CreateProjectDialog(self.main_window)
        if dialog.exec_():
            project_name, description, init_readme = dialog.get_data()
            self.create_project(project_name, description, init_readme)
    
    def create_project(self, project_name: str, description: str = "", init_readme: bool = True):
        """Create a new project"""
        projects_dir = self.config_manager.get_projects_directory()
        project_path = projects_dir / project_name
        
        if project_path.exists():
            self.show_error("Project exists", f"Project '{project_name}' already exists locally.")
            return
        
        # Initialize Git repository
        repo = GitManager.init_repository(str(project_path))
        if not repo:
            self.show_error("Error", "Failed to initialize Git repository.")
            return
        
        # Create README if requested
        if init_readme:
            readme_path = project_path / "README.md"
            readme_path.write_text(f"# {project_name}\n\n{description}\n")
        
        # Create initial commit
        if not GitManager.create_initial_commit(repo, "Initial commit"):
            self.show_error("Error", "Failed to create initial commit.")
            return
        
        self.show_success("Success", f"Project '{project_name}' created successfully!")
        self.refresh_projects_list()
    
    def upload_project(self):
        """Upload project to GitHub"""
        if not self.github_manager:
            self.show_error("Not logged in", "Please login to GitHub first.")
            return
        
        selected_project = self.get_selected_project()
        if not selected_project:
            self.show_error("No project selected", "Please select a project to upload.")
            return
        
        if not selected_project["local"]:
            self.show_error("Not a local project", "Please select a local project to upload.")
            return

        project_name = selected_project["name"]
        project_path = selected_project["path"]
        
        # Check if repository exists on GitHub
        if self.github_manager.repository_exists(project_name):
            reply = QMessageBox.question(
                self.main_window,
                "Repository exists",
                f"Repository '{project_name}' already exists on GitHub. Continue?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
        else:
            # Create repository on GitHub
            repo_data = self.github_manager.create_repository(project_name, "")
            if not repo_data:
                self.show_error("Error", "Failed to create repository on GitHub.")
                return
        
        # Add remote and push
        repo = GitManager.open_repository(str(project_path))
        if not repo:
            self.show_error("Error", "Failed to open local repository.")
            return
        
        repo_data = self.github_manager.get_repository(project_name)
        if not repo_data:
            self.show_error("Error", "Failed to get repository information.")
            return
        
        if not GitManager.add_remote(repo, "origin", repo_data.clone_url):
            self.show_error("Error", "Failed to add remote.")
            return
        
        if not GitManager.push_to_remote(repo, "origin", "master"):
            self.show_error("Error", "Failed to push to GitHub.")
            return
        
        self.show_success("Success", f"Project uploaded to GitHub!\n{repo_data.html_url}")
    
    def show_release_dialog(self):
        """Show release creation dialog"""
        if not self.github_manager:
            self.show_error("Not logged in", "Please login to GitHub first.")
            return
        
        selected_project = self.get_selected_project()
        if not selected_project:
            self.show_error("No project selected", "Please select a project.")
            return
        
        project_name = selected_project["name"]
        self.show_release_dialog_for_project(project_name)
    
    def create_release(self, repo_name: str, tag_name: str, 
                      release_name: str, body: str, draft: bool,
                      asset_paths=None):
        """Create a release"""
        result = self.github_manager.create_release(
            repo_name, tag_name, release_name, body, draft, asset_paths=asset_paths
        )
        
        if result:
            uploaded_count = len(result.get("uploaded_assets", []))
            failed_assets = result.get("failed_assets", [])
            failed_count = len(failed_assets)
            message = f"Release created!\n{result['url']}\n\nUploaded assets: {uploaded_count}"
            if failed_count:
                message += f"\nFailed assets: {failed_count}"
            self.show_success("Success", message)
        else:
            self.show_error("Error", "Failed to create release.")
    
    def delete_project(self):
        """Delete a project"""
        selected_project = self.get_selected_project()
        if not selected_project:
            self.show_error("No project selected", "Please select a project to delete.")
            return
        
        if not selected_project["local"]:
            self.show_error("Not a local project", "This action only deletes local projects.")
            return

        project_name = selected_project["name"]
        
        reply = QMessageBox.question(
            self.main_window,
            "Confirm deletion",
            f"Are you sure you want to delete '{project_name}'? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        project_path = selected_project["path"]
        
        if GitManager.delete_directory(str(project_path)):
            self.show_success("Success", f"Project '{project_name}' deleted.")
            self.refresh_projects_list()
        else:
            self.show_error("Error", "Failed to delete project.")
    
    def open_project(self):
        """Open project in file explorer"""
        selected_project = self.get_selected_project()
        if not selected_project:
            self.show_error("No project selected", "Please select a project.")
            return
        
        if not selected_project["local"]:
            self.show_error("Not a local project", "Selected project is online only.")
            return

        project_path = selected_project["path"]
        self.open_path_in_system(project_path)

    def show_project_content(self):
        """Show project content in a viewer dialog"""
        selected_project = self.get_selected_project()
        if not selected_project:
            self.show_error("No project selected", "Please select a project.")
            return
        self.show_project_content_for(selected_project)

    def show_project_content_for(self, selected_project):
        """Show content dialog for a specified project item"""
        if not selected_project:
            return

        project_name = selected_project["name"]
        files = []
        source = ""
        content_loader = None
        release_callback = None

        if selected_project["local"]:
            project_path = selected_project["path"]
            files = self.get_local_project_files(project_path)
            source = "Local"
            content_loader = lambda file_path: self.get_local_file_content(project_path, file_path)
            if self.github_manager and selected_project["remote"]:
                release_callback = lambda: self.show_release_dialog_for_project(project_name)
        elif selected_project["remote"]:
            if not self.github_manager:
                self.show_error("Not logged in", "Please login to GitHub first.")
                return
            files = self.github_manager.get_repository_files(project_name)
            source = "GitHub"
            content_loader = lambda file_path: self.github_manager.get_repository_file_content(project_name, file_path)
            release_callback = lambda: self.show_release_dialog_for_project(project_name)

        if not files:
            self.show_error("No content found", "This project has no readable files.")
            return

        dialog = ProjectContentDialog(
            self.main_window,
            project_name=project_name,
            source=source,
            files=files,
            content_loader=content_loader,
            release_callback=release_callback
        )
        dialog.set_editor_opener(lambda file_path: self.open_project_file_in_editor(selected_project, file_path))
        dialog.exec_()

    def on_project_item_double_clicked(self, item: QListWidgetItem):
        """Double-click project item to expand directory/content view"""
        if not item:
            return
        selected_project = self.get_selected_project()
        self.show_project_content_for(selected_project)

    def show_release_dialog_for_project(self, project_name: str):
        """Show release dialog for a specific project name"""
        if not self.github_manager:
            self.show_error("Not logged in", "Please login to GitHub first.")
            return
        dialog = ReleaseDialog(self.main_window, project_name)
        if dialog.exec_():
            tag_name, release_name, body, draft, asset_paths = dialog.get_data()
            self.create_release(project_name, tag_name, release_name, body, draft, asset_paths)

    def get_local_project_files(self, project_path: Path):
        """Get local project files recursively"""
        file_paths = []
        for root, dirs, files in os.walk(project_path):
            # Skip git metadata directory
            dirs[:] = [d for d in dirs if d != ".git"]
            for file_name in files:
                full_path = Path(root) / file_name
                relative_path = full_path.relative_to(project_path).as_posix()
                file_paths.append(relative_path)
        return sorted(file_paths, key=str.lower)

    def get_local_file_content(self, project_path: Path, relative_path: str):
        """Get local file content for preview"""
        file_path = project_path / relative_path
        try:
            return file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return "[Binary or non-UTF8 file, preview not supported]"
        except Exception as e:
            return f"Failed to read file: {e}"

    def open_path_in_system(self, path: Path) -> bool:
        """Open file or directory in system default application"""
        try:
            if platform.system() == "Windows":
                os.startfile(str(path))
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", str(path)])
            else:
                subprocess.Popen(["xdg-open", str(path)])
            return True
        except Exception as e:
            print(f"Error opening path in system: {e}")
            return False

    def open_project_file_in_editor(self, selected_project, relative_path: str) -> bool:
        """Open project file in system editor for local or remote project"""
        try:
            if selected_project["local"]:
                local_path = selected_project["path"] / relative_path
                return self.open_path_in_system(local_path)

            if selected_project["remote"] and self.github_manager:
                content = self.github_manager.get_repository_file_content(
                    selected_project["name"], relative_path
                )
                if content is None:
                    return False

                temp_root = Path(tempfile.gettempdir()) / "github_project_manager_preview" / selected_project["name"]
                preview_file = temp_root / relative_path
                preview_file.parent.mkdir(parents=True, exist_ok=True)
                preview_file.write_text(content, encoding="utf-8")
                return self.open_path_in_system(preview_file)

            return False
        except Exception as e:
            print(f"Error opening project file in editor: {e}")
            return False
    
    def refresh_projects_list(self):
        """Refresh the projects list (local + owned GitHub repositories)"""
        self.projects_list.clear()
        self.project_items = {}
        projects_dir = self.config_manager.get_projects_directory()
        
        if projects_dir.exists():
            for item in projects_dir.iterdir():
                if item.is_dir() and (item / ".git").exists():
                    self.project_items[item.name] = {
                        "name": item.name,
                        "local": True,
                        "remote": False,
                        "path": item,
                        "html_url": None
                    }

        if self.github_manager:
            for repo in self.github_manager.get_owned_repositories():
                repo_name = repo["name"]
                if repo_name in self.project_items:
                    self.project_items[repo_name]["remote"] = True
                    self.project_items[repo_name]["html_url"] = repo.get("html_url")
                else:
                    self.project_items[repo_name] = {
                        "name": repo_name,
                        "local": False,
                        "remote": True,
                        "path": None,
                        "html_url": repo.get("html_url")
                    }

        for project_name in sorted(self.project_items.keys(), key=str.lower):
            data = self.project_items[project_name]
            if data["local"] and data["remote"]:
                source_label = "Local + GitHub"
            elif data["local"]:
                source_label = "Local"
            else:
                source_label = "GitHub"

            list_item = QListWidgetItem(f"{project_name}  [{source_label}]")
            list_item.setData(Qt.UserRole, project_name)
            self.projects_list.addItem(list_item)

    def get_selected_project(self):
        """Get selected project metadata"""
        current_item = self.projects_list.currentItem()
        if not current_item:
            return None

        project_name = current_item.data(Qt.UserRole)
        if not project_name:
            return None

        return self.project_items.get(project_name)
    
    def choose_projects_directory(self):
        """Choose projects directory"""
        directory = QFileDialog.getExistingDirectory(
            self.main_window,
            "Select Projects Directory"
        )
        
        if directory:
            self.config_manager.set_projects_directory(directory)
            self.projects_dir_label.setText(directory)
            self.refresh_projects_list()
    
    def show_error(self, title: str, message: str):
        """Show error message"""
        QMessageBox.critical(self.main_window, title, message)
    
    def show_success(self, title: str, message: str):
        """Show success message"""
        QMessageBox.information(self.main_window, title, message)
    
    def run(self):
        """Run the application"""
        self.exec_()
