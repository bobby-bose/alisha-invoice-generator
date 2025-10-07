from pymongo import MongoClient
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView
)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
from two_edit import PackingListFormEdit  # Edit form
import os
import json
from docxtpl import DocxTemplate  # <-- pip install docxtpl

# ---------------- MongoDB Config ----------------
MONGO_URL = "mongodb+srv://admin:admin@cluster.rnhig2f.mongodb.net/?retryWrites=true&w=majority&appName=cluster"
DB_NAME = "mamshi"
COLLECTION_NAME = "report_two"

client = MongoClient(MONGO_URL)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# ---------------- Fetch Data ----------------
def fetch_exporter_docs():
    try:
        docs = list(collection.find({"consignee_address": {"$exists": True}}))
        print(f"✅ {len(docs)} documents found")
        return docs
    except Exception as e:
        print("❌ MongoDB Error:", str(e))
        return []

# ---------------- UI Class ----------------
class PackingListTable(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Packing List Viewer")
        self.setGeometry(100, 50, 1400, 900)

        self.setStyleSheet("""
            QWidget { background-color: #ffffff; font-family: Arial; }
            QLabel { color: #1c1e21; font-weight: bold; }
            QPushButton { background-color: #1877f2; color: white; font-weight: bold; font-size: 15px; border-radius: 6px; padding: 6px 12px; }
            QPushButton:hover { background-color: #166fe5; }
            QTableWidget { border: 2px solid #ccd0d5; border-radius: 10px; gridline-color: #dfe3ee; background-color: #f5f6f7; selection-background-color: #1877f2; selection-color: white; }
            QHeaderView::section { background-color: #e4e6eb; font-weight: bold; color: #050505; padding: 8px; border: none; }
            QTableWidget::item { padding: 10px; color: #000000; font-weight: bold; }
        """)

        self.docs = fetch_exporter_docs()
        self.edit_windows = []
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # ---------- Header ----------
        header_layout = QHBoxLayout()
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo = QLabel()
        pixmap = QPixmap("wwe.jpg")
        if not pixmap.isNull():
            pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo.setPixmap(pixmap)
        else:
            logo.setText("No Logo")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(logo)

        info_layout = QVBoxLayout()
        info_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name = QLabel("ZAKA Controls & Devices")
        name.setFont(QFont("Arial", 26, QFont.Weight.Bold))
        desc = QLabel("Packing List Records (MongoDB)")
        desc.setFont(QFont("Arial", 18))
        info_layout.addWidget(name)
        info_layout.addWidget(desc)
        header_layout.addLayout(info_layout)

        layout.addLayout(header_layout)
        layout.addSpacing(20)

        # ---------- Table ----------
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Consignee Address", "PO No", "Date", "Tax No", "Packing List No",
            "Edit", "Hide", "Print"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setFont(QFont("Arial", 12, QFont.Weight.Bold))

        self.load_table_data()
        layout.addWidget(self.table)
        self.setLayout(layout)

    def load_table_data(self):
        """Reload table data from MongoDB"""
        self.docs = fetch_exporter_docs()
        self.table.setRowCount(0)

        for row_index, doc in enumerate(self.docs):
            self.table.insertRow(row_index)

            self.table.setItem(row_index, 0, QTableWidgetItem(doc.get("consignee_address", "")))
            self.table.setItem(row_index, 1, QTableWidgetItem(doc.get("po_no", "")))
            self.table.setItem(row_index, 2, QTableWidgetItem(doc.get("date", "")))
            self.table.setItem(row_index, 3, QTableWidgetItem(doc.get("tax_no", "")))
            self.table.setItem(row_index, 4, QTableWidgetItem(doc.get("packing_list_no", "")))

            # Buttons
            btn_edit = QPushButton("✏ Edit")
            btn_edit.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; border-radius: 6px;")
            btn_edit.clicked.connect(lambda _, d=doc: self.open_edit_form(d))
            self.table.setCellWidget(row_index, 5, btn_edit)

            btn_hide = QPushButton("🙈 Hide")
            btn_hide.setStyleSheet("background-color: #ff9800; color: white; font-weight: bold; border-radius: 6px;")
            btn_hide.clicked.connect(lambda _, r=row_index: self.hide_row(r))
            self.table.setCellWidget(row_index, 6, btn_hide)

            btn_print = QPushButton("🖨 Print")
            btn_print.setStyleSheet("background-color: #2196f3; color: white; font-weight: bold; border-radius: 6px;")
            btn_print.clicked.connect(lambda _, d=doc: self.generate_json_and_docx(d))
            self.table.setCellWidget(row_index, 7, btn_print)

            self.table.setRowHeight(row_index, 60)

    def open_edit_form(self, doc):
        try:
            edit_window = PackingListFormEdit(str(doc["_id"]))
            self.edit_windows.append(edit_window)
            edit_window.updated.connect(self.load_table_data)
            edit_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open edit form: {str(e)}")

    def hide_row(self, row):
        self.table.hideRow(row)
        QMessageBox.information(self, "Hidden", "Row has been hidden from the table view.")

    def generate_json_and_docx(self, doc):
        """Single-step: Save JSON & generate DOCX"""
        try:
            data = {k: v for k, v in doc.items() if k != "_id"}

            # Save JSON
            json_filename = f"data_packing_list_{doc.get('packing_list_no', 'output')}.json"
            json_path = os.path.join(os.path.dirname(__file__), json_filename)
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            # Load DOCX template
            template_path = os.path.join(os.path.dirname(__file__), "2.docx")
            if not os.path.exists(template_path):
                QMessageBox.warning(self, "Template Missing", f"Template not found: {template_path}")
                return

            docx = DocxTemplate(template_path)
            docx.render(data)

            output_docx_filename = f"PackingList_{doc.get('packing_list_no', 'output')}.docx"
            output_docx_path = os.path.join(os.path.dirname(__file__), output_docx_filename)
            docx.save(output_docx_path)

            QMessageBox.information(self, "Success",
                f"JSON and DOCX generated successfully!\n\nJSON: {json_path}\nDOCX: {output_docx_path}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate DOCX: {str(e)}")


# ---------------- Run App ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PackingListTable()
    window.show()
    sys.exit(app.exec())
