from qtsymbols import *

import gobject
from gui.dynalang import LDialog, LPushButton
from gui.usefulwidget import getIconButton

class VocabularyViewer(LDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("生词本管理")
        self.resize(600, 400)
        self.layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["单词", "句子", "时间"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        
        # Enable multi-selection
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        self.layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        self.refresh_btn = LPushButton("刷新")
        self.refresh_btn.clicked.connect(self.refresh)
        btn_layout.addWidget(self.refresh_btn)

        self.delete_btn = LPushButton("删除选中")
        self.delete_btn.clicked.connect(self.delete_selected)
        btn_layout.addWidget(self.delete_btn)
        
        self.layout.addLayout(btn_layout)

        gobject.base.vocabulary_manager.vocabulary_changed.connect(self.refresh)
        self.refresh()

    def refresh(self):
        self.table.setRowCount(0)
        words = gobject.base.vocabulary_manager.get_all_words()
        self.table.setRowCount(len(words))
        
        for row, entry in enumerate(words):
            word_item = QTableWidgetItem(entry.get("word", ""))
            sentence_item = QTableWidgetItem(entry.get("sentence", ""))
            date_item = QTableWidgetItem(entry.get("date", ""))
            
            self.table.setItem(row, 0, word_item)
            self.table.setItem(row, 1, sentence_item)
            self.table.setItem(row, 2, date_item)

    def delete_selected(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            return
        
        # We only need rows, and since we enabled SelectRows, selectedItems returns all cells in row.
        # We just need column 0 content (the word) for each distinct row.
        rows = set()
        words_to_delete = []
        for item in selected_items:
            if item.row() not in rows:
                rows.add(item.row())
                word = self.table.item(item.row(), 0).text()
                if word:
                    words_to_delete.append(word)
        
        if not words_to_delete:
            return

        if QMessageBox.question(self, "确认删除", f"确定要删除选中的 {len(words_to_delete)} 个单词吗？", 
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            for word in words_to_delete:
                gobject.base.vocabulary_manager.remove_word(word)
