"""
Главное окно приложения
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Optional
import threading

from data_info import DataInfo
from utils.license import check_license
from utils.exceptions import UserLicenseException, InitialDataException


class MainWindow:
    """Главное окно приложения"""
    
    def __init__(self):
        """Инициализация главного окна"""
        self.root = tk.Tk()
        self.root.title("DynStabSpace - Расчет динамической устойчивости")
        self.root.geometry("800x700")
        
        # Проверка лицензии
        try:
            if not check_license():
                messagebox.showerror("Ошибка лицензии", "Некорректный файл лицензии")
                self.root.destroy()
                return
        except UserLicenseException as e:
            messagebox.showerror("Ошибка лицензии", str(e))
            self.root.destroy()
            return
        
        # Инициализация данных
        self.data_info = DataInfo()
        
        # Создание интерфейса
        self._create_ui()
        
        # Обновление интерфейса
        self._update_ui()
    
    def _create_ui(self):
        """Создание элементов интерфейса"""
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Расчетные режимы
        ttk.Label(main_frame, text="Расчетные режимы:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.rgms_listbox = tk.Listbox(main_frame, height=5, selectmode=tk.SINGLE)
        self.rgms_listbox.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.rgms_listbox.bind('<Double-Button-1>', lambda e: self._deselect_rgms())
        
        # Аварийные процессы
        ttk.Label(main_frame, text="Аварийные процессы:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.scns_listbox = tk.Listbox(main_frame, height=5, selectmode=tk.SINGLE)
        self.scns_listbox.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        self.scns_listbox.bind('<Double-Button-1>', lambda e: self._deselect_scns())
        
        # Файлы
        files_frame = ttk.LabelFrame(main_frame, text="Исходные данные", padding="5")
        files_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Ремонтные схемы
        ttk.Label(files_frame, text="Ремонтные схемы:").grid(row=0, column=0, sticky=tk.W)
        self.rems_label = ttk.Label(files_frame, text="", foreground="gray")
        self.rems_label.grid(row=0, column=1, sticky=tk.W, padx=5)
        self.rems_label.bind('<Double-Button-1>', lambda e: self._clear_rems())
        
        # Автоматика
        ttk.Label(files_frame, text="Автоматика:").grid(row=1, column=0, sticky=tk.W)
        self.lapnu_label = ttk.Label(files_frame, text="", foreground="gray")
        self.lapnu_label.grid(row=1, column=1, sticky=tk.W, padx=5)
        self.lapnu_label.bind('<Double-Button-1>', lambda e: self._clear_lapnu())
        
        # Траектория
        ttk.Label(files_frame, text="Траектория:").grid(row=2, column=0, sticky=tk.W)
        self.vir_label = ttk.Label(files_frame, text="", foreground="gray")
        self.vir_label.grid(row=2, column=1, sticky=tk.W, padx=5)
        self.vir_label.bind('<Double-Button-1>', lambda e: self._clear_vir())
        
        # Сечения
        ttk.Label(files_frame, text="Сечения:").grid(row=3, column=0, sticky=tk.W)
        self.sechen_label = ttk.Label(files_frame, text="", foreground="gray")
        self.sechen_label.grid(row=3, column=1, sticky=tk.W, padx=5)
        self.sechen_label.bind('<Double-Button-1>', lambda e: self._clear_sechen())
        
        # Графический вывод
        ttk.Label(files_frame, text="Графический вывод:").grid(row=4, column=0, sticky=tk.W)
        self.grf_label = ttk.Label(files_frame, text="", foreground="gray")
        self.grf_label.grid(row=4, column=1, sticky=tk.W, padx=5)
        self.grf_label.bind('<Double-Button-1>', lambda e: self._clear_grf())
        
        # Кнопки управления
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(buttons_frame, text="Добавить", command=self._add_files).grid(row=0, column=0, padx=5)
        ttk.Button(buttons_frame, text="Удалить", command=self._delete_files).grid(row=0, column=1, padx=5)
        ttk.Button(buttons_frame, text="Настройки", command=self._open_settings).grid(row=0, column=2, padx=5)
        
        # Кнопки расчетов
        calc_frame = ttk.LabelFrame(main_frame, text="Расчеты", padding="5")
        calc_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(calc_frame, text="Определение шунта КЗ", 
                   command=self._calc_shunt_kz).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W+tk.E)
        ttk.Button(calc_frame, text="Определение предельного времени КЗ",
                   command=self._calc_max_kz_time).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        ttk.Button(calc_frame, text="Расчет ДУ",
                   command=self._calc_dyn_stability).grid(row=1, column=0, padx=5, pady=5, sticky=tk.W+tk.E)
        ttk.Button(calc_frame, text="Определение МДП ДУ",
                   command=self._calc_mdp_stability).grid(row=1, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        ttk.Button(calc_frame, text="Определение остаточного напряжения при КЗ",
                   command=self._calc_uost_stability).grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W+tk.E)
        
        # Прогресс
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.progress_label = ttk.Label(progress_frame, text="")
        self.progress_label.grid(row=0, column=0, sticky=tk.W)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        progress_frame.columnconfigure(0, weight=1)
    
    def _update_ui(self):
        """Обновление интерфейса"""
        # Обновление списков
        self.rgms_listbox.delete(0, tk.END)
        for rgm in self.data_info.rgms_info:
            self.rgms_listbox.insert(tk.END, rgm.display_name or rgm.name)
        
        self.scns_listbox.delete(0, tk.END)
        for scn in self.data_info.scns_info:
            self.scns_listbox.insert(tk.END, scn.display_name or scn.name)
        
        # Обновление меток файлов
        self.rems_label.config(text=self.data_info.rems.filename or "Не загружен", 
                              foreground="black" if self.data_info.rems.name else "gray")
        self.lapnu_label.config(text=self.data_info.lapnu.filename or "Не загружен",
                               foreground="black" if self.data_info.lapnu.name else "gray")
        self.vir_label.config(text=self.data_info.vir.filename or "Не загружен",
                            foreground="black" if self.data_info.vir.name else "gray")
        self.sechen_label.config(text=self.data_info.sechen.filename or "Не загружен",
                               foreground="black" if self.data_info.sechen.name else "gray")
        self.grf_label.config(text=self.data_info.grf.filename or "Не загружен",
                            foreground="black" if self.data_info.grf.name else "gray")
        
        # Обновление прогресса
        if self.data_info.max_progress > 0:
            progress_pct = (self.data_info.progress / self.data_info.max_progress) * 100
            self.progress_var.set(progress_pct)
            self.progress_label.config(text=self.data_info.label or f"Выполнено {progress_pct:.2f}%")
        else:
            self.progress_var.set(0)
            self.progress_label.config(text="")
    
    def _add_files(self):
        """Добавление файлов"""
        file_paths = filedialog.askopenfilenames(
            title="Выбор файлов",
            filetypes=[
                ("Rastr files", "*.rg2 *.rst *.sch *.ut2 *.scn *.vrn *.kpr *.csv *.lpn *.dwf"),
                ("All files", "*.*")
            ]
        )
        
        if file_paths:
            try:
                self.data_info.add_files(list(file_paths))
                self._update_ui()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при выполнении операции!\n\n{str(e)}")
    
    def _delete_files(self):
        """Удаление выбранных файлов"""
        selected_rgm_idx = self.rgms_listbox.curselection()
        selected_scn_idx = self.scns_listbox.curselection()
        
        selected_rgm = None
        if selected_rgm_idx:
            selected_rgm = self.data_info.rgms_info[selected_rgm_idx[0]]
        
        selected_scn = None
        if selected_scn_idx:
            selected_scn = self.data_info.scns_info[selected_scn_idx[0]]
        
        self.data_info.delete_selected(selected_rgm, selected_scn)
        self._update_ui()
    
    def _deselect_rgms(self):
        """Снятие выбора с расчетных режимов"""
        self.rgms_listbox.selection_clear(0, tk.END)
    
    def _deselect_scns(self):
        """Снятие выбора с аварийных процессов"""
        self.scns_listbox.selection_clear(0, tk.END)
    
    def _clear_rems(self):
        """Очистка ремонтных схем"""
        self.data_info.rems.name = None
        self._update_ui()
    
    def _clear_lapnu(self):
        """Очистка автоматики"""
        self.data_info.lapnu.name = None
        self.data_info.dyn_with_pa = False
        self._update_ui()
    
    def _clear_vir(self):
        """Очистка траектории"""
        self.data_info.vir.name = None
        self._update_ui()
    
    def _clear_sechen(self):
        """Очистка сечений"""
        self.data_info.sechen.name = None
        self.data_info.sch_inf.clear()
        self._update_ui()
    
    def _clear_grf(self):
        """Очистка графического вывода"""
        self.data_info.grf.name = None
        self.data_info.kpr_inf.clear()
        self._update_ui()
    
    def _open_settings(self):
        """Открытие окна настроек"""
        from .settings_window import SettingsWindow
        settings = SettingsWindow(self.root, self.data_info)
        settings.show()
        self._update_ui()
    
    def _progress_callback(self, progress: int):
        """Обратный вызов для обновления прогресса"""
        self.data_info.progress = progress
        if self.data_info.max_progress > 0:
            progress_pct = (progress / self.data_info.max_progress) * 100
            self.data_info.label = f"Выполнено {progress_pct:.2f}%"
        self.root.after(0, self._update_ui)
    
    def _calc_shunt_kz(self):
        """Расчет шунтов КЗ"""
        if self.data_info.is_active:
            messagebox.showwarning("Предупреждение", "Расчет уже выполняется!")
            return
        
        def run_calc():
            try:
                result_path = self.data_info.calc_shunt_kz(self._progress_callback)
                self.root.after(0, lambda: messagebox.showinfo(
                    "Успешно",
                    f"Операция выполнена успешно!\n\nРезультаты доступны в каталоге:\n{result_path}"
                ))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Ошибка",
                    f"Ошибка при выполнении операции!\n\n{str(e)}"
                ))
            finally:
                self.root.after(0, self._update_ui)
        
        thread = threading.Thread(target=run_calc, daemon=True)
        thread.start()
    
    def _calc_max_kz_time(self):
        """Расчет предельного времени КЗ"""
        if self.data_info.is_active:
            messagebox.showwarning("Предупреждение", "Расчет уже выполняется!")
            return
        
        def run_calc():
            try:
                result_path = self.data_info.calc_max_kz_time(self._progress_callback)
                self.root.after(0, lambda: messagebox.showinfo(
                    "Успешно",
                    f"Операция выполнена успешно!\n\nРезультаты доступны в каталоге:\n{result_path}"
                ))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Ошибка",
                    f"Ошибка при выполнении операции!\n\n{str(e)}"
                ))
            finally:
                self.root.after(0, self._update_ui)
        
        thread = threading.Thread(target=run_calc, daemon=True)
        thread.start()
    
    def _calc_dyn_stability(self):
        """Пакетный расчет ДУ"""
        if self.data_info.is_active:
            messagebox.showwarning("Предупреждение", "Расчет уже выполняется!")
            return
        
        def run_calc():
            try:
                result_path = self.data_info.calc_dyn_stability(self._progress_callback)
                self.root.after(0, lambda: messagebox.showinfo(
                    "Успешно",
                    f"Операция выполнена успешно!\n\nРезультаты доступны в каталоге:\n{result_path}"
                ))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Ошибка",
                    f"Ошибка при выполнении операции!\n\n{str(e)}"
                ))
            finally:
                self.root.after(0, self._update_ui)
        
        thread = threading.Thread(target=run_calc, daemon=True)
        thread.start()
    
    def _calc_mdp_stability(self):
        """Расчет МДП ДУ"""
        if self.data_info.is_active:
            messagebox.showwarning("Предупреждение", "Расчет уже выполняется!")
            return
        
        def run_calc():
            try:
                result_path = self.data_info.calc_mdp_stability(self._progress_callback)
                self.root.after(0, lambda: messagebox.showinfo(
                    "Успешно",
                    f"Операция выполнена успешно!\n\nРезультаты доступны в каталоге:\n{result_path}"
                ))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Ошибка",
                    f"Ошибка при выполнении операции!\n\n{str(e)}"
                ))
            finally:
                self.root.after(0, self._update_ui)
        
        thread = threading.Thread(target=run_calc, daemon=True)
        thread.start()
    
    def _calc_uost_stability(self):
        """Расчет остаточного напряжения при КЗ"""
        if self.data_info.is_active:
            messagebox.showwarning("Предупреждение", "Расчет уже выполняется!")
            return
        
        def run_calc():
            try:
                result_path = self.data_info.calc_uost_stability(self._progress_callback)
                self.root.after(0, lambda: messagebox.showinfo(
                    "Успешно",
                    f"Операция выполнена успешно!\n\nРезультаты доступны в каталоге:\n{result_path}"
                ))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Ошибка",
                    f"Ошибка при выполнении операции!\n\n{str(e)}"
                ))
            finally:
                self.root.after(0, self._update_ui)
        
        thread = threading.Thread(target=run_calc, daemon=True)
        thread.start()
    
    def run(self):
        """Запуск главного цикла"""
        self.root.mainloop()

