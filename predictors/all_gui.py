"""
GUI for Lottery Seek - All Predictors
Supports PySide6 (6.9.0) or falls back to PyQt5
Python 3.13.3
Place this at project root alongside predictor modules.
"""
import sys

# 嘗試使用 PySide6，若未安裝則退回 PyQt5

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QPushButton, QTextEdit, QLabel, QMessageBox
)
QtLib = "PySide6"


# 匯入 predictor 模組
import GUA_hexagram_predictor
import QimenZiwei_predictor
import mystic_predictor
import predict

class MainGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lottery Seek - 全部預測模式整合")
        self.resize(800, 600)

        layout = QVBoxLayout()
        # 顯示當前 Qt 庫
        layout.addWidget(QLabel(f"Using {QtLib}"))
        layout.addWidget(QLabel("請選擇預測模式："))

        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        layout.addWidget(self.text_output)

        # GUA 坤卦預測按鈕
        btn_gua = QPushButton("GUA 卦象預測")
        btn_gua.clicked.connect(self.run_gua)
        layout.addWidget(btn_gua)

        # 奇門紫微預測按鈕
        btn_qimen = QPushButton("奇門紫微預測")
        btn_qimen.clicked.connect(self.run_qimen)
        layout.addWidget(btn_qimen)

        # 神秘預測按鈕
        btn_mystic = QPushButton("神秘預測")
        btn_mystic.clicked.connect(self.run_mystic)
        layout.addWidget(btn_mystic)

        # 通用 predict 模式按鈕
        btn_generic = QPushButton("通用預測模式")
        btn_generic.clicked.connect(self.run_generic)
        layout.addWidget(btn_generic)

        self.setLayout(layout)

    def run_gua(self):
        try:
            result = GUA_hexagram_predictor.predict()
            self.text_output.setPlainText(str(result))
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"GUA 卦象預測發生錯誤：{e}")

    def run_qimen(self):
        try:
            result = QimenZiwei_predictor.predict()
            self.text_output.setPlainText(str(result))
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"奇門紫微預測發生錯誤：{e}")

    def run_mystic(self):
        try:
            result = mystic_predictor.predict()
            self.text_output.setPlainText(str(result))
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"神秘預測發生錯誤：{e}")

    def run_generic(self):
        try:
            result = predict.predict()
            self.text_output.setPlainText(str(result))
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"通用預測模式發生錯誤：{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainGUI()
    window.show()
    sys.exit(app.exec())
