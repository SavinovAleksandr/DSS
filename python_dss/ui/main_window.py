"""
Главное окно приложения
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Optional
import threading
from PIL import Image, ImageTk

from data_info import DataInfo
from utils.license import check_license
from utils.exceptions import UserLicenseException, InitialDataException
from utils.logger import logger
from utils.error_handler import error_handler


class MainWindow:
    """Главное окно приложения"""
    
    def __init__(self):
        """Инициализация главного окна"""
        self.root = tk.Tk()
        self.root.title("StabLimit - Расчет динамической устойчивости")
        self.root.geometry("800x700")
        
        # Установка иконки окна
        try:
            icon_path_png = Path(__file__).parent.parent / "resources" / "StabLimit.png"
            icon_path_ico = Path(__file__).parent.parent / "resources" / "StabLimit.ico"
            
            # На Windows предпочтительнее использовать .ico файл
            if icon_path_ico.exists():
                try:
                    self.root.iconbitmap(str(icon_path_ico))
                    logger.info(f"Иконка окна установлена (ICO): {icon_path_ico}")
                except Exception as e:
                    logger.warning(f"Не удалось установить ICO иконку: {e}, пробуем PNG")
                    if icon_path_png.exists():
                        img = Image.open(icon_path_png)
                        photo = ImageTk.PhotoImage(img)
                        self.root.iconphoto(False, photo)
                        self.root._icon_photo = photo
                        logger.info(f"Иконка окна установлена (PNG): {icon_path_png}")
            elif icon_path_png.exists():
                # Для tkinter используем iconphoto (поддерживает PNG)
                img = Image.open(icon_path_png)
                photo = ImageTk.PhotoImage(img)
                self.root.iconphoto(False, photo)
                # Сохраняем ссылку, чтобы изображение не удалилось
                self.root._icon_photo = photo
                logger.info(f"Иконка окна установлена (PNG): {icon_path_png}")
            else:
                logger.warning(f"Файл иконки не найден: {icon_path_png} или {icon_path_ico}")
        except Exception as e:
            logger.warning(f"Не удалось установить иконку окна: {e}")
        
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
        
        # Настройка drag-and-drop
        self._setup_drag_drop()
        
        # Обновление интерфейса
        self._update_ui()
        
        logger.info("Главное окно создано успешно")
    
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
        ttk.Button(buttons_frame, text="Как в предыдущем расчете", 
                   command=self._load_last_files).grid(row=0, column=2, padx=5)
        ttk.Button(buttons_frame, text="Настройки", command=self._open_settings).grid(row=0, column=3, padx=5)
        
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
        logger.audit("FILE_ADD_START", "Начало добавления файлов")
        file_paths = filedialog.askopenfilenames(
            title="Выбор файлов",
            filetypes=[
                ("Rastr files", "*.rg2 *.rst *.sch *.ut2 *.scn *.vrn *.kpr *.csv *.lpn *.dwf"),
                ("All files", "*.*")
            ]
        )
        
        if file_paths:
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
    
    def _add_files_from_list(self, file_paths):
        """Добавление файлов из списка (для drag-and-drop)"""
        if file_paths:
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
    
    def _setup_drag_drop(self):
        """Настройка drag & drop для файлов"""
        try:
            # Используем tkinterdnd2 если доступен
            try:
                from tkinterdnd2 import DND_FILES, TkinterDnD
                
                # Обертываем root в TkinterDnD
                dnd_root = TkinterDnD.DnDWrapper(self.root)
                dnd_root.drop_target_register(DND_FILES)
                dnd_root.dnd_bind('<<Drop>>', self._on_drop)
                
                # Регистрируем drag-and-drop на всех виджетах окна
                self._register_drag_drop_recursive(self.root, dnd_root)
                
                logger.info("Drag & drop настроен (tkinterdnd2)")
            except ImportError:
                logger.warning("tkinterdnd2 не установлен. Для drag-and-drop установите: pip install tkinterdnd2")
            except Exception as e:
                logger.warning(f"Не удалось настроить drag & drop: {e}")
        except Exception as e:
            logger.warning(f"Не удалось настроить drag & drop: {e}")
    
    def _register_drag_drop_recursive(self, widget, dnd_root):
        """Рекурсивно регистрировать drag-and-drop на всех виджетах"""
        try:
            from tkinterdnd2 import DND_FILES
            # Регистрируем на текущем виджете
            try:
                if hasattr(widget, 'drop_target_register'):
                    widget.drop_target_register(DND_FILES)
                    widget.dnd_bind('<<Drop>>', self._on_drop)
            except:
                pass
            
            # Рекурсивно обрабатываем дочерние виджеты
            try:
                for child in widget.winfo_children():
                    self._register_drag_drop_recursive(child, dnd_root)
            except:
                pass
        except:
            pass
    
    def _on_drop(self, event):
        """Обработка перетаскивания файлов"""
        try:
            # Получаем список файлов из события
            files = []
            try:
                # Для tkinterdnd2 - event.data содержит строку с путями файлов
                data = event.data
                if isinstance(data, str):
                    # Разделяем строку на отдельные пути
                    # tkinterdnd2 может возвращать пути в фигурных скобках или через пробелы
                    if '{' in data:
                        # Формат с фигурными скобками: {file1} {file2}
                        import re
                        files = re.findall(r'\{([^}]+)\}', data)
                    else:
                        # Простой формат: file1 file2
                        files = self.root.tk.splitlist(data) if hasattr(self.root.tk, 'splitlist') else data.split()
                else:
                    files = [str(data)]
            except Exception as e:
                logger.warning(f"Ошибка при парсинге данных drag-and-drop: {e}")
                # Альтернативный способ
                try:
                    files = str(event.data).split()
                except:
                    files = []
            
            # Фильтруем и очищаем пути к файлам
            clean_files = []
            for f in files:
                if not f:
                    continue
                # Убираем фигурные скобки и кавычки
                f = f.strip('{}"\'')
                # Проверяем существование файла
                file_path = Path(f)
                if file_path.exists() and file_path.is_file():
                    clean_files.append(str(file_path.absolute()))
            
            if clean_files:
                logger.info(f"Перетащено файлов: {len(clean_files)}")
                logger.audit("FILE_DROP", f"Перетащено файлов: {len(clean_files)}")
                self._add_files_from_list(clean_files)
            else:
                logger.warning(f"Не удалось определить файлы из drag-and-drop. Данные: {event.data}")
                messagebox.showwarning(
                    "Предупреждение",
                    "Не удалось определить файлы из перетаскивания.\n\nПопробуйте использовать кнопку 'Добавить' для выбора файлов."
                )
        except Exception as e:
            user_message, _ = error_handler.handle_error(
                e,
                context="Перетаскивание файлов",
                show_to_user=True
            )
            messagebox.showerror("Ошибка", user_message)
    
    def _load_last_files(self):
        """Загрузка файлов из предыдущего расчета"""
        try:
            logger.audit("FILE_LOAD_LAST_START", "Начало загрузки последних файлов")
            if self.data_info.load_last_files():
                self._update_ui()
                messagebox.showinfo("Успешно", "Файлы из предыдущего расчета загружены успешно")
                logger.audit("FILE_LOAD_LAST_SUCCESS", "Последние файлы загружены успешно")
            else:
                messagebox.showinfo("Информация", "Нет сохраненных файлов из предыдущего расчета")
                logger.audit("FILE_LOAD_LAST_EMPTY", "Нет сохраненных файлов")
        except Exception as e:
            user_message, recovered = error_handler.handle_error(
                e,
                context="Загрузка последних файлов",
                show_to_user=True
            )
            if not recovered:
                messagebox.showerror("Ошибка", user_message)
            logger.audit("FILE_LOAD_LAST_ERROR", f"Ошибка при загрузке последних файлов: {str(e)}")
    
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
        logger.audit("CALC_START", "Начало расчета: Определение шунта КЗ")
        if self.data_info.is_active:
            messagebox.showwarning("Предупреждение", "Расчет уже выполняется!")
            return
        
        def run_calc():
            try:
                logger.info("Запуск расчета: Определение шунта КЗ")
                result_path = self.data_info.calc_shunt_kz(self._progress_callback)
                logger.info(f"Расчет завершен успешно. Результаты: {result_path}")
                logger.audit("CALC_SUCCESS", f"Расчет завершен: Определение шунта КЗ | Результаты: {result_path}")
                self.root.after(0, lambda: messagebox.showinfo(
                    "Успешно",
                    f"Операция выполнена успешно!\n\nРезультаты доступны в каталоге:\n{result_path}"
                ))
            except Exception as e:
                user_message, recovered = error_handler.handle_error(
                    e,
                    context="Расчет: Определение шунта КЗ",
                    show_to_user=False  # Покажем пользователю через messagebox
                )
                logger.audit("CALC_ERROR", f"Ошибка расчета: Определение шунта КЗ | {str(e)}")
                self.root.after(0, lambda: messagebox.showerror("Ошибка", user_message))
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
                result_path = self.data_info.calc_max_kz_time(self._progress_callback)
                logger.info(f"Расчет завершен успешно. Результаты: {result_path}")
                logger.audit("CALC_SUCCESS", f"Расчет завершен: Определение предельного времени КЗ | Результаты: {result_path}")
                self.root.after(0, lambda: messagebox.showinfo(
                    "Успешно",
                    f"Операция выполнена успешно!\n\nРезультаты доступны в каталоге:\n{result_path}"
                ))
            except Exception as e:
                user_message, _ = error_handler.handle_error(
                    e,
                    context="Расчет: Определение предельного времени КЗ",
                    show_to_user=False
                )
                logger.audit("CALC_ERROR", f"Ошибка расчета: Определение предельного времени КЗ | {str(e)}")
                self.root.after(0, lambda: messagebox.showerror("Ошибка", user_message))
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
                result_path = self.data_info.calc_dyn_stability(self._progress_callback)
                logger.info(f"Расчет завершен успешно. Результаты: {result_path}")
                logger.audit("CALC_SUCCESS", f"Расчет завершен: Пакетный расчет ДУ | Результаты: {result_path}")
                self.root.after(0, lambda: messagebox.showinfo(
                    "Успешно",
                    f"Операция выполнена успешно!\n\nРезультаты доступны в каталоге:\n{result_path}"
                ))
            except Exception as e:
                user_message, _ = error_handler.handle_error(
                    e,
                    context="Расчет: Пакетный расчет ДУ",
                    show_to_user=False
                )
                logger.audit("CALC_ERROR", f"Ошибка расчета: Пакетный расчет ДУ | {str(e)}")
                self.root.after(0, lambda: messagebox.showerror("Ошибка", user_message))
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
                result_path = self.data_info.calc_mdp_stability(self._progress_callback)
                logger.info(f"Расчет завершен успешно. Результаты: {result_path}")
                logger.audit("CALC_SUCCESS", f"Расчет завершен: Определение МДП ДУ | Результаты: {result_path}")
                self.root.after(0, lambda: messagebox.showinfo(
                    "Успешно",
                    f"Операция выполнена успешно!\n\nРезультаты доступны в каталоге:\n{result_path}"
                ))
            except Exception as e:
                user_message, _ = error_handler.handle_error(
                    e,
                    context="Расчет: Определение МДП ДУ",
                    show_to_user=False
                )
                logger.audit("CALC_ERROR", f"Ошибка расчета: Определение МДП ДУ | {str(e)}")
                self.root.after(0, lambda: messagebox.showerror("Ошибка", user_message))
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
                result_path = self.data_info.calc_uost_stability(self._progress_callback)
                logger.info(f"Расчет завершен успешно. Результаты: {result_path}")
                logger.audit("CALC_SUCCESS", f"Расчет завершен: Определение остаточного напряжения при КЗ | Результаты: {result_path}")
                self.root.after(0, lambda: messagebox.showinfo(
                    "Успешно",
                    f"Операция выполнена успешно!\n\nРезультаты доступны в каталоге:\n{result_path}"
                ))
            except Exception as e:
                user_message, _ = error_handler.handle_error(
                    e,
                    context="Расчет: Определение остаточного напряжения при КЗ",
                    show_to_user=False
                )
                logger.audit("CALC_ERROR", f"Ошибка расчета: Определение остаточного напряжения при КЗ | {str(e)}")
                self.root.after(0, lambda: messagebox.showerror("Ошибка", user_message))
            finally:
                self.root.after(0, self._update_ui)
        
        thread = threading.Thread(target=run_calc, daemon=True)
        thread.start()
    
    def run(self):
        """Запуск главного цикла"""
        self.root.mainloop()

