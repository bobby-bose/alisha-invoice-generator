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
MONGO_URL = "mongodb+srv://username:password@cluster.rnhig2f.mongodb.net/?retryWrites=true&w=majority&appName=cluster"
DB_NAME = "mamshi"
COLLECTION_NAME = "report_two"


class PackingListFormEdit(QWidget):
    updated = pyqtSignal()  # Signal to notify parent window on successful update

    def __init__(self, doc_id):
        super().__init__()
        self.setWindowTitle("Edit Packing List Form")
        self.setGeometry(100, 50, 1400, 900)

        self.doc_id = doc_id

        # Main fields
        self.fields = [
            "consignee_address", "date", "po_no", "tax_no",
            "packing_list_no", "delivery_address", "loding_port", "discharge_port",
            "hs_code", "no_boxes", "sum_net_weight", "sum_gross_weight"
        ]

        # Item-level fields (repeatable)
        self.item_fields = [
            "item_number", "box_number", "material", "qty",
            "dimension", "net_weight", "gross_weight"
        ]

        self.controllers = {}   # main fields
        self.item_rows = []     # list of dictionaries for item rows

        self.doc_data = self.fetch_doc_data()
        self.initUI()

    def fetch_doc_data(self):
        """Fetch document from MongoDB"""
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

        # ---------------- Header ----------------
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

        company_layout = QVBoxLayout()
        company_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        company_name = QLabel("ZAKA Controls & Devices")
        company_name.setFont(QFont("Arial", 30, QFont.Weight.Bold))
        company_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description = QLabel("Edit the Packing List Form below")
        description.setFont(QFont("Arial", 20))
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        company_layout.addWidget(company_name)
        company_layout.addWidget(description)
        header_layout.addLayout(company_layout)
        main_layout.addLayout(header_layout)
        main_layout.addSpacing(20)

        # ---------------- Scroll Area ----------------
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)

        # ---------------- Main Fields ----------------
        for i in range(0, len(self.fields), 2):
            row_layout = QHBoxLayout()
            row_layout.setSpacing(30)
            left_fields = self.fields[i:i + 1]
            right_fields = self.fields[i + 1:i + 2]

            # Left container
            left_layout = QVBoxLayout()
            for field_name in left_fields:
                left_layout.addLayout(self.build_field_layout(field_name))
            left_container = QGroupBox()
            left_container.setLayout(left_layout)
            left_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            row_layout.addWidget(left_container)

            # Right container
            right_layout = QVBoxLayout()
            for field_name in right_fields:
                right_layout.addLayout(self.build_field_layout(field_name))
            right_container = QGroupBox()
            right_container.setLayout(right_layout)
            right_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            row_layout.addWidget(right_container)

            self.scroll_layout.addLayout(row_layout)
            self.scroll_layout.addSpacing(15)

        # ---------------- Item Rows Header ----------------
        header = QHBoxLayout()
        for field in self.item_fields:
            label = QLabel(field.replace("_", " ").title())
            label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            label.setFixedWidth(150)
            header.addWidget(label)
        header.addWidget(QLabel(""))  # placeholder for "+" button
        self.scroll_layout.addLayout(header)
        self.scroll_layout.addSpacing(5)

        # ---------------- Item Rows ----------------
        existing_items = self.doc_data.get("items", [])
        if existing_items:
            for item in existing_items:
                self.add_item_row(item)
        else:
            self.add_item_row()  # at least one row

        scroll_content.setLayout(self.scroll_layout)
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        # ---------------- Submit Button ----------------
        submit_btn = QPushButton("✅ Update Document")
        submit_btn.setFixedHeight(45)
        submit_btn.setFixedWidth(300)
        submit_btn.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; border-radius: 8px;")
        submit_btn.clicked.connect(self.handle_submit)
        main_layout.addWidget(submit_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addSpacing(20)

        self.setLayout(main_layout)

    # ---------------- Main field layout ----------------
    def build_field_layout(self, field_name):
        layout = QVBoxLayout()
        label = QLabel(field_name.replace("_", " ").title())
        label.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        line_edit = QLineEdit()
        line_edit.setFont(QFont("Arial", 12))
        line_edit.setFixedHeight(30)
        line_edit.setText(str(self.doc_data.get(field_name, "")))
        self.controllers[field_name] = line_edit
        layout.addWidget(label)
        layout.addWidget(line_edit)
        return layout

    # ---------------- Add item row ----------------
    def add_item_row(self, item_data=None):
        row_layout = QHBoxLayout()
        row_controllers = {}

        for field in self.item_fields:
            line_edit = QLineEdit()
            line_edit.setFixedWidth(150)
            if item_data and field in item_data:
                line_edit.setText(str(item_data[field]))
            row_layout.addWidget(line_edit)
            row_controllers[field] = line_edit

        # "+" button to add another row
        add_btn = QPushButton("+")
        add_btn.setFixedWidth(40)
        add_btn.clicked.connect(self.add_item_row)
        row_layout.addWidget(add_btn)

        self.item_rows.append(row_controllers)
        self.scroll_layout.addLayout(row_layout)
        self.scroll_layout.addSpacing(5)

    # ---------------- Submit ----------------
    def handle_submit(self):
        unfilled = []

        # Validate main fields
        for field, controller in self.controllers.items():
            if not controller.text().strip():
                unfilled.append(field)

        # Validate item rows
        for idx, row in enumerate(self.item_rows, start=1):
            for field, controller in row.items():
                if not controller.text().strip():
                    unfilled.append(f"Row {idx} - {field}")

        if unfilled:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Unfilled Fields")
            msg.setText("Please fill the following fields:")
            msg.setDetailedText("\n".join(unfilled))
            msg.exec()
            return

        # Prepare data to update
        data = {f: c.text() for f, c in self.controllers.items()}
        data["items"] = [{f: c.text() for f, c in row.items()} for row in self.item_rows]
        data["last_updated_date"] = datetime.now().strftime("%Y-%m-%d")
        data["last_updated_time"] = datetime.now().strftime("%H:%M:%S")

        try:
            client = MongoClient(MONGO_URL)
            db = client[DB_NAME]
            collection = db[COLLECTION_NAME]
            collection.update_one({"_id": ObjectId(self.doc_id)}, {"$set": data})
            QMessageBox.information(self, "Success", "✅ Packing List updated successfully!")
            self.updated.emit()  # notify parent window
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update MongoDB: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # replace with a real ObjectId for testing
    window = PackingListFormEdit("68e4a69b7c179cbe88953287")
    window.show()
    sys.exit(app.exec())
