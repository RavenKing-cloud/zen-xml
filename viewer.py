import sys
import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QTreeWidget, QTreeWidgetItem,
    QFileDialog, QAction, QDesktopWidget
)

# Main GUI Implementation
class XMLEditorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("XML Viewer")
        self.setGeometry(200, 100, 1200, 800)

        layout = QVBoxLayout()

        self.xml_tree_widget = QTreeWidget(self)
        self.xml_tree_widget.setHeaderLabels(["Element", "Attribute", "Value"])
        self.xml_tree_widget.setFocusPolicy(0)  # Prevent orange border on selection
        self.xml_tree_widget.setStyleSheet(
            "QTreeWidget::item { border: 1px solid #ccc; border-radius: 5px; padding: 2px; }"
        )

        layout.addWidget(self.xml_tree_widget)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")
        self.load_action = QAction("Load XML", self)
        self.load_action.triggered.connect(self.load_xml)
        file_menu.addAction(self.load_action)

    def load_xml(self):
        script_directory = "/Users/RavenKing/Documents/_ravenking/_gitHub/_Python/betaTesting/subModel/advanced/data"
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "Open XML File", script_directory, "XML Files (*.xml)", options=options)
        if file_name:
            try:
                self.xml_tree_widget.clear()
                tree = ET.parse(file_name)
                root = tree.getroot()
                self.populate_tree_widget(root, self.xml_tree_widget)
            except Exception as e:
                print(f"Error while loading XML: {e}")

    def populate_tree_widget(self, element, parent_item):
        item = QTreeWidgetItem(parent_item, [element.tag, element.get("name", ""), element.text])
        self.xml_tree_widget.setColumnWidth(0, 600)  # Adjust the width of the "Element" column
        self.xml_tree_widget.setColumnWidth(1, 400)  # Adjust the width of the "Attribute" column
        for child in element:
            self.populate_tree_widget(child, item)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    xml_editor = XMLEditorGUI()
    screen_center = QDesktopWidget().availableGeometry().center()
    xml_editor.move(screen_center - xml_editor.rect().center())
    xml_editor.show()
    sys.exit(app.exec_())