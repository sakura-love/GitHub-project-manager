"""
Dialog windows for the application
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTextEdit, QCheckBox, QFormLayout, QMessageBox,
    QTreeWidget, QTreeWidgetItem, QSplitter, QWidget, QFileDialog, QListWidget
)
from PyQt5.QtCore import Qt
from typing import Callable, List, Optional

class LoginDialog(QDialog):
    """GitHub login dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("GitHub Login")
        self.setGeometry(200, 200, 400, 200)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the login dialog UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)
        
        # Instructions
        instructions = QLabel(
            "Enter your GitHub Personal Access Token.\n"
            "Create one at: https://github.com/settings/tokens"
        )
        layout.addWidget(instructions)
        
        # Form
        form_layout = QFormLayout()
        
        self.token_input = QLineEdit()
        self.token_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Token:", self.token_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        login_btn = QPushButton("Login")
        login_btn.setObjectName("primaryButton")
        login_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(login_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def get_token(self) -> str:
        """Get the entered token"""
        return self.token_input.text()


class CreateProjectDialog(QDialog):
    """Create new project dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Project")
        self.setGeometry(200, 200, 450, 250)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the create project dialog UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)
        
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        form_layout.addRow("Project Name:", self.name_input)
        
        self.description_input = QLineEdit()
        form_layout.addRow("Description:", self.description_input)
        
        self.readme_check = QCheckBox("Create README.md")
        self.readme_check.setChecked(True)
        form_layout.addRow("", self.readme_check)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        create_btn = QPushButton("Create")
        create_btn.setObjectName("primaryButton")
        create_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(create_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def get_data(self):
        """Get the entered data"""
        return (
            self.name_input.text(),
            self.description_input.text(),
            self.readme_check.isChecked()
        )


class ReleaseDialog(QDialog):
    """Create release dialog"""
    
    def __init__(self, parent=None, repo_name: str = ""):
        super().__init__(parent)
        self.repo_name = repo_name
        self.setWindowTitle(f"Create Release - {repo_name}")
        self.setGeometry(200, 200, 500, 400)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the release dialog UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)
        
        form_layout = QFormLayout()
        
        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("e.g., v1.0.0")
        form_layout.addRow("Tag Name:", self.tag_input)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Release name (optional)")
        form_layout.addRow("Release Name:", self.name_input)
        
        layout.addLayout(form_layout)
        
        # Release notes
        notes_label = QLabel("Release Notes:")
        layout.addWidget(notes_label)
        
        self.notes_input = QTextEdit()
        layout.addWidget(self.notes_input)
        
        # Draft checkbox
        self.draft_check = QCheckBox("Save as draft")
        layout.addWidget(self.draft_check)

        # Asset upload
        assets_label = QLabel("Release Assets:")
        layout.addWidget(assets_label)

        self.assets_list = QListWidget()
        layout.addWidget(self.assets_list)

        assets_btn_layout = QHBoxLayout()
        add_assets_btn = QPushButton("Add Files")
        add_assets_btn.clicked.connect(self.add_assets)
        remove_asset_btn = QPushButton("Remove Selected")
        remove_asset_btn.clicked.connect(self.remove_selected_asset)
        assets_btn_layout.addWidget(add_assets_btn)
        assets_btn_layout.addWidget(remove_asset_btn)
        layout.addLayout(assets_btn_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        create_btn = QPushButton("Create Release")
        create_btn.setObjectName("primaryButton")
        create_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(create_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def get_data(self):
        """Get the entered data"""
        return (
            self.tag_input.text(),
            self.name_input.text(),
            self.notes_input.toPlainText(),
            self.draft_check.isChecked(),
            [self.assets_list.item(i).text() for i in range(self.assets_list.count())]
        )

    def add_assets(self):
        """Add asset files for release upload"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Release Asset Files"
        )
        if not file_paths:
            return

        existing = {self.assets_list.item(i).text() for i in range(self.assets_list.count())}
        for path in file_paths:
            if path not in existing:
                self.assets_list.addItem(path)
                existing.add(path)

    def remove_selected_asset(self):
        """Remove selected asset file from list"""
        for item in self.assets_list.selectedItems():
            self.assets_list.takeItem(self.assets_list.row(item))


class ProjectContentDialog(QDialog):
    """Project content viewer dialog"""

    def __init__(self, parent=None, project_name: str = "", source: str = "",
                 files: List[str] = None, content_loader: Callable[[str], str] = None,
                 release_callback: Callable[[], None] = None):
        super().__init__(parent)
        self.project_name = project_name
        self.source = source
        self.files = sorted(files or [], key=str.lower)
        self.content_loader = content_loader
        self.editor_opener: Optional[Callable[[str], bool]] = None
        self.release_callback = release_callback
        self.setWindowTitle(f"Project Content - {project_name}")
        self.setGeometry(180, 120, 900, 620)
        self.setup_ui()

    def set_editor_opener(self, editor_opener: Callable[[str], bool]):
        """Set system editor opener callback"""
        self.editor_opener = editor_opener

    def setup_ui(self):
        """Set up content viewer UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        info_label = QLabel(
            f"Project: {self.project_name} | Source: {self.source} | Files: {len(self.files)}"
        )
        layout.addWidget(info_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search file name, e.g. main.py")
        self.search_input.textChanged.connect(self.filter_files)
        layout.addWidget(self.search_input)

        splitter = QSplitter(Qt.Horizontal)

        self.files_tree = QTreeWidget()
        self.files_tree.setHeaderLabel("Project Files")
        self.files_tree.itemClicked.connect(self.on_tree_item_clicked)
        self.files_tree.itemDoubleClicked.connect(self.on_tree_item_double_clicked)
        splitter.addWidget(self.files_tree)

        preview_label = QLabel("File Preview:")
        preview_container = QVBoxLayout()
        preview_container.addWidget(preview_label)

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        preview_container.addWidget(self.preview_text)

        preview_widget = QWidget()
        preview_widget.setLayout(preview_container)
        splitter.addWidget(preview_widget)
        splitter.setSizes([330, 570])

        layout.addWidget(splitter)

        actions_layout = QHBoxLayout()
        if self.release_callback:
            publish_btn = QPushButton("Publish Release")
            publish_btn.setObjectName("primaryButton")
            publish_btn.clicked.connect(self.on_publish_release_clicked)
            actions_layout.addWidget(publish_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        actions_layout.addWidget(close_btn)
        layout.addLayout(actions_layout)

        self.setLayout(layout)
        self.build_files_tree(self.files)

    def build_files_tree(self, files: List[str]):
        """Build tree view from file paths"""
        self.files_tree.clear()
        nodes = {}

        for file_path in files:
            parts = file_path.split("/")
            parent_item = None
            current_key = ""

            for index, part in enumerate(parts):
                current_key = f"{current_key}/{part}" if current_key else part
                is_file = index == len(parts) - 1
                node_key = f"file:{current_key}" if is_file else f"dir:{current_key}"

                if node_key not in nodes:
                    item = QTreeWidgetItem([part])
                    if is_file:
                        item.setData(0, Qt.UserRole, file_path)
                    else:
                        item.setData(0, Qt.UserRole, None)
                    nodes[node_key] = item

                    if parent_item is None:
                        self.files_tree.addTopLevelItem(item)
                    else:
                        parent_item.addChild(item)

                parent_item = nodes[node_key]

        self.files_tree.expandToDepth(1)

    def filter_files(self, keyword: str):
        """Filter tree by filename/path keyword"""
        keyword = (keyword or "").strip().lower()
        if not keyword:
            filtered_files = self.files
        else:
            filtered_files = [
                path for path in self.files
                if keyword in path.lower() or keyword in path.split("/")[-1].lower()
            ]
        self.build_files_tree(filtered_files)
        self.preview_text.clear()

    def on_tree_item_clicked(self, item: QTreeWidgetItem):
        """Handle tree item click to preview file"""
        file_path = item.data(0, Qt.UserRole)
        if not file_path:
            return
        self.load_selected_file_content(file_path)

    def on_tree_item_double_clicked(self, item: QTreeWidgetItem):
        """Handle tree item double click to open in system editor"""
        file_path = item.data(0, Qt.UserRole)
        if not file_path:
            return

        if not self.editor_opener:
            QMessageBox.information(self, "Info", "Editor opener is not configured.")
            return

        ok = self.editor_opener(file_path)
        if not ok:
            QMessageBox.warning(self, "Open Failed", "Failed to open file in system editor.")

    def load_selected_file_content(self, file_path: str):
        """Load selected file content into preview"""
        if not file_path or not self.content_loader:
            self.preview_text.clear()
            return

        content = self.content_loader(file_path)
        if content is None:
            self.preview_text.setPlainText("Failed to load file content.")
            return

        self.preview_text.setPlainText(content)

    def on_publish_release_clicked(self):
        """Trigger release flow from content dialog"""
        if not self.release_callback:
            return
        self.release_callback()
