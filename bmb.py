import sys, os
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget,
    QLineEdit, QPushButton, QToolBar,
    QWidget, QVBoxLayout, QLabel, QFileDialog
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import (
    QWebEngineProfile, QWebEnginePage, QWebEngineDownloadRequest
)

# ================= PATHS =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PAGES_DIR = os.path.join(BASE_DIR, "pages")
PROFILES_DIR = os.path.join(BASE_DIR, "profiles")

HOME_URL = QUrl.fromLocalFile(os.path.join(PAGES_DIR, "home.html"))
SNAKE_URL = QUrl.fromLocalFile(os.path.join(PAGES_DIR, "snake.html"))

os.makedirs(PROFILES_DIR, exist_ok=True)

# ================= PROFILE CHOOSER =================
class ProfileChooser(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BMB PRO 3.1 — Choose Profile")
        self.resize(300, 300)

        layout = QVBoxLayout(self)
        label = QLabel("Select profile")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        self.selected = None

        for name in ["user1", "user2", "user3", "user4", "indigo"]:
            btn = QPushButton(name)
            btn.clicked.connect(lambda _, n=name: self.choose(n))
            layout.addWidget(btn)

    def choose(self, name):
        self.selected = name
        self.close()

# ================= TAB =================
class BrowserTab(QWebEngineView):
    def __init__(self, profile):
        super().__init__()
        self.setPage(QWebEnginePage(profile, self))

# ================= MAIN WINDOW =================
class Browser(QMainWindow):
    def __init__(self, profile_name):
        super().__init__()
        self.fullscreen = False

        # ===== TABS =====
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.sync_urlbar)
        self.setCentralWidget(self.tabs)

        # ===== TOOLBAR =====
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

        self.add_btn("⬅", self.go_back)
        self.add_btn("➡", self.go_forward)
        self.add_btn("🔄", self.reload_page)
        self.add_btn("🏠", self.go_home)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.load_url)
        self.toolbar.addWidget(self.url_bar)

        self.add_btn("GO", self.load_url)
        self.add_btn("+ Tab", self.new_tab)
        self.add_btn("🐍 Snake", self.open_snake)

        # ===== PROFILE =====
        if profile_name == "indigo":
            self.profile = QWebEngineProfile(self)
            self.setWindowTitle("BMB PRO 3.1 — Indigo (Incognito)")
        else:
            self.profile = self.create_profile(profile_name)
            self.setWindowTitle(f"BMB PRO 3.1 — Profile: {profile_name}")

        self.profile.downloadRequested.connect(self.handle_download)

        self.resize(1200, 800)
        self.new_tab()

    # ================= PROFILE =================
    def create_profile(self, name):
        path = os.path.join(PROFILES_DIR, name)
        os.makedirs(path, exist_ok=True)

        profile = QWebEngineProfile(name, self)
        profile.setPersistentStoragePath(path)
        profile.setCachePath(path)
        return profile

    # ================= NAVIGATION =================
    def go_back(self):
        self.tabs.currentWidget().back()

    def go_forward(self):
        self.tabs.currentWidget().forward()

    def reload_page(self):
        self.tabs.currentWidget().reload()

    def go_home(self):
        self.tabs.currentWidget().setUrl(HOME_URL)

    # ================= TABS =================
    def new_tab(self):
        tab = BrowserTab(self.profile)
        tab.setUrl(HOME_URL)
        tab.urlChanged.connect(lambda url, t=tab: self.update_urlbar(url, t))
        self.tabs.addTab(tab, "Tab")
        self.tabs.setCurrentWidget(tab)

    def open_snake(self):
        tab = BrowserTab(self.profile)
        tab.setUrl(SNAKE_URL)
        self.tabs.addTab(tab, "Snake")
        self.tabs.setCurrentWidget(tab)

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)

    # ================= URL =================
    def load_url(self):
        text = self.url_bar.text().strip()

        if os.path.exists(text):
            url = QUrl.fromLocalFile(text)
        else:
            url = QUrl(text)
            if not url.scheme():
                url.setScheme("https")

        self.tabs.currentWidget().setUrl(url)

    def update_urlbar(self, url, tab):
        if self.tabs.currentWidget() == tab:
            self.url_bar.setText(url.toString())

    def sync_urlbar(self):
        tab = self.tabs.currentWidget()
        if tab:
            self.url_bar.setText(tab.url().toString())

    # ================= DOWNLOAD =================
    def handle_download(self, download: QWebEngineDownloadRequest):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save file", download.downloadFileName()
        )
        if path:
            download.setDownloadFileName(os.path.basename(path))
            download.setPath(path)
            download.accept()

    # ================= UI =================
    def add_btn(self, text, func):
        btn = QPushButton(text)
        btn.clicked.connect(func)
        self.toolbar.addWidget(btn)

    # ================= FULLSCREEN =================
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_F11:
            self.setWindowState(
                Qt.WindowState.WindowFullScreen
                if not self.isFullScreen()
                else Qt.WindowState.WindowNoState
            )

# ================= RUN =================
app = QApplication(sys.argv)

chooser = ProfileChooser()
chooser.show()
app.exec()

if chooser.selected:
    window = Browser(chooser.selected)
    window.show()
    sys.exit(app.exec())
