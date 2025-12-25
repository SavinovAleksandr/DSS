"""
Операции с RASTR через COM-интерфейс
"""

import os
import math
import locale
from pathlib import Path
from typing import List, Optional, Union, Any
from .dynamic_result import DynamicResult
from .point import Point
from .shunt_kz_result import ShuntKZResult

try:
    import win32com.client

    RASTR_AVAILABLE = True
except ImportError:
    RASTR_AVAILABLE = False
    win32com = None


class RastrOperations:
    """Класс для работы с RASTR через COM-интерфейс"""

    # Имя COM-объекта RASTR (используется вместо GUID для лучшей совместимости)
    RASTR_PROGID = "Astra.Rastr"
    # GUID для RASTR COM объекта (fallback)
    RASTR_CLSID = "{EFC5E4AD-A3DD-11D3-B73F-00500454CF3F}"

    def __init__(self):
        if not RASTR_AVAILABLE:
            raise ImportError(
                "pywin32 не установлен. RASTR операции недоступны на этой платформе."
            )

        try:
            # Пытаемся использовать ProgID (как в рабочей версии)
            try:
                self._rastr = win32com.client.Dispatch(self.RASTR_PROGID)
            except:
                # Если не получилось, используем GUID
                try:
                    # Пытаемся использовать gencache для генерации типов
                    self._rastr = win32com.client.gencache.EnsureDispatch(
                        self.RASTR_CLSID
                    )
                except:
                    # Если не получилось, используем DispatchEx
                    try:
                        self._rastr = win32com.client.DispatchEx(self.RASTR_CLSID)
                    except:
                        # Fallback на обычный Dispatch
                        self._rastr = win32com.client.Dispatch(self.RASTR_CLSID)
        except Exception as e:
            raise RuntimeError(f"Не удалось подключиться к RASTR: {str(e)}")

    def __del__(self):
        """Очистка ресурсов"""
        self._rastr = None

    @staticmethod
    def find_template_path_with_extension(extension: str) -> Optional[str]:
        """Поиск шаблона по расширению"""
        from utils.config import config
        from utils.logger import logger

        # Получаем путь к директории шаблонов из конфигурации
        template_dir = config.get_path("paths.rastr_template_dir")

        if not template_dir.exists():
            logger.error(f"Директория шаблонов не найдена: {template_dir}")
            logger.error(f"Проверьте настройку paths.rastr_template_dir в конфигурации")
            return None

        # Ищем шаблон с нужным расширением
        for file in template_dir.glob(f"*{extension}"):
            if file.stem != "базовый режим мт":
                logger.debug(f"Найден шаблон: {file}")
                return str(file)

        logger.warning(f"Шаблон для расширения {extension} не найден в {template_dir}")
        return None

    def load(self, file: str):
        """Загрузка файла в RASTR"""
        from utils.config import config
        from utils.logger import logger

        # ИСПРАВЛЕНО: Проверка на None или пустую строку
        if not file:
            raise ValueError(f"Путь к файлу не может быть None или пустой строкой")
        
        file_path = Path(file)
        extension = file_path.suffix

        if not file_path.exists():
            raise FileNotFoundError(f"Файл не найден: {file}")

        shabl = self.find_template_path_with_extension(extension)
        if shabl:
            self._rastr.NewFile(shabl)
            # RG_REPL = 0 (замена)
            self._rastr.Load(0, str(file_path), shabl)
        else:
            # Более подробное сообщение об ошибке
            template_dir = config.get_path("paths.rastr_template_dir")
            error_msg = (
                f"Шаблон для расширения {extension} не найден.\n\n"
                f"Проверьте:\n"
                f"1. Существует ли директория шаблонов: {template_dir}\n"
                f"2. Есть ли в ней файл с расширением {extension}\n"
                f"3. Правильно ли настроен путь в конфигурации (paths.rastr_template_dir)"
            )
            raise FileNotFoundError(error_msg)

    def load_template(self, extension: str):
        """Загрузка шаблона"""
        from utils.config import config

        shabl = self.find_template_path_with_extension(extension)
        if shabl:
            self._rastr.NewFile(shabl)
        else:
            template_dir = config.get_path("paths.rastr_template_dir")
            error_msg = (
                f"Шаблон для расширения {extension} не найден.\n\n"
                f"Проверьте:\n"
                f"1. Существует ли директория шаблонов: {template_dir}\n"
                f"2. Есть ли в ней файл с расширением {extension}\n"
                f"3. Правильно ли настроен путь в конфигурации "
                f"(paths.rastr_template_dir)"
            )
            raise FileNotFoundError(error_msg)

    def save(self, file: str):
        """Сохранение файла"""
        from utils.config import config

        extension = Path(file).suffix
        shabl = self.find_template_path_with_extension(extension)
        if shabl:
            self._rastr.Save(file, shabl)
        else:
            template_dir = config.get_path("paths.rastr_template_dir")
            error_msg = (
                f"Шаблон для расширения {extension} не найден.\n\n"
                f"Проверьте:\n"
                f"1. Существует ли директория шаблонов: {template_dir}\n"
                f"2. Есть ли в ней файл с расширением {extension}\n"
                f"3. Правильно ли настроен путь в конфигурации "
                f"(paths.rastr_template_dir)"
            )
            raise FileNotFoundError(error_msg)

    def add(self, file: str):
        """Добавление файла (RG_ADD = 1)"""
        from utils.config import config

        extension = Path(file).suffix
        shabl = self.find_template_path_with_extension(extension)
        if shabl:
            self._rastr.Load(1, file, shabl)
        else:
            template_dir = config.get_path("paths.rastr_template_dir")
            error_msg = (
                f"Шаблон для расширения {extension} не найден.\n\n"
                f"Проверьте:\n"
                f"1. Существует ли директория шаблонов: {template_dir}\n"
                f"2. Есть ли в ней файл с расширением {extension}\n"
                f"3. Правильно ли настроен путь в конфигурации "
                f"(paths.rastr_template_dir)"
            )
            raise FileNotFoundError(error_msg)

    def rgm(
        self,
        param: str = "",
        iterations: Optional[int] = None,
        voltage: Optional[float] = None,
    ) -> bool:
        """Расчет установившегося режима"""
        table = self._rastr.Tables.Item("com_regim")
        col_it_max = table.Cols.Item("it_max")
        col_dv_min = table.Cols.Item("dv_min")

        if iterations is not None:
            col_it_max.SetZ(0, iterations)
        if voltage is not None:
            col_dv_min.SetZ(0, voltage)

        # AST_OK = 0
        return self._rastr.rgm(param) == 0

    def add_table_row(self, table_name: str) -> int:
        """Добавление строки в таблицу"""
        table = self._rastr.Tables.Item(table_name)
        table.AddRow()
        table_size = table.Size
        # ИСПРАВЛЕНО: Преобразуем table.Size в int, если это строка
        if not isinstance(table_size, int):
            try:
                table_size = int(table_size)
            except (ValueError, TypeError):
                from utils.logger import logger

                logger.error(
                    f"Некорректный тип table.Size для {table_name}: {table_size} (тип: {type(table_size)})"
                )
                table_size = 0
        return table_size - 1

    def set_line_for_uost_calc(self, id1: int, id2: int, r: float, x: float, l: float):
        """Установка параметров линии для расчета остаточного напряжения"""
        # ИСПРАВЛЕНО: Преобразуем id1 и id2 в int, если это строки
        if not isinstance(id1, int):
            try:
                id1 = int(id1)
            except (ValueError, TypeError) as e:
                from utils.logger import logger

                logger.error(
                    f"Некорректный тип id1: {id1} (тип: {type(id1)}), ошибка: {e}"
                )
                raise TypeError(
                    f"id1 должен быть int, получен {type(id1).__name__}: {id1}"
                )
        if not isinstance(id2, int):
            try:
                id2 = int(id2)
            except (ValueError, TypeError) as e:
                from utils.logger import logger

                logger.error(
                    f"Некорректный тип id2: {id2} (тип: {type(id2)}), ошибка: {e}"
                )
                raise TypeError(
                    f"id2 должен быть int, получен {type(id2).__name__}: {id2}"
                )

        table = self._rastr.Tables.Item("vetv")
        col_r = table.Cols.Item("r")
        col_x = table.Cols.Item("x")

        r_part = l * r / 100.0
        x_part = l * x / 100.0

        col_r.SetZ(id1, r_part)
        col_r.SetZ(id2, r - r_part)
        col_x.SetZ(id1, x_part)
        col_x.SetZ(id2, x - x_part)

        self.rgm()

    def change_rx_for_uost_calc(
        self, x_id: int, x: float, r_id: int = 0, r: float = -1.0
    ):
        """Изменение R/X для расчета остаточного напряжения"""
        # ИСПРАВЛЕНО: Преобразуем x_id и r_id в int, если это строки
        if not isinstance(x_id, int):
            try:
                x_id = int(x_id)
            except (ValueError, TypeError) as e:
                from utils.logger import logger

                logger.error(
                    f"Некорректный тип x_id: {x_id} (тип: {type(x_id)}), ошибка: {e}"
                )
                raise TypeError(
                    f"x_id должен быть int, получен {type(x_id).__name__}: {x_id}"
                )
        if not isinstance(r_id, int):
            try:
                r_id = int(r_id)
            except (ValueError, TypeError) as e:
                from utils.logger import logger

                logger.error(
                    f"Некорректный тип r_id: {r_id} (тип: {type(r_id)}), ошибка: {e}"
                )
                raise TypeError(
                    f"r_id должен быть int, получен {type(r_id).__name__}: {r_id}"
                )

        table = self._rastr.Tables.Item("DFWAutoActionScn")
        col_formula = table.Cols.Item("Formula")

        col_formula.SetZ(x_id, str(x).replace(",", "."))
        if r != -1.0:
            col_formula.SetZ(r_id, str(r).replace(",", "."))

    def selection(self, table_name: str, selection: str = "") -> List[int]:
        """Выборка строк по условию"""
        table = self._rastr.Tables.Item(table_name)
        table.SetSel(selection)

        result = []
        idx = table.FindNextSel(-1)
        # ИСПРАВЛЕНО: Преобразуем idx в int, если это строка
        if not isinstance(idx, int) and idx is not None:
            try:
                idx = int(idx)
            except (ValueError, TypeError):
                idx = -1

        while idx != -1:
            result.append(int(idx))  # Убеждаемся, что добавляем int
            idx = table.FindNextSel(idx)
            # ИСПРАВЛЕНО: Преобразуем idx в int перед сравнением
            if not isinstance(idx, int) and idx is not None:
                try:
                    idx = int(idx)
                except (ValueError, TypeError):
                    idx = -1

        return result

    def apply_variant(self, num: int, file: str) -> bool:
        """Применение варианта из файла"""
        # ИСПРАВЛЕНО: Проверка на None или пустую строку перед загрузкой
        if not file:
            from utils.logger import logger
            logger.error(f"Путь к файлу ремонтных схем не может быть None или пустой строкой для варианта {num}")
            raise ValueError(f"Путь к файлу ремонтных схем не может быть None или пустой строкой")
        
        self.load(file)
        self._rastr.ApplyVariant(num)
        return self.rgm()

    def get_val(
        self, table_name: str, col_name: str, selection_or_index: Union[str, int]
    ) -> Any:
        """Получение значения из таблицы"""
        try:
            table = self._rastr.Tables.Item(table_name)
            col = table.Cols.Item(col_name)

            if isinstance(selection_or_index, str):
                table.SetSel(selection_or_index)
                idx = table.FindNextSel(-1)
                # ИСПРАВЛЕНО: Преобразуем idx в int, если это строка
                if not isinstance(idx, int) and idx is not None:
                    try:
                        idx = int(idx)
                    except (ValueError, TypeError):
                        idx = -1

                if idx != -1:
                    # Пытаемся получить значение разными способами
                    try:
                        # Способ 1: Z(index) - свойство с индексом (как в рабочей версии)
                        return col.Z(idx)
                    except (AttributeError, TypeError):
                        try:
                            # Способ 2: прямое обращение через индекс
                            return col[idx]
                        except (AttributeError, TypeError, IndexError):
                            try:
                                # Способ 3: GetZ (с заглавной буквы)
                                return col.GetZ(idx)
                            except AttributeError:
                                try:
                                    # Способ 4: get_Z (маленькая буква)
                                    return col.get_Z(idx)
                                except AttributeError as e:
                                    raise AttributeError(
                                        f"Не удалось получить значение для колонки {col_name}[{idx}]: {e}"
                                    )
                return None
            else:
                # ИСПРАВЛЕНО: Преобразуем selection_or_index в int, если это строка
                if not isinstance(selection_or_index, int):
                    try:
                        selection_or_index = int(selection_or_index)
                    except (ValueError, TypeError) as e:
                        from utils.logger import logger

                        logger.error(
                            f"Некорректный тип индекса для {table_name}.{col_name}: {selection_or_index} (тип: {type(selection_or_index)}), ошибка: {e}"
                        )
                        raise TypeError(
                            f"Индекс должен быть int, получен {type(selection_or_index).__name__}: {selection_or_index}"
                        )

                # Проверяем, что индекс валиден
                table_size = table.Size
                if not isinstance(table_size, int):
                    try:
                        table_size = int(table_size)
                    except (ValueError, TypeError):
                        table_size = 0

                if selection_or_index < 0 or selection_or_index >= table_size:
                    raise IndexError(
                        f"Индекс {selection_or_index} вне диапазона таблицы {table_name} (размер: {table_size})"
                    )
                # Пытаемся получить значение разными способами
                try:
                    # Способ 1: Z(index) - свойство с индексом (как в рабочей версии)
                    return col.Z(selection_or_index)
                except (AttributeError, TypeError):
                    try:
                        # Способ 2: прямое обращение через индекс
                        return col[selection_or_index]
                    except (AttributeError, TypeError, IndexError):
                        try:
                            # Способ 3: GetZ (с заглавной буквы)
                            return col.GetZ(selection_or_index)
                        except AttributeError:
                            try:
                                # Способ 4: get_Z (маленькая буква)
                                return col.get_Z(selection_or_index)
                            except AttributeError as e:
                                raise AttributeError(
                                    f"Не удалось получить значение для колонки {col_name}[{selection_or_index}]: {e}"
                                )
        except Exception as e:
            from utils.logger import logger

            logger.error(
                f"Ошибка при получении значения из {table_name}.{col_name} (индекс/выборка: {selection_or_index}): {e}"
            )
            raise

    def set_val(
        self,
        table_name: str,
        col_name: str,
        index_or_selection: Union[int, str],
        value: Any,
    ) -> bool:
        """Установка значения в таблицу (поддерживает индекс или строку выборки, как в C#)"""
        try:
            from utils.logger import logger

            table = self._rastr.Tables.Item(table_name)
            col = table.Cols.Item(col_name)

            # ИСПРАВЛЕНО: Поддержка строки выборки (как в C# setVal с selection)
            if isinstance(index_or_selection, str):
                # Используем строку выборки
                table.SetSel(index_or_selection)
                idx = table.FindNextSel(-1)
                # ИСПРАВЛЕНО: Преобразуем idx в int, если это строка
                if not isinstance(idx, int) and idx is not None:
                    try:
                        idx = int(idx)
                    except (ValueError, TypeError):
                        idx = -1

                if idx != -1:
                    try:
                        col.SetZ(idx, value)
                        return True
                    except AttributeError:
                        try:
                            col.set_Z(idx, value)
                            return True
                        except AttributeError as e:
                            logger.error(
                                f"Не удалось установить значение для {table_name}.{col_name} (выборка: {index_or_selection}): {e}"
                            )
                            return False
                return False
            else:
                # Используем индекс
                index = index_or_selection
                # ИСПРАВЛЕНО: Преобразуем index в int, если это строка
                if not isinstance(index, int):
                    try:
                        index = int(index)
                    except (ValueError, TypeError) as e:
                        logger.error(
                            f"Некорректный тип индекса для {table_name}.{col_name}: {index} (тип: {type(index)}), ошибка: {e}"
                        )
                        raise TypeError(
                            f"Индекс должен быть int, получен {type(index).__name__}: {index}"
                        )

                # Проверяем, что индекс валиден
                table_size = table.Size
                if not isinstance(table_size, int):
                    try:
                        table_size = int(table_size)
                    except (ValueError, TypeError):
                        table_size = 0

                if index < 0 or index >= table_size:
                    raise IndexError(
                        f"Индекс {index} вне диапазона таблицы {table_name} (размер: {table_size})"
                    )

                try:
                    # Способ 1: SetZ(index, value) - метод (как в рабочей версии)
                    col.SetZ(index, value)
                except AttributeError:
                    try:
                        # Способ 2: прямое присваивание через индекс
                        col[index] = value
                    except (AttributeError, TypeError, IndexError):
                        try:
                            # Способ 3: set_Z (маленькая буква)
                            col.set_Z(index, value)
                        except AttributeError as e:
                            raise AttributeError(
                                f"Не удалось установить значение для колонки {col_name}[{index}] = {value}: {e}"
                            )
                return True
        except Exception as e:
            from utils.logger import logger

            logger.error(
                f"Ошибка при установке значения в {table_name}.{col_name}[{index_or_selection}] = {value}: {e}"
            )
            raise

    def set_val_by_selection(
        self, table_name: str, col_name: str, selection: str, value: Any
    ) -> bool:
        """Установка значения по условию выборки"""
        try:
            from utils.logger import logger

            table = self._rastr.Tables.Item(table_name)
            col = table.Cols.Item(col_name)
            table.SetSel(selection)
            idx = table.FindNextSel(-1)

            # ИСПРАВЛЕНО: Преобразуем idx в int, если это строка
            if not isinstance(idx, int) and idx is not None:
                try:
                    idx = int(idx)
                except (ValueError, TypeError):
                    idx = -1

            if idx != -1:
                col.SetZ(idx, value)
                return True
            return False
        except Exception as e:
            from utils.logger import logger

            logger.error(
                f"Ошибка при установке значения в {table_name}.{col_name} (выборка: {selection}) = {value}: {e}"
            )
            raise

    def create_scn_from_lpn(
        self, lpn_file: str, lpn: str, scn_file: str, save_file: str = ""
    ):
        """Создание сценария из LPN файла"""
        self.load_template(".vrn")
        self.load(lpn_file)

        table = self._rastr.Tables.Item("var_mer")
        col_num = table.Cols.Item("Num")
        col_type = table.Cols.Item("Type")

        table.AddRow()
        col_num.SetZ(0, 1)
        col_type.SetZ(0, 1)

        self._rastr.LAPNUSMZU("1" + lpn)
        self.add(scn_file)

        if save_file:
            self.save(save_file)

    def run_ut(self) -> float:
        """Запуск утяжеления и получение суммы коэффициентов"""
        from utils.logger import logger

        logger.info("run_ut: Начало выполнения утяжеления")
        try:
            logger.info("run_ut: Получение таблиц vetv и ut_common")
            table_vetv = self._rastr.Tables.Item("vetv")
            table_ut = self._rastr.Tables.Item("ut_common")
            col_sum_kfc = table_ut.Cols.Item("sum_kfc")
            logger.info("run_ut: Таблицы получены успешно")
        except Exception as e:
            logger.error(f"run_ut: Ошибка при получении таблиц: {e}")
            raise

        # step_ut("i") - инициализация
        # step_ut("z") - шаг утяжеления
        # AST_OK = 0
        logger.info("run_ut: Начало инициализации (step_ut('i'))")
        init_iteration = 0
        max_init_iterations = 1000  # Максимум итераций инициализации
        prev_result = None
        stagnation_count = 0

        while True:
            result = self._rastr.step_ut("i")
            if result != 0:
                logger.info(f"run_ut: Инициализация завершена, результат: {result}")
                break

            init_iteration += 1
            if init_iteration >= max_init_iterations:
                logger.warning(
                    f"run_ut: Достигнуто максимальное количество итераций инициализации ({max_init_iterations}), прерываем цикл"
                )
                break

            # Проверка на застой (если результат не меняется)
            if result == prev_result and init_iteration > 10:
                stagnation_count += 1
                if stagnation_count >= 10:
                    logger.warning(
                        f"run_ut: Обнаружен застой в инициализации (итерация {init_iteration}), прерываем цикл"
                    )
                    break
            else:
                stagnation_count = 0

            prev_result = result

            if init_iteration % 100 == 0:
                logger.debug(f"run_ut: Инициализация, итерация {init_iteration}")

        logger.info(f"run_ut: Инициализация завершена за {init_iteration} итераций")

        logger.info("run_ut: Начало шага утяжеления (step_ut('z'))")
        step_iteration = 0
        max_step_iterations = 1000  # Максимум итераций шага
        prev_step_result = None
        step_stagnation_count = 0

        while True:
            result = self._rastr.step_ut("z")
            if result != 0:
                logger.info(f"run_ut: Шаг утяжеления завершен, результат: {result}")
                break

            step_iteration += 1
            if step_iteration >= max_step_iterations:
                logger.warning(
                    f"run_ut: Достигнуто максимальное количество итераций шага ({max_step_iterations}), прерываем цикл"
                )
                break

            # Проверка на застой
            if result == prev_step_result and step_iteration > 10:
                step_stagnation_count += 1
                if step_stagnation_count >= 10:
                    logger.warning(
                        f"run_ut: Обнаружен застой в шаге утяжеления (итерация {step_iteration}), прерываем цикл"
                    )
                    break
            else:
                step_stagnation_count = 0

            prev_step_result = result

            if step_iteration % 100 == 0:
                logger.debug(f"run_ut: Шаг утяжеления, итерация {step_iteration}")

        logger.info(f"run_ut: Шаг утяжеления завершен за {step_iteration} итераций")

        logger.info("run_ut: Получение значения sum_kfc")
        # Используем Z(index) - свойство с индексом (как в рабочей версии)
        try:
            result = col_sum_kfc.Z(0)
            logger.info(f"run_ut: sum_kfc получен через Z(0): {result}")
            return result
        except (AttributeError, TypeError) as e:
            logger.debug(f"run_ut: Z(0) не сработал, пробуем [0]: {e}")
            try:
                result = col_sum_kfc[0]
                logger.info(f"run_ut: sum_kfc получен через [0]: {result}")
                return result
            except (AttributeError, TypeError, IndexError) as e2:
                logger.debug(f"run_ut: [0] не сработал, пробуем GetZ(0): {e2}")
                try:
                    result = col_sum_kfc.GetZ(0)
                    logger.info(f"run_ut: sum_kfc получен через GetZ(0): {result}")
                    return result
                except AttributeError as e3:
                    logger.debug(f"run_ut: GetZ(0) не сработал, пробуем get_Z(0): {e3}")
                    result = col_sum_kfc.get_Z(0)
                    logger.info(f"run_ut: sum_kfc получен через get_Z(0): {result}")
                    return result

    def step(self, step_value: float = 1.0, init: bool = True) -> float:
        """Выполнение шага утяжеления"""
        table_ut = self._rastr.Tables.Item("ut_common")
        col_sum_kfc = table_ut.Cols.Item("sum_kfc")
        col_kfc = table_ut.Cols.Item("kfc")

        if init:
            self._rastr.step_ut("i")

        col_kfc.SetZ(0, step_value)
        self._rastr.step_ut("z")

        # Используем Z(index) - свойство с индексом (как в рабочей версии)
        try:
            return col_sum_kfc.Z(0)
        except (AttributeError, TypeError):
            try:
                return col_sum_kfc[0]
            except (AttributeError, TypeError, IndexError):
                try:
                    return col_sum_kfc.GetZ(0)
                except AttributeError:
                    return col_sum_kfc.get_Z(0)

    def dyn_settings(self):
        """Настройка параметров динамики"""
        try:
            from utils.logger import logger

            # Пытаемся получить таблицу com_dynamics
            try:
                table = self._rastr.Tables.Item("com_dynamics")
            except Exception as e:
                # Если таблица не существует, загружаем шаблон .dfw
                logger.warning(
                    f"Таблица com_dynamics не найдена, загружаем шаблон .dfw: {e}"
                )
                try:
                    self.load_template(".dfw")
                    table = self._rastr.Tables.Item("com_dynamics")
                except Exception as e2:
                    logger.error(
                        f"Не удалось загрузить шаблон .dfw или получить таблицу com_dynamics: {e2}"
                    )
                    raise RuntimeError(
                        f"Таблица com_dynamics недоступна. Проверьте, что шаблон .dfw существует в директории шаблонов."
                    )

            # Проверяем, что таблица существует и имеет хотя бы одну строку
            table_size = table.Size
            if not isinstance(table_size, int):
                try:
                    table_size = int(table_size)
                except (ValueError, TypeError):
                    table_size = 0
            if table_size == 0:
                logger.warning("Таблица com_dynamics пуста, добавляем строку")
                table.AddRow()

            # Получаем колонки с проверкой существования
            try:
                col_max_result_files = table.Cols.Item("MaxResultFiles")
                col_snap_auto_load = table.Cols.Item("SnapAutoLoad")
                col_snap_max_count = table.Cols.Item("SnapMaxCount")
            except Exception as e:
                logger.error(f"Не удалось получить колонки таблицы com_dynamics: {e}")
                raise RuntimeError(
                    f"Колонки таблицы com_dynamics недоступны. Возможно, файл режима не загружен правильно."
                )

            # Устанавливаем значения с обработкой ошибок для каждой колонки отдельно
            try:
                col_max_result_files.SetZ(0, 1)
            except AttributeError:
                # Fallback на set_Z для совместимости
                col_max_result_files.set_Z(0, 1)
            except Exception as e:
                logger.error(f"Ошибка при установке MaxResultFiles: {e}")
                raise

            try:
                col_snap_auto_load.SetZ(0, 1)
            except AttributeError:
                # Fallback на set_Z для совместимости
                col_snap_auto_load.set_Z(0, 1)
            except Exception as e:
                logger.error(f"Ошибка при установке SnapAutoLoad: {e}")
                raise

            try:
                col_snap_max_count.SetZ(0, 1)
            except AttributeError:
                # Fallback на set_Z для совместимости
                col_snap_max_count.set_Z(0, 1)
            except Exception as e:
                logger.error(f"Ошибка при установке SnapMaxCount: {e}")
                raise

        except RuntimeError:
            # Пробрасываем RuntimeError как есть
            raise
        except Exception as e:
            from utils.logger import logger

            logger.error(f"Ошибка при настройке параметров динамики: {e}")
            raise RuntimeError(f"Не удалось настроить параметры динамики: {e}")

    def run_dynamic(self, ems: bool = False, max_time: float = -1.0) -> DynamicResult:
        """Запуск динамического расчета"""
        try:
            from utils.logger import logger

            result = DynamicResult()

            table = self._rastr.Tables.Item("com_dynamics")

            # Проверяем, что таблица существует и имеет хотя бы одну строку
            table_size = table.Size
            if not isinstance(table_size, int):
                try:
                    table_size = int(table_size)
                except (ValueError, TypeError):
                    table_size = 0
            if table_size == 0:
                logger.warning("Таблица com_dynamics пуста, добавляем строку")
                table.AddRow()

            col_tras = table.Cols.Item("Tras")
            # Используем Z(index) - свойство с индексом (как в рабочей версии)
            try:
                original_time = col_tras.Z(0)
            except (AttributeError, TypeError):
                try:
                    original_time = col_tras[0]
                except (AttributeError, TypeError, IndexError):
                    try:
                        original_time = col_tras.GetZ(0)
                    except AttributeError:
                        original_time = col_tras.get_Z(0)

            self.load_template(".dfw")

            if ems and max_time != -1.0:
                col_tras.SetZ(0, max_time)

            fw_dynamic = self._rastr.FWDynamic()

            # SYNC_LOSS_NONE = 0
            if ems:
                ret_code = fw_dynamic.RunEMSmode()
            else:
                ret_code = fw_dynamic.Run()

            result.is_success = ret_code == 0
            result.is_stable = fw_dynamic.SyncLossCause == 0  # SYNC_LOSS_NONE
            result.result_message = (
                fw_dynamic.ResultMessage if fw_dynamic.ResultMessage else " - "
            )
            result.time_reached = fw_dynamic.TimeReached

            # Восстанавливаем исходное время
            try:
                col_tras.SetZ(0, original_time)
            except Exception as e:
                logger.warning(f"Не удалось восстановить исходное время Tras: {e}")

            return result
        except Exception as e:
            from utils.logger import logger

            logger.error(f"Ошибка при выполнении динамического расчета: {e}")
            raise

    def find_crt_time(self, precision: float, max_time: float) -> float:
        """Поиск критического времени отключения КЗ"""
        crt_time = max_time
        self.load_template(".dfw")

        self._reset_crt_time(max_time)

        fw_dynamic = self._rastr.FWDynamic()
        ret_code = fw_dynamic.RunEMSmode()

        # SYNC_LOSS_NONE = 0
        if fw_dynamic.SyncLossCause != 0:
            time_max = max_time
            time_min = 0.0
            time_step = (time_max - time_min) * 0.5

            while abs(time_step) > precision or fw_dynamic.SyncLossCause != 0:
                crt_time += time_step * (1 if fw_dynamic.SyncLossCause == 0 else -1)
                self._reset_crt_time(crt_time)

                fw_dynamic = self._rastr.FWDynamic()
                ret_code = fw_dynamic.RunEMSmode()

                if fw_dynamic.SyncLossCause == 0:
                    time_min = crt_time
                else:
                    time_max = crt_time

                time_step = (time_max - time_min) * 0.5

        return crt_time

    def _reset_crt_time(self, dt: float):
        """Сброс времени КЗ для расчета критического времени"""
        time_start = 1.0
        items = self.selection("DFWAutoActionScn")

        for item in items:
            obj_class = self.get_val("DFWAutoActionScn", "ObjectClass", item)

            if obj_class == "node":
                self.set_val("DFWAutoActionScn", "TimeStart", item, time_start)
                self.set_val("DFWAutoActionScn", "DT", item, dt)
            elif obj_class == "vetv":
                self.set_val("DFWAutoActionScn", "TimeStart", item, time_start + dt)
                self.set_val("DFWAutoActionScn", "DT", item, 999)

        self.set_val("com_dynamics", "Tras", 0, time_start + dt + 3.0)

    def find_shunt_kz(
        self, node: int, u_ost: float, x_isx: float, r_isx: float = -1.0
    ) -> ShuntKZResult:
        """Поиск шунта КЗ для заданного остаточного напряжения"""
        table = self._rastr.Tables.Item("com_dynamics")
        col_tras = table.Cols.Item("Tras")
        col_tras.SetZ(0, 1.1)

        self.load_template(".dfw")

        # Логирование результатов
        prot = []

        def on_log_handler(
            code, level, stage_id, table_name, table_index, description, form_name
        ):
            # code == 0 соответствует LogErrorCodes.LOG_INFO в исходном C# коде
            if code == 0 and "Величина остаточного напряжения в узле" in description:
                prot.append(description)

        # Подключение обработчика событий через COM события
        # В исходном C# коде используется AddEventHandler для подключения OnLog события
        try:
            # Подключаем обработчик событий OnLog
            # RASTR COM объект должен поддерживать события _IRastrEvents_Event
            if hasattr(self._rastr, "OnLog"):
                # Если событие доступно напрямую
                self._rastr.OnLog += on_log_handler
                event_connected = True
            else:
                # Альтернативный способ через win32com события
                from win32com.client import WithEvents

                # Попытка подключения через WithEvents (может не работать для всех COM объектов)
                event_connected = False
        except Exception as e:
            from utils.logger import logger

            logger.warning(
                f"Не удалось подключить обработчик событий OnLog: {e}. Используется альтернативный метод."
            )
            event_connected = False

        z_mod = math.sqrt((r_isx**2 if r_isx != -1.0 else 0) + x_isx**2)
        z_angle = (math.pi / 2.0) if r_isx == -1.0 else math.atan(x_isx / r_isx)

        if r_isx == -1.0:
            self._create_shunt_scn(node, z_mod * math.sin(z_angle))
        else:
            self._create_shunt_scn(
                node, z_mod * math.sin(z_angle), z_mod * math.cos(z_angle)
            )

        fw_dynamic = self._rastr.FWDynamic()
        ret_code = fw_dynamic.Run()

        # Парсинг результата из протокола
        if prot:
            last_msg = prot[-1]
            # Извлечение напряжения из сообщения
            # Формат: "Величина остаточного напряжения в узле ... (Uкз=XXX кВ, ...)"
            try:
                u_kz_str = (
                    last_msg.split("Uкз=")[1]
                    .split(" кВ")[0]
                    .replace(".", locale.localeconv()["decimal_point"])
                )
                u_current = float(u_kz_str)
            except:
                u_current = 0.0
        else:
            u_current = 0.0

        u_nom = self.get_val("node", "uhom", f"ny={node}")
        precision = min(2.0, 0.02 * u_nom)

        while abs(u_current - u_ost) > precision:
            z_mod = z_mod * u_ost / u_current if u_current > 0 else z_mod

            if r_isx == -1.0:
                self._create_shunt_scn(node, z_mod * math.sin(z_angle))
            else:
                self._create_shunt_scn(
                    node, z_mod * math.sin(z_angle), z_mod * math.cos(z_angle)
                )

            fw_dynamic = self._rastr.FWDynamic()
            ret_code = fw_dynamic.Run()

            # ИСПРАВЛЕНО: Сначала извлекаем значение, потом очищаем протокол (как в исходном C# коде)
            if prot:
                last_msg = prot[-1]
                try:
                    u_kz_str = (
                        last_msg.split("Uкз=")[1]
                        .split(" кВ")[0]
                        .replace(".", locale.localeconv()["decimal_point"])
                    )
                    u_current = float(u_kz_str)
                except:
                    break
            else:
                # Если протокол пустой, прерываем цикл
                break

            # Очистка протокола ПОСЛЕ извлечения значения (как в исходном C# коде, строка 339)
            prot.clear()

        return ShuntKZResult(
            r=(-1.0 if r_isx == -1.0 else z_mod * math.cos(z_angle)),
            x=z_mod * math.sin(z_angle),
            u=u_current,
        )

    def _create_shunt_scn(self, node: int, x: float, r: float = -1.0):
        """Создание сценария с шунтом КЗ"""
        self.load_template(".scn")

        table = self._rastr.Tables.Item("DFWAutoActionScn")
        col_id = table.Cols.Item("Id")
        col_type = table.Cols.Item("Type")
        col_formula = table.Cols.Item("Formula")
        col_obj_class = table.Cols.Item("ObjectClass")
        col_obj_prop = table.Cols.Item("ObjectProp")
        col_obj_key = table.Cols.Item("ObjectKey")
        col_runs_count = table.Cols.Item("RunsCount")
        col_time_start = table.Cols.Item("TimeStart")
        col_dt = table.Cols.Item("DT")

        # Добавление строки для X
        table.AddRow()
        # ИСПРАВЛЕНО: Преобразуем table.Size в int
        table_size = table.Size
        if not isinstance(table_size, int):
            try:
                table_size = int(table_size)
            except (ValueError, TypeError):
                table_size = 0
        row_idx = table_size - 1
        col_id.SetZ(row_idx, table_size)
        col_type.SetZ(row_idx, 1)
        col_formula.SetZ(row_idx, str(x).replace(",", "."))
        col_obj_class.SetZ(row_idx, "node")
        col_obj_prop.SetZ(row_idx, "x")
        col_obj_key.SetZ(row_idx, node)
        col_runs_count.SetZ(row_idx, 1)
        col_time_start.SetZ(row_idx, 1)
        col_dt.SetZ(row_idx, 0.06)

        # Добавление строки для R (если задано)
        if r != -1.0:
            table.AddRow()
            # ИСПРАВЛЕНО: Преобразуем table.Size в int
            table_size = table.Size
            if not isinstance(table_size, int):
                try:
                    table_size = int(table_size)
                except (ValueError, TypeError):
                    table_size = 0
            row_idx = table_size - 1
            col_id.SetZ(row_idx, table_size)
            col_type.SetZ(row_idx, 1)
            col_formula.SetZ(row_idx, str(r).replace(",", "."))
            col_obj_class.SetZ(row_idx, "node")
            col_obj_prop.SetZ(row_idx, "r")
            col_obj_key.SetZ(row_idx, node)
            col_runs_count.SetZ(row_idx, 1)
            col_time_start.SetZ(row_idx, 1)
            col_dt.SetZ(row_idx, 0.06)

    def get_points_from_exit_file(
        self, table_name: str, col_name: str, selection: str
    ) -> List[Point]:
        """Получение точек из выходного файла для построения графика"""
        table = self._rastr.Tables.Item(table_name)
        table.SetSel(selection)

        points = []
        idx = table.FindNextSel(-1)

        # ИСПРАВЛЕНО: Преобразуем idx в int, если это строка
        if not isinstance(idx, int) and idx is not None:
            try:
                idx = int(idx)
            except (ValueError, TypeError):
                idx = -1

        if idx < 0:
            return points

        # Получение цепочки снимков
        graph_data = self._rastr.GetChainedGraphSnapshot(table_name, col_name, idx, 0)

        # graph_data - двумерный массив [time, value]
        for i in range(len(graph_data)):
            if len(graph_data[i]) >= 2:
                points.append(
                    Point(graph_data[i][1], graph_data[i][0])
                )  # X=time, Y=value

        return points
