from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .command_files import CommandFileEngine


class CommandFileLab(QWidget):
    def __init__(self, engine: CommandFileEngine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self._build()
        self.refresh_files()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(8)

        header = QFrame()
        header.setObjectName("WorkbenchHeader")
        h = QHBoxLayout(header)
        h.addWidget(QLabel("COMMAND FILES"))
        h.addWidget(QLabel("Deterministic batch execution lab"), 1)
        self.clock_label = QLabel("VIRTUAL CLOCK 00:00")
        self.clock_label.setObjectName("StatusChip")
        h.addWidget(self.clock_label)
        root.addWidget(header)

        controls = QFrame()
        controls.setObjectName("CommandDock")
        form = QVBoxLayout(controls)

        top = QHBoxLayout()
        top.addWidget(QLabel("FILE"))
        self.file_name = QLineEdit()
        self.file_name.setPlaceholderText("block-demo")
        top.addWidget(self.file_name, 1)

        self.schedule_time = QLineEdit()
        self.schedule_time.setPlaceholderText("HH:MM")
        self.schedule_time.setMaximumWidth(90)
        top.addWidget(QLabel("SCHEDULE"))
        top.addWidget(self.schedule_time)

        save_btn = QPushButton("ACCEPT")
        save_btn.clicked.connect(self.accept_file)
        top.addWidget(save_btn)

        execute_btn = QPushButton("EXECUTE")
        execute_btn.clicked.connect(self.execute_file)
        top.addWidget(execute_btn)
        form.addLayout(top)

        editor_row = QHBoxLayout()
        self.editor = QTextEdit()
        self.editor.setPlaceholderText(
            "> block-demo;\n"
            "> mod sub: dn=2233500, blk=accsusp;\n"
            "> disp sub: dn=2233500;\n"
            "> endfile;"
        )
        editor_row.addWidget(self.editor, 2)

        right = QVBoxLayout()
        right.addWidget(QLabel("SCHEDULED RUN"))
        schedule_btn = QPushButton("SCHEDULE")
        schedule_btn.clicked.connect(self.schedule_file)
        right.addWidget(schedule_btn)

        load_btn = QPushButton("LOAD DEMO")
        load_btn.clicked.connect(self.load_demo)
        right.addWidget(load_btn)

        advance5 = QPushButton("+5 MIN")
        advance5.clicked.connect(lambda: self.advance_clock(5))
        right.addWidget(advance5)

        advance60 = QPushButton("+1 HOUR")
        advance60.clicked.connect(lambda: self.advance_clock(60))
        right.addWidget(advance60)

        set_btn = QPushButton("SET CLOCK")
        set_btn.clicked.connect(self.set_clock)
        right.addWidget(set_btn)

        reset_btn = QPushButton("RESET CLOCK")
        reset_btn.clicked.connect(self.reset_clock)
        right.addWidget(reset_btn)

        right.addWidget(QLabel("Files"))
        self.file_list = QListWidget()
        self.file_list.currentItemChanged.connect(self.load_selected)
        right.addWidget(self.file_list, 1)
        editor_row.addLayout(right, 1)

        form.addLayout(editor_row)
        root.addWidget(controls, 1)

        self.status_label = QLabel("Accepted → Started → Finished → Executed")
        self.status_label.setStyleSheet("font-weight:800;")
        root.addWidget(self.status_label)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(190)
        self.log.setObjectName("Terminal")
        root.addWidget(self.log)

    def refresh_files(self):
        current = self.file_name.text().strip()
        self.file_list.clear()
        for item in self.engine.list_files():
            row = QListWidgetItem(
                f"{item.file_name} · {item.status}"
                + (f" · @{item.scheduled_at}" if item.scheduled_at else "")
            )
            row.setData(Qt.UserRole, item.file_name)
            self.file_list.addItem(row)
        if current:
            for i in range(self.file_list.count()):
                if self.file_list.item(i).data(Qt.UserRole) == current:
                    self.file_list.setCurrentRow(i)
                    break
        self.clock_label.setText(f"VIRTUAL CLOCK {self.engine.clock.current}")

    def load_selected(self, item, _previous=None):
        if not item:
            return
        name = item.data(Qt.UserRole)
        file = self.engine.get(name)
        if not file:
            return
        self.file_name.setText(file.file_name)
        self.editor.setPlainText(file.raw_commands)
        self.show_log(file)

    def show_log(self, file):
        lines = [
            f"{file.file_name} · {file.status}",
            f"Scheduled: {file.scheduled_at or '—'}",
        ]
        for entry in file.executed_log:
            lines.append(
                f"L{entry.get('line','?')} · "
                f"{entry.get('code','')} · "
                f"{'OK' if entry.get('ok') else 'FAILED'} · "
                f"{entry.get('message','')}"
            )
        self.log.setPlainText("\n".join(lines))

    def accept_file(self):
        try:
            file = self.engine.save(
                self.file_name.text().strip(),
                self.editor.toPlainText(),
            )
        except ValueError as exc:
            QMessageBox.warning(self, "Command File", str(exc))
            return
        self.status_label.setText(f"{file.file_name} · ACCEPTED")
        self.refresh_files()

    def schedule_file(self):
        try:
            name = self.file_name.text().strip()
            if not self.engine.get(name):
                self.accept_file()
            file = self.engine.schedule(name, self.schedule_time.text().strip())
        except ValueError as exc:
            QMessageBox.warning(self, "Schedule", str(exc))
            return
        self.status_label.setText(
            f"{file.file_name} · ACCEPTED · scheduled {file.scheduled_at}"
        )
        self.refresh_files()

    def execute_file(self):
        name = self.file_name.text().strip()
        result = self.engine.execute(name)
        self.status_label.setText(
            f"{result.file_name} · {result.status} · "
            f"{result.executed} executed · {result.failed} failed"
        )
        self.refresh_files()
        file = self.engine.get(name)
        if file:
            self.show_log(file)

    def advance_clock(self, minutes: int):
        results = self.engine.advance(minutes)
        self.refresh_files()
        if results:
            messages = [
                f"{result.file_name}: {result.status} ({result.message})"
                for result in results
            ]
            self.log.append("\n".join(messages))
            self.status_label.setText(
                f"VIRTUAL CLOCK {self.engine.clock.current} · "
                f"{len(results)} scheduled file(s) processed"
            )
        else:
            self.status_label.setText(
                f"VIRTUAL CLOCK {self.engine.clock.current} · no due files"
            )

    def set_clock(self):
        try:
            value = self.engine.clock.set(self.schedule_time.text().strip())
        except ValueError as exc:
            QMessageBox.warning(self, "Virtual Clock", str(exc))
            return
        self.clock_label.setText(f"VIRTUAL CLOCK {value}")
        self.status_label.setText(f"VIRTUAL CLOCK {value}")

    def reset_clock(self):
        value = self.engine.reset_clock()
        self.refresh_files()
        self.status_label.setText(f"VIRTUAL CLOCK {value}")

    def load_demo(self):
        self.file_name.setText("block-demo")
        self.editor.setPlainText(
            "> block-demo;\n"
            "> mod sub: dn=2233500, blk=accsusp;\n"
            "> disp sub: dn=2233500;\n"
            "> endfile;"
        )
        self.schedule_time.setText("02:00")
