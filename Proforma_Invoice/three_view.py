from pymongo import MongoClient
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QFrame
)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
# lso try to import the InvoiceFormEdit from the sibling file three_edit.py
from Proforma_Invoice.three_edit import InvoiceFormEdit
import json
import os
from Proforma_Invoice.sub_merge import perform_mail_merge
# ---------------- MongoDB Config ----------------
MONGO_URL = "mongodb+srv://username:password@cluster.rnhig2f.mongodb.net/?retryWrites=true&w=majority&appName=cluster"
DB_NAME = "mamshi"
COLLECTION_NAME = "report_two"

client = MongoClient(MONGO_URL)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]


def fetch_invoice_docs():
    try:
        docs = list(collection.find({"invoice_no": {"$exists": True}}))
        print(f"✅ {len(docs)} invoices found")
        return docs
    except Exception as e:
        print("❌ MongoDB Error:", str(e))
        return []


class InvoiceTable(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Invoice Data Viewer")
        self.setGeometry(100, 50, 1300, 900)

        self.setStyleSheet("""
            QWidget { background-color: #ffffff; font-family: Arial; }
            QLabel { color: #1c1e21; font-weight: bold; }
            QPushButton { 
                color: white; 
                font-weight: bold; 
                font-size: 15px; 
                border-radius: 6px; 
                padding: 6px 12px; 
            }
            QPushButton:hover { opacity: 0.9; }
            QTableWidget { 
                border: 2px solid #ccd0d5; 
                border-radius: 10px; 
                background-color: #f5f6f7; 
                selection-background-color: #1877f2; 
                selection-color: white; 
            }
            QHeaderView::section { 
                background-color: #e4e6eb; 
                font-weight: bold; 
                color: #050505; 
                padding: 8px; 
                border: none; 
            }
        """)

        self.docs = fetch_invoice_docs()
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
            pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio,
                                   Qt.TransformationMode.SmoothTransformation)
            logo.setPixmap(pixmap)
        else:
            logo.setText("No Logo")
        header_layout.addWidget(logo)

        title = QLabel("ZAKA Controls & Devices — Invoice Records")
        title.setFont(QFont("Arial", 26, QFont.Weight.Bold))
        header_layout.addWidget(title)

        layout.addLayout(header_layout)
        layout.addSpacing(20)

        # ---------- Table ----------
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Invoice No", "Invoice Date", "PO No", "Bill Address", "Total Amount",
            "Edit", "Print", "Hide"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.load_table_data()
        layout.addWidget(self.table)
        self.setLayout(layout)

    def load_table_data(self):
        self.docs = fetch_invoice_docs()
        self.table.setRowCount(0)

        for row_index, doc in enumerate(self.docs):
            self.table.insertRow(row_index)

            # Create styled, centered QTableWidgetItem
            def make_item(text):
                item = QTableWidgetItem(str(text))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setFont(QFont("Arial", 11, QFont.Weight.Bold))
                item.setForeground(Qt.GlobalColor.black)
                return item
                
            self.table.setItem(row_index, 0, make_item(doc.get("invoice_no", "")))      # Invoice No
            self.table.setItem(row_index, 1, make_item(doc.get("invoice_date", "")))    # Invoice Date
            self.table.setItem(row_index, 2, make_item(doc.get("po_no", "")))           # PO No
            self.table.setItem(row_index, 3, make_item(doc.get("bill_address", "")))    # Bill Address
            self.table.setItem(row_index, 4, make_item(doc.get("total_amount", "")))    # Total Amount
       

            # Create a container frame for buttons
            def create_button_container(buttons):
                frame = QFrame()
                frame_layout = QHBoxLayout(frame)
                frame_layout.setContentsMargins(8, 4, 8, 4)
                frame_layout.setSpacing(10)
                frame_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                for btn in buttons:
                    frame_layout.addWidget(btn)
                return frame

            # --- Edit Button ---
            btn_edit = QPushButton("✏ Edit")
            btn_edit.setStyleSheet("background-color: #28a745;")
            btn_edit.clicked.connect(lambda _, d=doc: self.open_edit_form(d))

            # --- Print Button ---
            btn_print = QPushButton("🖨 Print")
            btn_print.setStyleSheet("background-color: #007bff;")
            btn_print.clicked.connect(lambda _, d=doc: self.print_invoice(d))

            # --- Hide Button ---
            btn_hide = QPushButton("🙈 Hide")
            btn_hide.setStyleSheet("background-color: #ff9800;")
            btn_hide.clicked.connect(lambda _, r=row_index: self.hide_row(r))

            # Add buttons to cells
            self.table.setCellWidget(row_index, 5, create_button_container([btn_edit]))
            self.table.setCellWidget(row_index, 6, create_button_container([btn_print]))
            self.table.setCellWidget(row_index, 7, create_button_container([btn_hide]))

            self.table.setRowHeight(row_index, 60)

    def open_edit_form(self, doc):
        try:
            edit_window = InvoiceFormEdit(str(doc["_id"]))
            self.edit_windows.append(edit_window)
            edit_window.updated.connect(self.load_table_data)
            edit_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Cannot open edit form: {str(e)}")

    

    def print_invoice(self, doc):
        from bson import ObjectId
        from datetime import datetime

        def convert_objectid(doc):
            """
            Recursively convert ObjectId to string in a dict.
            """
            if isinstance(doc, dict):
                return {k: convert_objectid(v) for k, v in doc.items()}
            elif isinstance(doc, list):
                return [convert_objectid(i) for i in doc]
            elif isinstance(doc, ObjectId):
                return str(doc)
            else:
                return doc

        try:
            doc_serializable = convert_objectid(doc)
            # 1️⃣ Generate data.json from the MongoDB doc
            with open("data.json", "w", encoding="utf-8") as f:
                json.dump(doc_serializable, f, indent=4, ensure_ascii=False)

            # 2️⃣ Paths
            TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "3.docx")
            OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
            os.makedirs(OUTPUT_DIR, exist_ok=True)

            # 3️⃣ Generate human-readable timestamp
            now = datetime.now()
            day = now.day
            # Day suffix
            day_suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
            timestamp = f"{day}{day_suffix} of {now.strftime('%B')} of {now.year} - {now.strftime('%I.%M%p').lstrip('0')}"

            OUTPUT_PATH = os.path.join(OUTPUT_DIR, f"report-{timestamp}.docx")

            # 4️⃣ Perform mail merge
            perform_mail_merge("data.json", TEMPLATE_PATH, OUTPUT_PATH)

            QMessageBox.information(
                self, "Success", f"Invoice generated successfully:\n{OUTPUT_PATH}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Cannot generate invoice: {str(e)}")

    def hide_row(self, row):
        self.table.hideRow(row)
        QMessageBox.information(self, "Hidden", "Row hidden from view.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InvoiceTable()
    window.show()
    sys.exit(app.exec())
