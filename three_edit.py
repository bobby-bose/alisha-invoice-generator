import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QGroupBox, QMessageBox, QScrollArea, QSizePolicy
)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt, pyqtSignal
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

# ---------------- MongoDB Config ----------------
MONGO_URL = "mongodb+srv://admin:admin@cluster.rnhig2f.mongodb.net/?retryWrites=true&w=majority&appName=cluster"
DB_NAME = "mamshi"
COLLECTION_NAME = "report_two"

class InvoiceFormEdit(QWidget):
    updated = pyqtSignal()

    def __init__(self, doc_id):
        super().__init__()
        self.doc_id = doc_id
        self.setWindowTitle("Edit Invoice Form")
        self.setGeometry(100, 50, 1200, 900)

        self.fields = [
            "invoice_date", "invoice_no", "po_no", "ref_no", "our_ref_no",
            "bill_address", "line_no", "items", "qty", "units", "total",
            "total_amount", "discount_percentage", "discount_amount", "received_details",
            "received_amount", "balance_amount", "country", "port_embarkation",
            "port_discharge", "date_by", "prepared_by", "verified_by", "authorized_by"
        ]
        self.controllers = {}
        self.doc_data = self.fetch_doc_data()
        self.initUI()

    def fetch_doc_data(self):
        try:
            client = MongoClient(MONGO_URL)
            db = client[DB_NAME]
            collection = db[COLLECTION_NAME]
            doc = collection.find_one({"_id": ObjectId(self.doc_id)})
            return doc if doc else {}
        except Exception as e:
            print("❌ MongoDB Error:", str(e))
            return {}

    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # ---------- Header ----------
        header_layout = QHBoxLayout()
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo = QLabel()
        pixmap = QPixmap("wwe.jpg")
        if not pixmap.isNull():
            pixmap = pixmap.scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo.setPixmap(pixmap)
        else:
            logo.setText("No Logo")
        header_layout.addWidget(logo)

        company_name = QLabel("ZAKA Controls & Devices — Edit Invoice")
        company_name.setFont(QFont("Arial", 26, QFont.Weight.Bold))
        header_layout.addWidget(company_name)
        main_layout.addLayout(header_layout)
        main_layout.addSpacing(20)

        # ---------- Scroll Area ----------
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        for i in range(0, len(self.fields), 4):
            row_layout = QHBoxLayout()
            row_layout.setSpacing(30)

            for field_group in [self.fields[i:i+2], self.fields[i+2:i+4]]:
                group_layout = QVBoxLayout()
                for field_name in field_group:
                    group_layout.addLayout(self.build_field_layout(field_name))
                group_box = QGroupBox()
                group_box.setLayout(group_layout)
                group_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                row_layout.addWidget(group_box)

            scroll_layout.addLayout(row_layout)
            scroll_layout.addSpacing(15)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        # ---------- Submit Button ----------
        submit_btn = QPushButton("✅ Update Invoice")
        submit_btn.setFixedHeight(45)
        submit_btn.setFixedWidth(300)
        submit_btn.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; border-radius: 8px;")
        submit_btn.clicked.connect(self.handle_submit)
        main_layout.addWidget(submit_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addSpacing(20)

        self.setLayout(main_layout)

    def build_field_layout(self, field_name):
        layout = QVBoxLayout()
        label = QLabel(field_name.replace("_", " ").title())
        label.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        line_edit = QLineEdit()
        line_edit.setFont(QFont("Arial", 12))
        line_edit.setFixedHeight(30)
        line_edit.setText(str(self.doc_data.get(field_name, "")))  # ✅ preload
        self.controllers[field_name] = line_edit
        layout.addWidget(label)
        layout.addWidget(line_edit)
        return layout

    def handle_submit(self):
        unfilled = [f for f, c in self.controllers.items() if not c.text().strip()]
        if unfilled:
            QMessageBox.warning(self, "Unfilled Fields", f"Please fill: {', '.join(unfilled)}")
            return

        data = {f: c.text() for f, c in self.controllers.items()}
        data["last_updated_date"] = datetime.now().strftime("%Y-%m-%d")
        data["last_updated_time"] = datetime.now().strftime("%H:%M:%S")

        try:
            client = MongoClient(MONGO_URL)
            db = client[DB_NAME]
            collection = db[COLLECTION_NAME]
            collection.update_one({"_id": ObjectId(self.doc_id)}, {"$set": data})
            QMessageBox.information(self, "Success", "✅ Invoice updated successfully!")
            self.updated.emit()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update: {str(e)}")
