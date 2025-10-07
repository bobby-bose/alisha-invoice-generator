import sys
import random
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QGroupBox, QMessageBox, QScrollArea, QSizePolicy
)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
import database  # <-- your module to push data

class PackingListForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Packing List Form")
        self.setGeometry(100, 50, 1200, 900)

        # ---------------- Facebook-style theme ----------------
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                font-family: Arial;
            }
            QLabel {
                color: #1c1e21;
                font-weight: bold;
            }
            QLineEdit {
                border: 1px solid #ccd0d5;
                border-radius: 5px;
                padding: 5px;
                font-size: 13px;
                color: black; 
            }
            QPushButton {
                background-color: #1877f2;
                color: white;
                font-weight: bold;
                font-size: 16px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #166fe5;
            }
            QGroupBox {
                border: 2px solid #ccd0d5;
                border-radius: 12px;
            }
            QLabel#LogoLabel {
                height:400;
                width:400;
                border: 2px solid #1877f2;
                border-radius: 60px;
                background-color: #f5f6f7;
                padding: 10px;
            }
        """)

        # ---------------- Form Fields (Packing List placeholders) ----------------
        self.fields = [
            "consignee_address", "date", "po_no", "tax_no",
            "packing_list_no", "delivery_address", "loding_port", "discharge_port",
            "hs_code", "no_boxes", "item_number", "box_number",
            "material", "qty", "dimension", "net_weight", "gross_weight",
            "sum_net_weight", "sum_gross_weight"
        ]

        self.controllers = {}
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

        # Logo QLabel
        logo = QLabel()
        pixmap = QPixmap("wwe.jpg")
        if not pixmap.isNull():
            pixmap = pixmap.scaled(350, 350, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo.setPixmap(pixmap)
        else:
            logo.setText("No Logo")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(logo)

        # Company Info Layout
        company_layout = QVBoxLayout()
        company_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        company_name = QLabel("ZAKA Controls & Devices")
        company_name.setFont(QFont("Arial", 30, QFont.Weight.Bold))
        company_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description = QLabel("This is a Packing List Form. Fill the details below.")
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

        # ---------------- Form Fields ----------------
        for i in range(0, len(self.fields), 4):
            row_layout = QHBoxLayout()
            row_layout.setSpacing(30)

            left_fields = self.fields[i:i+2]
            right_fields = self.fields[i+2:i+4]

            # Left side fields
            left_layout = QVBoxLayout()
            for field_name in left_fields:
                left_layout.addLayout(self.build_field_layout(field_name))
            left_container = QGroupBox()
            left_container.setLayout(left_layout)
            left_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            row_layout.addWidget(left_container)

            # Right side fields
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

        # ---------------- Submit Button ----------------
        submit_btn = QPushButton("Submit")
        submit_btn.setFixedHeight(45)
        submit_btn.setFixedWidth(300)
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
        line_edit.setText(self.generate_dummy())
        line_edit.setFixedHeight(30)
        self.controllers[field_name] = line_edit
        layout.addWidget(label)
        layout.addWidget(line_edit)
        return layout

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
            print("Form Data:", data)

            # Push to MongoDB using your second module
            database.push_to_mongo(data)

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("Success")
            msg.setText("Packing List form submitted successfully and pushed to MongoDB!")
            msg.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PackingListForm()
    window.show()
    sys.exit(app.exec())
