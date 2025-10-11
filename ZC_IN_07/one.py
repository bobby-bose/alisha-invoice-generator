import sys
import random
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QMessageBox, QScrollArea, QSizePolicy, QComboBox, QTextEdit, QDateEdit, QSpinBox
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

        # Styling (unchanged base)
        self.setStyleSheet("""
            QWidget { background-color: #ffffff; font-family: Arial; }
            QLabel { color: #000000; font-weight: bold; font-size: 16pt; }
            QLineEdit, QTextEdit, QDateEdit, QComboBox, QSpinBox {
                border: 1px solid #666666;
                border-radius: 6px;
                padding: 10px;
                font-size: 14pt;
                color: #000000;
                height: 45px;
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
        """)

        self.controllers = {}
        self.table_rows = []
        self.initUI()

    def make_form_row(self, fields):
        row = QHBoxLayout()
        row.setSpacing(20)
        for label_text, widget in fields:
            group = QVBoxLayout()
            label = QLabel(label_text)
            label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            group.addWidget(label)
            group.addWidget(widget)
            row.addLayout(group)
        return row

    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Header
        header_layout = QHBoxLayout()
        logo = QLabel()
        pixmap = QPixmap("wwe.jpg")
        if not pixmap.isNull():
            pixmap = pixmap.scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo.setPixmap(pixmap)
        logo.setAlignment(Qt.AlignmentFlag.AlignLeft)  # aligned to left edge
        header_layout.addWidget(logo)

        # Only one heading text (removed company name)
        heading_label = QLabel("Fill the details for the export invoice below.")
        heading_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        heading_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        header_layout.addWidget(heading_label)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        main_layout.addSpacing(20)

        # Scroll container
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Row 1: Invoice details (with fixed prefix "ZC/IN/")
        invoice_layout = QHBoxLayout()
        invoice_label = QLabel("Invoice Number")
        invoice_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        invoice_prefix = QLineEdit("ZC/IN/")
        invoice_prefix.setReadOnly(True)
        invoice_prefix.setFixedWidth(120)
        invoice_prefix.setStyleSheet("background-color: #e9ecef; color: #333; font-weight: bold;")

        invoice_suffix = QLineEdit()
        invoice_suffix.setPlaceholderText("Enter remaining part")
        invoice_suffix.textChanged.connect(lambda text: self.controllers['invoice_no'].setText(f"ZC/IN/{text}"))

        # Hidden field to store combined invoice number
        invoice_full = QLineEdit()
        invoice_full.setVisible(False)
        self.controllers['invoice_no'] = invoice_full

        invoice_row = QHBoxLayout()
        invoice_row.addWidget(invoice_prefix)
        invoice_row.addWidget(invoice_suffix)
        invoice_widget = QWidget()
        invoice_widget.setLayout(invoice_row)

        invoice_date_input = QDateEdit()
        invoice_date_input.setCalendarPopup(True)
        invoice_date_input.setDate(QDate.currentDate())
        self.controllers['date'] = invoice_date_input
        buyer_order_input = QLineEdit()
        self.controllers['order_no'] = buyer_order_input

        scroll_layout.addLayout(self.make_form_row([
            ("Invoice Number", invoice_widget),
            ("Invoice Date", invoice_date_input),
            ("Buyer's Order Number", buyer_order_input),
        ]))

        # Row 2: Order date, exporter ref, IEC
        buyer_order_date_input = QDateEdit()
        buyer_order_date_input.setCalendarPopup(True)
        buyer_order_date_input.setDate(QDate.currentDate())
        self.controllers['order_date'] = buyer_order_date_input
        exporter_ref_input = QLineEdit()
        self.controllers['exporter_ref'] = exporter_ref_input
        iec_input = QLineEdit()
        self.controllers['iec'] = iec_input

        scroll_layout.addLayout(self.make_form_row([
            ("Buyer's Order Date", buyer_order_date_input),
            ("Exporter's Reference", exporter_ref_input),
            ("IEC Number", iec_input),
        ]))

        # Row 3: Tax, LUT, Terms
        tax_input = QLineEdit()
        self.controllers['tax_no'] = tax_input
        lut_input = QLineEdit()
        self.controllers['lut_arn_no'] = lut_input
        terms_box = QComboBox()
        terms_box.addItems(["Prepaid", "Postpaid"])
        self.controllers['terms'] = terms_box

        scroll_layout.addLayout(self.make_form_row([
            ("Tax Registration Number", tax_input),
            ("LUT ARN Number", lut_input),
            ("Terms of Delivery & Payment", terms_box),
        ]))

        # Row 4: Ports
        port_load_input = QLineEdit()
        self.controllers['port_loading'] = port_load_input
        port_discharge_input = QLineEdit()
        self.controllers['port_Discharge'] = port_discharge_input
        pre_carriage_input = QLineEdit()
        self.controllers['pre_carriage'] = pre_carriage_input

        scroll_layout.addLayout(self.make_form_row([
            ("Port of Loading", port_load_input),
            ("Port of Discharge", port_discharge_input),
            ("Pre-Carriage By", pre_carriage_input),
        ]))

        # Row 5: Place receipt, port destination, destination
        place_receipt_input = QLineEdit()
        self.controllers['place_receipt'] = place_receipt_input
        port_destination_box = QComboBox()
        port_destination_box.addItems(["USA", "India", "Dubai"])
        self.controllers['port_destination'] = port_destination_box
        destination_box = QComboBox()
        destination_box.addItems(["USA", "India", "Dubai"])
        self.controllers['destination'] = destination_box

        scroll_layout.addLayout(self.make_form_row([
            ("Place of Receipt", place_receipt_input),
            ("Port of Destination", port_destination_box),
            ("Destination", destination_box),
        ]))

        # Row 6: Currency, vessel, country
        currency_box = QComboBox()
        currency_box.addItems(["INR (₹)", "USD ($)"])
        self.controllers['currency_sign'] = currency_box
        vessel_box = QComboBox()
        vessel_box.addItems(["By Air", "By Ship", "By Road"])
        self.controllers['vessel_no'] = vessel_box
        country_box = QComboBox()
        country_box.addItems(["India", "USA", "Dubai"])
        self.controllers['country'] = country_box

        scroll_layout.addLayout(self.make_form_row([
            ("Currency", currency_box),
            ("Vessel / Flight", vessel_box),
            ("Country of Origin", country_box),
        ]))

        # Row 7: Final Destination + Other Reference, Consignee, Delivery
        final_destination_box = QComboBox()
        final_destination_box.addItems(["India", "USA", "Dubai"])
        self.controllers['final_destination'] = final_destination_box

        other_ref_input = QLineEdit()
        self.controllers['other_reference'] = other_ref_input

        # Left column: Final Destination above Other Reference
        left_col_layout = QVBoxLayout()
        label_final = QLabel("Final Destination")
        label_final.setAlignment(Qt.AlignmentFlag.AlignLeft)
        label_other = QLabel("Other Reference")
        label_other.setAlignment(Qt.AlignmentFlag.AlignLeft)
        left_col_layout.addWidget(label_final)
        left_col_layout.addWidget(final_destination_box)
        left_col_layout.addSpacing(10)
        left_col_layout.addWidget(label_other)
        left_col_layout.addWidget(other_ref_input)

        # Middle and right columns: Consignee & Delivery addresses (height increased)
        consignee_input = QTextEdit()
        consignee_input.setFixedHeight(160)
        self.controllers['consignee_address'] = consignee_input

        delivery_input = QTextEdit()
        delivery_input.setFixedHeight(160)
        self.controllers['delivery'] = delivery_input

        row7 = QHBoxLayout()
        row7.addLayout(left_col_layout)

        consignee_layout = QVBoxLayout()
        consignee_label = QLabel("Consignee Address")
        consignee_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        consignee_layout.addWidget(consignee_label)
        consignee_layout.addWidget(consignee_input)
        row7.addLayout(consignee_layout)

        delivery_layout = QVBoxLayout()
        delivery_label = QLabel("Delivery Address")
        delivery_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        delivery_layout.addWidget(delivery_label)
        delivery_layout.addWidget(delivery_input)
        row7.addLayout(delivery_layout)

        scroll_layout.addLayout(row7)

        # Row 8: Contact Details
        contact_name_input = QLineEdit()
        self.controllers['contact_details_name'] = contact_name_input
        contact_email_input = QLineEdit()
        self.controllers['contact_details_email'] = contact_email_input
        dummy = QLineEdit()
        dummy.setPlaceholderText("Optional field")

        scroll_layout.addLayout(self.make_form_row([
            ("Contact Person Name", contact_name_input),
            ("Contact Email", contact_email_input),
            ("Other Info", dummy),
        ]))

        # Table section (unchanged)
        self.table_layout = QVBoxLayout()
        header_row = QHBoxLayout()
        for col in ["No./Range of Packages", "Description of Goods", "Unit", "Quantity", "Rate", "Amount"]:
            lbl = QLabel(col)
            lbl.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            lbl.setFixedWidth(180)
            header_row.addWidget(lbl)
        self.table_layout.addLayout(header_row)
        scroll_layout.addLayout(self.table_layout)

        # Add/Remove buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Row")
        add_btn.clicked.connect(self.add_row)
        remove_btn = QPushButton("Remove Row")
        remove_btn.clicked.connect(self.remove_row)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        scroll_layout.addLayout(btn_layout)

        # Totals
        totals_row = QHBoxLayout()
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

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        # Submit
        submit_btn = QPushButton("Submit")
        submit_btn.setFixedHeight(50)
        submit_btn.setFixedWidth(350)
        submit_btn.clicked.connect(self.handle_submit)
        main_layout.addWidget(submit_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(main_layout)

    # --- Existing logic unchanged ---
    def add_row(self):
        row_layout = QHBoxLayout()
        cols = []
        for default_text in ["1-11", "GRP Sunshine for Push Button", "Each", "10", "100"]:
            le = QLineEdit()
            le.setFixedWidth(180)
            le.setText(default_text)
            cols.append(le)
        qty_input = QSpinBox()
        qty_input.setValue(10)
        qty_input.setFixedWidth(180)
        qty_input.valueChanged.connect(self.update_totals)
        cols[3] = qty_input
        amount_input = QLineEdit()
        amount_input.setReadOnly(True)
        amount_input.setFixedWidth(180)
        cols.append(amount_input)
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
        table_data = []
        for row in self.table_rows:
            table_data.append({
                "range": row[0].text(),
                "description": row[1].text(),
                "unit": row[2].text(),
                "quantity": row[3].value() if isinstance(row[3], QSpinBox) else row[3].text(),
                "rate": row[4].text(),
                "amount": row[5].text()
            })
        data['table'] = table_data
        data['total_export_value'] = self.total_export_value.text()
        data['total_gst_value'] = self.total_gst_value.text()
        data['total_invoice_value'] = self.total_invoice_value.text()
        database.push_to_mongo(data)
        QMessageBox.information(self, "Success", "Form submitted successfully and pushed to MongoDB!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExportForm()
    window.show()
    sys.exit(app.exec())
