from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt
from pymongo import MongoClient
from bson.objectid import ObjectId
import sys
from datetime import datetime

# 🔹 MongoDB Config
MONGO_URL = "mongodb+srv://admin:admin@cluster.rnhig2f.mongodb.net/?retryWrites=true&w=majority&appName=cluster"
DB_NAME = "mamshi"
COLLECTION_NAME = "report_two"
DOCUMENT_ID = "68e79e7912f4d0a21dfe0399"

class EditInvoiceForm(QWidget):
    def __init__(self):
        super().__init__()
        self.db = MongoClient(MONGO_URL)[DB_NAME][COLLECTION_NAME]
        self.doc = self.db.find_one({"_id": ObjectId(DOCUMENT_ID)})

        if not self.doc:
            QMessageBox.critical(self, "Error", f"No document found with ID {DOCUMENT_ID}")
            sys.exit(1)

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Edit Invoice Form")
        self.resize(900, 700)

        layout = QVBoxLayout()

        # --- Basic Fields ---
        self.date_edit = QLineEdit(self.doc.get("date", ""))
        self.invoice_no_edit = QLineEdit(self.doc.get("invoice_no", ""))
        self.eo_number_edit = QLineEdit(self.doc.get("eo_number", ""))
        self.your_ref_edit = QLineEdit(self.doc.get("your_reference_no", ""))
        self.our_ref_edit = QLineEdit(self.doc.get("our_reference_no", ""))
        self.supplier_address_edit = QTextEdit(self.doc.get("supplier_address", ""))
        self.bill_to_address_edit = QTextEdit(self.doc.get("bill_to_address", ""))

        layout.addWidget(QLabel("Date"))
        layout.addWidget(self.date_edit)
        layout.addWidget(QLabel("Invoice No"))
        layout.addWidget(self.invoice_no_edit)
        layout.addWidget(QLabel("EO Number"))
        layout.addWidget(self.eo_number_edit)
        layout.addWidget(QLabel("Your Reference No"))
        layout.addWidget(self.your_ref_edit)
        layout.addWidget(QLabel("Our Reference No"))
        layout.addWidget(self.our_ref_edit)

        # --- Table for Line Items ---
        layout.addWidget(QLabel("Line Items"))
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Line No", "Part No", "Description", "Qty", "Unit Rate", "Total"])
        layout.addWidget(self.table)

        self.load_table_data()

        # --- Totals ---
        self.total_edit = QLineEdit(self.doc.get("total_amount", ""))
        self.receivable_edit = QLineEdit(self.doc.get("receivable_amount", ""))
        self.received_edit = QLineEdit(self.doc.get("received_amount", ""))
        self.balance_edit = QLineEdit(self.doc.get("balance_amount", ""))
        self.received_edit.textChanged.connect(self.update_balance)

        layout.addWidget(QLabel("Total Amount"))
        layout.addWidget(self.total_edit)
        layout.addWidget(QLabel("Receivable Amount"))
        layout.addWidget(self.receivable_edit)
        layout.addWidget(QLabel("Received Amount"))
        layout.addWidget(self.received_edit)
        layout.addWidget(QLabel("Balance Amount"))
        layout.addWidget(self.balance_edit)

        # --- Buttons ---
        save_btn = QPushButton("💾 Save Changes")
        save_btn.clicked.connect(self.save_to_db)
        layout.addWidget(save_btn)

        self.setLayout(layout)

    def load_table_data(self):
        """Load table rows from MongoDB line_items."""
        items = self.doc.get("line_items", [])
        self.table.setRowCount(len(items))
        for i, item in enumerate(items):
            self.table.setItem(i, 0, QTableWidgetItem(str(item.get("line_no", ""))))
            self.table.setItem(i, 1, QTableWidgetItem(item.get("part_number", "")))
            self.table.setItem(i, 2, QTableWidgetItem(item.get("description", "")))
            self.table.setItem(i, 3, QTableWidgetItem(str(item.get("quantity", ""))))
            self.table.setItem(i, 4, QTableWidgetItem(str(item.get("unit_rate", ""))))
            self.table.setItem(i, 5, QTableWidgetItem(str(item.get("total", ""))))

    def update_balance(self):
        """Recalculate balance when received amount changes."""
        try:
            receivable = float(self.receivable_edit.text() or 0)
            received = float(self.received_edit.text() or 0)
            balance = receivable - received
            self.balance_edit.setText(f"{balance:.2f}")
        except ValueError:
            self.balance_edit.setText("Invalid")

    def save_to_db(self):
        """Update existing MongoDB document with new values."""
        updated_doc = {
            "date": self.date_edit.text(),
            "invoice_no": self.invoice_no_edit.text(),
            "eo_number": self.eo_number_edit.text(),
            "your_reference_no": self.your_ref_edit.text(),
            "our_reference_no": self.our_ref_edit.text(),
            "supplier_address": self.supplier_address_edit.toPlainText(),
            "bill_to_address": self.bill_to_address_edit.toPlainText(),
            "total_amount": self.total_edit.text(),
            "receivable_amount": self.receivable_edit.text(),
            "received_amount": self.received_edit.text(),
            "balance_amount": self.balance_edit.text(),
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Save table data back to list
        line_items = []
        for row in range(self.table.rowCount()):
            line = {
                "line_no": self.table.item(row, 0).text() if self.table.item(row, 0) else "",
                "part_number": self.table.item(row, 1).text() if self.table.item(row, 1) else "",
                "description": self.table.item(row, 2).text() if self.table.item(row, 2) else "",
                "quantity": self.table.item(row, 3).text() if self.table.item(row, 3) else "",
                "unit_rate": self.table.item(row, 4).text() if self.table.item(row, 4) else "",
                "total": self.table.item(row, 5).text() if self.table.item(row, 5) else "",
            }
            line_items.append(line)

        updated_doc["line_items"] = line_items

        self.db.update_one({"_id": ObjectId(DOCUMENT_ID)}, {"$set": updated_doc})
        QMessageBox.information(self, "✅ Success", "Invoice updated successfully in MongoDB!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EditInvoiceForm()
    window.show()
    sys.exit(app.exec())
