"""
Окно настроек
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Optional

from data_info import DataInfo


class SettingsWindow:
    """Окно настроек приложения"""
    
    def __init__(self, parent: tk.Tk, data_info: DataInfo):
        """Инициализация окна настроек"""
        self.parent = parent
        self.data_info = data_info
        
        self.window = tk.Toplevel(parent)
        self.window.title("Настройки")
        self.window.geometry("600x700")
        self.window.transient(parent)
        self.window.grab_set()
        
        self._create_ui()
        self._load_settings()
    
    def _create_ui(self):
        """Создание элементов интерфейса"""
        # Основной фрейм с прокруткой
        canvas = tk.Canvas(self.window)
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Блок для шунтов КЗ
        shunt_frame = ttk.LabelFrame(scrollable_frame, text="Параметры для расчетов шунтов КЗ", padding="10")
        shunt_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(shunt_frame, text="Исходные данные для расчетов шунтов КЗ:").pack(anchor=tk.W)
        shunt_file_frame = ttk.Frame(shunt_frame)
        shunt_file_frame.pack(fill=tk.X, pady=5)
        
        self.shunt_file_label = ttk.Label(shunt_file_frame, text="", foreground="gray")
        self.shunt_file_label.pack(side=tk.LEFT, padx=5)
        ttk.Button(shunt_file_frame, text="Выбрать файл", 
                   command=self._select_shunt_file).pack(side=tk.LEFT)
        
        self.use_sel_nodes_var = tk.BooleanVar()
        ttk.Checkbutton(shunt_frame, text="Использовать отмеченные узлы",
                       variable=self.use_sel_nodes_var).pack(anchor=tk.W, pady=2)
        
        self.use_type_val_u_var = tk.BooleanVar()
        ttk.Checkbutton(shunt_frame, text="Расчет по типовым значениям Uост",
                       variable=self.use_type_val_u_var).pack(anchor=tk.W, pady=2)
        
        self.calc_one_phase_var = tk.BooleanVar()
        ttk.Checkbutton(shunt_frame, text="Расчет для однофазного КЗ",
                       variable=self.calc_one_phase_var).pack(anchor=tk.W, pady=2)
        
        self.calc_two_phase_var = tk.BooleanVar()
        ttk.Checkbutton(shunt_frame, text="Расчет для двухфазного КЗ",
                       variable=self.calc_two_phase_var).pack(anchor=tk.W, pady=2)
        
        # Блок для предельного времени КЗ
        time_frame = ttk.LabelFrame(scrollable_frame, text="Параметры для расчетов предельного времени отключения КЗ", padding="10")
        time_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(time_frame, text="Точность расчета предельного времени отключения КЗ (с):").pack(anchor=tk.W)
        self.crt_time_precision_var = tk.DoubleVar()
        ttk.Spinbox(time_frame, from_=0.001, to=1.0, increment=0.001, 
                   textvariable=self.crt_time_precision_var, width=15).pack(anchor=tk.W, pady=2)
        
        ttk.Label(time_frame, text="Максимальное время отключения КЗ (с):").pack(anchor=tk.W)
        self.crt_time_max_var = tk.DoubleVar()
        ttk.Spinbox(time_frame, from_=0.1, to=10.0, increment=0.1,
                   textvariable=self.crt_time_max_var, width=15).pack(anchor=tk.W, pady=2)
        
        # Блок для расчета ДУ
        dyn_frame = ttk.LabelFrame(scrollable_frame, text="Параметры расчета динамической устойчивости", padding="10")
        dyn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.dyn_no_pa_var = tk.BooleanVar()
        ttk.Checkbutton(dyn_frame, text="Расчет устойчивости (МДП) без ПА",
                       variable=self.dyn_no_pa_var).pack(anchor=tk.W, pady=2)
        
        self.dyn_with_pa_var = tk.BooleanVar()
        ttk.Checkbutton(dyn_frame, text="Расчет устойчивости (МДП) с ПА",
                       variable=self.dyn_with_pa_var).pack(anchor=tk.W, pady=2)
        
        self.save_grf_var = tk.BooleanVar()
        ttk.Checkbutton(dyn_frame, text="Построение графиков",
                       variable=self.save_grf_var).pack(anchor=tk.W, pady=2)
        
        ttk.Label(dyn_frame, text="№ сечения:").pack(anchor=tk.W)
        self.selected_sch_var = tk.IntVar()
        ttk.Spinbox(dyn_frame, from_=0, to=100, textvariable=self.selected_sch_var,
                   width=15).pack(anchor=tk.W, pady=2)
        
        # Кнопки
        buttons_frame = ttk.Frame(scrollable_frame)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(buttons_frame, text="Сохранить", command=self._save_settings).pack(side=tk.RIGHT, padx=5)
        ttk.Button(buttons_frame, text="Отмена", command=self.window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def _load_settings(self):
        """Загрузка текущих настроек"""
        self.use_sel_nodes_var.set(self.data_info.use_sel_nodes)
        self.use_type_val_u_var.set(self.data_info.use_type_val_u)
        self.calc_one_phase_var.set(self.data_info.calc_one_phase)
        self.calc_two_phase_var.set(self.data_info.calc_two_phase)
        self.crt_time_precision_var.set(self.data_info.crt_time_precision)
        self.crt_time_max_var.set(self.data_info.crt_time_max)
        self.dyn_no_pa_var.set(self.data_info.dyn_no_pa)
        self.dyn_with_pa_var.set(self.data_info.dyn_with_pa)
        self.save_grf_var.set(self.data_info.save_grf)
        self.selected_sch_var.set(self.data_info.selected_sch)
        
        if self.data_info.shunt_kz.name:
            self.shunt_file_label.config(text=Path(self.data_info.shunt_kz.name).name, foreground="black")
        else:
            self.shunt_file_label.config(text="Не загружен", foreground="gray")
    
    def _select_shunt_file(self):
        """Выбор файла для шунтов КЗ"""
        file_path = filedialog.askopenfilename(
            title="Выбор файла задания для расчета шунтов КЗ",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.data_info.shunt_kz.name = file_path
                self.shunt_file_label.config(text=Path(file_path).name, foreground="black")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при загрузке файла:\n\n{str(e)}")
    
    def _save_settings(self):
        """Сохранение настроек"""
        self.data_info.use_sel_nodes = self.use_sel_nodes_var.get()
        self.data_info.use_type_val_u = self.use_type_val_u_var.get()
        self.data_info.calc_one_phase = self.calc_one_phase_var.get()
        self.data_info.calc_two_phase = self.calc_two_phase_var.get()
        self.data_info.crt_time_precision = self.crt_time_precision_var.get()
        self.data_info.crt_time_max = self.crt_time_max_var.get()
        self.data_info.dyn_no_pa = self.dyn_no_pa_var.get()
        self.data_info.dyn_with_pa = self.dyn_with_pa_var.get()
        self.data_info.save_grf = self.save_grf_var.get()
        self.data_info.selected_sch = self.selected_sch_var.get()
        
        self.window.destroy()
    
    def show(self):
        """Показать окно"""
        self.window.wait_window()

