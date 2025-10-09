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


class PackingListFormEdit(QWidget):
    updated = pyqtSignal()  # Signal to notify parent window on successful update

    def __init__(self, doc_id):
        super().__init__()
        self.setWindowTitle("Edit Packing List Form")
        self.setGeometry(100, 50, 1400, 900)

        self.doc_id = doc_id

        # ---------------- Fields ----------------
        # Main fields
        self.fields = [
            "consignee_address", "delivery_address", "date", "po_no",
            "tax_no", "packing_list_no", "loding_port", "discharge_port",
            "hs_code", "total_boxes", "total_net_weight", "total_gross_weight"
        ]

        # Item-level fields
        self.item_fields = ["item_number", "material", "packaging_description"]

        # Box-level fields
        self.box_fields = ["box_number", "quantity", "length", "width", "height", "net_weight", "gross_weight"]

        self.controllers = {}   # main fields
        self.item_rows = []     # list of item dictionaries

        self.doc_data = self.fetch_doc_data()
        self.initUI()

    # ---------------- Fetch data ----------------
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

    # ---------------- UI ----------------
    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # ---------------- Header ----------------
        header_layout = QHBoxLayout()
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo = QLabel()
        pixmap = QPixmap("wwe.jpg")
        if not pixmap.isNull():
            pixmap = pixmap.scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
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

        # ---------------- Items & Boxes ----------------
        existing_items = self.doc_data.get("items", [])
        if existing_items:
            for item in existing_items:
                self.add_item_row(item)
        else:
            self.add_item_row()

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

    # ---------------- Main Field Layout ----------------
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

    # ---------------- Add Item Row ----------------
    def add_item_row(self, item_data=None):
        item_layout = QVBoxLayout()
        item_controllers = {}

        # Item-level fields
        for field in self.item_fields:
            sub_layout = QVBoxLayout()
            label = QLabel(field.replace("_", " ").title())
            label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            line_edit = QLineEdit()
            line_edit.setFixedHeight(30)
            if item_data and field in item_data:
                line_edit.setText(str(item_data[field]))
            sub_layout.addWidget(label)
            sub_layout.addWidget(line_edit)
            item_layout.addLayout(sub_layout)
            item_controllers[field] = line_edit

        # Boxes for this item
        boxes_layout = QVBoxLayout()
        item_controllers["boxes"] = []
        existing_boxes = item_data.get("boxes", []) if item_data else []

        if existing_boxes:
            for box in existing_boxes:
                self.add_box_row(boxes_layout, item_controllers, box)
        else:
            self.add_box_row(boxes_layout, item_controllers)

        # "+" button to add new box
        add_box_btn = QPushButton("+ Add Box")
        add_box_btn.setFixedWidth(120)
        add_box_btn.clicked.connect(lambda _, l=boxes_layout, c=item_controllers: self.add_box_row(l, c))
        boxes_layout.addWidget(add_box_btn)
        item_layout.addLayout(boxes_layout)
        item_layout.addSpacing(10)

        # Wrap item in a GroupBox
        group_title = f"Item {item_data.get('item_number', len(self.item_rows)+1) if item_data else len(self.item_rows)+1}"
        group = QGroupBox(group_title)
        group.setLayout(item_layout)
        self.scroll_layout.addWidget(group)
        self.scroll_layout.addSpacing(10)

        self.item_rows.append(item_controllers)

    # ---------------- Add Box Row ----------------
    def add_box_row(self, layout, item_controllers, box_data=None):
        row_layout = QHBoxLayout()
        box_controllers = {}
        for field in self.box_fields:
            line_edit = QLineEdit()
            line_edit.setFixedWidth(100)
            if box_data and field in box_data:
                line_edit.setText(str(box_data[field]))
            row_layout.addWidget(line_edit)
            box_controllers[field] = line_edit
        item_controllers["boxes"].append(box_controllers)
        layout.addLayout(row_layout)

    # ---------------- Submit ----------------
    def handle_submit(self):
        unfilled = []

        # Main fields
        for field, controller in self.controllers.items():
            if not controller.text().strip():
                unfilled.append(field)

        # Items & Boxes
        for idx, item in enumerate(self.item_rows, start=1):
            for field in self.item_fields:
                if not item[field].text().strip():
                    unfilled.append(f"Item {idx} - {field}")
            for box_idx, box in enumerate(item["boxes"], start=1):
                for field in self.box_fields:
                    if not box[field].text().strip():
                        unfilled.append(f"Item {idx} Box {box_idx} - {field}")

        if unfilled:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Unfilled Fields")
            msg.setText("Please fill the following fields:")
            msg.setDetailedText("\n".join(unfilled))
            msg.exec()
            return

        # Prepare data to update MongoDB
        data = {f: c.text() for f, c in self.controllers.items()}
        data["items"] = []
        for item in self.item_rows:
            item_data = {f: item[f].text() for f in self.item_fields}
            item_data["boxes"] = [{f: box[f].text() for f in self.box_fields} for box in item["boxes"]]
            data["items"].append(item_data)

        data["last_updated_date"] = datetime.now().strftime("%Y-%m-%d")
        data["last_updated_time"] = datetime.now().strftime("%H:%M:%S")

        try:
            client = MongoClient(MONGO_URL)
            db = client[DB_NAME]
            collection = db[COLLECTION_NAME]
            collection.update_one({"_id": ObjectId(self.doc_id)}, {"$set": data})
            QMessageBox.information(self, "Success", "✅ Packing List updated successfully!")
            self.updated.emit()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update MongoDB: {str(e)}")


# ---------------- MAIN ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Replace with a valid ObjectId from your MongoDB collection
    window = PackingListFormEdit("replace_with_actual_id")
    window.show()
    sys.exit(app.exec())

