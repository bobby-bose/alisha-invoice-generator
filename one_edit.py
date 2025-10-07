import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QGroupBox, QMessageBox, QScrollArea, QSizePolicy
)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

# ---------------- MongoDB Config ----------------
MONGO_URL = "mongodb+srv://admin:admin@cluster.rnhig2f.mongodb.net/?retryWrites=true&w=majority&appName=cluster"
DB_NAME = "mamshi"
COLLECTION_NAME = "report_two"

class ExportFormEdit(QWidget):
    def __init__(self, doc):
        super().__init__()
        self.setWindowTitle("Edit Export Form")
        self.setGeometry(100, 50, 1200, 900)

        self.doc_id = doc.get("_id")  # MongoDB document _id
        self.fields = [
            "Exporter", "Invoice No", "Exporter's Ref", "IEC",
            "GST No", "Consignee", "Pre-carraige by", "Port Of Discharge",
            "Date", "Buyer's order No", "Buyer's order Date", "Other references",
            "TAX Registration Number", "Country of origin of Goods",
            "Country Of Final Destination", "Country Of Destination",
            "Terms Of Delivery and Payment", "LUT ARN NO", "Vessel / Flight No",
            "Final Destination", "Port Of landing", "AD Code", "Total Packages",
            "Total Export Value", "Total GST Value", "Total Invoice Value"
        ]

        self.controllers = {}
        self.doc_data = self.fetch_doc_data()  # fetch latest data from MongoDB
        self.initUI()

    # ---------------- Fetch MongoDB Data ----------------
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

    # ---------------- UI Setup ----------------
    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Header with logo
        header_layout = QHBoxLayout()
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo = QLabel()
        pixmap = QPixmap("wwe.jpg")
        if not pixmap.isNull():
            pixmap = pixmap.scaled(350, 350, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo.setPixmap(pixmap)
        else:
            logo.setText("No Logo")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(logo)

        # Company info
        company_layout = QVBoxLayout()
        company_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        company_name = QLabel("ZAKA Controls & Devices")
        company_name.setFont(QFont("Arial", 30, QFont.Weight.Bold))
        company_name.setAlignment(Qt.AlignmentFlag.AlignCenter)

        description = QLabel("Edit the export form below")
        description.setFont(QFont("Arial", 20))
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)

        company_layout.addWidget(company_name)
        company_layout.addWidget(description)
        header_layout.addLayout(company_layout)
        main_layout.addLayout(header_layout)
        main_layout.addSpacing(20)

        # Scroll area for form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Create form fields
        for i in range(0, len(self.fields), 4):
            row_layout = QHBoxLayout()
            row_layout.setSpacing(30)

            left_fields = self.fields[i:i+2]
            right_fields = self.fields[i+2:i+4]

            # Left side
            left_layout = QVBoxLayout()
            for field_name in left_fields:
                left_layout.addLayout(self.build_field_layout(field_name))
            left_container = QGroupBox()
            left_container.setLayout(left_layout)
            left_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            row_layout.addWidget(left_container)

            # Right side
            right_layout = QVBoxLayout()
            for field_name in right_fields:
                right_layout.addLayout(self.build_field_layout(field_name))
            right_container = QGroupBox()
            right_container.setLayout(right_layout)
            right_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            row_layout.addWidget(right_container)

            scroll_layout.addLayout(row_layout)
            scroll_layout.addSpacing(15)

        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        # Submit button
        submit_btn = QPushButton("Update")
        submit_btn.setFixedHeight(45)
        submit_btn.setFixedWidth(300)
        submit_btn.clicked.connect(self.handle_submit)
        main_layout.addWidget(submit_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addSpacing(20)

        self.setLayout(main_layout)

    def build_field_layout(self, field_name):
        layout = QVBoxLayout()
        label = QLabel(field_name)
        label.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        line_edit = QLineEdit()
        line_edit.setFont(QFont("Arial", 12))
        line_edit.setFixedHeight(30)

        # Preload value from MongoDB
        line_edit.setText(str(self.doc_data.get(field_name, "")))
        self.controllers[field_name] = line_edit

        layout.addWidget(label)
        layout.addWidget(line_edit)
        return layout

    # ---------------- Submit / Update ----------------
    def handle_submit(self):
        unfilled = []
        for field, controller in self.controllers.items():
            if not controller.text().strip():
                unfilled.append(field)

        if unfilled:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Unfilled Fields")
            msg.setText("Please fill the following fields:")
            msg.setDetailedText("\n".join(unfilled))
            msg.exec()
        else:
            data = {field: controller.text() for field, controller in self.controllers.items()}

            # Update MongoDB document
            try:
                client = MongoClient(MONGO_URL)
                db = client[DB_NAME]
                collection = db[COLLECTION_NAME]
                data["last_updated_date"] = datetime.now().strftime("%Y-%m-%d")
                data["last_updated_time"] = datetime.now().strftime("%H:%M:%S")

                collection.update_one({"_id": ObjectId(self.doc_id)}, {"$set": data})
                QMessageBox.information(self, "Success", "Document updated successfully!")
                self.close()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update MongoDB: {str(e)}")
