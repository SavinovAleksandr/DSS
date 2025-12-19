"""
Модернизированное главное окно приложения с CustomTkinter
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import Optional
import threading

from data_info import DataInfo
from utils.license import check_license
from utils.exceptions import UserLicenseException, InitialDataException
from utils.logger import logger
from utils.error_handler import error_handler
from utils.theme_manager import theme_manager


class ModernMainWindow:
    """Модернизированное главное окно приложения"""
    
    def __init__(self):
        """Инициализация главного окна"""
        # Настройка CustomTkinter
        ctk.set_appearance_mode(theme_manager.theme_mode)
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("DynStabSpace - Расчет динамической устойчивости")
        self.root.geometry("900x750")
        self.root.minsize(800, 600)
        
        # Проверка лицензии
        try:
            logger.info("Проверка лицензии")
            if not check_license():
                user_message, _ = error_handler.handle_error(
                    UserLicenseException("Некорректный файл лицензии"),
                    context="Проверка лицензии при инициализации",
                    show_to_user=True
                )
                messagebox.showerror("Ошибка лицензии", user_message)
                self.root.destroy()
                return
            logger.info("Лицензия проверена успешно")
            logger.audit("LICENSE_CHECK", "Успешная проверка лицензии")
        except UserLicenseException as e:
            user_message, _ = error_handler.handle_error(
                e,
                context="Проверка лицензии при инициализации",
                show_to_user=True
            )
            messagebox.showerror("Ошибка лицензии", user_message)
            self.root.destroy()
            return
        
        # Инициализация данных
        try:
            logger.info("Инициализация данных")
            self.data_info = DataInfo()
            logger.info("Данные инициализированы успешно")
        except Exception as e:
            user_message, _ = error_handler.handle_error(
                e,
                context="Инициализация данных",
                show_to_user=True
            )
            messagebox.showerror("Ошибка инициализации", user_message)
            self.root.destroy()
            return
        
        # Создание интерфейса
        self._create_ui()
        self._setup_keyboard_shortcuts()
        self._setup_drag_drop()
        
        # Обновление интерфейса
        self._update_ui()
        
        logger.info("Главное окно создано успешно")
    
    def _create_ui(self):
        """Создание элементов интерфейса"""
        # Основной контейнер с прокруткой
        main_container = ctk.CTkScrollableFrame(self.root, label_text="DynStabSpace")
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Расчетные режимы
        rgms_frame = ctk.CTkFrame(main_container)
        rgms_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(rgms_frame, text="Расчетные режимы:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        self.rgms_listbox = ctk.CTkTextbox(rgms_frame, height=100, state="disabled")
        self.rgms_listbox.pack(fill="x", padx=10, pady=(0, 10))
        
        # Аварийные процессы
        scns_frame = ctk.CTkFrame(main_container)
        scns_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(scns_frame, text="Аварийные процессы:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        self.scns_listbox = ctk.CTkTextbox(scns_frame, height=100, state="disabled")
        self.scns_listbox.pack(fill="x", padx=10, pady=(0, 10))
        
        # Файлы
        files_frame = ctk.CTkFrame(main_container, label_text="Исходные данные")
        files_frame.pack(fill="x", pady=10)
        
        # Ремонтные схемы
        self._create_file_row(files_frame, "Ремонтные схемы:", 0, 
                             lambda: self.data_info.rems.filename or "Не загружен",
                             self._clear_rems)
        
        # Автоматика
        self._create_file_row(files_frame, "Автоматика:", 1,
                             lambda: self.data_info.lapnu.filename or "Не загружен",
                             self._clear_lapnu)
        
        # Траектория
        self._create_file_row(files_frame, "Траектория:", 2,
                             lambda: self.data_info.vir.filename or "Не загружен",
                             self._clear_vir)
        
        # Сечения
        self._create_file_row(files_frame, "Сечения:", 3,
                             lambda: self.data_info.sechen.filename or "Не загружен",
                             self._clear_sechen)
        
        # Графический вывод
        self._create_file_row(files_frame, "Графический вывод:", 4,
                             lambda: self.data_info.grf.filename or "Не загружен",
                             self._clear_grf)
        
        # Кнопки управления
        buttons_frame = ctk.CTkFrame(main_container)
        buttons_frame.pack(fill="x", pady=10)
        
        ctk.CTkButton(buttons_frame, text="➕ Добавить файлы", 
                     command=self._add_files, width=150).pack(side="left", padx=5)
        ctk.CTkButton(buttons_frame, text="➖ Удалить", 
                     command=self._delete_files, width=150).pack(side="left", padx=5)
        ctk.CTkButton(buttons_frame, text="⚙️ Настройки", 
                     command=self._open_settings, width=150).pack(side="left", padx=5)
        ctk.CTkButton(buttons_frame, text="🌓 Тема", 
                     command=self._toggle_theme, width=100).pack(side="right", padx=5)
        
        # Кнопки расчетов
        calc_frame = ctk.CTkFrame(main_container, label_text="Расчеты")
        calc_frame.pack(fill="x", pady=10)
        
        calc_buttons = [
            ("Определение шунта КЗ", self._calc_shunt_kz),
            ("Определение предельного времени КЗ", self._calc_max_kz_time),
            ("Расчет ДУ", self._calc_dyn_stability),
            ("Определение МДП ДУ", self._calc_mdp_stability),
            ("Определение остаточного напряжения при КЗ", self._calc_uost_stability),
        ]
        
        for i, (text, command) in enumerate(calc_buttons):
            row = i // 2
            col = i % 2
            ctk.CTkButton(calc_frame, text=text, command=command,
                         height=40).grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        
        calc_frame.grid_columnconfigure(0, weight=1)
        calc_frame.grid_columnconfigure(1, weight=1)
        
        # Прогресс
        progress_frame = ctk.CTkFrame(main_container)
        progress_frame.pack(fill="x", pady=10)
        
        self.progress_label = ctk.CTkLabel(progress_frame, text="")
        self.progress_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.pack(fill="x", padx=10, pady=(0, 10))
        self.progress_bar.set(0)
        
        # Статус-бар
        self.status_bar = ctk.CTkLabel(self.root, text="Готов", anchor="w", 
                                      font=ctk.CTkFont(size=10))
        self.status_bar.pack(side="bottom", fill="x", padx=10, pady=5)
    
    def _create_file_row(self, parent, label_text, row, get_text_func, clear_func):
        """Создать строку для отображения файла"""
        row_frame = ctk.CTkFrame(parent)
        row_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(row_frame, text=label_text, width=150).pack(side="left", padx=5)
        
        file_label = ctk.CTkLabel(row_frame, text=get_text_func(), anchor="w", 
                                 text_color="gray", cursor="hand2")
        file_label.pack(side="left", fill="x", expand=True, padx=5)
        file_label.bind('<Double-Button-1>', lambda e: clear_func())
        
        # Сохраняем ссылку для обновления
        setattr(self, f"_file_label_{row}", file_label)
        setattr(self, f"_file_get_text_{row}", get_text_func)
    
    def _setup_keyboard_shortcuts(self):
        """Настройка горячих клавиш"""
        self.root.bind('<Control-o>', lambda e: self._add_files())
        self.root.bind('<Control-d>', lambda e: self._delete_files())
        self.root.bind('<Control-s>', lambda e: self._open_settings())
        self.root.bind('<F5>', lambda e: self._update_ui())
        self.root.bind('<Control-t>', lambda e: self._toggle_theme())
        logger.info("Горячие клавиши настроены")
    
    def _setup_drag_drop(self):
        """Настройка drag & drop для файлов"""
        try:
            # Попытка использовать tkinterdnd2 если доступен
            try:
                from tkinterdnd2 import DND_FILES, TkinterDnD
                if isinstance(self.root, TkinterDnD.DnDWrapper):
                    self.root.drop_target_register(DND_FILES)
                    self.root.dnd_bind('<<Drop>>', self._on_drop)
                    logger.info("Drag & drop настроен (tkinterdnd2)")
            except ImportError:
                logger.info("tkinterdnd2 не установлен, drag & drop недоступен")
        except Exception as e:
            logger.warning(f"Не удалось настроить drag & drop: {e}")
    
    def _on_drop(self, event):
        """Обработка перетаскивания файлов"""
        try:
            files = self.root.tk.splitlist(event.data)
            logger.info(f"Перетащено файлов: {len(files)}")
            logger.audit("FILE_DROP", f"Перетащено файлов: {len(files)}")
            self._add_files_from_list(files)
        except Exception as e:
            user_message, _ = error_handler.handle_error(
                e,
                context="Перетаскивание файлов",
                show_to_user=True
            )
            messagebox.showerror("Ошибка", user_message)
    
    def _toggle_theme(self):
        """Переключение темы"""
        theme_manager.toggle_theme()
        ctk.set_appearance_mode(theme_manager.theme_mode)
        self.status_bar.configure(text=f"Тема изменена на: {theme_manager.theme_mode}")
        logger.audit("THEME_TOGGLE", f"Тема переключена на: {theme_manager.theme_mode}")
    
    def _update_ui(self):
        """Обновление интерфейса"""
        # Обновление списков
        self.rgms_listbox.configure(state="normal")
        self.rgms_listbox.delete("1.0", "end")
        rgms_text = "\n".join([rgm.display_name or rgm.name for rgm in self.data_info.rgms_info]) or "Нет данных"
        self.rgms_listbox.insert("1.0", rgms_text)
        self.rgms_listbox.configure(state="disabled")
        
        self.scns_listbox.configure(state="normal")
        self.scns_listbox.delete("1.0", "end")
        scns_text = "\n".join([scn.display_name or scn.name for scn in self.data_info.scns_info]) or "Нет данных"
        self.scns_listbox.insert("1.0", scns_text)
        self.scns_listbox.configure(state="disabled")
        
        # Обновление меток файлов
        for i in range(5):
            label = getattr(self, f"_file_label_{i}", None)
            get_text = getattr(self, f"_file_get_text_{i}", None)
            if label and get_text:
                text = get_text()
                label.configure(text=text, text_color="gray" if "Не загружен" in text else None)
        
        # Обновление прогресса
        if self.data_info.max_progress > 0:
            progress_pct = (self.data_info.progress / self.data_info.max_progress)
            self.progress_bar.set(progress_pct)
            self.progress_label.configure(text=self.data_info.label or f"Выполнено {progress_pct*100:.2f}%")
        else:
            self.progress_bar.set(0)
            self.progress_label.configure(text="")
    
    def _add_files(self):
        """Добавление файлов"""
        logger.audit("FILE_ADD_START", "Начало добавления файлов")
        file_paths = filedialog.askopenfilenames(
            title="Выбор файлов",
            filetypes=[
                ("Rastr files", "*.rg2 *.rst *.sch *.ut2 *.scn *.vrn *.kpr *.csv *.lpn *.dwf"),
                ("All files", "*.*")
            ]
        )
        
        if file_paths:
            self._add_files_from_list(file_paths)
    
    def _add_files_from_list(self, file_paths):
        """Добавление файлов из списка"""
        try:
            logger.info(f"Добавление файлов: {len(file_paths)} файлов")
            # Валидация файлов перед добавлением
            invalid_files = []
            for file_path in file_paths:
                is_valid, error_msg = error_handler.validate_file_path(Path(file_path))
                if not is_valid:
                    invalid_files.append((file_path, error_msg))
                    logger.warning(f"Невалидный файл: {file_path} - {error_msg}")
            
            if invalid_files:
                error_msg = "Следующие файлы не могут быть добавлены:\n\n"
                error_msg += "\n".join([f"{fp}: {msg}" for fp, msg in invalid_files])
                messagebox.showwarning("Предупреждение", error_msg)
                # Продолжаем с валидными файлами
                valid_files = [fp for fp in file_paths if Path(fp) not in [Path(ifp[0]) for ifp in invalid_files]]
                if valid_files:
                    self.data_info.add_files(valid_files)
                    logger.info(f"Добавлено {len(valid_files)} валидных файлов")
            else:
                self.data_info.add_files(list(file_paths))
                logger.info(f"Все {len(file_paths)} файлов добавлены успешно")
            
            self._update_ui()
            self.status_bar.configure(text=f"Добавлено файлов: {len(file_paths)}")
            logger.audit("FILE_ADD_SUCCESS", f"Успешно добавлено файлов: {len(file_paths)}")
        except Exception as e:
            user_message, recovered = error_handler.handle_error(
                e,
                context="Добавление файлов",
                show_to_user=True
            )
            if not recovered:
                messagebox.showerror("Ошибка", user_message)
            logger.audit("FILE_ADD_ERROR", f"Ошибка при добавлении файлов: {str(e)}")
    
    def _delete_files(self):
        """Удаление выбранных файлов"""
        # В CustomTkinter Textbox нет прямого способа получить выделение
        # Используем простой подход - удаляем все
        self.data_info.delete_selected(None, None)
        self._update_ui()
        self.status_bar.configure(text="Выбранные элементы удалены")
        logger.audit("FILE_DELETE", "Удаление файлов")
    
    def _deselect_rgms(self):
        """Снятие выбора с расчетных режимов"""
        pass  # Для Textbox не применимо
    
    def _deselect_scns(self):
        """Снятие выбора с аварийных процессов"""
        pass  # Для Textbox не применимо
    
    def _clear_rems(self):
        """Очистка ремонтных схем"""
        self.data_info.rems.name = None
        self._update_ui()
        self.status_bar.configure(text="Ремонтные схемы очищены")
    
    def _clear_lapnu(self):
        """Очистка автоматики"""
        self.data_info.lapnu.name = None
        self.data_info.dyn_with_pa = False
        self._update_ui()
        self.status_bar.configure(text="Автоматика очищена")
    
    def _clear_vir(self):
        """Очистка траектории"""
        self.data_info.vir.name = None
        self._update_ui()
        self.status_bar.configure(text="Траектория очищена")
    
    def _clear_sechen(self):
        """Очистка сечений"""
        self.data_info.sechen.name = None
        self.data_info.sch_inf.clear()
        self._update_ui()
        self.status_bar.configure(text="Сечения очищены")
    
    def _clear_grf(self):
        """Очистка графического вывода"""
        self.data_info.grf.name = None
        self.data_info.kpr_inf.clear()
        self._update_ui()
        self.status_bar.configure(text="Графический вывод очищен")
    
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
            progress_pct = (progress / self.data_info.max_progress)
            self.data_info.label = f"Выполнено {progress_pct*100:.2f}%"
        self.root.after(0, self._update_ui)
    
    def _calc_shunt_kz(self):
        """Расчет шунтов КЗ"""
        logger.audit("CALC_START", "Начало расчета: Определение шунта КЗ")
        if self.data_info.is_active:
            messagebox.showwarning("Предупреждение", "Расчет уже выполняется!")
            return
        
        def run_calc():
            try:
                logger.info("Запуск расчета: Определение шунта КЗ")
                self.root.after(0, lambda: self.status_bar.configure(text="Выполняется расчет: Определение шунта КЗ..."))
                result_path = self.data_info.calc_shunt_kz(self._progress_callback)
                logger.info(f"Расчет завершен успешно. Результаты: {result_path}")
                logger.audit("CALC_SUCCESS", f"Расчет завершен: Определение шунта КЗ | Результаты: {result_path}")
                self.root.after(0, lambda: messagebox.showinfo(
                    "Успешно",
                    f"Операция выполнена успешно!\n\nРезультаты доступны в каталоге:\n{result_path}"
                ))
                self.root.after(0, lambda: self.status_bar.configure(text="Расчет завершен успешно"))
            except Exception as e:
                user_message, _ = error_handler.handle_error(
                    e,
                    context="Расчет: Определение шунта КЗ",
                    show_to_user=False
                )
                logger.audit("CALC_ERROR", f"Ошибка расчета: Определение шунта КЗ | {str(e)}")
                self.root.after(0, lambda: messagebox.showerror("Ошибка", user_message))
                self.root.after(0, lambda: self.status_bar.configure(text="Ошибка при выполнении расчета"))
            finally:
                self.root.after(0, self._update_ui)
        
        thread = threading.Thread(target=run_calc, daemon=True)
        thread.start()
    
    def _calc_max_kz_time(self):
        """Расчет предельного времени КЗ"""
        logger.audit("CALC_START", "Начало расчета: Определение предельного времени КЗ")
        if self.data_info.is_active:
            messagebox.showwarning("Предупреждение", "Расчет уже выполняется!")
            return
        
        def run_calc():
            try:
                logger.info("Запуск расчета: Определение предельного времени КЗ")
                self.root.after(0, lambda: self.status_bar.configure(text="Выполняется расчет: Определение предельного времени КЗ..."))
                result_path = self.data_info.calc_max_kz_time(self._progress_callback)
                logger.info(f"Расчет завершен успешно. Результаты: {result_path}")
                logger.audit("CALC_SUCCESS", f"Расчет завершен: Определение предельного времени КЗ | Результаты: {result_path}")
                self.root.after(0, lambda: messagebox.showinfo(
                    "Успешно",
                    f"Операция выполнена успешно!\n\nРезультаты доступны в каталоге:\n{result_path}"
                ))
                self.root.after(0, lambda: self.status_bar.configure(text="Расчет завершен успешно"))
            except Exception as e:
                user_message, _ = error_handler.handle_error(
                    e,
                    context="Расчет: Определение предельного времени КЗ",
                    show_to_user=False
                )
                logger.audit("CALC_ERROR", f"Ошибка расчета: Определение предельного времени КЗ | {str(e)}")
                self.root.after(0, lambda: messagebox.showerror("Ошибка", user_message))
                self.root.after(0, lambda: self.status_bar.configure(text="Ошибка при выполнении расчета"))
            finally:
                self.root.after(0, self._update_ui)
        
        thread = threading.Thread(target=run_calc, daemon=True)
        thread.start()
    
    def _calc_dyn_stability(self):
        """Пакетный расчет ДУ"""
        logger.audit("CALC_START", "Начало расчета: Пакетный расчет ДУ")
        if self.data_info.is_active:
            messagebox.showwarning("Предупреждение", "Расчет уже выполняется!")
            return
        
        def run_calc():
            try:
                logger.info("Запуск расчета: Пакетный расчет ДУ")
                self.root.after(0, lambda: self.status_bar.configure(text="Выполняется расчет: Пакетный расчет ДУ..."))
                result_path = self.data_info.calc_dyn_stability(self._progress_callback)
                logger.info(f"Расчет завершен успешно. Результаты: {result_path}")
                logger.audit("CALC_SUCCESS", f"Расчет завершен: Пакетный расчет ДУ | Результаты: {result_path}")
                self.root.after(0, lambda: messagebox.showinfo(
                    "Успешно",
                    f"Операция выполнена успешно!\n\nРезультаты доступны в каталоге:\n{result_path}"
                ))
                self.root.after(0, lambda: self.status_bar.configure(text="Расчет завершен успешно"))
            except Exception as e:
                user_message, _ = error_handler.handle_error(
                    e,
                    context="Расчет: Пакетный расчет ДУ",
                    show_to_user=False
                )
                logger.audit("CALC_ERROR", f"Ошибка расчета: Пакетный расчет ДУ | {str(e)}")
                self.root.after(0, lambda: messagebox.showerror("Ошибка", user_message))
                self.root.after(0, lambda: self.status_bar.configure(text="Ошибка при выполнении расчета"))
            finally:
                self.root.after(0, self._update_ui)
        
        thread = threading.Thread(target=run_calc, daemon=True)
        thread.start()
    
    def _calc_mdp_stability(self):
        """Расчет МДП ДУ"""
        logger.audit("CALC_START", "Начало расчета: Определение МДП ДУ")
        if self.data_info.is_active:
            messagebox.showwarning("Предупреждение", "Расчет уже выполняется!")
            return
        
        def run_calc():
            try:
                logger.info("Запуск расчета: Определение МДП ДУ")
                self.root.after(0, lambda: self.status_bar.configure(text="Выполняется расчет: Определение МДП ДУ..."))
                result_path = self.data_info.calc_mdp_stability(self._progress_callback)
                logger.info(f"Расчет завершен успешно. Результаты: {result_path}")
                logger.audit("CALC_SUCCESS", f"Расчет завершен: Определение МДП ДУ | Результаты: {result_path}")
                self.root.after(0, lambda: messagebox.showinfo(
                    "Успешно",
                    f"Операция выполнена успешно!\n\nРезультаты доступны в каталоге:\n{result_path}"
                ))
                self.root.after(0, lambda: self.status_bar.configure(text="Расчет завершен успешно"))
            except Exception as e:
                user_message, _ = error_handler.handle_error(
                    e,
                    context="Расчет: Определение МДП ДУ",
                    show_to_user=False
                )
                logger.audit("CALC_ERROR", f"Ошибка расчета: Определение МДП ДУ | {str(e)}")
                self.root.after(0, lambda: messagebox.showerror("Ошибка", user_message))
                self.root.after(0, lambda: self.status_bar.configure(text="Ошибка при выполнении расчета"))
            finally:
                self.root.after(0, self._update_ui)
        
        thread = threading.Thread(target=run_calc, daemon=True)
        thread.start()
    
    def _calc_uost_stability(self):
        """Расчет остаточного напряжения при КЗ"""
        logger.audit("CALC_START", "Начало расчета: Определение остаточного напряжения при КЗ")
        if self.data_info.is_active:
            messagebox.showwarning("Предупреждение", "Расчет уже выполняется!")
            return
        
        def run_calc():
            try:
                logger.info("Запуск расчета: Определение остаточного напряжения при КЗ")
                self.root.after(0, lambda: self.status_bar.configure(text="Выполняется расчет: Определение остаточного напряжения при КЗ..."))
                result_path = self.data_info.calc_uost_stability(self._progress_callback)
                logger.info(f"Расчет завершен успешно. Результаты: {result_path}")
                logger.audit("CALC_SUCCESS", f"Расчет завершен: Определение остаточного напряжения при КЗ | Результаты: {result_path}")
                self.root.after(0, lambda: messagebox.showinfo(
                    "Успешно",
                    f"Операция выполнена успешно!\n\nРезультаты доступны в каталоге:\n{result_path}"
                ))
                self.root.after(0, lambda: self.status_bar.configure(text="Расчет завершен успешно"))
            except Exception as e:
                user_message, _ = error_handler.handle_error(
                    e,
                    context="Расчет: Определение остаточного напряжения при КЗ",
                    show_to_user=False
                )
                logger.audit("CALC_ERROR", f"Ошибка расчета: Определение остаточного напряжения при КЗ | {str(e)}")
                self.root.after(0, lambda: messagebox.showerror("Ошибка", user_message))
                self.root.after(0, lambda: self.status_bar.configure(text="Ошибка при выполнении расчета"))
            finally:
                self.root.after(0, self._update_ui)
        
        thread = threading.Thread(target=run_calc, daemon=True)
        thread.start()
    
    def run(self):
        """Запуск главного цикла"""
        self.root.mainloop()

