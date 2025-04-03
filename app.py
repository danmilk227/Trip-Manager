import tkinter as tk
from tkinter import ttk  # Добавьте этот импорт
from tkinter import messagebox, filedialog
from tkcalendar import Calendar
import customtkinter as ctk
from datetime import datetime, timedelta
import calendar
import os
import json
import logging
from PIL import Image, ImageTk
import sys
import shutil

# Настройка внешнего вида
ctk.set_appearance_mode("System")  # Системная тема
ctk.set_default_color_theme("blue")  # Цветовая тема

# Настройка логирования
logging.basicConfig(filename='Trip_Manager.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class BusinessTripTracker:
    def __init__(self, root):
        self.root = root
        self.selected_employee = ctk.StringVar(value="")
        self.root.title("Trip Manager")
        self.root.geometry("1200x800")
        
        # Иконка приложения
        try:
            self.root.iconbitmap(default='app.ico')
        except:
            pass

        # Загрузка данных из JSON-файлов
        self.employees = self.load_data('employees.json')
        self.trips = self.load_data('trips.json')
        self.documents = self.load_data('documents.json')

        # Переменные
        self.current_date = datetime.now()
        self.selected_trip = None
        self.selected_employee = ctk.StringVar()

        # Создание интерфейса
        self.create_widgets()

    def load_data(self, filename):
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as file:
                return json.load(file)
        return []

    def save_data(self, filename, data):
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def create_widgets(self):
        # Панель управления
        control_frame = ctk.CTkFrame(self.root, corner_radius=10)
        control_frame.pack(fill=tk.X, padx=10, pady=10, ipady=5)

        # Выбор сотрудника
        ctk.CTkLabel(control_frame, text="Сотрудник:").grid(row=0, column=0, padx=5, pady=5)
        self.employee_combo = ctk.CTkComboBox(control_frame, variable=self.selected_employee)
        self.employee_combo.grid(row=0, column=1, padx=5, pady=5)
        self.update_employee_combo()

        # Кнопка управления сотрудниками
        ctk.CTkButton(control_frame, text="Управление сотрудниками", 
                     command=self.manage_employees).grid(row=0, column=2, padx=5, pady=5)

        # Кнопки навигации по месяцам
        ctk.CTkButton(control_frame, text="◀", width=30, 
                     command=self.prev_month).grid(row=0, column=3, padx=5, pady=5)
        self.month_year_label = ctk.CTkLabel(control_frame, text="", font=('Arial', 14, 'bold'))
        self.month_year_label.grid(row=0, column=4, padx=5, pady=5)
        ctk.CTkButton(control_frame, text="▶", width=30, 
                     command=self.next_month).grid(row=0, column=5, padx=5, pady=5)

        # Кнопки управления
        ctk.CTkButton(control_frame, text="Добавить командировку", 
                     command=self.add_trip).grid(row=0, column=6, padx=5, pady=5)
        ctk.CTkButton(control_frame, text="Обновить", 
                     command=self.update_calendar).grid(row=0, column=7, padx=5, pady=5)

        # Календарь
        self.calendar_frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.calendar_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Детали командировки
        self.details_frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.details_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.update_month_year_label()
        self.create_calendar()

    def show_calendar_popup(self, entry_widget):
        """Показывает всплывающий календарь для выбора даты"""
        def set_date():
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, cal.get_date())
            top.destroy()

        top = ctk.CTkToplevel(self.root)
        top.title("Выберите дату")
        top.geometry("300x300")
        top.grab_set()

        cal = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd')
        cal.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        ctk.CTkButton(top, text="Выбрать", command=set_date).pack(pady=5)

    def manage_employees(self):
        """Окно управления сотрудниками"""
        manage_window = ctk.CTkToplevel(self.root)
        manage_window.title("Управление сотрудниками")
        manage_window.geometry("800x500")
        manage_window.grab_set()

        # Список сотрудников
        tree_frame = ctk.CTkFrame(manage_window)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Создаем Treeview с использованием ttk
        columns = ("id", "name", "position", "department")
        self.employee_tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="headings",
            style="Custom.Treeview",
            selectmode="browse"
        )

        # Настройка стиля для Treeview
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Custom.Treeview",
                      background="#2a2d2e",
                      foreground="white",
                      fieldbackground="#2a2d2e",
                      bordercolor="#343638",
                      borderwidth=0,
                      font=('Arial', 10))
        style.map('Custom.Treeview', background=[('selected', '#22559b' )])

        # Настройка колонок
        self.employee_tree.heading("id", text="ID", anchor=tk.CENTER)
        self.employee_tree.heading("name", text="ФИО", anchor=tk.W)
        self.employee_tree.heading("position", text="Должность", anchor=tk.W)
        self.employee_tree.heading("department", text="Отдел", anchor=tk.W)

        self.employee_tree.column("id", width=50, anchor=tk.CENTER)
        self.employee_tree.column("name", width=200, anchor=tk.W)
        self.employee_tree.column("position", width=150, anchor=tk.W)
        self.employee_tree.column("department", width=150, anchor=tk.W)

        # Добавление данных
        self.update_employee_tree()

        # Полоса прокрутки
        scrollbar = ctk.CTkScrollbar(
            tree_frame,
            orientation="vertical",
            command=self.employee_tree.yview
       )
        self.employee_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.employee_tree.pack(fill=tk.BOTH, expand=True)

        # Кнопки управления
        btn_frame = ctk.CTkFrame(manage_window)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        ctk.CTkButton(btn_frame, text="Добавить", 
                     command=self.add_employee).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(btn_frame, text="Редактировать", 
                     command=self.edit_employee).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(btn_frame, text="Удалить", 
                     command=self.delete_employee).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(btn_frame, text="Закрыть", 
                     command=manage_window.destroy).pack(side=tk.RIGHT, padx=5)
        
    def update_employee_tree(self):
        """Обновление списка сотрудников в Treeview"""
        # Очищаем текущие данные
        for item in self.employee_tree.get_children():
            self.employee_tree.delete(item)
    
        # Добавляем новые данные
        for emp in sorted(self.employees, key=lambda x: x['id']):
            self.employee_tree.insert("", "end", values=(
                emp["id"],
                emp["name"],
                emp.get("position", ""),
                emp.get("department", "")
            ))

    def add_employee(self):
        """Добавление нового сотрудника"""
        add_window = ctk.CTkToplevel(self.root)
        add_window.title("Добавить сотрудника")
        add_window.geometry("400x300")
        add_window.grab_set()

        # Поля формы
        ctk.CTkLabel(add_window, text="ФИО:").pack(pady=5)
        name_entry = ctk.CTkEntry(add_window)
        name_entry.pack(fill=tk.X, padx=10, pady=5)

        ctk.CTkLabel(add_window, text="Должность:").pack(pady=5)
        position_entry = ctk.CTkEntry(add_window)
        position_entry.pack(fill=tk.X, padx=10, pady=5)

        ctk.CTkLabel(add_window, text="Отдел:").pack(pady=5)
        department_entry = ctk.CTkEntry(add_window)
        department_entry.pack(fill=tk.X, padx=10, pady=5)

        def save_employee():
            name = name_entry.get()
            position = position_entry.get()
            department = department_entry.get()

            if not name:
                messagebox.showerror("Ошибка", "Введите ФИО сотрудника")
                return

            try:
                emp_id = max(emp["id"] for emp in self.employees) + 1 if self.employees else 1
                new_employee = {
                    "id": emp_id,
                    "name": name,
                    "position": position,
                    "department": department
                }
                self.employees.append(new_employee)
                self.save_data('employees.json', self.employees)

                messagebox.showinfo("Успех", "Сотрудник добавлен")
                logging.info(f"Employee added: {name}")
                add_window.destroy()
                self.update_employee_combo()
                self.update_employee_tree()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при сохранении: {str(e)}")
                logging.error(f"Error saving employee: {str(e)}")

        ctk.CTkButton(add_window, text="Сохранить", command=save_employee).pack(pady=10)

    def edit_employee(self):
        """Редактирование сотрудника"""
        selected = self.employee_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите сотрудника для редактирования")
            return

        item = self.employee_tree.item(selected[0])
        emp_id = item["values"][0]
        employee = next((emp for emp in self.employees if emp["id"] == emp_id), None)
        
        if not employee:
            messagebox.showerror("Ошибка", "Сотрудник не найден")
            return

        edit_window = ctk.CTkToplevel(self.root)
        edit_window.title("Редактировать сотрудника")
        edit_window.geometry("400x300")
        edit_window.grab_set()

        # Поля формы
        ctk.CTkLabel(edit_window, text="ФИО:").pack(pady=5)
        name_entry = ctk.CTkEntry(edit_window)
        name_entry.pack(fill=tk.X, padx=10, pady=5)
        name_entry.insert(0, employee["name"])

        ctk.CTkLabel(edit_window, text="Должность:").pack(pady=5)
        position_entry = ctk.CTkEntry(edit_window)
        position_entry.pack(fill=tk.X, padx=10, pady=5)
        position_entry.insert(0, employee.get("position", ""))

        ctk.CTkLabel(edit_window, text="Отдел:").pack(pady=5)
        department_entry = ctk.CTkEntry(edit_window)
        department_entry.pack(fill=tk.X, padx=10, pady=5)
        department_entry.insert(0, employee.get("department", ""))

        def update_employee():
            name = name_entry.get()
            position = position_entry.get()
            department = department_entry.get()

            if not name:
                messagebox.showerror("Ошибка", "Введите ФИО сотрудника")
                return

            try:
                employee.update({
                    "name": name,
                    "position": position,
                    "department": department
                })
                self.save_data('employees.json', self.employees)

                messagebox.showinfo("Успех", "Данные сотрудника обновлены")
                logging.info(f"Employee updated: {name}")
                edit_window.destroy()
                self.update_employee_combo()
                self.update_employee_tree()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при обновлении: {str(e)}")
                logging.error(f"Error updating employee: {str(e)}")

        ctk.CTkButton(edit_window, text="Обновить", command=update_employee).pack(pady=10)

    def delete_employee(self):
        """Удаление сотрудника"""
        selected = self.employee_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите сотрудника для удаления")
            return

        item = self.employee_tree.item(selected[0])
        emp_id = item["values"][0]
        emp_name = item["values"][1]

        # Проверка на наличие командировок у сотрудника
        has_trips = any(trip["employee_id"] == emp_id for trip in self.trips)
        
        if has_trips:
            messagebox.showerror("Ошибка", "Нельзя удалить сотрудника с активными командировками")
            return

        if messagebox.askyesno("Подтверждение", f"Удалить сотрудника {emp_name}?"):
            try:
                self.employees = [emp for emp in self.employees if emp["id"] != emp_id]
                self.save_data('employees.json', self.employees)

                messagebox.showinfo("Успех", "Сотрудник удален")
                logging.info(f"Employee deleted: {emp_name}")
                self.update_employee_combo()
                self.update_employee_tree()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при удалении: {str(e)}")
                logging.error(f"Error deleting employee: {str(e)}")

    def update_employee_combo(self):
        employees = [f"{emp['name']}" for emp in self.employees]
        self.employee_combo.configure(values=employees)

        if employees:
            self.selected_employee.set(employees[0])  # Автоматически выбираем первого сотрудника
        else:
            self.selected_employee.set("")  # Очищаем выбор, если список пуст
            messagebox.showwarning(
                "Внимание",
                "Список сотрудников пуст.\nПожалуйста, добавьте сотрудников через меню управления."
            )

    def update_month_year_label(self):
        self.month_year_label.configure(text=f"{self.current_date.strftime('%B %Y')}")

    def prev_month(self):
        self.current_date = self.current_date.replace(day=1) - timedelta(days=1)
        self.update_month_year_label()
        self.create_calendar()

    def next_month(self):
        self.current_date = (self.current_date.replace(day=1) + timedelta(days=31)).replace(day=1)
        self.update_month_year_label()
        self.create_calendar()

    def create_calendar(self):
        # Очистка предыдущего календаря
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        # Заголовки дней недели
        days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
        for i, day in enumerate(days):
            ctk.CTkLabel(self.calendar_frame, text=day, font=('Arial', 12, 'bold'), 
                         width=100, height=30, corner_radius=5).grid(row=0, column=i, padx=2, pady=2)

        # Получаем календарь на текущий месяц
        cal = calendar.monthcalendar(self.current_date.year, self.current_date.month)

        # Отображаем дни
        for week_num, week in enumerate(cal, start=1):
            for day_num, day in enumerate(week):
                if day == 0:
                    continue

                day_frame = ctk.CTkFrame(self.calendar_frame, width=100, height=80, 
                                       corner_radius=5, border_width=1, fg_color=("#f9f9fa", "#2a2d2e"))
                day_frame.grid(row=week_num, column=day_num, sticky="nsew", padx=2, pady=2)
                day_frame.bind("<Button-1>", lambda e, d=day: self.show_day_details(d))

                # Номер дня
                day_label = ctk.CTkLabel(day_frame, text=str(day), font=('Arial', 10))
                day_label.pack(anchor="nw", padx=5, pady=2)

                # Получаем командировки на этот день
                trips = self.get_trips_for_day(day)
                for trip in trips:
                    # Находим имя сотрудника по ID
                    employee = next((emp for emp in self.employees if emp['id'] == trip['employee_id']), None)
                    employee_name = employee['name'] if employee else "Неизвестный"

                    trip_frame = ctk.CTkFrame(day_frame, height=20, corner_radius=3, 
                                            fg_color=("#3b8ed0", "#1f6aa5"))
                    trip_frame.pack(fill=tk.X, padx=2, pady=1)

                    # Отображаем имя сотрудника вместо места назначения
                    trip_label = ctk.CTkLabel(trip_frame, text=employee_name, 
                                            font=('Arial', 8), anchor="w")
                    trip_label.pack(side=tk.LEFT, padx=2)
                    trip_frame.bind("<Button-1>", lambda e, t=trip: self.show_trip_details(t))

        # Настройка пропорций столбцов
        for i in range(7):
            self.calendar_frame.grid_columnconfigure(i, weight=1)

        # Настройка пропорций строк
        for i in range(len(cal) + 1):
            self.calendar_frame.grid_rowconfigure(i, weight=1)

    def get_trips_for_day(self, day):
        date_str = f"{self.current_date.year}-{self.current_date.month:02d}-{day:02d}"

        if not self.selected_employee.get():
            return []

        emp_name = self.selected_employee.get()
        emp_id = next((emp['id'] for emp in self.employees if emp['name'] == emp_name), None)

        if emp_id is None:
            return []

        return [trip for trip in self.trips if trip['employee_id'] == emp_id and date_str >= trip['start_date'] and date_str <= trip['end_date']]
    
    def show_day_details(self, day):
        for widget in self.details_frame.winfo_children():
            widget.destroy()

        date_str = f"{self.current_date.year}-{self.current_date.month:02d}-{day:02d}"
        ctk.CTkLabel(self.details_frame, 
                    text=f"События на {day}.{self.current_date.month}.{self.current_date.year}",
                    font=('Arial', 14, 'bold')).pack(anchor="w", padx=10, pady=5)

        if not self.selected_employee.get():
            return

        emp_name = self.selected_employee.get()
        emp_id = next((emp['id'] for emp in self.employees if emp['name'] == emp_name), None)
        if emp_id is None:
            return

        trips = [trip for trip in self.trips if trip['employee_id'] == emp_id and date_str >= trip['start_date'] and date_str <= trip['end_date']]

        if not trips:
            ctk.CTkLabel(self.details_frame, text="Нет командировок в этот день").pack(pady=10)
            return

        for trip in trips:
            trip_frame = ctk.CTkFrame(self.details_frame, corner_radius=5)
            trip_frame.pack(fill=tk.X, pady=5, padx=10)

            ctk.CTkLabel(trip_frame, text=f"Комадировка в: {trip['destination']}", 
                         font=('Arial', 12, 'bold')).pack(anchor="w")
            ctk.CTkLabel(trip_frame, text=f"Цель: {trip['purpose']}").pack(anchor="w")
            ctk.CTkLabel(trip_frame, text=f"Даты: {trip['start_date']} - {trip['end_date']}").pack(anchor="w")

            # Кнопки для управления документами
            doc_frame = ctk.CTkFrame(trip_frame, fg_color="transparent")
            doc_frame.pack(fill=tk.X, pady=5)

            ctk.CTkButton(doc_frame, text="Добавить билет", width=100,
                         command=lambda t=trip['id']: self.add_document(t, "ticket")).pack(side=tk.LEFT, padx=2)
            ctk.CTkButton(doc_frame, text="Добавить ваучер", width=100,
                         command=lambda t=trip['id']: self.add_document(t, "voucher")).pack(side=tk.LEFT, padx=2)
            ctk.CTkButton(doc_frame, text="Добавить визу", width=100,
                         command=lambda t=trip['id']: self.add_document(t, "visa")).pack(side=tk.LEFT, padx=2)

            # Показать существующие документы
            self.show_trip_documents(trip['id'])

    def show_trip_details(self, trip):
        self.selected_trip = trip
        for widget in self.details_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.details_frame, 
                    text=f"Комадировка в: {trip['destination']}", 
                    font=('Arial', 14, 'bold')).pack(anchor="w", padx=10, pady=5)

        # Полная информация о командировке
        info_frame = ctk.CTkFrame(self.details_frame, fg_color="transparent")
        info_frame.pack(fill=tk.X, pady=5, padx=10)

        employee = next((emp for emp in self.employees if emp['id'] == trip['employee_id']), None)
        if employee:
            ctk.CTkLabel(info_frame, text=f"Сотрудник: {employee['name']}").grid(row=0, column=0, sticky="w")
            ctk.CTkLabel(info_frame, text=f"Должность: {employee['position']}").grid(row=1, column=0, sticky="w")
            ctk.CTkLabel(info_frame, text=f"Отдел: {employee['department']}").grid(row=2, column=0, sticky="w")
            ctk.CTkLabel(info_frame, text=f"Цель: {trip['purpose']}").grid(row=0, column=1, sticky="w", padx=20)
            ctk.CTkLabel(info_frame, text=f"Начало: {trip['start_date']}").grid(row=1, column=1, sticky="w", padx=20)
            ctk.CTkLabel(info_frame, text=f"Окончание: {trip['end_date']}").grid(row=2, column=1, sticky="w", padx=20)

        # Кнопки управления
        btn_frame = ctk.CTkFrame(self.details_frame, fg_color="transparent")
        btn_frame.pack(fill=tk.X, pady=5, padx=10)

        ctk.CTkButton(btn_frame, text="Редактировать", 
                     command=self.edit_trip).pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(btn_frame, text="Удалить", 
                     command=self.delete_trip).pack(side=tk.LEFT, padx=5)

        # Документы
        doc_frame = ctk.CTkFrame(self.details_frame, fg_color="transparent")
        doc_frame.pack(fill=tk.X, pady=5, padx=10)

        ctk.CTkButton(doc_frame, text="Добавить билет",
                     command=lambda: self.add_document(trip['id'], "ticket")).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(doc_frame, text="Добавить ваучер",
                     command=lambda: self.add_document(trip['id'], "voucher")).pack(side=tk.LEFT, padx=2)
        ctk.CTkButton(doc_frame, text="Добавить визу",
                     command=lambda: self.add_document(trip['id'], "visa")).pack(side=tk.LEFT, padx=2)

        # Показать существующие документы
        self.show_trip_documents(trip['id'])

    def show_trip_documents(self, trip_id):
        documents = [doc for doc in self.documents if doc['trip_id'] == trip_id]

        if not documents:
            return

        doc_list_frame = ctk.CTkFrame(self.details_frame)
        doc_list_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)

        ctk.CTkLabel(doc_list_frame, text="Прикрепленные документы:", 
                    font=('Arial', 12, 'bold')).pack(anchor="w", padx=5, pady=5)

        for doc in documents:
            doc_item_frame = ctk.CTkFrame(doc_list_frame, corner_radius=5)
            doc_item_frame.pack(fill=tk.X, pady=2, padx=5)

            ctk.CTkLabel(doc_item_frame, 
                        text=f"{doc['document_type']}: {os.path.basename(doc['file_path'])}").pack(side=tk.LEFT, padx=5)
            
            btn_frame = ctk.CTkFrame(doc_item_frame, fg_color="transparent")
            btn_frame.pack(side=tk.RIGHT)
            
            ctk.CTkButton(btn_frame, text="Просмотр", width=80,
                         command=lambda p=doc['file_path']: self.view_document(p)).pack(side=tk.LEFT, padx=2)
            ctk.CTkButton(btn_frame, text="Удалить", width=80,
                         command=lambda d=doc['id']: self.delete_document(d)).pack(side=tk.LEFT, padx=2)
    def add_trip(self):
        """Добавление новой командировки"""
        # Проверка выбора сотрудника
        if not self.selected_employee.get():
            messagebox.showerror(
                "Ошибка",
                "Не выбран сотрудник!\nПожалуйста, выберите сотрудника из списка."
            )
            logging.error("Attempted to add trip without selecting an employee.")
            return

        emp_name = self.selected_employee.get()
        emp_id = next((emp['id'] for emp in self.employees if emp['name'] == emp_name), None)
        
        if emp_id is None:
            messagebox.showerror(
                "Ошибка",
                f"Сотрудник '{emp_name}' не найден.\nВозможно, он был удален."
            )
            logging.error(f"Invalid employee selection: {emp_name}")
            self.update_employee_combo()  # Обновляем список сотрудников
            return

        add_window = ctk.CTkToplevel(self.root)
        add_window.title("Добавить командировку")
        add_window.geometry("500x400")
        add_window.grab_set()

        # Поля формы
        ctk.CTkLabel(add_window, text=f"Сотрудник: {emp_name}", 
                    font=('Arial', 12, 'bold')).pack(pady=5)

        ctk.CTkLabel(add_window, text="Место назначения:").pack(pady=5)
        destination_entry = ctk.CTkEntry(add_window)
        destination_entry.pack(fill=tk.X, padx=10, pady=5)

        ctk.CTkLabel(add_window, text="Цель командировки:").pack(pady=5)
        purpose_entry = ctk.CTkEntry(add_window)
        purpose_entry.pack(fill=tk.X, padx=10, pady=5)

        # Дата начала
        start_frame = ctk.CTkFrame(add_window, fg_color="transparent")
        start_frame.pack(fill=tk.X, padx=10, pady=5)
        ctk.CTkLabel(start_frame, text="Дата начала:").pack(side=tk.LEFT)
        start_entry = ctk.CTkEntry(start_frame)
        start_entry.pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(start_frame, text="📅", width=30,
                     command=lambda: self.show_calendar_popup(start_entry)).pack(side=tk.LEFT)

        # Дата окончания
        end_frame = ctk.CTkFrame(add_window, fg_color="transparent")
        end_frame.pack(fill=tk.X, padx=10, pady=5)
        ctk.CTkLabel(end_frame, text="Дата окончания:").pack(side=tk.LEFT)
        end_entry = ctk.CTkEntry(end_frame)
        end_entry.pack(side=tk.LEFT, padx=5)
        ctk.CTkButton(end_frame, text="📅", width=30,
                     command=lambda: self.show_calendar_popup(end_entry)).pack(side=tk.LEFT)

        def save_trip():
            # Проверка заполнения полей
            if not all([destination_entry.get(), start_entry.get(), end_entry.get()]):
                messagebox.showerror(
                    "Ошибка",
                    "Заполните все обязательные поля!\n(Место назначения и даты)"
                )
                return

            # Проверка формата дат
            try:
                start_date = datetime.strptime(start_entry.get(), '%Y-%m-%d')
                end_date = datetime.strptime(end_entry.get(), '%Y-%m-%d')
                
                if end_date < start_date:
                    messagebox.showerror(
                        "Ошибка",
                        "Дата окончания не может быть раньше даты начала!"
                    )
                    return
                    
            except ValueError:
                messagebox.showerror(
                    "Ошибка",
                    "Неверный формат даты!\nИспользуйте ГГГГ-ММ-ДД (например, 2025-04-10)"
                )
                return

            # Сохранение командировки
            try:
                trip_id = max(trip['id'] for trip in self.trips) + 1 if self.trips else 1
                new_trip = {
                    "id": trip_id,
                    "employee_id": emp_id,
                    "destination": destination_entry.get(),
                    "purpose": purpose_entry.get(),
                    "start_date": start_entry.get(),
                    "end_date": end_entry.get()
                }
                self.trips.append(new_trip)
                self.save_data('trips.json', self.trips)

                messagebox.showinfo(
                    "Успех",
                    f"Командировка для {emp_name} успешно добавлена!"
                )
                logging.info(f"Trip added for employee ID {emp_id} to {destination_entry.get()}.")
                add_window.destroy()
                self.update_calendar()
                
            except Exception as e:
                messagebox.showerror(
                    "Ошибка",
                    f"Ошибка при сохранении:\n{str(e)}"
                )
                logging.error(f"Error saving trip: {str(e)}")

        ctk.CTkButton(add_window, text="Сохранить", command=save_trip).pack(pady=10)

    def edit_trip(self):
        if not self.selected_trip:
            return

        edit_window = ctk.CTkToplevel(self.root)
        edit_window.title("Редактировать командировку")
        edit_window.geometry("500x400")
        edit_window.grab_set()

        # Поля формы
        ctk.CTkLabel(edit_window, text="Место назначения:").pack(pady=5)
        destination_entry = ctk.CTkEntry(edit_window)
        destination_entry.pack(fill=tk.X, padx=10, pady=5)
        destination_entry.insert(0, self.selected_trip['destination'])

        ctk.CTkLabel(edit_window, text="Цель командировки:").pack(pady=5)
        purpose_entry = ctk.CTkEntry(edit_window)
        purpose_entry.pack(fill=tk.X, padx=10, pady=5)
        purpose_entry.insert(0, self.selected_trip['purpose'])

        # Дата начала
        start_frame = ctk.CTkFrame(edit_window, fg_color="transparent")
        start_frame.pack(fill=tk.X, padx=10, pady=5)
        ctk.CTkLabel(start_frame, text="Дата начала:").pack(side=tk.LEFT)
        start_entry = ctk.CTkEntry(start_frame)
        start_entry.pack(side=tk.LEFT, padx=5)
        start_entry.insert(0, self.selected_trip['start_date'])
        ctk.CTkButton(start_frame, text="📅", width=30, 
                     command=lambda: self.show_calendar_popup(start_entry)).pack(side=tk.LEFT)

        # Дата окончания
        end_frame = ctk.CTkFrame(edit_window, fg_color="transparent")
        end_frame.pack(fill=tk.X, padx=10, pady=5)
        ctk.CTkLabel(end_frame, text="Дата окончания:").pack(side=tk.LEFT)
        end_entry = ctk.CTkEntry(end_frame)
        end_entry.pack(side=tk.LEFT, padx=5)
        end_entry.insert(0, self.selected_trip['end_date'])
        ctk.CTkButton(end_frame, text="📅", width=30, 
                     command=lambda: self.show_calendar_popup(end_entry)).pack(side=tk.LEFT)

        def update_trip():
            destination = destination_entry.get()
            purpose = purpose_entry.get()
            start_date = start_entry.get()
            end_date = end_entry.get()

            if not all([destination, start_date, end_date]):
                messagebox.showerror("Ошибка", "Заполните обязательные поля")
                logging.error("Attempted to update trip with missing fields.")
                return

            try:
                # Проверка формата даты
                datetime.strptime(start_date, '%Y-%m-%d')
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД.")
                logging.error("Incorrect date format provided.")
                return

            try:
                self.selected_trip.update({
                    "destination": destination,
                    "purpose": purpose,
                    "start_date": start_date,
                    "end_date": end_date
                })
                self.save_data('trips.json', self.trips)

                messagebox.showinfo("Успех", "Командировка обновлена")
                logging.info(f"Trip updated for ID {self.selected_trip['id']} to {destination}.")
                edit_window.destroy()
                self.update_calendar()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при обновлении: {str(e)}")
                logging.error(f"Error updating trip: {str(e)}")

        ctk.CTkButton(edit_window, text="Обновить", command=update_trip).pack(pady=10)

    def delete_trip(self):
        if not self.selected_trip:
            return

        if messagebox.askyesno("Подтверждение", "Удалить эту командировку и все связанные документы?"):
            try:
                # Удаляем документы
                self.documents = [doc for doc in self.documents if doc['trip_id'] != self.selected_trip['id']]
                self.save_data('documents.json', self.documents)

                # Удаляем командировку
                self.trips.remove(self.selected_trip)
                self.save_data('trips.json', self.trips)

                messagebox.showinfo("Успех", "Командировка удалена")
                logging.info(f"Trip deleted with ID {self.selected_trip['id']}.")
                self.selected_trip = None
                self.update_calendar()

                # Очищаем панель деталей
                for widget in self.details_frame.winfo_children():
                    widget.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при удалении: {str(e)}")
                logging.error(f"Error deleting trip: {str(e)}")

    def add_document(self, trip_id, doc_type):
        file_path = filedialog.askopenfilename(
            title=f"Выберите файл {doc_type}",
            filetypes=[("Все файлы", "*.*"), ("PDF", "*.pdf"), ("Изображения", "*.jpg *.png")]
        )

        if not file_path:
            return

        try:
            # Создаем папку для документов, если ее нет
            os.makedirs("trip_documents", exist_ok=True)

            # Копируем файл в папку с документами
            filename = os.path.basename(file_path)
            dest_path = os.path.join("trip_documents", f"{trip_id}_{doc_type}_{filename}")

            shutil.copy(file_path, dest_path)

            doc_id = len(self.documents) + 1
            new_document = {
                "id": doc_id,
                "trip_id": trip_id,
                "document_type": doc_type,
                "file_path": dest_path
            }
            self.documents.append(new_document)
            self.save_data('documents.json', self.documents)

            messagebox.showinfo("Успех", "Документ добавлен")
            logging.info(f"Document added for trip ID {trip_id}: {doc_type}.")
            self.show_trip_documents(trip_id)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при добавлении документа: {str(e)}")
            logging.error(f"Error adding document: {str(e)}")

    def delete_document(self, doc_id):
        if messagebox.askyesno("Подтверждение", "Удалить этот документ?"):
            try:
                self.documents = [doc for doc in self.documents if doc['id'] != doc_id]
                self.save_data('documents.json', self.documents)
                messagebox.showinfo("Успех", "Документ удален")
                logging.info(f"Document deleted with ID {doc_id}.")
                self.update_calendar()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при удалении: {str(e)}")
                logging.error(f"Error deleting document: {str(e)}")

    def view_document(self, file_path):
        if not os.path.exists(file_path):
            messagebox.showerror("Ошибка", "Файл не найден")
            logging.error(f"Attempted to view non-existent file: {file_path}")
            return

        # Для примера просто откроем файл стандартным способом
        import subprocess
        try:
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            elif os.name == 'posix':  # macOS, Linux
                subprocess.run(['open', file_path] if sys.platform == 'darwin' else ['xdg-open', file_path])
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть файл: {str(e)}")
            logging.error(f"Error opening file: {str(e)}")

    def update_calendar(self):
        self.create_calendar()

if __name__ == "__main__":
    root = ctk.CTk()
    app = BusinessTripTracker(root)
    root.mainloop()