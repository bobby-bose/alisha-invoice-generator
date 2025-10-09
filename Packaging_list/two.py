# packing_list_app.py
import sys
import random
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QGroupBox, QMessageBox, QScrollArea, QSizePolicy, QTextEdit, QDialog,
    QGridLayout, QSpacerItem
)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDateEdit
from PyQt6.QtCore import QDate
from database import push_to_mongo

# ---------- Helpers ----------
def clear_layout(layout):
    """Recursively clear all items from a layout."""
    if layout is None:
        return
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.setParent(None)
        else:
            sublayout = item.layout()
            if sublayout is not None:
                clear_layout(sublayout)


# ---------- Box Modal ----------
class BoxDialog(QDialog):
    """Modal to add boxes for an item with separate L, W, H inputs."""
    def __init__(self, parent=None, start_box_number=1):
        super().__init__(parent)
        self.setWindowTitle("Add Boxes")
        self.setModal(True)
        self.next_box_number = start_box_number
        self.box_rows = []  # list of dicts {box_number, widgets...}
        self.setMinimumSize(800, 450)
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QDialog { background: white; color: black; }
            QLabel { color: black; }
            QLineEdit { background: #ffffff; color: black; padding: 6px; }
            QPushButton { padding: 6px 10px; }
            .boxRow { border: 1px solid #e0e0e0; border-radius: 6px; padding: 6px; }
        """)
        main = QVBoxLayout()
        main.setAlignment(Qt.AlignmentFlag.AlignTop)

        info = QLabel("Add boxes for this item. Box numbers are auto-generated and unique across all items.")
        info.setWordWrap(True)
        info.setFont(QFont("Segoe UI", 10))
        main.addWidget(info)

        date_group = QGroupBox()
        date_group.setObjectName("section")
        v = QVBoxLayout()
        title = QLabel("Date")
        title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        date_picker = QDateEdit()
        date_picker.setCalendarPopup(True)
        date_picker.setDate(QDate.currentDate())
        date_picker.setDisplayFormat("dd/MM/yyyy")
        v.addWidget(title)
        v.addWidget(date_picker)
        date_group.setLayout(v)


        # Scroll area for rows
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.rows_layout = QVBoxLayout(self.scroll_content)
        self.rows_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        main.addWidget(self.scroll, stretch=1)

        # initial box row
        self.add_box_row()

        # buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        add_btn = QPushButton("+ Add Another Box")
        add_btn.clicked.connect(self.add_box_row)
        btn_row.addWidget(add_btn)

        save_btn = QPushButton("Save Boxes")
        save_btn.clicked.connect(self.accept)
        btn_row.addWidget(save_btn)

        main.addLayout(btn_row)
        self.setLayout(main)

    def add_box_row(self):
        row_widget = QGroupBox()
        row_widget.setObjectName("boxRow")
        row_layout = QHBoxLayout()
        row_widget.setLayout(row_layout)

        # Box number label
        box_no = self.next_box_number
        lbl = QLabel(f"Box {box_no}")
        lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        lbl.setFixedWidth(80)
        row_layout.addWidget(lbl)

        # Quantity
        qty = QLineEdit()
        qty.setPlaceholderText("Quantity")
        qty.setFixedWidth(110)
        row_layout.addWidget(qty)

        # Dimensions: L, W, H
        dim_layout = QHBoxLayout()
        le = QLineEdit(); le.setPlaceholderText("L"); le.setFixedWidth(50)
        wi = QLineEdit(); wi.setPlaceholderText("W"); wi.setFixedWidth(50)
        hi = QLineEdit(); hi.setPlaceholderText("H"); hi.setFixedWidth(50)
        dim_layout.addWidget(le)
        dim_layout.addWidget(wi)
        dim_layout.addWidget(hi)
        row_layout.addLayout(dim_layout)

        # Net weight
        net = QLineEdit()
        net.setPlaceholderText("Net Weight")
        net.setFixedWidth(120)
        row_layout.addWidget(net)

        # Gross weight
        gross = QLineEdit()
        gross.setPlaceholderText("Gross Weight")
        gross.setFixedWidth(120)
        row_layout.addWidget(gross)

        # Remove button
        remove_btn = QPushButton("Remove")
        def remove_row():
            self.rows_layout.removeWidget(row_widget)
            row_widget.setParent(None)
            self.box_rows = [b for b in self.box_rows if b["box_number"] != box_no]
        remove_btn.clicked.connect(remove_row)
        row_layout.addWidget(remove_btn)

        self.rows_layout.addWidget(row_widget)
        self.box_rows.append({
            "box_number": box_no,
            "quantity": qty,
            "length": le,
            "width": wi,
            "height": hi,
            "net_weight": net,
            "gross_weight": gross
        })
        self.next_box_number += 1

    def get_boxes(self):
        boxes = []
        for r in self.box_rows:
            boxes.append({
                "box_number": r["box_number"],
                "quantity": r["quantity"].text().strip(),
                "length": r["length"].text().strip(),
                "width": r["width"].text().strip(),
                "height": r["height"].text().strip(),
                "net_weight": r["net_weight"].text().strip(),
                "gross_weight": r["gross_weight"].text().strip()
            })
        return boxes, self.next_box_number


# ---------- Main Form ----------
class PackingListForm(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Packing List Form")
        self.setGeometry(100, 50, 1280, 920)
        self.global_font = QFont("Segoe UI", 10)
        QApplication.instance() and QApplication.instance().setFont(self.global_font)
        self.setStyleSheet("""
            QWidget { background: white; color: #111111; }
            QGroupBox#section { border: 3px solid black; border-radius: 8px; margin-top: 8px; padding: 10px; }
            QGroupBox#itemCard { border: 3px solid red; border-radius: 8px; padding: 10px; background: #ffffff; }
            QLabel.title { font-weight: bold; font-size: 20px; }
            QLabel.sectionTitle { font-weight: 600; font-size: 18px; }
            QLineEdit, QTextEdit { border: 3px solid green; border-radius: 6px; padding: 6px; }
            QPushButton { background: #f5f5f5; border: 3px solid red; border-radius: 6px; padding: 6px 10px; }
            QPushButton#primary { background: #1976d2; font-size: 20px; color: white; border: none; padding: 20px 250px; border-radius: 6px; }
        """)
        self.controllers = {}
        self.items = []
        self.global_box_counter = 1
        self.item_cards = []
        self.init_ui()

    def generate_dummy(self, chars=4):
        letters = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=chars))
        number = str(random.randint(10, 9999))
        return letters + number

    def init_ui(self):
        root = QVBoxLayout()
        root.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Header
        # Header
# Header
        header = QHBoxLayout()
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setContentsMargins(0, 0, 0, 0)  # remove default margins
        header.setSpacing(12)  # optional spacing between logo and title

        logo_lbl = QLabel()
        pixmap = QPixmap("wwe.jpg")
        if not pixmap.isNull():
            pixmap = pixmap.scaled(280, 280, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_lbl.setPixmap(pixmap)
        else:
            logo_lbl.setText("ZAKA\nControls &\nDevices")
            logo_lbl.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        logo_lbl.setFixedSize(pixmap.width(), pixmap.height())  # match pixmap size
        logo_lbl.setContentsMargins(0,0,0,0)  # remove any QLabel internal padding
        header.addWidget(logo_lbl, alignment=Qt.AlignmentFlag.AlignCenter)

        title_block = QVBoxLayout()
        title_block.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_block.setContentsMargins(0, 0, 0, 0)  # remove padding
        title_block.setSpacing(4)  # small spacing between title and subtitle

        title = QLabel("ZAKA Controls & Devices")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        subtitle = QLabel("Packing List Form - Fill all details below")
        subtitle.setFont(QFont("Segoe UI", 18))
        title_block.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        title_block.addWidget(subtitle, alignment=Qt.AlignmentFlag.AlignCenter)

        header.addLayout(title_block)


        # Remove header.addStretch() to keep it centered
        root.addLayout(header)
        root.addSpacing(4)


        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll.setWidget(content)
        root.addWidget(scroll)

        # ---------- Main form fields (addresses + GST/PO/ports/HS) ----------
        main_group = QGroupBox()
        main_group.setObjectName("section")
        grid = QGridLayout()
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(12)
        main_group.setLayout(grid)

        consignee = self._labeled_textarea("Consignee Address", "Consignee address (3 lines)")
        delivery = self._labeled_textarea("Delivery Address", "Delivery address (3 lines)")
        exporter = self._labeled_textarea("Exporter Address", "Exporter address (3 lines)")
        self.controllers['consignee_address'] = consignee['widget']
        self.controllers['delivery_address'] = delivery['widget']
        self.controllers['exporter_address'] = exporter['widget']

        grid.addWidget(consignee['group'], 0, 0)
        grid.addWidget(delivery['group'], 0, 1)
        grid.addWidget(exporter['group'], 0, 2)

        gst = self._labeled_lineedit("GST / Tax No", self.generate_dummy())
        po = self._labeled_lineedit("PO Number", self.generate_dummy())
        self.controllers['tax_no'] = gst['widget']
        date_picker = QDateEdit()
        date_picker.setCalendarPopup(True)
        date_picker.setDate(QDate.currentDate())
        date_picker.setDisplayFormat("dd/MM/yyyy")
        date_group = QGroupBox()
        date_group.setObjectName("section")
        v = QVBoxLayout()
        title = QLabel("Date")
        title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        v.addWidget(title)
        v.addWidget(date_picker)
        date_group.setLayout(v)
        self.controllers['date'] = date_picker
   # store in controllers

        self.controllers['po_no'] = po['widget']

        grid.addWidget(gst['group'], 1, 0)
        grid.addWidget(date_group, 1, 1)
        grid.addWidget(po['group'], 1, 2)

        lp = self._labeled_lineedit("Loading Port", self.generate_dummy())
        dp = self._labeled_lineedit("Discharge Port", self.generate_dummy())
        hs = self._labeled_lineedit("HS Code", self.generate_dummy())
        self.controllers['loding_port'] = lp['widget']
        self.controllers['discharge_port'] = dp['widget']
        self.controllers['hs_code'] = hs['widget']

        grid.addWidget(lp['group'], 2, 0)
        grid.addWidget(dp['group'], 2, 1)
        grid.addWidget(hs['group'], 2, 2)

        self.content_layout.addWidget(main_group)
        self.content_layout.addSpacing(12)

        # ---------- Items Header ----------
        items_header = QHBoxLayout()
        items_title = QLabel("Items")
        items_title.setProperty("class", "sectionTitle")
        items_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        items_header.addWidget(items_title)
        items_header.addStretch()
        add_item_btn = QPushButton("+ Add Item")
        add_item_btn.clicked.connect(self.add_item)
        items_header.addWidget(add_item_btn)
        self.content_layout.addLayout(items_header)
        self.content_layout.addSpacing(8)

        # ---------- Items container ----------
        self.items_container = QGroupBox()
        self.items_container.setObjectName("section")
        self.items_grid = QGridLayout()
        self.items_grid.setSpacing(12)
        self.items_grid.setContentsMargins(8, 8, 8, 8)
        self.items_container.setLayout(self.items_grid)
        self.content_layout.addWidget(self.items_container)

        # Add default item
        self.add_item()

        # ---------- Submit ----------
        submit_row = QHBoxLayout()
        submit_row.addStretch()
        submit_btn = QPushButton("Submit")
        submit_btn.setObjectName("primary")
        submit_btn.clicked.connect(self.handle_submit)
        submit_row.addWidget(submit_btn)
        submit_row.addStretch()
        self.content_layout.addSpacing(8)
        self.content_layout.addLayout(submit_row)
        self.content_layout.addSpacing(20)

        self.setLayout(root)

    # ---- UI helpers ----
    def _labeled_lineedit(self, label_text, default_text=""):
        group = QGroupBox()
        group.setObjectName("section")
        v = QVBoxLayout()
        title = QLabel(label_text)
        title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        le = QLineEdit()
        le.setText(default_text)
        v.addWidget(title)
        v.addWidget(le)
        group.setLayout(v)
        return {"group": group, "widget": le}

    def _labeled_textarea(self, label_text, placeholder=""):
        group = QGroupBox()
        group.setObjectName("section")
        v = QVBoxLayout()
        title = QLabel(label_text)
        title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        te = QTextEdit()
        te.setPlaceholderText(placeholder)
        te.setFixedHeight(86)
        v.addWidget(title)
        v.addWidget(te)
        group.setLayout(v)
        return {"group": group, "widget": te}

    # ---------- Items ----------
    def add_item(self):
        item_index = len(self.items) + 1
        card = QGroupBox()
        card.setObjectName("itemCard")
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        card_layout = QVBoxLayout()
        card_layout.setSpacing(8)
        card.setLayout(card_layout)

        hdr = QHBoxLayout()
        item_label = QLabel(f"Item {item_index}")
        item_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        hdr.addWidget(item_label)
        hdr.addStretch()
        add_boxes_btn = QPushButton("+")
        add_boxes_btn.setToolTip("Add boxes for this item")
        add_boxes_btn.setFixedWidth(40)
        hdr.addWidget(add_boxes_btn)
        card_layout.addLayout(hdr)

        # material and packaging
        mid = QHBoxLayout()
        mat_group = QGroupBox()
        mg_layout = QVBoxLayout()
        mat_label = QLabel("Material")
        mat_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        mat_input = QLineEdit()
        mg_layout.addWidget(mat_label)
        mg_layout.addWidget(mat_input)
        mat_group.setLayout(mg_layout)
        mid.addWidget(mat_group, stretch=2)

        pack_group = QGroupBox()
        pg_layout = QVBoxLayout()
        pack_label = QLabel("Packaging Description")
        pack_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        pack_input = QLineEdit()
        pg_layout.addWidget(pack_label)
        pg_layout.addWidget(pack_input)
        pack_group.setLayout(pg_layout)
        mid.addWidget(pack_group, stretch=3)

        card_layout.addLayout(mid)

        # box summary
        summary = QLabel("Boxes: 0")
        summary.setFont(QFont("Segoe UI", 10))
        card_layout.addWidget(summary)

        item = {
            "item_number": item_index,
            "material": mat_input,
            "packaging_description": pack_input,
            "boxes": [],
            "card_widget": card,
            "summary_label": summary
        }

        def open_boxes():
            dlg = BoxDialog(self, start_box_number=self.global_box_counter)
            dlg.exec()
            boxes, next_num = dlg.get_boxes()
            if boxes:
                item["boxes"] = boxes
                self.global_box_counter = next_num
                item["summary_label"].setText(f"Boxes: {len(item['boxes'])}")
                self.refresh_items_grid()

        add_boxes_btn.clicked.connect(open_boxes)

        self.items.append(item)
        self.refresh_items_grid()

    def refresh_items_grid(self):
        clear_layout(self.items_grid)
        cols = 2
        for idx, item in enumerate(self.items):
            row = idx // cols
            col = idx % cols
            self.items_grid.addWidget(item["card_widget"], row, col)

    # ---------- Submit ----------
    def handle_submit(self):
        missing = []
        if not self.controllers['consignee_address'].toPlainText().strip():
            missing.append("Consignee Address")
        if not self.controllers['delivery_address'].toPlainText().strip():
            missing.append("Delivery Address")
        if not self.items:
            missing.append("At least one item is required.")
        else:
            for idx, it in enumerate(self.items, start=1):
                if not it['material'].text().strip():
                    missing.append(f"Item {idx} - Material")
                if not it['packaging_description'].text().strip():
                    missing.append(f"Item {idx} - Packaging Description")
                if len(it['boxes']) == 0:
                    missing.append(f"Item {idx} - At least one box")

        if missing:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Missing Fields")
            msg.setText("Please fill the required fields.")
            msg.setDetailedText("\n".join(missing))
            msg.exec()
            return

        # ---------- Calculate totals ----------
        total_boxes = 0
        total_net_weight = 0.0
        total_gross_weight = 0.0

        for it in self.items:
            total_boxes += len(it["boxes"])
            for box in it["boxes"]:
                try:
                    total_net_weight += float(box["net_weight"]) if box["net_weight"] else 0
                except ValueError:
                    total_net_weight += 0
                try:
                    total_gross_weight += float(box["gross_weight"]) if box["gross_weight"] else 0
                except ValueError:
                    total_gross_weight += 0

        # ---------- Prepare data ----------
        data = {
            "consignee_address": self.controllers['consignee_address'].toPlainText(),
            "delivery_address": self.controllers['delivery_address'].toPlainText(),
            "exporter_address": self.controllers['exporter_address'].toPlainText(),
            "date": self.controllers['date'].date().toString("dd/MM/yyyy"),

            "tax_no": self.controllers['tax_no'].text(),
            "po_no": self.controllers['po_no'].text(),
            "loding_port": self.controllers['loding_port'].text(),
            "discharge_port": self.controllers['discharge_port'].text(),
            "hs_code": self.controllers['hs_code'].text(),
            "total_boxes": total_boxes,
            "total_net_weight": total_net_weight,
            "total_gross_weight": total_gross_weight,
            "items": []
        }

        for it in self.items:
            data["items"].append({
                "item_number": it["item_number"],
                "material": it["material"].text(),
                "packaging_description": it["packaging_description"].text(),
                "boxes": it["boxes"]
            })

        # ✅ Push data to MongoDB
        try:
            push_to_mongo(data)
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Database Error")
            msg.setText(f"Failed to save to database:\n{str(e)}")
            msg.exec()
            return

    # Show output
        print("Packing List Submitted:")
        print(data)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Success")
        msg.setText("Packing list submitted successfully!")
        msg.exec()

# ---------- Run ----------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PackingListForm()
    window.show()
    sys.exit(app.exec())
