import sys
import random
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QGroupBox, QMessageBox, QScrollArea, QSizePolicy, QComboBox, QTextEdit, QDateEdit, QSpinBox
)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt, QDate
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import database

class ExportForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Export Form")
        self.setGeometry(100, 50, 1300, 1000)

        # ---------------- Style ----------------
        self.setStyleSheet("""
            QWidget { background-color: #ffffff; font-family: Arial; }
            QLabel { color: #1c1e21; font-weight: bold; font-size: 14pt; }
            QLineEdit, QTextEdit, QDateEdit, QComboBox, QSpinBox {
                border: 1px solid #666666; 
                border-radius: 6px; 
                padding: 5px; 
                font-size: 13px; 
                color: black;
            }
            QComboBox { background-color: white; color: black; }
            QPushButton { 
                background-color: #1877f2; 
                color: white; 
                font-weight: bold; 
                font-size: 16px; 
                border-radius: 8px; 
                padding: 5px 20px;
            }
            QPushButton:hover { background-color: #166fe5; }
            QGroupBox { border: 2px solid #ccd0d5; border-radius: 12px; padding: 10px; }
            QLabel#LogoLabel { height:400px; width:400px; border: 2px solid #1877f2; border-radius: 60px; background-color: #f5f6f7; padding: 10px; }
        """)

        self.controllers = {}
        self.table_rows = []
        self.initUI()

    def generate_dummy(self, length_options=[3,5,7]):
        length = random.choice(length_options)
        letters = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=length))
        number = str(random.randint(10,9999))
        return letters + number

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
        description = QLabel("Fill the details for the export invoice below.")
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
        scroll_layout = QVBoxLayout(scroll_content)

        # ---------------- Row 1: Invoice Number ----------------
        row1 = QHBoxLayout()
        row1.setSpacing(20)

        invoice_label = QLabel("Invoice Number:")
        row1.addWidget(invoice_label)
        prefix_label = QLabel("CIN/IN")
        row1.addWidget(prefix_label)
        invoice_input = QLineEdit()
        self.controllers['invoice_no'] = invoice_input
        row1.addWidget(invoice_input)

        scroll_layout.addLayout(row1)
        scroll_layout.addSpacing(15)

        # ---------------- Row 2: Dates ----------------
        row2 = QHBoxLayout()
        row2.setSpacing(20)

        invoice_date_label = QLabel("Invoice Date:")
        row2.addWidget(invoice_date_label)
        invoice_date_input = QDateEdit()
        invoice_date_input.setCalendarPopup(True)
        invoice_date_input.setDate(QDate.currentDate())
        self.controllers['invoice_date'] = invoice_date_input
        row2.addWidget(invoice_date_input)

        buyer_order_label = QLabel("Buyer's Order Date:")
        row2.addWidget(buyer_order_label)
        buyer_order_input = QDateEdit()
        buyer_order_input.setCalendarPopup(True)
        buyer_order_input.setDate(QDate.currentDate())
        self.controllers['buyer_order_date'] = buyer_order_input
        row2.addWidget(buyer_order_input)

        scroll_layout.addLayout(row2)
        scroll_layout.addSpacing(15)

        # ---------------- Row 3: Exporter & Consignee Addresses ----------------
        row3 = QHBoxLayout()
        row3.setSpacing(20)

        exporter_label = QLabel("Exporter Address:")
        row3.addWidget(exporter_label)
        exporter_input = QTextEdit()
        exporter_input.setFixedHeight(100)
        self.controllers['exporter_address'] = exporter_input
        row3.addWidget(exporter_input)

        consignee_label = QLabel("Consignee Address:")
        row3.addWidget(consignee_label)
        consignee_input = QTextEdit()
        consignee_input.setFixedHeight(100)
        self.controllers['consignee_address'] = consignee_input
        row3.addWidget(consignee_input)

        scroll_layout.addLayout(row3)
        scroll_layout.addSpacing(15)

        # ---------------- Row 4: Currency & Vessel ----------------
        row4 = QHBoxLayout()
        row4.setSpacing(20)

        currency_label = QLabel("Currency:")
        row4.addWidget(currency_label)
        currency_box = QComboBox()
        currency_box.addItems(["INR", "USD"])
        self.controllers['currency'] = currency_box
        row4.addWidget(currency_box)

        vessel_label = QLabel("Vessel/Flight:")
        row4.addWidget(vessel_label)
        vessel_box = QComboBox()
        vessel_box.addItems(["By Air", "By Ship", "By Road"])
        self.controllers['vessel_type'] = vessel_box
        row4.addWidget(vessel_box)

        scroll_layout.addLayout(row4)
        scroll_layout.addSpacing(15)

        # ---------------- Row 5: Final Destination & Country ----------------
        row5 = QHBoxLayout()
        row5.setSpacing(20)

        final_dest_label = QLabel("Final Destination:")
        row5.addWidget(final_dest_label)
        final_dest_box = QComboBox()
        final_dest_box.addItems(["Dubai-UAE", "Sharjah-UAE", "India", "USA"])
        self.controllers['final_destination'] = final_dest_box
        row5.addWidget(final_dest_box)

        country_label = QLabel("Country of Origin:")
        row5.addWidget(country_label)
        country_box = QComboBox()
        country_box.addItems(["India", "USA", "Dubai"])
        self.controllers['country_of_origin'] = country_box
        row5.addWidget(country_box)

        scroll_layout.addLayout(row5)
        scroll_layout.addSpacing(20)

        # ---------------- Table Header ----------------
        self.table_layout = QVBoxLayout()
        header_row = QHBoxLayout()
        for col in ["No./Range of Packages", "Description of Goods", "Unit", "Quantity", "Rate", "Amount"]:
            lbl = QLabel(col)
            lbl.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            lbl.setFixedWidth(180)
            header_row.addWidget(lbl)
        self.table_layout.addLayout(header_row)
        scroll_layout.addLayout(self.table_layout)

        # ---------------- Add/Remove Row Buttons ----------------
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Row")
        add_btn.clicked.connect(self.add_row)
        btn_layout.addWidget(add_btn)
        remove_btn = QPushButton("Remove Row")
        remove_btn.clicked.connect(self.remove_row)
        btn_layout.addWidget(remove_btn)
        scroll_layout.addLayout(btn_layout)

        # ---------------- Totals Row ----------------
        totals_row = QHBoxLayout()
        totals_row.setSpacing(20)

        self.total_export_value = QLineEdit()
        self.total_export_value.setReadOnly(True)
        self.total_export_value.setPlaceholderText("Total Export Value")
        totals_row.addWidget(self.total_export_value)

        self.total_gst_value = QLineEdit()
        self.total_gst_value.setPlaceholderText("Enter Total GST Value")
        self.total_gst_value.textChanged.connect(self.update_totals)
        totals_row.addWidget(self.total_gst_value)

        self.total_invoice_value = QLineEdit()
        self.total_invoice_value.setReadOnly(True)
        self.total_invoice_value.setPlaceholderText("Total Invoice Value")
        totals_row.addWidget(self.total_invoice_value)

        scroll_layout.addLayout(totals_row)
        scroll_layout.addSpacing(20)

        scroll_content.setLayout(scroll_layout)
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        # ---------------- Submit Button ----------------
        submit_btn = QPushButton("Submit")
        submit_btn.setFixedHeight(50)
        submit_btn.setFixedWidth(350)
        submit_btn.clicked.connect(self.handle_submit)
        main_layout.addWidget(submit_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addSpacing(20)

        self.setLayout(main_layout)

    # ---------------- Add/Remove Table Rows ----------------
    def add_row(self):
        row_layout = QHBoxLayout()
        cols = []

        # No./Range
        no_input = QLineEdit()
        no_input.setFixedWidth(180)
        no_input.setText("1-11")
        cols.append(no_input)

        # Description
        desc_input = QLineEdit()
        desc_input.setFixedWidth(180)
        desc_input.setText("GRP Sunshine for Push Button")
        cols.append(desc_input)

        # Unit
        unit_input = QLineEdit()
        unit_input.setFixedWidth(180)
        unit_input.setText("Each")
        cols.append(unit_input)

        # Quantity
        qty_input = QSpinBox()
        qty_input.setFixedWidth(180)
        qty_input.setMaximum(10000)
        qty_input.setValue(10)
        qty_input.valueChanged.connect(self.update_totals)
        cols.append(qty_input)

        # Rate
        rate_input = QLineEdit()
        rate_input.setFixedWidth(180)
        rate_input.setText("100")
        rate_input.textChanged.connect(self.update_totals)
        cols.append(rate_input)

        # Amount
        amount_input = QLineEdit()
        amount_input.setReadOnly(True)
        amount_input.setFixedWidth(180)
        cols.append(amount_input)

        # Add widgets to layout
        for w in cols:
            row_layout.addWidget(w)

        self.table_layout.addLayout(row_layout)
        self.table_rows.append(cols)
        self.update_totals()

    def remove_row(self):
        if self.table_rows:
            last_row = self.table_rows.pop()
            for w in last_row:
                w.hide()
            self.update_totals()

    # ---------------- Update Totals ----------------
    def update_totals(self):
        total_export = 0
        for row in self.table_rows:
            try:
                qty = int(row[3].value()) if isinstance(row[3], QSpinBox) else int(row[3].text())
                rate = float(row[4].text())
                row[5].setText(str(qty * rate))
                total_export += qty * rate
            except:
                continue
        self.total_export_value.setText(str(total_export))

        try:
            gst_val = float(self.total_gst_value.text())
        except:
            gst_val = 0
        self.total_invoice_value.setText(str(total_export + gst_val))

    # ---------------- Submit ----------------
    def handle_submit(self):
        data = {}
        for key, widget in self.controllers.items():
            if isinstance(widget, QLineEdit):
                data[key] = widget.text()
            elif isinstance(widget, QTextEdit):
                data[key] = widget.toPlainText()
            elif isinstance(widget, QDateEdit):
                data[key] = widget.date().toString("yyyy-MM-dd")
            elif isinstance(widget, QComboBox):
                data[key] = widget.currentText()

        # Table Data
        table_data = []
        for row in self.table_rows:
            row_dict = {
                "range": row[0].text(),
                "description": row[1].text(),
                "unit": row[2].text(),
                "quantity": row[3].value() if isinstance(row[3], QSpinBox) else row[3].text(),
                "rate": row[4].text(),
                "amount": row[5].text()
            }
            table_data.append(row_dict)

        data['table'] = table_data
        data['total_export_value'] = self.total_export_value.text()
        data['total_gst_value'] = self.total_gst_value.text()
        data['total_invoice_value'] = self.total_invoice_value.text()

        database.push_to_mongo(data)

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Success")
        msg.setText("Form submitted successfully and pushed to MongoDB!")
        msg.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExportForm()
    window.show()
    sys.exit(app.exec())
