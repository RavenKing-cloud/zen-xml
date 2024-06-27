import sys
import os
import xml.etree.ElementTree as ET
from PyQt5.QtCore import Qt  # To use Qt.Alignment enums
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QTreeWidget, QTreeWidgetItem,
    QFileDialog, QTextEdit, QDialog, QHBoxLayout, QMenu, QAction, QCheckBox,
    QButtonGroup, QLabel, QDialogButtonBox, QMessageBox, QDesktopWidget, QPushButton
)

# Pre Main Loop Template Selection
class SizeSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ZenXML Start")
        self.setFixedSize(256, 200)

        layout = QVBoxLayout()

        size_label = QLabel("Select XML Template:")
        size_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(size_label)
        layout.setAlignment(size_label, Qt.AlignHCenter)

        self.small_checkbox = QCheckBox("Small")
        self.med_checkbox = QCheckBox("Medium")
        self.large_checkbox = QCheckBox("Large")

        checkbox_layout = QHBoxLayout()
        checkbox_layout.addStretch()
        checkbox_layout.addWidget(self.small_checkbox)
        checkbox_layout.addWidget(self.med_checkbox)
        checkbox_layout.addWidget(self.large_checkbox)
        checkbox_layout.addStretch()

        layout.addLayout(checkbox_layout)

        layout.addSpacing(40)
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.check_selection)  # Connect to custom slot
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

        self.button_group = QButtonGroup()
        self.button_group.addButton(self.small_checkbox)
        self.button_group.addButton(self.med_checkbox)
        self.button_group.addButton(self.large_checkbox)
        self.button_group.setExclusive(True)

    def check_selection(self):
        if not any([self.small_checkbox.isChecked(), self.med_checkbox.isChecked(), self.large_checkbox.isChecked()]):
            QMessageBox.critical(self, "Error", "Please select a template size.", QMessageBox.Ok)
        else:
            self.accept()


# Element Text Editor
class TextEditDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.text_edit = QTextEdit(self)
        layout.addWidget(self.text_edit)
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")  # Add this line to create the save_button
        self.save_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")  # Assuming cancel_button is defined elsewhere
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        self.setLayout(layout)


# Main GUI Implementation
class XMLEditorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("XML Editor")
        self.setGeometry(200, 100, 1200, 800)

        layout = QVBoxLayout()

        self.xml_tree_widget = QTreeWidget(self)
        self.xml_tree_widget.setHeaderLabels(["Element", "Attribute", "Value"])
        self.xml_tree_widget.setContextMenuPolicy(1)  # Custom context menu policy
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
        self.save_action = QAction("Save XML", self)
        self.save_action.triggered.connect(self.save_xml)
        file_menu.addAction(self.load_action)
        file_menu.addAction(self.save_action)

        edit_menu = menu_bar.addMenu("Edit")
        self.new_element_action = QAction("New Element", self)
        self.new_element_action.triggered.connect(self.create_new_element)
        edit_menu.addAction(self.new_element_action)

        self.xml_tree_widget.itemDoubleClicked.connect(self.open_text_editor)
        self.xml_tree_widget.setEditTriggers(QTreeWidget.SelectedClicked | QTreeWidget.EditKeyPressed)

        self.define_context_menu()

    def load_template_xml(self, template_size):
        template_filename = f"template_{template_size}.xml"
        template_path = os.path.join(os.path.dirname(__file__), template_folder, template_filename)

        # Load the selected template XML directly into the tree widget
        self.xml_tree_widget.clear()
        tree = ET.parse(template_path)
        root = tree.getroot()
        self.populate_tree_widget(root, self.xml_tree_widget)

    def load_xml(self):
        script_directory = os.path.dirname(os.path.abspath(__file__))
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

    def define_context_menu(self):
        self.context_menu = QMenu(self.xml_tree_widget)
        self.duplicate_action = QAction("Duplicate", self)
        self.duplicate_action.triggered.connect(self.duplicate_item)
        self.delete_action = QAction("Delete", self)
        self.delete_action.triggered.connect(self.delete_item)  # Connect to the delete_item method
        self.context_menu.addAction(self.duplicate_action)
        self.context_menu.addAction(self.delete_action)  # Add the delete action


    def contextMenuEvent(self, event):
        selected_item = self.xml_tree_widget.currentItem()
        if selected_item:
            self.context_menu.exec_(event.globalPos())

    def create_new_element(self):
        return

    def duplicate_item(self):
        selected_item = self.xml_tree_widget.currentItem()
        if selected_item:
            parent_item = selected_item.parent() if selected_item.parent() else self.xml_tree_widget.invisibleRootItem()
            new_item = QTreeWidgetItem(parent_item)
            self.copy_item(selected_item, new_item)
            self.xml_tree_widget.expandItem(new_item)

    def delete_item(self):
        selected_item = self.xml_tree_widget.currentItem()
        if selected_item:
            parent_item = selected_item.parent() if selected_item.parent() else self.xml_tree_widget.invisibleRootItem()
            parent_item.removeChild(selected_item)

    def copy_item(self, source_item, target_item):
        target_item.setText(0, source_item.text(0))
        target_item.setText(1, source_item.text(1))
        target_item.setText(2, source_item.text(2))
        for i in range(source_item.childCount()):
            source_child_item = source_item.child(i)
            new_child_item = QTreeWidgetItem(target_item)
            self.copy_item(source_child_item, new_child_item)

    def open_text_editor(self, item, column):
        dialog = TextEditDialog(self)
        if column == 0:
            dialog.setWindowTitle("Edit Element Name")
        elif column == 1:
            dialog.setWindowTitle("Edit Attribute Name")
        else:
            dialog.setWindowTitle("Edit Value")
        dialog.text_edit.setPlainText(item.text(column))
        if dialog.exec_() == QDialog.Accepted:
            item.setText(column, dialog.text_edit.toPlainText())
            item.setExpanded(False)  # Collapse the item after editing

    def serialize_tree_item(self, item, level=0):
        element = ET.Element(item.text(0))
        if item.text(1):
            element.set("name", item.text(1))
        element.text = item.text(2)
    
        # Define the indentation string (4 spaces) based on the current level
        indentation = "\t" * level
    
        # Add indentation before the element's children
        if item.childCount() > 0:
            element.text = "\n" + indentation + "\t"
    
        for i in range(item.childCount()):
            child_element = self.serialize_tree_item(item.child(i), level + 1)
            element.append(child_element)
    
        # Add indentation after the element's children, if there are children
        if item.childCount() > 0:
            element[-1].tail = "\n" + indentation
    
        return element

    def save_xml(self):
        script_directory = os.path.dirname(os.path.abspath(__file__))
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save XML File", script_directory, "XML Files (*.xml);;All Files (*)", options=options
        )
        if file_name:
            try:
                if not file_name.lower().endswith('.xml'):
                    file_name += '.xml'  # Append .xml extension if not already present
                
                root = self.xml_tree_widget.topLevelItem(0)
                xml_content = self.serialize_tree_item(root)
                xml_str = ET.tostring(xml_content, encoding="utf-8").decode("utf-8")
                with open(file_name, "w") as file:
                    file.write(xml_str)
            except Exception as e:
                print(f"Error while saving XML: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    template_path = os.path.join(os.path.dirname(__file__))
    template_folder = os.path.join(template_path, "template")

    size_selection_dialog = SizeSelectionDialog()
    result = size_selection_dialog.exec_()

    if result == QDialog.Accepted:
        selected_size = None
        if size_selection_dialog.small_checkbox.isChecked():
            selected_size = "small"
        elif size_selection_dialog.med_checkbox.isChecked():
            selected_size = "medium"
        elif size_selection_dialog.large_checkbox.isChecked():
            selected_size = "large"

        if selected_size:
            xml_editor = XMLEditorGUI()
            xml_editor.load_template_xml(selected_size)
            screen_center = QDesktopWidget().availableGeometry().center()
            xml_editor.move(screen_center - xml_editor.rect().center())
            xml_editor.show()
            sys.exit(app.exec_())