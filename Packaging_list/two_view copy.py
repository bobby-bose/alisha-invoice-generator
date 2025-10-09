# dashboard.py
from pymongo import MongoClient
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView
)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
from Packaging_list.two_edit import PackingListFormEdit
from Packaging_list.two import PackingListForm
import os
from datetime import datetime
from Packaging_list.delete import start
import json
from docx import Document

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
        self.setStyleSheet("background-color: #ffffff;color:black")  # White background
        self.docs = fetch_exporter_docs()
        self.edit_windows = []
        self.initUI()

    def open_add_form(self):
        try:
            add_window = PackingListForm()
            self.edit_windows.append(add_window)
            add_window.show()
        except Exception as e:
            # Create a custom QMessageBox with black text
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("Error")
            msg_box.setText(f"Failed to open Add form: {str(e)}")
            msg_box.setStyleSheet("QLabel { color: black; } QPushButton { color: black; }")
            msg_box.exec()


    def initUI(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Header
        header_layout = QHBoxLayout()
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo = QLabel()
        pixmap = QPixmap("wwe.jpg")
        if not pixmap.isNull():
            logo.setPixmap(pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio))
        else:
            logo.setText("No Logo")
        header_layout.addWidget(logo)

        info_layout = QVBoxLayout()
        info_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label = QLabel("ZAKA Controls & Devices")
        name_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        name_label.setStyleSheet("color: black;")
        info_layout.addWidget(name_label)
        header_layout.addLayout(info_layout)

        layout.addLayout(header_layout)

        # Add button
        btn_add = QPushButton("➕  Add")
        btn_add.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        
        btn_add.setStyleSheet("background-color: #28a745; color: black; padding: 10px 20px; border-radius: 8px;")
        btn_add.clicked.connect(self.open_add_form)
        layout.addWidget(btn_add, alignment=Qt.AlignmentFlag.AlignCenter)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Consignee Address", "PO No", "Date", "Tax No", "Packing List No",
            "Edit", "Hide", "Print"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setFont(QFont("Arial", 14))
        self.table.setStyleSheet("""
            QTableWidget { background-color: #ffffff; gridline-color: #dfe3ee;color: black; }
            QHeaderView::section { background-color: #f0f0f0; font-weight: bold; font-size: 14px;color: black; }
            QTableWidget::item { padding: 8px; font-size: 14px; color: black; }
        """)
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.load_table_data()

    def load_table_data(self):
        from functools import partial
        self.docs = fetch_exporter_docs()
        self.table.setRowCount(0)

        for row_index, doc in enumerate(self.docs):
            self.table.insertRow(row_index)
            for col, key in enumerate(["consignee_address", "po_no", "date", "tax_no", "packing_list_no"]):
                item = QTableWidgetItem(doc.get(key, ""))
                item.setFont(QFont("Arial", 13))
                item.setForeground(Qt.GlobalColor.black)
                self.table.setItem(row_index, col, item)

            # Edit button
            btn_edit = QPushButton("✏ Edit")
            btn_edit.setFont(QFont("Arial", 12))
            btn_edit.setStyleSheet("color: black;")  # Edit button text black
            btn_edit.clicked.connect(partial(self.open_edit_form, doc))
            self.table.setCellWidget(row_index, 5, btn_edit)

            # Hide button
            btn_hide = QPushButton("🙈 Hide")
            btn_hide.setFont(QFont("Arial", 12))
            btn_hide.setStyleSheet("color: black;")  # Hide button text black
            btn_hide.clicked.connect(partial(self.hide_row, row_index))
            self.table.setCellWidget(row_index, 6, btn_hide)

            # Print button
            btn_print = QPushButton("🖨 Print")
            btn_print.setFont(QFont("Arial", 12))

            btn_print.setStyleSheet("color: black;") # Print button text black
            btn_print.clicked.connect(partial(self.generate_docx_in_outputs, doc))
            self.table.setCellWidget(row_index, 7, btn_print)

            self.table.setRowHeight(row_index, 60)

    def open_edit_form(self, doc):
        edit_window = PackingListFormEdit(str(doc["_id"]))
        self.edit_windows.append(edit_window)
        edit_window.updated.connect(self.load_table_data)
        edit_window.show()

    def hide_row(self, row):
        self.table.hideRow(row)
        QMessageBox.information(self, "Hidden", "Row hidden from table.")

    def generate_docx_in_outputs(self, doc):
        try:
            import os
            import json
            import datetime
            from bson import ObjectId, Decimal128, DBRef, Timestamp

            # ---------- Robust recursive cleaner ----------
            def clean_mongo_doc(doc):
                if isinstance(doc, dict):
                    return {k: clean_mongo_doc(v) for k, v in doc.items()}
                elif isinstance(doc, list):
                    return [clean_mongo_doc(v) for v in doc]
                elif isinstance(doc, ObjectId):
                    return str(doc)
                elif isinstance(doc, Decimal128):
                    return float(doc.to_decimal())
                elif isinstance(doc, (datetime.datetime, datetime.date)):
                    return doc.isoformat()
                elif isinstance(doc, DBRef):
                    return str(doc)
                elif isinstance(doc, Timestamp):
                    return int(doc.time)
                else:
                    return doc

            # ---------- Path to data.json ----------
            base_dir = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.join(base_dir, "data.json")

            # ---------- Fetch the document ----------
            doc_id = doc["_id"]
            mongo_doc = collection.find_one({"_id": doc_id})
            if not mongo_doc:
                QMessageBox.warning(self, "Warning", f"No data found for this ID: {doc_id}")
                return

            # ---------- Clean it ----------
            mongo_doc_cleaned = clean_mongo_doc(mongo_doc)

            # ---------- Write to JSON ----------
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(mongo_doc_cleaned, f, ensure_ascii=False, indent=4)

            print(f"📄 data.json updated for ID: {doc_id}")

            # ---------- Generate DOCX ----------
            start()
            QMessageBox.information(self, "Success", "DOCX and PDF generated!")

        except Exception as e:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("Error")
            msg_box.setText(f"Failed to generate document: {str(e)}")
            msg_box.setStyleSheet("QLabel { color: black; } QPushButton { color: black; }")
            msg_box.exec()

# ---------------- Run App ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PackingListTable()
    window.show()
    sys.exit(app.exec())
