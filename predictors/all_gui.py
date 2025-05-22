#!/usr/bin/env python3
"""
all_gui.py

PySide6 Unified GUI integrating all lottery prediction methods

Integrates:
 - 八卦卦象預測 (GUA_hexagram_predictor)
 - 玄學規則預測 (mystic_predictor)
 - 奇門紫微映射預測 (mapping_engine)
 - 科學權重預測 (predict.py 方法集)
 - 簡易奇門紫微預測 (QimenZiwei_predictor)

Requirements:
 - Python 3.13+
 - PySide6 (pip install PySide6)
 - 所有 predictor 模組與本檔放同一資料夾
"""
import sys
import os
from datetime import datetime
import numpy as np

from PySide6.QtWidgets import (
    QApplication, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QLineEdit, QDoubleSpinBox,
    QSpinBox, QCheckBox, QComboBox, QMessageBox
)

# ----- GUA 卦象預測 -----
from GUA_hexagram_predictor import auto_hexagram, datetime_hexagram, generate_numbers

# ----- 玄學神秘預測 -----
from mystic_predictor import generate_combo

# ----- 映射(奇門紫微)預測 -----
from mapping_engine import (
    qimen_number_weights, ziwei_number_weights,
    combine_weights, predict_top, predict_random
)

# ----- 科學權重預測 -----
from predict import (
    load_history, frequency_weights, recency_weights,
    numerology_weights, fibonacci_weights, combine as sc_combine,
    predict as sc_predict
)

# ----- 簡易奇門紫微預測 -----
from QimenZiwei_predictor import (
    qimen_weights as qz_qimen_weights,
    ziwei_weights as qz_ziwei_weights,
    pick_numbers as qz_pick_numbers
)

class MainGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lottery Seek – 全部預測模式整合")
        self.resize(800, 600)
        main_layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self._init_tab_gua()
        self._init_tab_mystic()
        self._init_tab_map()
        self._init_tab_sci()
        self._init_tab_qz()

    # Tab: 八卦卦象預測
    def _init_tab_gua(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        btn_rand = QPushButton("隨機起卦")
        btn_rand.clicked.connect(self.run_hex_random)
        btn_time = QPushButton("以當前時間起卦")
        btn_time.clicked.connect(self.run_hex_time)
        layout.addWidget(btn_rand)
        layout.addWidget(btn_time)
        self.hex_output = QTextEdit(); self.hex_output.setReadOnly(True)
        layout.addWidget(self.hex_output)
        self.tabs.addTab(tab, "八卦預測")

    def run_hex_random(self):
        try:
            lines = auto_hexagram()
            nums = generate_numbers(lines)
            self.hex_output.setPlainText(f"爻: {lines}\n預測號碼: {nums}")
        except Exception as e:
            QMessageBox.critical(self, "錯誤", str(e))

    def run_hex_time(self):
        try:
            lines = datetime_hexagram(datetime.now())
            nums = generate_numbers(lines)
            self.hex_output.setPlainText(f"爻: {lines}\n預測號碼: {nums}")
        except Exception as e:
            QMessageBox.critical(self, "錯誤", str(e))

    # Tab: 玄學神秘預測
    def _init_tab_mystic(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        btn = QPushButton("生成神秘預測")
        btn.clicked.connect(self.run_mystic)
        layout.addWidget(btn)
        self.mystic_output = QTextEdit(); self.mystic_output.setReadOnly(True)
        layout.addWidget(self.mystic_output)
        self.tabs.addTab(tab, "玄學神秘")

    def run_mystic(self):
        try:
            combo = generate_combo()
            if combo:
                self.mystic_output.setPlainText(f"預測號碼: {combo}")
            else:
                raise ValueError("無法生成符合條件的組合")
        except Exception as e:
            QMessageBox.critical(self, "錯誤", str(e))

    # Tab: 映射(奇門紫微)預測
    def _init_tab_map(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        # 輸入: 出生日期
        layout.addWidget(QLabel("出生日期 (YYYY-MM-DD HH:MM):"))
        self.map_birth = QLineEdit("1990-05-17 15:30")
        layout.addWidget(self.map_birth)
        # 時區偏移
        layout.addWidget(QLabel("時區偏移 (例:8.0):"))
        self.map_tz = QDoubleSpinBox(); self.map_tz.setRange(-12,12); self.map_tz.setValue(8.0)
        layout.addWidget(self.map_tz)
        # 經度
        layout.addWidget(QLabel("當地經度 (度):"))
        self.map_lon = QDoubleSpinBox(); self.map_lon.setRange(-180,180); self.map_lon.setValue(120.0)
        layout.addWidget(self.map_lon)
        # 比重 α
        layout.addWidget(QLabel("奇門比重 α (0~1):"))
        self.map_alpha = QDoubleSpinBox(); self.map_alpha.setRange(0,1); self.map_alpha.setSingleStep(0.1); self.map_alpha.setValue(0.5)
        layout.addWidget(self.map_alpha)
        # 策略
        layout.addWidget(QLabel("選號策略:"))
        self.map_method = QComboBox(); self.map_method.addItems(["top","random"])
        layout.addWidget(self.map_method)
        # K 值
        layout.addWidget(QLabel("選取數量 K:"))
        self.map_k = QSpinBox(); self.map_k.setRange(1,49); self.map_k.setValue(6)
        layout.addWidget(self.map_k)
        btn = QPushButton("生成映射預測")
        btn.clicked.connect(self.run_map)
        layout.addWidget(btn)
        self.map_output = QTextEdit(); self.map_output.setReadOnly(True)
        layout.addWidget(self.map_output)
        self.tabs.addTab(tab, "映射預測")

    def run_map(self):
        try:
            dt = datetime.strptime(self.map_birth.text(), '%Y-%m-%d %H:%M')
            tz = self.map_tz.value()
            lon = self.map_lon.value()
            alpha = self.map_alpha.value()
            k = self.map_k.value()
            w_qm = qimen_number_weights(datetime.now(), lon)
            w_zw = ziwei_number_weights(dt, tz)
            w = combine_weights(w_qm, w_zw, alpha)
            if self.map_method.currentText() == 'top':
                nums = predict_top(w, k)
            else:
                nums = predict_random(w, k)
            self.map_output.setPlainText(f"預測號碼: {nums}")
        except Exception as e:
            QMessageBox.critical(self, "錯誤", str(e))

    # Tab: 科學權重預測
    def _init_tab_sci(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        # 方法選擇
        self.sci_checks = {}
        for name, func in [('頻率', frequency_weights), ('時序', recency_weights), ('數字學', numerology_weights), ('Fibonacci', fibonacci_weights)]:
            cb = QCheckBox(name); cb.setChecked(True)
            self.sci_checks[name] = (cb, func)
            layout.addWidget(cb)
        # 策略
        layout.addWidget(QLabel("策略:"))
        self.sci_method = QComboBox(); self.sci_method.addItems(['top','random'])
        layout.addWidget(self.sci_method)
        # K 值
        layout.addWidget(QLabel("K:"))
        self.sci_k = QSpinBox(); self.sci_k.setRange(1,49); self.sci_k.setValue(6)
        layout.addWidget(self.sci_k)
        btn = QPushButton("生成科學預測")
        btn.clicked.connect(self.run_sci)
        layout.addWidget(btn)
        self.sci_output = QTextEdit(); self.sci_output.setReadOnly(True)
        layout.addWidget(self.sci_output)
        self.tabs.addTab(tab, "科學預測")

    def run_sci(self):
        try:
            reds = load_history()
            weights = []
            for name, (cb, func) in self.sci_checks.items():
                if cb.isChecked(): weights.append(func(reds))
            if not weights: raise ValueError("請至少選擇一種方法")
            alphas = [1/len(weights)]*len(weights)
            w = sc_combine(weights, alphas)
            k = self.sci_k.value()
            if self.sci_method.currentText() == 'top':
                nums = sc_predict(w, 'top', k)
            else:
                nums = sc_predict(w, 'random', k)
            self.sci_output.setPlainText(f"預測號碼: {nums}")
        except Exception as e:
            QMessageBox.critical(self, "錯誤", str(e))

    # Tab: 簡易奇門紫微
    def _init_tab_qz(self):
        tab = QWidget(); layout = QVBoxLayout(tab)
        layout.addWidget(QLabel("輸入生日 (YYYY-MM-DD):"))
        self.qz_birth = QLineEdit('1990-05-17')
        layout.addWidget(self.qz_birth)
        layout.addWidget(QLabel("α 奇門比重 (0~1):"))
        self.qz_alpha = QDoubleSpinBox(); self.qz_alpha.setRange(0,1); self.qz_alpha.setSingleStep(0.1); self.qz_alpha.setValue(0.5)
        layout.addWidget(self.qz_alpha)
        btn = QPushButton("生成簡易奇門紫微")
        btn.clicked.connect(self.run_qz)
        layout.addWidget(btn)
        self.qz_output = QTextEdit(); self.qz_output.setReadOnly(True)
        layout.addWidget(self.qz_output)
        self.tabs.addTab(tab, "簡易奇門紫微")

    def run_qz(self):
        try:
            birth = datetime.strptime(self.qz_birth.text(), '%Y-%m-%d')
            alpha = self.qz_alpha.value()
            qm_w = qz_qimen_weights(datetime.now())
            zw_w = qz_ziwei_weights(birth)
            w = qm_w*alpha + zw_w*(1-alpha)
            w /= w.sum()
            top6 = np.argsort(w)[-6:][::-1]+1
            rand6 = qz_pick_numbers(w, 6)
            self.qz_output.setPlainText(f"Top6: {list(top6)}\nRandom6: {rand6}")
        except Exception as e:
            QMessageBox.critical(self, "錯誤", str(e))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainGUI()
    window.show()
    sys.exit(app.exec())
