import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QCheckBox, QLabel, QComboBox, QCalendarWidget, QDialog, QTableWidget, QTableWidgetItem, QInputDialog, QListWidget
from PyQt5.QtCore import QDate

class HabitTrackerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SmartHabits")
        self.setGeometry(100, 100, 600, 600)
        self.db = self.init_db()
        self.initUI()

    def init_db(self):
        try:
            conn = sqlite3.connect("habit_tracker.db")
            cursor = conn.cursor()

            # Создаем таблицы, если они не существуют
            cursor.execute('''CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                period INTEGER NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL
            )''')

            cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                is_checked BOOLEAN NOT NULL,
                FOREIGN KEY (habit_id) REFERENCES habits(id)
            )''')

            cursor.execute('''CREATE TABLE IF NOT EXISTS day_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                task TEXT NOT NULL
            )''')

            conn.commit()
            return conn
        except sqlite3.Error as e:
            print(f"Ошибка при подключении к базе данных: {e}")
            sys.exit(1)

    def initUI(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # Календарь
        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(True)
        self.calendar.setFixedSize(600, 300)
        self.calendar.selectionChanged.connect(self.update_selected_date)
        layout.addWidget(self.calendar)

        # Поле добавления привычки
        self.habit_input_layout = QHBoxLayout()
        self.habit_input = QLineEdit(self)
        self.habit_input.setPlaceholderText("Введите привычку")
        self.habit_input.setStyleSheet("padding: 10px; border-radius: 5px; border: 1px solid #ccc; font-size: 14px;")
        self.habit_input_layout.addWidget(self.habit_input)

        self.period_input = QComboBox(self)
        self.period_input.addItems([str(i) + " дней" for i in range(1, 31)])
        self.habit_input_layout.addWidget(self.period_input)

        self.add_habit_button = QPushButton("Добавить", self)
        self.add_habit_button.setStyleSheet("background-color: #5cb85c; color: white; padding: 10px; border-radius: 5px;")
        self.add_habit_button.clicked.connect(self.add_habit)
        self.habit_input_layout.addWidget(self.add_habit_button)
        layout.addLayout(self.habit_input_layout)

        # Список привычек и галочки
        self.habits_layout = QVBoxLayout()
        layout.addLayout(self.habits_layout)

        # Кнопка удаления привычки
        self.delete_habit_button = QPushButton("Удалить привычку", self)
        self.delete_habit_button.setStyleSheet("background-color: #d9534f; color: white; padding: 10px; border-radius: 5px;")
        self.delete_habit_button.clicked.connect(self.delete_habit)
        layout.addWidget(self.delete_habit_button)

        # Кнопка статистики
        self.stats_button = QPushButton("Статистика", self)
        self.stats_button.setStyleSheet("background-color: #0275d8; color: white; padding: 10px; border-radius: 5px;")
        self.stats_button.clicked.connect(self.show_statistics)
        layout.addWidget(self.stats_button)

        # Поле добавления задачи
        self.task_input = QLineEdit(self)
        self.task_input.setPlaceholderText("Введите задачу")
        self.task_input.setStyleSheet("padding: 10px; border-radius: 5px; border: 1px solid #ccc; font-size: 14px;")
        layout.addWidget(self.task_input)

        # Кнопка добавления задачи
        self.add_task_button = QPushButton("Добавить задачу", self)
        self.add_task_button.setStyleSheet("background-color: #5cb85c; color: white; padding: 10px; border-radius: 5px;")
        self.add_task_button.clicked.connect(self.add_task)
        layout.addWidget(self.add_task_button)

        # Список задач на день
        self.selected_date_tasks_layout = QVBoxLayout()
        layout.addLayout(self.selected_date_tasks_layout)

        # Список для выбора задачи для удаления
        self.task_list_widget = QListWidget(self)
        self.selected_date_tasks_layout.addWidget(self.task_list_widget)

        # Кнопка удаления выбранной задачи
        self.delete_task_button = QPushButton("Удалить выбранную задачу", self)
        self.delete_task_button.setStyleSheet("background-color: #d9534f; color: white; padding: 10px; border-radius: 5px;")
        self.delete_task_button.clicked.connect(self.delete_selected_task)
        layout.addWidget(self.delete_task_button)

        self.setLayout(layout)

        self.selected_date = QDate.currentDate()
        self.update_selected_date()

    def update_selected_date(self):
        self.selected_date = self.calendar.selectedDate()
        self.update_task_display()

    def add_habit(self):
        habit_name = self.habit_input.text().strip()
        if not habit_name:
            return

        habit_period = int(self.period_input.currentText().split()[0])

        start_date = self.selected_date
        end_date = start_date.addDays(habit_period - 1)

        try:
            cursor = self.db.cursor()
            cursor.execute("INSERT INTO habits (name, period, start_date, end_date) VALUES (?, ?, ?, ?)",
                           (habit_name, habit_period, start_date.toString("yyyy-MM-dd"), end_date.toString("yyyy-MM-dd")))
            self.db.commit()
            self.habit_input.clear()
            self.update_task_display()
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении привычки: {e}")

    def add_task(self):
        task_name = self.task_input.text().strip()
        if not task_name:
            return

        try:
            cursor = self.db.cursor()
            cursor.execute("INSERT INTO day_tasks (date, task) VALUES (?, ?)",
                           (self.selected_date.toString("yyyy-MM-dd"), task_name))
            self.db.commit()
            self.task_input.clear()
            self.update_task_display()
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении задачи: {e}")

    def update_task_display(self):
        # Очищаем текущие отображаемые привычки и задачи
        for i in reversed(range(self.habits_layout.count())):
            widget = self.habits_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        # Отображаем задачи на день
        self.task_list_widget.clear()

        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT id, task FROM day_tasks WHERE date = ?", (self.selected_date.toString("yyyy-MM-dd"),))
            tasks = cursor.fetchall()

            for task_id, task_name in tasks:
                self.task_list_widget.addItem(task_name)

            # Отображаем привычки
            cursor.execute("SELECT id, name, start_date, end_date FROM habits")
            habits = cursor.fetchall()

            for habit_id, habit_name, start_date, end_date in habits:
                if self.selected_date >= QDate.fromString(start_date, "yyyy-MM-dd") and self.selected_date <= QDate.fromString(end_date, "yyyy-MM-dd"):
                    habit_label = QLabel(habit_name)
                    habit_checkbox = QCheckBox()
                    habit_checkbox.setChecked(self.is_habit_done(habit_id))
                    habit_checkbox.toggled.connect(lambda checked, habit_id=habit_id: self.toggle_habit_check(habit_id, checked))
                    self.habits_layout.addWidget(habit_label)
                    self.habits_layout.addWidget(habit_checkbox)
        except sqlite3.Error as e:
            print(f"Ошибка при обновлении отображения задач и привычек: {e}")

    def is_habit_done(self, habit_id):
        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT is_checked FROM tasks WHERE habit_id = ? AND date = ?",
                           (habit_id, self.selected_date.toString("yyyy-MM-dd")))
            task = cursor.fetchone()
            return task[0] if task else False
        except sqlite3.Error as e:
            print(f"Ошибка при проверке выполнения привычки: {e}")
            return False

    def toggle_habit_check(self, habit_id, checked):
        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT * FROM tasks WHERE habit_id = ? AND date = ?",
                           (habit_id, self.selected_date.toString("yyyy-MM-dd")))
            task = cursor.fetchone()

            if task:
                cursor.execute("UPDATE tasks SET is_checked = ? WHERE habit_id = ? AND date = ?",
                               (checked, habit_id, self.selected_date.toString("yyyy-MM-dd")))
            else:
                cursor.execute("INSERT INTO tasks (habit_id, date, is_checked) VALUES (?, ?, ?)",
                               (habit_id, self.selected_date.toString("yyyy-MM-dd"), checked))
            self.db.commit()
        except sqlite3.Error as e:
            print(f"Ошибка при обновлении состояния привычки: {e}")

    def delete_habit(self):
        habit_name, ok = QInputDialog.getItem(self, "Удалить привычку", "Выберите привычку для удаления:", self.get_habit_names(), 0, False)
        if ok:
            try:
                cursor = self.db.cursor()
                cursor.execute("DELETE FROM habits WHERE name = ?", (habit_name,))
                cursor.execute("DELETE FROM tasks WHERE habit_id NOT IN (SELECT id FROM habits)")
                self.db.commit()
                self.update_task_display()
            except sqlite3.Error as e:
                print(f"Ошибка при удалении привычки: {e}")

    def get_habit_names(self):
        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT name FROM habits")
            habits = cursor.fetchall()
            return [habit[0] for habit in habits]
        except sqlite3.Error as e:
            print(f"Ошибка при получении списка привычек: {e}")
            return []

    def show_statistics(self):
        stats_dialog = StatsDialog(self.db)
        stats_dialog.exec_()

    def delete_selected_task(self):
        selected_item = self.task_list_widget.currentItem()
        if selected_item:
            task_name = selected_item.text()
            try:
                cursor = self.db.cursor()
                cursor.execute("DELETE FROM day_tasks WHERE task = ? AND date = ?",
                               (task_name, self.selected_date.toString("yyyy-MM-dd")))
                self.db.commit()
                self.update_task_display()
            except sqlite3.Error as e:
                print(f"Ошибка при удалении задачи: {e}")


class StatsDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("Статистика выполнения привычек")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()
        self.table = QTableWidget(self)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Привычка", "Количество выполнений"])
        layout.addWidget(self.table)

        self.load_stats()
        self.setLayout(layout)

    def load_stats(self):
        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT habits.name, COUNT(tasks.id) FROM habits "
                           "LEFT JOIN tasks ON habits.id = tasks.habit_id AND tasks.is_checked = 1 "
                           "GROUP BY habits.id")
            stats = cursor.fetchall()

            self.table.setRowCount(len(stats))
            for row, (habit_name, count) in enumerate(stats):
                self.table.setItem(row, 0, QTableWidgetItem(habit_name))
                self.table.setItem(row, 1, QTableWidgetItem(str(count)))
        except sqlite3.Error as e:
            print(f"Ошибка при получении статистики: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HabitTrackerApp()
    window.show()
    sys.exit(app.exec_())
