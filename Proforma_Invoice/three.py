import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QGroupBox, QMessageBox, QScrollArea,
    QTableWidget, QTableWidgetItem, QComboBox, QDateEdit
)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt, QDate
import inflect
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import database

p = inflect.engine()

class InvoiceForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Invoice Form")
        self.setGeometry(100, 50, 1300, 950)
        self.controllers = {}
        self.initUI()

    def initUI(self):
        self.setStyleSheet("""
            QWidget { background-color: #ffffff; font-family: Arial; color: black; }
            QLabel { font-weight: bold; color: black; }
            QLineEdit, QTextEdit, QDateEdit, QComboBox { border: 1px solid #000000; border-radius: 5px; padding: 5px; font-size: 13px; color: black; }
            QPushButton { background-color: #1877f2; color: white; font-weight: bold; font-size: 16px; border-radius: 8px; padding: 6px 15px; }
            QPushButton:hover { background-color: #166fe5; }
            QGroupBox { border: 2px solid #000000; border-radius: 12px; font-size: 16px; font-weight: bold; }
            QTableWidget { gridline-color: #ccd0d5; font-size: 14px; }
        """)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # ---------------- Header ----------------
        header_layout = QHBoxLayout()
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo = QLabel()
        pixmap = QPixmap("wwe.jpg")
        if not pixmap.isNull():
            pixmap = pixmap.scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio)
            logo.setPixmap(pixmap)
        else:
            logo.setText("No Logo")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(logo)

        company_layout = QVBoxLayout()
        company_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        company_name = QLabel("ZAKA Controls & Devices")
        company_name.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        company_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description = QLabel("This is an Invoice Form. Fill the details below.")
        description.setFont(QFont("Arial", 18))
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        company_layout.addWidget(company_name)
        company_layout.addWidget(description)
        header_layout.addLayout(company_layout)
        main_layout.addLayout(header_layout)
        main_layout.addSpacing(15)

        # ---------------- Scroll Area ----------------
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)

        # ---------------- Top Fields ----------------
        self.add_top_fields()

        # ---------------- Line Items ----------------
        self.add_line_items_table()

        # ---------------- Totals Section ----------------
        self.add_totals_section()

        scroll_content.setLayout(self.scroll_layout)
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        # ---------------- Submit ----------------
        submit_btn = QPushButton("Submit")
        submit_btn.setFixedHeight(45)
        submit_btn.setFixedWidth(300)
        submit_btn.clicked.connect(self.handle_submit)
        main_layout.addWidget(submit_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addSpacing(20)

        self.setLayout(main_layout)

    def add_top_fields(self):
        fields_layout = QVBoxLayout()

        # Invoice Date
        date_layout = QVBoxLayout()
        date_label = QLabel("Invoice Date")
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_edit)
        fields_layout.addLayout(date_layout)

        # Invoice / Reference Numbers
        numbers_layout = QHBoxLayout()
        for label_text in ["Invoice No", "EO Number", "Your Reference No", "Our Reference No"]:
            v = QVBoxLayout()
            label = QLabel(label_text)
            line_edit = QLineEdit()
            line_edit.setFixedHeight(30)
            v.addWidget(label)
            v.addWidget(line_edit)
            numbers_layout.addLayout(v)
            self.controllers[label_text.lower().replace(" ", "_")] = line_edit
        fields_layout.addLayout(numbers_layout)

        # Supplier / Bill To (5 rows)
        addr_layout = QHBoxLayout()
        for label_text in ["Supplier Address", "Bill To Address"]:
            v = QVBoxLayout()
            label = QLabel(label_text)
            text_edit = QTextEdit()
            text_edit.setFixedHeight(120)  # approx 5 rows
            v.addWidget(label)
            v.addWidget(text_edit)
            addr_layout.addLayout(v)
            self.controllers[label_text.lower().replace(" ", "_")] = text_edit
        fields_layout.addLayout(addr_layout)
        self.scroll_layout.addLayout(fields_layout)
        self.scroll_layout.addSpacing(15)

    def add_line_items_table(self):
        group = QGroupBox("Line Items")
        layout = QVBoxLayout()

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Line No", "Part Number", "Description", "Quantity", "Unit Rate", "Total"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setDefaultSectionSize(200)
        self.table.setSizeAdjustPolicy(QTableWidget.SizeAdjustPolicy.AdjustToContents)  # Auto adjust height
        layout.addWidget(self.table)

        add_row_layout = QHBoxLayout()
        add_row_label = QLabel("Add a new line item:")
        add_row_label.setFont(QFont("Arial", 14))
        add_row_btn = QPushButton("Add Row")
        add_row_btn.setFixedWidth(120)
        add_row_btn.clicked.connect(self.add_line_item_row)
        add_row_layout.addWidget(add_row_label)
        add_row_layout.addSpacing(10)
        add_row_layout.addWidget(add_row_btn)
        add_row_layout.addStretch()
        layout.addLayout(add_row_layout)

        group.setLayout(layout)
        self.scroll_layout.addWidget(group)
        self.scroll_layout.addSpacing(15)




    def add_line_item_row(self):
        row_pos = self.table.rowCount()
        self.table.insertRow(row_pos)

        # Line No
        line_no = QTableWidgetItem(str(row_pos + 1))
        line_no.setFlags(Qt.ItemFlag.ItemIsEnabled)
        line_no.setFont(QFont("Arial", 13))
        self.table.setItem(row_pos, 0, line_no)

        # Part Number, Description, Quantity, Unit Rate
        for col in range(1, 5):
            item = QTableWidgetItem("0" if col in [3,4] else "")
            item.setFont(QFont("Arial", 13))
            self.table.setItem(row_pos, col, item)

        # Total
        total = QTableWidgetItem("0.00")
        total.setFlags(Qt.ItemFlag.ItemIsEnabled)
        total.setFont(QFont("Arial", 13))
        self.table.setItem(row_pos, 5, total)

        # Adjust the table height dynamically
        self.table.setFixedHeight(self.table.verticalHeader().length() + self.table.horizontalHeader().height() + 5)

        # Connect signals safely
        try:
            self.table.itemChanged.disconnect()
        except:
            pass
        self.table.itemChanged.connect(self.update_all_line_totals)


    def update_all_line_totals(self, changed_item=None):
        self.table.blockSignals(True)
        for row in range(self.table.rowCount()):
            qty_item = self.table.item(row, 3)
            rate_item = self.table.item(row, 4)
            total_item = self.table.item(row, 5)

            # Ensure items exist
            if qty_item is None:
                qty_item = QTableWidgetItem("0")
                self.table.setItem(row, 3, qty_item)
            if rate_item is None:
                rate_item = QTableWidgetItem("0")
                self.table.setItem(row, 4, rate_item)
            if total_item is None:
                total_item = QTableWidgetItem("0.00")
                total_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                self.table.setItem(row, 5, total_item)

            # Safely parse numbers
            try:
                qty = float(qty_item.text())
            except:
                qty = 0.0
            try:
                rate = float(rate_item.text())
            except:
                rate = 0.0
            total_item.setText(f"{qty * rate:.2f}")

        self.table.blockSignals(False)
        self.update_totals()

    def add_totals_section(self):
        group = QGroupBox("Totals")
        layout = QVBoxLayout()

        # Total Amount
        total_layout = QVBoxLayout()
        total_label = QLabel("Total Amount (USD)")
        total_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.total_amount_edit = QLineEdit("0.00")
        self.total_amount_edit.setReadOnly(True)
        self.total_amount_edit.setFont(QFont("Arial", 14))
        total_layout.addWidget(total_label)
        total_layout.addWidget(self.total_amount_edit)
        layout.addLayout(total_layout)

        # Receivable (50%)
        rec_layout = QVBoxLayout()
        rec_label = QLabel("Receivable Amount (50%)")
        rec_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.receivable_edit = QLineEdit("0.00")
        self.receivable_edit.setReadOnly(True)
        self.receivable_edit.setFont(QFont("Arial", 14))
        self.receivable_text_edit = QLineEdit("")
        self.receivable_text_edit.setReadOnly(True)
        self.receivable_text_edit.setFont(QFont("Arial", 14))
        rec_layout.addWidget(rec_label)
        rec_layout.addWidget(self.receivable_edit)
        rec_layout.addWidget(self.receivable_text_edit)
        layout.addLayout(rec_layout)

        # Received / Balance
        received_layout = QVBoxLayout()
        recvd_label = QLabel("Received Amount")
        recvd_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.received_edit = QLineEdit("0.00")
        self.received_edit.setFont(QFont("Arial", 14))
        self.received_edit.textChanged.connect(self.update_balance)
        received_layout.addWidget(recvd_label)
        received_layout.addWidget(self.received_edit)
        layout.addLayout(received_layout)

        balance_layout = QVBoxLayout()
        balance_label = QLabel("Balance Amount")
        balance_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.balance_edit = QLineEdit("0.00")
        self.balance_edit.setFont(QFont("Arial", 14))
        self.balance_edit.setReadOnly(True)
        balance_layout.addWidget(balance_label)
        balance_layout.addWidget(self.balance_edit)
        layout.addLayout(balance_layout)

        # Dropdowns
        dropdown_layout = QHBoxLayout()
        dropdowns = {
            "Country of Origin": ["India","USA","China"],
            "Port of Embarkation": ["Nhava Sheva","Mumbai","Chennai"],
            "Port of Discharge": ["Los Angeles","New York","Chicago"]
        }
        for label_text, values in dropdowns.items():
            v = QVBoxLayout()
            label = QLabel(label_text)
            label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            combo = QComboBox()
            combo.setFont(QFont("Arial", 14))
            combo.addItems(values)
            v.addWidget(label)
            v.addWidget(combo)
            dropdown_layout.addLayout(v)
            self.controllers[label_text.lower().replace(" ","_")] = combo
        layout.addLayout(dropdown_layout)

        group.setLayout(layout)
        self.scroll_layout.addWidget(group)
        self.scroll_layout.addSpacing(15)

    def update_totals(self):
        total = 0
        for row in range(self.table.rowCount()):
            try:
                total += float(self.table.item(row,5).text())
            except:
                pass
        self.total_amount_edit.setText(f"{total:.2f}")
        receivable = total*0.5
        self.receivable_edit.setText(f"{receivable:.2f}")
        self.receivable_text_edit.setText(f"{p.number_to_words(int(receivable))} dollars")
        self.update_balance()

    def update_balance(self):
        try:
            receivable = float(self.receivable_edit.text())
            received = float(self.received_edit.text())
            balance = receivable - received
            self.balance_edit.setText(f"{balance:.2f}")
        except:
            self.balance_edit.setText("0.00")

    def handle_submit(self):
        self.update_all_line_totals()  # Ensure totals are updated
        data = {}
        data["date"] = self.date_edit.date().toString("dd-MM-yyyy")
        for key, ctrl in self.controllers.items():
            if isinstance(ctrl, (QLineEdit, QTextEdit)):
                data[key] = ctrl.text() if isinstance(ctrl, QLineEdit) else ctrl.toPlainText()
            elif isinstance(ctrl, QComboBox):
                data[key] = ctrl.currentText()

        items = []
        for row in range(self.table.rowCount()):
            items.append({
                "line_no": self.table.item(row,0).text(),
                "part_number": self.table.item(row,1).text(),
                "description": self.table.item(row,2).text(),
                "quantity": self.table.item(row,3).text(),
                "unit_rate": self.table.item(row,4).text(),
                "total": self.table.item(row,5).text()
            })
        data["line_items"] = items
        data["total_amount"] = self.total_amount_edit.text()
        data["receivable_amount"] = self.receivable_edit.text()
        data["receivable_amount_text"] = self.receivable_text_edit.text()
        data["received_amount"] = self.received_edit.text()
        data["balance_amount"] = self.balance_edit.text()

        database.push_to_mongo(data)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Success")
        msg.setText("Invoice form submitted successfully and pushed to MongoDB!")
        msg.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InvoiceForm()
    window.show()
    sys.exit(app.exec())
