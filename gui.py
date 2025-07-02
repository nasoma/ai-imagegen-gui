import sys
import requests
import json
import base64
import os
import random
import string
import keyring
from pathlib import Path
from io import BytesIO
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QTextEdit,
    QPushButton,
    QProgressBar,
    QMessageBox,
    QFileDialog,
    QSplitter,
    QScrollArea,
    QComboBox,
    QLineEdit,
    QMenuBar,
    QAction,
    QDialog,
    QFormLayout,
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont, QPixmap, QIcon, QPalette, QColor
from PIL import Image
from openai import OpenAI


# Constants for keyring service and username
KEYRING_SERVICE = "ai_image_generator"
KEYRING_USERNAME = "api_key"


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About AI Image Generator")
        self.setFixedSize(400, 350)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        # Center the dialog on the parent window
        if parent:
            parent_geometry = parent.geometry()
            x = parent_geometry.x() + (parent_geometry.width() - 400) // 2
            y = parent_geometry.y() + (parent_geometry.height() - 350) // 2
            self.move(x, y)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # App icon/title
        title_label = QLabel("🎨 AI Image Generator")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #141413; margin: 10px 0;")
        layout.addWidget(title_label)

        # Version
        version_label = QLabel("Version 1.0.0")
        version_label.setFont(QFont("Arial", 12))
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("color: #666666; margin: 5px 0;")
        layout.addWidget(version_label)

        # Description
        description = QLabel(
            "A powerful AI image generator with smart prompt enhancement. "
            "Generates high-quality PNG images in predefined or custom sizes."
        )
        description.setWordWrap(True)
        description.setFont(QFont("Arial", 11))
        description.setAlignment(Qt.AlignCenter)
        description.setStyleSheet("color: #333333; margin: 15px 0; line-height: 1.4;")
        layout.addWidget(description)

        # Copyright
        copyright_label = QLabel("© 2025 Nasoma. All rights reserved.")
        copyright_label.setFont(QFont("Arial", 10))
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setStyleSheet("color: #666666; margin: 5px 0;")
        layout.addWidget(copyright_label)

        # Technology info
        tech_label = QLabel("Powered by Nebius AI  and black-forest-labs/flux-dev")
        tech_label.setFont(QFont("Arial", 10))
        tech_label.setAlignment(Qt.AlignCenter)
        tech_label.setStyleSheet("color: #7B68EE; margin: 10px 0;")
        layout.addWidget(tech_label)

        # Add some spacing
        layout.addStretch()

        # OK button
        ok_button = QPushButton("OK")
        ok_button.setFixedHeight(35)
        ok_button.setStyleSheet(
            """
            QPushButton {
                background-color: #141413;
                color: white;
                border: none;
                padding: 8px 24px;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2a2a28;
            }
            """
        )
        ok_button.clicked.connect(self.accept)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)
        layout.addWidget(QLabel())  # Small spacing at bottom

        self.setLayout(layout)


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(400, 300)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        # Center the dialog on the parent window
        if parent:
            parent_geometry = parent.geometry()
            x = parent_geometry.x() + (parent_geometry.width() - 400) // 2
            y = parent_geometry.y() + (parent_geometry.height() - 300) // 2
            self.move(x, y)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Title
        title_label = QLabel("🔑 API Key Configuration")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Form layout for settings
        form_layout = QFormLayout()

        # API Key field
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Enter your Nebius AI API key")
        self.api_key_input.setEchoMode(QLineEdit.Password)  # Mask the API key
        form_layout.addRow("API Key:", self.api_key_input)

        # Add form layout to main layout
        layout.addLayout(form_layout)
        help_label = QLabel(
            "• Get your API key from Nebius AI Studio\n"
            "• Your key is securely stored in macOS Keychain\n"
            "• The key is only accessible by this application"
        )
        help_label.setFont(QFont("Arial", 10))
        help_label.setStyleSheet(
            "color: #666666; background-color: #f8f9fa; padding: 10px; border-radius: 5px;"
        )
        layout.addWidget(help_label)

        # Buttons
        button_layout = QHBoxLayout()

        # Save button
        save_button = QPushButton("Save")
        save_button.setFixedHeight(35)
        save_button.setStyleSheet(
            """
            QPushButton {
                background-color: #141413;
                color: white;
                border: none;
                padding: 8px 24px;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2a2a28;
            }
            """
        )
        save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(save_button)

        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.setFixedHeight(35)
        cancel_button.setStyleSheet(
            """
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px 24px;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            """
        )
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Load current settings
        self.load_settings()

    def load_settings(self):
        # Retrieve API key from keyring
        api_key = keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)
        if api_key:
            self.api_key_input.setText(api_key)

    def save_settings(self):
        api_key = self.api_key_input.text().strip()

        if not api_key:
            QMessageBox.warning(self, "Warning", "Please enter an API key")
            return

        # Save API key to keyring
        keyring.set_password(KEYRING_SERVICE, KEYRING_USERNAME, api_key)

        QMessageBox.information(self, "Success", "Settings saved successfully")
        self.accept()


class PromptEnhancerWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, api_key, original_prompt):
        super().__init__()
        self.api_key = api_key
        self.original_prompt = original_prompt

    def run(self):
        try:
            client = OpenAI(
                base_url="https://api.studio.nebius.com/v1", api_key=self.api_key
            )
            response = client.chat.completions.create(
                model="microsoft/phi-4",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"Rewrite the following image generation prompt to be more detailed, vivid, and creative, while keeping its core idea. Respond only with the enhanced prompt—no explanations, no headers, just the prompt. Limit the enhanced prompt to 100 words:\n{self.original_prompt}",
                            }
                        ],
                    }
                ],
            )
            enhanced_prompt = response.choices[0].message.content.strip()
            self.finished.emit(enhanced_prompt)
        except Exception as e:
            print(f"PromptEnhancerWorker error: {e}")
            self.error.emit(str(e))


class APIWorker(QThread):
    finished = pyqtSignal(int, str, object)
    error = pyqtSignal(str)

    def __init__(self, api_key, prompt, width=1024, height=1024):
        super().__init__()
        self.api_key = api_key
        self.prompt = prompt
        self.width = width
        self.height = height

    def run(self):
        try:
            url = "https://api.studio.nebius.com/v1/images/generations"
            headers = {
                "Content-Type": "application/json",
                "Accept": "*/*",
                "Authorization": f"Bearer {self.api_key}",
            }
            data = {
                "model": "black-forest-labs/flux-dev",
                "prompt": self.prompt,
                "width": self.width,
                "height": self.height,
                "response_extension": "png",
                "num_inference_steps": 64,
                "negative_prompt": "blurry, distorted",
            }

            response = requests.post(url, headers=headers, json=data)
            image_data = None

            if response.status_code == 200:
                try:
                    response_json = response.json()
                    print(
                        f"API Response: {json.dumps(response_json, indent=2)}"
                    )  # Log response for debugging

                    if "data" in response_json and response_json["data"]:
                        first_item = response_json["data"][0]
                        if "b64_json" in first_item and first_item["b64_json"]:
                            try:
                                image_data = base64.b64decode(first_item["b64_json"])
                            except Exception as e:
                                print(f"Failed to decode b64_json: {e}")
                        elif "url" in first_item and first_item["url"]:
                            try:
                                img_response = requests.get(first_item["url"])
                                if img_response.status_code == 200:
                                    image_data = img_response.content
                                else:
                                    print(
                                        f"Failed to download image from URL: {img_response.status_code}"
                                    )
                            except Exception as e:
                                print(f"Failed to fetch URL: {e}")
                    elif "image" in response_json and response_json["image"]:
                        image_str = response_json["image"]
                        if image_str and isinstance(image_str, str):
                            if image_str.startswith("data:image"):
                                image_str = image_str.split(",", 1)[1]
                            try:
                                image_data = base64.b64decode(image_str)
                            except Exception as e:
                                print(f"Failed to decode image field: {e}")
                        else:
                            print("Image field is not a valid string")
                    elif "images" in response_json and response_json["images"]:
                        first_image = response_json["images"][0]
                        if isinstance(first_image, str):
                            if first_image.startswith("data:image"):
                                first_image = first_image.split(",", 1)[1]
                            try:
                                image_data = base64.b64decode(first_image)
                            except Exception as e:
                                print(f"Failed to decode images field: {e}")
                        elif isinstance(first_image, dict) and "url" in first_image:
                            try:
                                img_response = requests.get(first_image["url"])
                                if img_response.status_code == 200:
                                    image_data = img_response.content
                                else:
                                    print(
                                        f"Failed to download image from URL: {img_response.status_code}"
                                    )
                            except Exception as e:
                                print(f"Failed to fetch URL: {e}")
                    elif response.headers.get("content-type", "").startswith("image/"):
                        image_data = response.content
                    else:
                        print("No valid image data found in response")
                except json.JSONDecodeError:
                    print("Failed to parse JSON response")
                    if response.headers.get("content-type", "").startswith("image/"):
                        image_data = response.content
            else:
                print(
                    f"API request failed with status {response.status_code}: {response.text}"
                )

            self.finished.emit(response.status_code, response.text, image_data)
        except Exception as e:
            print(f"APIWorker error: {e}")
            self.error.emit(str(e))


class ImageLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(400, 400)
        self.setStyleSheet(
            """
            QLabel {
                background-color: #f8f9fa;
                color: #666666;
                font-size: 14px;
            }
            """
        )
        self.setText("Generated image will appear here")
        self.original_pixmap = None

    def setImageFromData(self, image_data):
        if not image_data:
            return False
        try:
            pil_image = Image.open(BytesIO(image_data))
            if pil_image.mode != "RGB":
                pil_image = pil_image.convert("RGB")
            img_buffer = BytesIO()
            pil_image.save(img_buffer, format="PNG")
            img_buffer.seek(0)
            pixmap = QPixmap()
            pixmap.loadFromData(img_buffer.getvalue())
            if pixmap.isNull():
                return False
            self.original_pixmap = pixmap
            self.updateScaledPixmap()
            return True
        except Exception:
            return False

    def updateScaledPixmap(self):
        if self.original_pixmap:
            scaled_pixmap = self.original_pixmap.scaled(
                self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateScaledPixmap()


class ImageGeneratorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_image_data = None
        self.api_key = None  # Will be loaded from keyring
        self.init_ui()
        self.load_api_key()

    def load_api_key(self):
        # Load API key from keyring
        self.api_key = keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)
        if not self.api_key:
            # Prompt user to enter API key if not already set
            self.show_settings_dialog()

    def init_ui(self):
        self.setWindowTitle("AI Image Generator")
        self.setFixedSize(900, 700)  # Increased size to accommodate new elements
        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width() - 900) // 2, (screen.height() - 700) // 2)

        # Create menu bar
        self.create_menu_bar()

        self.setStyleSheet(
            """
            QMainWindow { background-color: #f5f5f5; }
            QLabel { color: #333333; }
            QPushButton {
                background-color: #141413;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #2a2a28; }
            QPushButton:disabled { background-color: #cccccc; color: #666666; }
            QTextEdit {
                border: 1px solid #666666;
                padding: 4px;
                font-size: 12px;
                border-radius: 5px;
            }
            QTextEdit:focus { border-color: #333333; }
            QComboBox {
                border: 1px solid #666666;
                padding: 6px;
                font-size: 12px;
                background-color: white;
                color: black;
                border-radius: 5px;
            }
            QComboBox:hover { border-color: #333333; }
            QComboBox:focus { border-color: #123456; }
            QComboBox::drop-down {
                width: 20px;
                border: none;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
                background-color: #141413;
            }
            QComboBox::down-arrow {
                width: 10px;
                height: 10px;
                image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAAAXNSR0IArs4c6QAAAERlWElmTU0AKgAAAAgAAYdpAAQAAAABAAAAGgAAAAAAA6ABAAMAAAABAAEAAKACAAQAAAABAAAACqADAAQAAAABAAAACgAAAAA2b0mQAAAATElEQVQ4EWNgYGBgSGH4z8DA8P7//4cE/f//PwP379//k/j//7/5gP7+/WMC9vb2KSDp6en/AeL7+3sSEhISEhISEhISEhLyAfEHALb6F/6N4q9FAAAAAElFTkSuQmCC);
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: black;
                selection-background-color: #e0e0e0;
                selection-color: black;
                border: 1px solid #666666;
                padding: 4px;
            }
            QLineEdit {
                border: 1px solid red;
                padding: 6px;
                font-size: 12px;
                border-radius: 5px;
            }
            QLineEdit:focus { border-color: #4CAF50; }
            QPushButton#downloadButton {
                background-color: #132B5D;
                color: white;
            }
            QPushButton#downloadButton:hover {
                background-color: #1e3f7a;
            }
            QPushButton#enhanceButton {
                background-color: #7B68EE;
                color: white;
            }
            QPushButton#enhanceButton:hover {
                background-color: #9370DB;
            }
            """
        )

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        left_panel = QWidget()
        left_panel.setMinimumWidth(350)  # Increased width
        left_layout = QVBoxLayout(left_panel)

        title = QLabel("🎨 AI Image Generator")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("margin: 8px 0; color: #000000;")
        left_layout.addWidget(title)

        prompt_label = QLabel("Enter Prompt:")
        prompt_label.setFont(QFont("Arial", 12, QFont.Bold))
        left_layout.addWidget(prompt_label)

        self.prompt_input = QTextEdit()
        self.prompt_input.setFixedHeight(100)
        self.prompt_input.setPlaceholderText(
            "Describe the image you want to generate..."
        )
        left_layout.addWidget(self.prompt_input)

        # Enhance prompt button
        self.enhance_btn = QPushButton("✨ Enhance Prompt")
        self.enhance_btn.setObjectName("enhanceButton")
        self.enhance_btn.clicked.connect(self.enhance_prompt)
        self.enhance_btn.setFixedHeight(40)
        left_layout.addWidget(self.enhance_btn)

        # Enhanced prompt section
        enhanced_prompt_label = QLabel("Enhanced Prompt (editable):")
        enhanced_prompt_label.setFont(QFont("Arial", 12, QFont.Bold))
        left_layout.addWidget(enhanced_prompt_label)

        self.enhanced_prompt_input = QTextEdit()
        self.enhanced_prompt_input.setFixedHeight(100)
        self.enhanced_prompt_input.setPlaceholderText(
            "Enhanced prompt will appear here (editable)..."
        )
        left_layout.addWidget(self.enhanced_prompt_input)

        size_label = QLabel("Image Size:")
        size_label.setFont(QFont("Arial", 12, QFont.Bold))
        left_layout.addWidget(size_label)

        self.size_combo = QComboBox()
        self.size_combo.addItems(
            [
                "Square (512x512)",
                "Square (1024x1024)",
                "Square (2000x2000)",
                "Portrait 3:4 (768x1024)",
                "Portrait 9:16 (576x1024)",
                "Landscape 4:3 (1024x768)",
                "Landscape 16:9 (1024x576)",
                "Landscape 16:9 (1280x720)",
                "Landscape 16:9 (1920x1080)",
                "Custom Size",
            ]
        )
        self.size_combo.setCurrentIndex(1)
        self.size_combo.currentTextChanged.connect(self.on_size_changed)
        left_layout.addWidget(self.size_combo)

        self.custom_size_label = QLabel("Custom Size (width x height):")
        self.custom_size_label.setFont(QFont("Arial", 10))
        self.custom_size_label.setVisible(False)
        left_layout.addWidget(self.custom_size_label)

        self.custom_size_input = QLineEdit()
        self.custom_size_input.setPlaceholderText("e.g., 800x600")
        self.custom_size_input.setVisible(False)
        left_layout.addWidget(self.custom_size_input)

        self.generate_btn = QPushButton("🚀 Generate Image")
        self.generate_btn.clicked.connect(self.generate_image)
        self.generate_btn.setFixedHeight(40)
        left_layout.addWidget(self.generate_btn)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        left_layout.addWidget(self.progress_bar)

        self.download_btn = QPushButton("💾 Download Image")
        self.download_btn.setObjectName("downloadButton")
        self.download_btn.clicked.connect(self.download_image)
        self.download_btn.setEnabled(False)
        self.download_btn.setFixedHeight(40)
        left_layout.addWidget(self.download_btn)

        left_layout.addStretch()

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        image_title = QLabel("Generated Image")
        image_title.setFont(QFont("Arial", 14, QFont.Bold))
        image_title.setAlignment(Qt.AlignCenter)
        image_title.setStyleSheet("margin: 8px 0; color: #000000;")
        right_layout.addWidget(image_title)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.image_label = ImageLabel()
        scroll_area.setWidget(self.image_label)
        right_layout.addWidget(scroll_area)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([350, 550])

        self.statusBar().showMessage("Ready to generate images")

    def create_menu_bar(self):
        menubar = self.menuBar()

        # Help menu
        help_menu = menubar.addMenu("Help")

        # Settings action
        settings_action = QAction("Settings", self)
        settings_action.setStatusTip("Application settings")
        settings_action.triggered.connect(self.show_settings_dialog)
        settings_action.setMenuRole(QAction.PreferencesRole)

        # About action
        about_action = QAction("About", self)
        about_action.setStatusTip("About AI Image Generator")
        about_action.triggered.connect(self.show_about_dialog)
        about_action.setMenuRole(QAction.AboutRole)

        # Add actions to menu in correct order
        help_menu.addAction(settings_action)
        help_menu.addSeparator()
        help_menu.addAction(about_action)

    def show_about_dialog(self):
        about_dialog = AboutDialog(self)
        about_dialog.exec_()

    def show_settings_dialog(self):
        dialog = SettingsDialog(self)
        if dialog.exec_():
            # Reload API key after settings dialog closes
            self.load_api_key()

    def on_size_changed(self, text):
        self.custom_size_label.setVisible(text == "Custom Size")
        self.custom_size_input.setVisible(text == "Custom Size")

    def check_api_key(self):
        if not self.api_key:
            QMessageBox.warning(
                self,
                "API Key Required",
                "Please enter your API key in the settings before using this feature.",
            )
            self.show_settings_dialog()
            return False
        return True

    def get_image_size(self):
        size_map = {
            "Square (512x512)": (512, 512),
            "Square (1024x1024)": (1024, 1024),
            "Square (2000x2000)": (2000, 2000),
            "Portrait 3:4 (768x1024)": (768, 1024),
            "Portrait 9:16 (576x1024)": (576, 1024),
            "Landscape 4:3 (1024x768)": (1024, 768),
            "Landscape 16:9 (1024x576)": (1024, 576),
            "Landscape 16:9 (1280x720)": (1280, 720),
            "Landscape 16:9 (1920x1080)": (1920, 1080),
        }

        if self.size_combo.currentText() == "Custom Size":
            try:
                width, height = map(
                    int, self.custom_size_input.text().lower().split("x")
                )
                return width, height
            except ValueError:
                return None, None

        return size_map.get(self.size_combo.currentText(), (1024, 1024))

    def enhance_prompt(self):
        if not self.check_api_key():
            return

        original_prompt = self.prompt_input.toPlainText().strip()
        if not original_prompt:
            QMessageBox.warning(self, "Warning", "Please enter a prompt to enhance")
            return

        self.enhance_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.statusBar().showMessage("Enhancing prompt...")

        self.prompt_enhancer = PromptEnhancerWorker(self.api_key, original_prompt)
        self.prompt_enhancer.finished.connect(self.on_prompt_enhanced)
        self.prompt_enhancer.error.connect(self.on_prompt_enhancement_error)
        self.prompt_enhancer.start()

    def on_prompt_enhanced(self, enhanced_prompt):
        self.enhance_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.enhanced_prompt_input.setPlainText(enhanced_prompt)
        self.statusBar().showMessage("Prompt enhanced successfully")
        # QMessageBox.information(
        #     self, "Success", "Prompt enhanced successfully! You can edit it if needed."
        # )

    def on_prompt_enhancement_error(self, error_message):
        self.enhance_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage("Prompt enhancement failed")
        QMessageBox.critical(
            self, "Error", f"Failed to enhance prompt: {error_message}"
        )

    def generate_image(self):
        if not self.check_api_key():
            return

        # Use enhanced prompt if available, otherwise use original prompt
        enhanced_prompt = self.enhanced_prompt_input.toPlainText().strip()
        original_prompt = self.prompt_input.toPlainText().strip()
        prompt = enhanced_prompt if enhanced_prompt else original_prompt

        if not prompt:
            QMessageBox.warning(
                self, "Warning", "Please enter a prompt or enhance an existing one"
            )
            return

        width, height = self.get_image_size()
        if not width or not height:
            QMessageBox.warning(
                self, "Warning", "Please enter a valid image size (e.g., 800x600)"
            )
            return

        if not (64 <= width <= 4096 and 64 <= height <= 4096):
            QMessageBox.warning(
                self, "Warning", "Image size must be between 64x64 and 4096x4096"
            )
            return

        self.generate_btn.setEnabled(False)
        self.download_btn.setEnabled(False)
        self.enhance_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.image_label.setText("Generating image...")
        self.statusBar().showMessage("Generating image...")

        self.worker = APIWorker(self.api_key, prompt, width, height)
        self.worker.finished.connect(self.on_generation_finished)
        self.worker.error.connect(self.on_generation_error)
        self.worker.start()

    def on_generation_finished(self, status_code, response_text, image_data):
        self.generate_btn.setEnabled(True)
        self.enhance_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

        if image_data and self.image_label.setImageFromData(image_data):
            self.current_image_data = image_data
            self.download_btn.setEnabled(True)
            self.statusBar().showMessage("Image generated successfully")
            # QMessageBox.information(self, "Success", "Image generated successfully")
        else:
            self.image_label.setText("Failed to generate image")
            self.statusBar().showMessage("Image generation failed")
            try:
                response_json = json.loads(response_text)
                error_msg = response_json.get("error", {}).get(
                    "message", "Unknown error"
                )
                QMessageBox.warning(
                    self,
                    "API Error",
                    f"API error: {error_msg}\nResponse: {response_text}",
                )
            except json.JSONDecodeError:
                QMessageBox.warning(
                    self,
                    "API Error",
                    f"Request failed with status {status_code}: {response_text}",
                )

    def on_generation_error(self, error_message):
        self.generate_btn.setEnabled(True)
        self.enhance_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.image_label.setText("Error occurred during generation")
        self.statusBar().showMessage("Generation failed")
        QMessageBox.critical(
            self, "Error", f"Failed to generate image: {error_message}"
        )

    def download_image(self):
        if not self.current_image_data:
            QMessageBox.warning(self, "Warning", "No image to download")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_str = "".join(
            random.choices(string.ascii_lowercase + string.digits, k=6)
        )
        default_filename = f"ai_image_{timestamp}_{random_str}.png"
        downloads_path = str(Path.home() / "Downloads")

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Image",
            os.path.join(downloads_path, default_filename),
            "PNG files (*.png);;JPEG files (*.jpg);;All files (*.*)",
        )

        if filename:
            try:
                with open(filename, "wb") as f:
                    f.write(self.current_image_data)
                self.statusBar().showMessage(f"Image saved to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save image: {e}")


def main():

    app = QApplication(sys.argv)
    # Force light palette for consistent appearance, so it doesnt default to dark mode
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(245, 245, 245))
    palette.setColor(QPalette.WindowText, Qt.black)
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.Text, Qt.black)
    palette.setColor(QPalette.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ButtonText, Qt.black)
    palette.setColor(QPalette.Highlight, QColor(123, 104, 238))  # Dark Violet
    app.setPalette(palette)

    app.setApplicationName("AI Image Generator")
    window = ImageGeneratorApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
