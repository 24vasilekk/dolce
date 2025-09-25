#!/usr/bin/env python3
"""
BestSecret Parser GUI - Графический интерфейс для управления парсером
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import json
import sys
import os
from bestsecret_parser import BestSecretParser
import re

class ParserGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("BestSecret Parser")
        self.root.geometry("800x600")
        
        # Парсер
        self.parser = None
        self.parsing_thread = None
        
        # Создаем интерфейс
        self.create_widgets()
        
        # Загружаем настройки
        self.load_credentials()
    
    def create_widgets(self):
        """Создание элементов интерфейса"""
        
        # Рамка для авторизации
        auth_frame = ttk.LabelFrame(self.root, text="Авторизация", padding=10)
        auth_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(auth_frame, text="Email:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.email_var = tk.StringVar()
        self.email_entry = ttk.Entry(auth_frame, textvariable=self.email_var, width=30)
        self.email_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        
        ttk.Label(auth_frame, text="Пароль:").grid(row=0, column=2, sticky="w", padx=(0, 5))
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(auth_frame, textvariable=self.password_var, show="*", width=30)
        self.password_entry.grid(row=0, column=3, sticky="ew")
        
        auth_frame.columnconfigure(1, weight=1)
        auth_frame.columnconfigure(3, weight=1)
        
        # Рамка для настроек парсинга
        settings_frame = ttk.LabelFrame(self.root, text="Настройки парсинга", padding=10)
        settings_frame.pack(fill="x", padx=10, pady=5)
        
        # Категория
        ttk.Label(settings_frame, text="Категория:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.category_var = tk.StringVar(value="Женское")
        category_combo = ttk.Combobox(settings_frame, textvariable=self.category_var, 
                                    values=["Женское", "Мужское", "Детское"], state="readonly")
        category_combo.grid(row=0, column=1, sticky="ew", padx=(0, 10))
        
        # Подкатегория
        ttk.Label(settings_frame, text="Подкатегория:").grid(row=0, column=2, sticky="w", padx=(0, 5))
        self.subcategory_var = tk.StringVar()
        subcategory_combo = ttk.Combobox(settings_frame, textvariable=self.subcategory_var,
                                       values=["", "WOMEN_LUXURY", "WOMEN_SHOES", "WOMEN_ACCESSORIES", "WOMEN_DESIGNER"],
                                       state="readonly")
        subcategory_combo.grid(row=0, column=3, sticky="ew")
        
        # Максимум товаров
        ttk.Label(settings_frame, text="Макс. товаров:").grid(row=1, column=0, sticky="w", padx=(0, 5), pady=(5, 0))
        self.max_products_var = tk.StringVar(value="10")
        max_products_entry = ttk.Entry(settings_frame, textvariable=self.max_products_var, width=10)
        max_products_entry.grid(row=1, column=1, sticky="w", pady=(5, 0))
        
        settings_frame.columnconfigure(1, weight=1)
        settings_frame.columnconfigure(3, weight=1)
        
        # Кнопки управления
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        self.login_btn = ttk.Button(control_frame, text="Войти", command=self.login_clicked)
        self.login_btn.pack(side="left", padx=(0, 5))
        
        self.parse_btn = ttk.Button(control_frame, text="Начать парсинг", command=self.parse_clicked, state="disabled")
        self.parse_btn.pack(side="left", padx=(0, 5))
        
        self.stop_btn = ttk.Button(control_frame, text="Остановить", command=self.stop_clicked, state="disabled")
        self.stop_btn.pack(side="left", padx=(0, 5))
        
        self.view_data_btn = ttk.Button(control_frame, text="Просмотреть данные", command=self.view_data_clicked)
        self.view_data_btn.pack(side="right")
        
        # Прогресс бар
        self.progress = ttk.Progressbar(self.root, mode="indeterminate")
        self.progress.pack(fill="x", padx=10, pady=5)
        
        # Лог
        log_frame = ttk.LabelFrame(self.root, text="Лог выполнения", padding=5)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, state="disabled")
        self.log_text.pack(fill="both", expand=True)
        
        # Статус бар
        self.status_var = tk.StringVar(value="Готов")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken")
        status_bar.pack(fill="x", side="bottom")
    
    def load_credentials(self):
        """Загрузка данных авторизации из .env"""
        try:
            if os.path.exists('.env'):
                with open('.env', 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    email_match = re.search(r'BESTSECRET_EMAIL=(.+)', content)
                    password_match = re.search(r'BESTSECRET_PASSWORD=(.+)', content)
                    
                    if email_match:
                        self.email_var.set(email_match.group(1))
                    if password_match:
                        self.password_var.set(password_match.group(1))
        except Exception as e:
            self.log_message(f"❌ Не удалось загрузить данные из .env: {e}")
    
    def log_message(self, message):
        """Добавление сообщения в лог"""
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.config(state="disabled")
        self.log_text.see(tk.END)
        self.root.update()
    
    def login_clicked(self):
        """Обработка клика по кнопке входа"""
        if not self.email_var.get() or not self.password_var.get():
            messagebox.showerror("Ошибка", "Введите email и пароль")
            return
        
        def login_thread():
            try:
                self.log_message("🔄 Инициализация браузера...")
                self.parser = BestSecretParser(self.email_var.get(), self.password_var.get())
                
                if not self.parser.initialize_driver():
                    self.log_message("❌ Не удалось запустить браузер")
                    return
                
                self.log_message("🔑 Выполняется авторизация...")
                if self.parser.login():
                    self.log_message("✅ Авторизация успешна!")
                    self.status_var.set("Авторизован")
                    
                    # Активируем кнопку парсинга
                    self.parse_btn.config(state="normal")
                    self.login_btn.config(text="Перезайти")
                else:
                    self.log_message("❌ Ошибка авторизации")
                    self.status_var.set("Ошибка авторизации")
                    
            except Exception as e:
                self.log_message(f"❌ Ошибка: {e}")
                self.status_var.set("Ошибка")
            finally:
                self.progress.stop()
        
        self.progress.start()
        threading.Thread(target=login_thread, daemon=True).start()
    
    def parse_clicked(self):
        """Обработка клика по кнопке парсинга"""
        if not self.parser or not self.parser.is_logged_in:
            messagebox.showerror("Ошибка", "Сначала выполните авторизацию")
            return
        
        try:
            max_products = int(self.max_products_var.get())
            if max_products <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное количество товаров")
            return
        
        def parse_thread():
            try:
                self.parse_btn.config(state="disabled")
                self.stop_btn.config(state="normal")
                self.status_var.set("Выполняется парсинг...")
                
                category = self.category_var.get()
                subcategory = self.subcategory_var.get() if self.subcategory_var.get() else None
                
                self.log_message(f"🎯 Начинаем парсинг: {category}" + (f" → {subcategory}" if subcategory else ""))
                
                products = self.parser.parse_category(category, subcategory, max_products)
                
                self.log_message(f"✅ Парсинг завершен! Найдено товаров: {len(products)}")
                
                # Статистика
                if products:
                    with_prices = sum(1 for p in products if p.current_price)
                    with_sizes = sum(1 for p in products if p.available_sizes)
                    
                    self.log_message(f"📊 Статистика:")
                    self.log_message(f"   С ценами: {with_prices}/{len(products)} ({with_prices/len(products)*100:.1f}%)")
                    self.log_message(f"   С размерами: {with_sizes}/{len(products)} ({with_sizes/len(products)*100:.1f}%)")
                
                self.status_var.set("Парсинг завершен")
                
            except Exception as e:
                self.log_message(f"❌ Ошибка парсинга: {e}")
                self.status_var.set("Ошибка парсинга")
            finally:
                self.parse_btn.config(state="normal")
                self.stop_btn.config(state="disabled")
                self.progress.stop()
        
        self.progress.start()
        self.parsing_thread = threading.Thread(target=parse_thread, daemon=True)
        self.parsing_thread.start()
    
    def stop_clicked(self):
        """Остановка парсинга"""
        self.log_message("⏹️ Остановка парсинга...")
        if self.parser:
            self.parser.cleanup()
        self.status_var.set("Остановлено")
        self.parse_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.progress.stop()
    
    def view_data_clicked(self):
        """Просмотр сохраненных данных"""
        try:
            if os.path.exists("products_database.json"):
                with open("products_database.json", 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Создаем окно просмотра
                view_window = tk.Toplevel(self.root)
                view_window.title("Сохраненные товары")
                view_window.geometry("900x600")
                
                # Таблица товаров
                columns = ("name", "brand", "price", "sizes", "category")
                tree = ttk.Treeview(view_window, columns=columns, show="headings", height=20)
                
                tree.heading("name", text="Название")
                tree.heading("brand", text="Бренд")
                tree.heading("price", text="Цена")
                tree.heading("sizes", text="Размеры")
                tree.heading("category", text="Категория")
                
                tree.column("name", width=250)
                tree.column("brand", width=100)
                tree.column("price", width=100)
                tree.column("sizes", width=150)
                tree.column("category", width=100)
                
                # Заполняем данными
                for item in data:
                    price = f"{item.get('current_price', 0)}€" if item.get('current_price') else "N/A"
                    sizes = ", ".join(item.get('available_sizes', []))[:20] + ("..." if len(", ".join(item.get('available_sizes', []))) > 20 else "")
                    
                    tree.insert("", "end", values=(
                        item.get('name', 'N/A')[:30],
                        item.get('brand', 'N/A'),
                        price,
                        sizes,
                        item.get('category', 'N/A')
                    ))
                
                tree.pack(fill="both", expand=True, padx=10, pady=10)
                
                # Скроллбар
                scrollbar = ttk.Scrollbar(view_window, orient="vertical", command=tree.yview)
                tree.configure(yscrollcommand=scrollbar.set)
                scrollbar.pack(side="right", fill="y")
                
                # Информация
                info_label = ttk.Label(view_window, text=f"Всего товаров: {len(data)}")
                info_label.pack(pady=5)
                
            else:
                messagebox.showinfo("Информация", "Файл с данными не найден. Выполните парсинг.")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
    
    def on_closing(self):
        """Обработка закрытия приложения"""
        if self.parser:
            self.parser.cleanup()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = ParserGUI(root)
    
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()