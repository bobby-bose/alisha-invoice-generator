from pymongo import MongoClient
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView
)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
import os
# Import the Edit Form
from one_edit import ExportFormEdit  # <-- your edit form module
from bson.objectid import ObjectId
import json

# ---------------- MongoDB Config ----------------
MONGO_URL = "mongodb+srv://admin:admin@cluster.rnhig2f.mongodb.net/?retryWrites=true&w=majority&appName=cluster"
DB_NAME = "mamshi"
COLLECTION_NAME = "report_two"
PLACEHOLDER_MAPPING = {
    "Invoice No": "invoice_no",
    "Exporter's Ref": "exporter_ref",
    "IEC": "iec",
    "GST No": "tax_no",
    "Consignee": "consignee_address",
    "Pre-carraige by": "pre_carriage",
    "Port Of Discharge": "port_Discharge",
    "Date": "date",
    "Buyer's order No": "order_no",
    "Buyer's order Date": "order_date",
    "Other references": "other_reference",
    "TAX Registration Number": "tax_no",
    "Country of origin of Goods": "country",
    "Country Of Final Destination": "final_destination",
    "Country Of Destination": "destination",
    "Terms Of Delivery and Payment": "terms",
    "LUT ARN NO": "lut_arn_no",
    "Vessel / Flight No": "vessel_no",
    "Final Destination": "port_destination",
    "Port Of landing": "port_loading",
    "AD Code": "ad_code",
    "Total Packages": "total_packages",
    "Total Export Value": "export_values",
    "Total GST Value": "gst_values",
    "Total Invoice Value": "total_invoice_value",
    "Units": "units",
    "Qty": "qty",
    "Rate": "rate",
    "Amount": "amount",
    "Taxable Value": "taxable_value",
    "IGST": "igst",
    "IGST Amount": "igst_amount",
    "Amount Chargeable (in words)": "amount_inwords",
    "Shipping Mark": "shipping_mark",
    "Description of Goods": "description",
    "Delivery": "delivery",
    "Contact Details": "contact_details",
    # Add any other mappings you need
}

# ---------------- Fetch Data ----------------
def fetch_exporter_docs():
    try:
        client = MongoClient(MONGO_URL)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        docs = list(collection.find({"exporter_ref": {"$exists": True}}))  # only with "Exporter"
        print(f"✅ {len(docs)} documents found with key 'exporter_ref'")
        return docs
    except Exception as e:
        print("❌ MongoDB Error:", str(e))
        return []

# ---------------- UI Class ----------------
class ExportTable(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Exporter Data Viewer")
        self.setGeometry(100, 50, 1300, 900)

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
        self.edit_windows = []  # keep references to edit windows
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
        desc = QLabel("Exporter Form Records (MongoDB)")
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
            "exporter_ref", "iec", "order_no", "order_date", "tax_no",
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
        self.table.setRowCount(0)
        for doc in self.docs:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)

            exporter = str(doc.get("exporter_ref", ""))
            invoice_no = str(doc.get("iec", ""))
            date = str(doc.get("order_no", ""))
            total_invoice = str(doc.get("order_date", ""))
            total_gst = str(doc.get("tax_no", ""))

            self.table.setItem(row_position, 0, QTableWidgetItem(exporter))
            self.table.setItem(row_position, 1, QTableWidgetItem(invoice_no))
            self.table.setItem(row_position, 2, QTableWidgetItem(date))
            self.table.setItem(row_position, 3, QTableWidgetItem(total_invoice))
            self.table.setItem(row_position, 4, QTableWidgetItem(total_gst))

            # Buttons
            btn_edit = QPushButton("Edit")
            btn_edit.clicked.connect(lambda _, d=doc: self.open_edit_form(d))
            self.table.setCellWidget(row_position, 5, btn_edit)

            btn_hide = QPushButton("Hide")
            btn_hide.clicked.connect(lambda _, r=row_position: self.hide_row(r))
            self.table.setCellWidget(row_position, 6, btn_hide)

            btn_print = QPushButton("🖨 Print")
            btn_print.clicked.connect(lambda _, doc_id=str(doc["_id"]): self.print_doc(doc_id))

            self.table.setCellWidget(row_position, 7, btn_print)

            self.table.setRowHeight(row_position, 70)

    def open_edit_form(self, doc):
        # Open Edit Form and keep a reference so it doesn't get garbage collected
        edit_window = ExportFormEdit(doc)
        self.edit_windows.append(edit_window)
        edit_window.show()

    def hide_row(self, row):
        self.table.hideRow(row)
        QMessageBox.information(self, "Hidden", "Row has been hidden from the table view.")

    
    def print_doc(self, doc_id):
        try:
            from bson import ObjectId
            import json
            import os

            from pymongo import MongoClient

            # MongoDB config
            MONGO_URL = "mongodb+srv://admin:admin@cluster.rnhig2f.mongodb.net/?retryWrites=true&w=majority&appName=cluster"
            DB_NAME = "mamshi"
            COLLECTION_NAME = "report_two"

            # Fetch document by ID
            client = MongoClient(MONGO_URL)
            db = client[DB_NAME]
            collection = db[COLLECTION_NAME]

            # Convert doc_id string to ObjectId
            doc = collection.find_one({"_id": ObjectId(doc_id)})

            if not doc:
                QMessageBox.warning(self, "Not found", f"No document found with ID: {doc_id}")
                return

            # Mapping MongoDB keys to DOCX placeholders
            key_mapping = {
                "Total Packages": "total_packages",
                "Vessel / Flight No": "vessel_no",
                "Total Export Value": "export_values",
                "Date": "date",
                "Total Invoice Value": "total_amount",
                "Buyer's order No": "order_no",
                "Other references": "other_reference",
                "Final Destination": "destination",
                "Country Of Final Destination": "final_destination",
                "TAX Registration Number": "tax_no",
                "LUT ARN NO": "lut_arn_no",
                "Consignee": "consignee_address",
                "GST No": "gst_values",
                "IEC": "iec",
                "Port Of Discharge": "port_Discharge",
                "Port Of landing": "port_loading",
                "Pre-carraige by": "pre_carriage",
                "Total GST Value": "total_igst_amount",
                "Amount In Words": "amount_inwords",
                "Exporter": "exporter_ref",
                "Invoice No": "invoice_no",
                "Terms Of Delivery and Payment": "terms",
                "Currency Sign": "currency_sign",
                "Delivery": "delivery",
                "Quantity": "qty",
                "Rate": "rate",
                "IGST": "igst",
                "IGST Amount": "igst_amount",
                "Amount": "amount",
                "Description": "description",
                "Units": "units",
                "Place of Receipt": "place_receipt",
                "Country of origin of Goods": "country",
                "Buyer's order Date": "order_date",
                "AD Code": "ad_code",
            }

            # Generate mapped data
            mapped_data = {}
            for k, v in doc.items():
                if k == "_id":
                    continue
                new_key = key_mapping.get(k, k)
                mapped_data[new_key] = str(v)

            # Save JSON to same folder as script
            json_path = os.path.join(os.path.dirname(__file__), "data_one.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(mapped_data, f, ensure_ascii=False, indent=4)

   

            QMessageBox.information(self, "Saved", f"Invoice DOCX and PDF generated successfully.\nSaved JSON: {json_path}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate invoice: {str(e)}")


# ---------------- Run App ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExportTable()
    window.show()
    sys.exit(app.exec())
