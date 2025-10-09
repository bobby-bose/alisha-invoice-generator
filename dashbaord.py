import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSizePolicy
)
from PyQt6.QtGui import QFont, QPixmap, QColor
from PyQt6.QtCore import Qt

from Packaging_list import two_view
from Proforma_Invoice import three_view
from ZC_IN_07 import one_view

# ---- Dashboard ----
class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard")
        self.setMinimumSize(900, 650)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout()
        central.setLayout(main_layout)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Align everything to top

        # --- Logo ---
        self.logo_label = QLabel()
        self.logo_pixmap = QPixmap("wwe.jpg")  # <-- replace with your logo path
        self.logo_pixmap = self.logo_pixmap.scaledToWidth(400, Qt.TransformationMode.SmoothTransformation)
        self.logo_label.setPixmap(self.logo_pixmap)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.logo_label)

        # --- Heading ---
        self.heading_label = QLabel("Select a Form to Open")
        self.heading_label.setFont(QFont("Arial", 40, QFont.Weight.Bold))
        # add some margin to the top and bottom
        self.heading_label.setContentsMargins(0, 40, 0, 40)
        self.heading_label.setStyleSheet("color: #2E86C1;")  # Blue color, change if needed
        self.heading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.heading_label)

        # --- Horizontal layout for buttons ---
        button_layout = QHBoxLayout()
        button_layout.setSpacing(60)  # Space between buttons
        button_layout.setContentsMargins(50, 20, 20, 20)  # Top and left padding

        # Buttons
        self.btn_packing = QPushButton("Packaging List")
        self.btn_export = QPushButton("ZC/IN")
        self.btn_invoice = QPushButton("Proforma Invoice")

        for btn in [self.btn_packing, self.btn_export, self.btn_invoice]:
            btn.setFont(QFont("Arial", 25, QFont.Weight.Bold))
            btn.setMinimumWidth(200)
            btn.setMinimumHeight(50)
            # add padding inside the button
            btn.setStyleSheet("""

                QPushButton {
                    background-color: #117A65;  /* Dark Green */
                    color: white;
                    border-radius: 10px;
                    padding: 10px 20px;
                }
                QPushButton:hover {
                    background-color: #148F77;  /* Lighter Green on hover */
                }
                QPushButton:pressed {
                    background-color: #0E6655;  /* Even Darker Green on press */
                }
            """)
            btn.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            button_layout.addWidget(btn)

        main_layout.addLayout(button_layout)

        # Connect buttons
        self.btn_packing.clicked.connect(self.open_packing_form)
        self.btn_export.clicked.connect(self.open_export_form)
        self.btn_invoice.clicked.connect(self.open_invoice_form)

    # ---- Navigation functions ----
    def open_packing_form(self):
        self.packing_window = two_view.PackingListTable()
        self.packing_window.show()

    def open_export_form(self):
        self.export_window = one_view.ExportTable()
        self.export_window.show()

    def open_invoice_form(self):
        self.invoice_window = three_view.InvoiceTable()
        self.invoice_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Dashboard()
    window.show()
    sys.exit(app.exec())
