"""
Расчет остаточного напряжения на шинах энергообъекта при КЗ на границе устойчивости
"""

import os
import math
import locale
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Callable
from models import (
    RgmsInfo,
    ScnsInfo,
    VrnInfo,
    KprInfo,
    UostResults,
    UostShems,
    UostEvents,
    Values,
)
from rastr_operations import RastrOperations, DynamicResult
from utils.exceptions import InitialDataException


class UostStabilityCalc:
    """Расчет остаточного напряжения при КЗ на границе устойчивости"""

    def __init__(
        self,
        progress_callback: Optional[Callable[[int], None]],
        rgms: List[RgmsInfo],
        scns: List[ScnsInfo],
        vrns: List[VrnInfo],
        rems_path: Optional[str],
        kprs: List[KprInfo],
    ):
        """
        Инициализация расчета остаточного напряжения

        Args:
            progress_callback: Функция обратного вызова для обновления прогресса
            rgms: Список расчетных режимов
            scns: Список аварийных процессов
            vrns: Список вариантов (ремонтных схем)
            rems_path: Путь к файлу ремонтных схем
            kprs: Список контролируемых величин
        """
        if not rgms or not scns:
            error_msg = "Не заданы все исходные данные для определения остаточного напряжения!\n\n"
            error_msg += f"Результаты проверки:\n"
            error_msg += f"Загружено расчетных режимов - {len(rgms)}\n"
            error_msg += f"Загружено аварийных процесслов - {len(scns)}\n"
            raise InitialDataException(error_msg)

        self._progress_callback = progress_callback
        self._rgms = rgms
        self._scns = scns
        self._vrns = [v for v in vrns if not v.deactive]
        self._rems_path = rems_path
        self._kprs = kprs

        # Создание папки для результатов
        from utils.config import config

        results_dir = config.get_path("paths.results_dir")
        self._root = (
            results_dir
            / f"{datetime.now():%Y-%m-%d %H-%M-%S} Uост на границе устойчивости"
        )
        self._root.mkdir(parents=True, exist_ok=True)

    @property
    def root(self) -> str:
        """Путь к папке с результатами"""
        return str(self._root)

    @property
    def max(self) -> int:
        """Максимальное количество шагов расчета"""
        return (
            len(self._rgms)
            * len([v for v in self._vrns if not v.deactive])
            * len(self._scns)
            + 1
        )

    def calc(self) -> List[UostResults]:
        """Выполнение расчета"""
        from utils.logger import logger

        progress = 0
        results = []
        new_node_counter = 1  # ИСПРАВЛЕНО: Счетчик для новых узлов (как num2 в C#)

        logger.info(
            f"Начало расчета остаточного напряжения: {len(self._rgms)} режимов, {len(self._vrns)} вариантов, {len(self._scns)} сценариев"
        )

        for rgm_idx, rgm in enumerate(self._rgms):
            logger.info(
                f"[РЕЖИМ {rgm_idx + 1}/{len(self._rgms)}] Загрузка режима: {Path(rgm.name).stem}"
            )
            uost_shems_list = []
            # ИСПРАВЛЕНО: Сбрасываем счетчик для каждого режима (как в C# num2 инициализируется один раз)
            new_node_counter = 1

            for vrn_idx, vrn in enumerate(self._vrns):
                logger.info(
                    f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}/{len(self._vrns)}] Вариант: {vrn.name}"
                )
                events_list = []

                for scn_idx, scn in enumerate(self._scns):
                    logger.info(
                        f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}/{len(self._scns)}] Начало обработки сценария: {Path(scn.name).stem}"
                    )
                    rastr = RastrOperations()
                    rastr.load(rgm.name)
                    rastr.dyn_settings()

                    # Применение варианта
                    is_stable = (
                        rastr.rgm()
                        if vrn.id == -1
                        else rastr.apply_variant(vrn.num, self._rems_path)
                    )

                    if not is_stable:
                        logger.warning(
                            f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Режим неустойчив после применения варианта, пропуск"
                        )
                        continue

                    rastr.load(scn.name)
                    logger.debug(
                        f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Сценарий загружен"
                    )

                    # Извлечение информации о КЗ из сценария
                    distance = 100.0
                    line_key = ""
                    node_kz = 0
                    time_start = 0.0
                    r_shunt = -1.0
                    x_shunt = -1.0
                    r_id = 0
                    x_id = 0
                    # Инициализация параметров линии для вывода в Excel
                    begin_r = -1.0
                    begin_x = -1.0
                    end_r = -1.0
                    end_x = -1.0

                    actions = rastr.selection("DFWAutoActionScn")
                    logger.debug(
                        f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Найдено действий в сценарии: {len(actions)}"
                    )

                    if not actions:
                        logger.warning(
                            f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Сценарий не содержит действий (DFWAutoActionScn пуст), пропуск"
                        )
                        continue

                    for action_id in actions:
                        # ИСПРАВЛЕНО: Убеждаемся, что action_id - это int
                        if not isinstance(action_id, int):
                            try:
                                action_id = int(action_id)
                            except (ValueError, TypeError) as e:
                                from utils.logger import logger

                                logger.error(
                                    f"Некорректный тип action_id: {action_id} (тип: {type(action_id)}), ошибка: {e}"
                                )
                                continue

                        obj_class = rastr.get_val(
                            "DFWAutoActionScn", "ObjectClass", action_id
                        )

                        if obj_class == "vetv":
                            line_key = rastr.get_val(
                                "DFWAutoActionScn", "ObjectKey", action_id
                            )
                            rastr.set_val("DFWAutoActionScn", "State", action_id, 1)

                        if obj_class == "node":
                            try:
                                obj_key = rastr.get_val(
                                    "DFWAutoActionScn", "ObjectKey", action_id
                                )
                                # Преобразуем в int, если это строка
                                if isinstance(obj_key, str):
                                    node_kz = int(obj_key.strip())
                                else:
                                    node_kz = int(obj_key)
                            except (ValueError, TypeError) as e:
                                from utils.logger import logger

                                logger.error(
                                    f"Ошибка при получении node_kz из ObjectKey: {e}, значение: {rastr.get_val('DFWAutoActionScn', 'ObjectKey', action_id)}"
                                )
                                continue
                            time_start = rastr.get_val(
                                "DFWAutoActionScn", "TimeStart", action_id
                            )

                            # ИСПРАВЛЕНО: Изменяем ObjectKey на new_node_counter (как в C# строке 89)
                            rastr.set_val(
                                "DFWAutoActionScn",
                                "ObjectKey",
                                action_id,
                                new_node_counter,
                            )

                            obj_prop = rastr.get_val(
                                "DFWAutoActionScn", "ObjectProp", action_id
                            )
                            if obj_prop == "r":
                                r_shunt = float(
                                    str(
                                        rastr.get_val(
                                            "DFWAutoActionScn", "Formula", action_id
                                        )
                                    ).replace(".", locale.localeconv()["decimal_point"])
                                )
                                r_id = action_id
                            if obj_prop == "x":
                                x_shunt = float(
                                    str(
                                        rastr.get_val(
                                            "DFWAutoActionScn", "Formula", action_id
                                        )
                                    ).replace(".", locale.localeconv()["decimal_point"])
                                )
                                x_id = action_id

                    # Парсинг ключа линии
                    if not line_key:
                        logger.warning(
                            f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Ключ линии не найден в сценарии, пропуск"
                        )
                        continue

                    logger.debug(
                        f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Ключ линии: {line_key}, node_kz: {node_kz}"
                    )

                    line_parts = line_key.split(",")
                    if len(line_parts) >= 3:
                        try:
                            ip = int(line_parts[0].strip())
                            iq = int(line_parts[1].strip())
                            np = int(line_parts[2].strip())
                            logger.debug(
                                f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Параметры линии: ip={ip}, iq={iq}, np={np}"
                            )
                        except (ValueError, TypeError) as e:
                            logger.error(
                                f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Ошибка при парсинге ключа линии '{line_key}': {e}"
                            )
                            continue
                    else:
                        logger.warning(
                            f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Некорректный формат ключа линии '{line_key}' (ожидается 3 части через запятую), пропуск"
                        )
                        continue

                    # Получение параметров линии
                    # ИСПРАВЛЕНО: Используем формат с пробелами как в C# (строки 109-114)
                    logger.debug(
                        f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Получение параметров линии: ip={ip}, iq={iq}, np={np}"
                    )
                    try:
                        r_line = rastr.get_val(
                            "vetv", "r", f"ip = {ip} & iq = {iq} & np = {np}"
                        )
                        x_line = rastr.get_val(
                            "vetv", "x", f"ip = {ip} & iq = {iq} & np = {np}"
                        )
                        b_line = rastr.get_val(
                            "vetv", "b", f"ip = {ip} & iq = {iq} & np = {np}"
                        )
                        logger.debug(
                            f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Параметры линии получены: r={r_line}, x={x_line}, b={b_line}"
                        )
                    except Exception as e:
                        logger.error(
                            f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Ошибка при получении параметров линии: {e}"
                        )
                        continue

                    # Отключение исходной линии и добавление новой
                    # ИСПРАВЛЕНО: В C# используется setVal с selection (строка 112-114)
                    logger.debug(
                        f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Отключение линии и установка bsh"
                    )
                    try:
                        result1 = rastr.set_val(
                            "vetv", "sta", f"ip = {ip} & iq = {iq} & np = {np}", 1
                        )
                        result2 = rastr.set_val(
                            "node", "bsh", f"ny = {ip}", b_line / 2.0
                        )
                        result3 = rastr.set_val(
                            "node", "bsh", f"ny = {iq}", b_line / 2.0
                        )
                        logger.debug(
                            f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Результаты set_val: vetv.sta={result1}, node.bsh(ip)={result2}, node.bsh(iq)={result3}"
                        )
                        if not result1 or not result2 or not result3:
                            logger.warning(
                                f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Не удалось установить значения через set_val, пропуск"
                            )
                            continue
                    except Exception as e:
                        logger.error(
                            f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Ошибка при установке значений: {e}"
                        )
                        continue

                    # ИСПРАВЛЕНО: Создаем новый узел с номером new_node_counter (как в C# строке 115-117)
                    new_node_id = rastr.add_table_row("node")
                    rastr.set_val("node", "ny", new_node_id, new_node_counter)
                    rastr.set_val(
                        "node",
                        "uhom",
                        new_node_id,
                        rastr.get_val("node", "uhom", f"ny = {node_kz}"),
                    )

                    # Добавление новых ветвей
                    branch1_id = rastr.add_table_row("vetv")
                    branch2_id = rastr.add_table_row("vetv")

                    # ИСПРАВЛЕНО: Убеждаемся, что все ID - это int
                    if not isinstance(branch1_id, int):
                        branch1_id = int(branch1_id)
                    if not isinstance(branch2_id, int):
                        branch2_id = int(branch2_id)
                    if not isinstance(new_node_id, int):
                        new_node_id = int(new_node_id)

                    # ИСПРАВЛЕНО: Используем new_node_counter вместо new_node_id для ветвей (как в C# строках 120-123)
                    rastr.set_val("vetv", "ip", branch1_id, ip)
                    rastr.set_val("vetv", "iq", branch1_id, new_node_counter)
                    rastr.set_val("vetv", "ip", branch2_id, new_node_counter)
                    rastr.set_val("vetv", "iq", branch2_id, iq)

                    rastr.rgm()

                    # Расчет угла и модуля шунта
                    logger.info(
                        f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Расчет параметров шунта КЗ: r_shunt={r_shunt:.6f}, x_shunt={x_shunt:.6f}, r_id={r_id}, x_id={x_id}"
                    )
                    z_angle = (
                        (math.pi / 2.0)
                        if r_shunt == -1.0
                        else math.atan(x_shunt / r_shunt)
                    )
                    z_mod = math.sqrt(
                        (r_shunt**2 if r_shunt != -1.0 else 0) + x_shunt**2
                    )
                    logger.info(
                        f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Параметры шунта рассчитаны: z_angle={z_angle:.6f} рад ({math.degrees(z_angle):.2f}°), z_mod={z_mod:.6f} Ом"
                    )

                    # ДОБАВЛЕНО: Инициализация переменной для финального значения шунта
                    z_mod_final = z_mod  # Начальное значение

                    # Определение начальной позиции КЗ
                    # ИСПРАВЛЕНО: Убеждаемся, что оба значения - числа перед сравнением
                    ip_int = int(ip) if not isinstance(ip, int) else ip
                    node_kz_int = (
                        int(node_kz) if not isinstance(node_kz, int) else node_kz
                    )
                    l_start = 0.1 if ip_int == node_kz_int else 99.9
                    l_end = 100.0 - l_start

                    # Первый расчет
                    logger.info(
                        f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Начало первого динамического расчета (l_start={l_start:.2f})"
                    )
                    rastr.set_line_for_uost_calc(
                        branch1_id, branch2_id, r_line, x_line, l_start
                    )
                    dyn_result1 = rastr.run_dynamic(ems=True)
                    logger.info(
                        f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Первый расчет завершен: успех={dyn_result1.is_success}, устойчивость={dyn_result1.is_stable}"
                    )

                    # Второй расчет
                    logger.info(
                        f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Начало второго динамического расчета (l_end={l_end:.2f})"
                    )
                    rastr.set_line_for_uost_calc(
                        branch1_id, branch2_id, r_line, x_line, l_end
                    )
                    dyn_result2 = rastr.run_dynamic(ems=True)
                    logger.info(
                        f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Второй расчет завершен: успех={dyn_result2.is_success}, устойчивость={dyn_result2.is_stable}"
                    )

                    # Определение границы устойчивости
                    if (
                        dyn_result1.is_success
                        and dyn_result2.is_success
                        and (dyn_result1.is_stable != dyn_result2.is_stable)
                    ):
                        # Бинарный поиск границы
                        logger.info(
                            f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Начало бинарного поиска границы устойчивости"
                        )
                        logger.info(
                            f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Исходные значения: l_start={l_start:.2f} (устойчивость={dyn_result1.is_stable}), l_end={l_end:.2f} (устойчивость={dyn_result2.is_stable})"
                        )
                        logger.info(
                            f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Начальное значение шунта: z_mod={z_mod:.6f}, z_angle={z_angle:.6f}, r_shunt={r_shunt:.6f}, x_shunt={x_shunt:.6f}, r_id={r_id}, x_id={x_id}"
                        )

                        l_stable = l_start if dyn_result1.is_stable else l_end
                        l_unstable = l_end if dyn_result1.is_stable else l_start
                        # ИСПРАВЛЕНО: В C# используется Math.Abs(num17 - num18) * 0.5 (строка 133)
                        # Это половина разницы, а не среднее
                        l_current = abs(l_stable - l_unstable) * 0.5

                        logger.info(
                            f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Бинарный поиск: l_stable={l_stable:.2f}, l_unstable={l_unstable:.2f}, l_current={l_current:.2f}"
                        )

                        iteration = 0
                        max_iterations = 50
                        rastr.set_line_for_uost_calc(
                            branch1_id, branch2_id, r_line, x_line, l_current
                        )
                        dyn_result3 = rastr.run_dynamic(ems=True)
                        logger.info(
                            f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Бинарный поиск, итерация {iteration}: l_current={l_current:.2f}, устойчивость={dyn_result3.is_stable}"
                        )

                        while (
                            dyn_result3.is_success
                            and (
                                not dyn_result3.is_stable
                                or abs(l_stable - l_unstable) > 0.5
                            )
                            and iteration < max_iterations
                        ):
                            if dyn_result3.is_stable:
                                l_stable = l_current
                            else:
                                l_unstable = l_current

                            # ИСПРАВЛЕНО: Используем формулу из C# (строка 146)
                            # num19 += Math.Abs(num18 - num17) * 0.5 * (double)(((dynamicResult.IsStable && dynamicResult3.IsStable) || (!dynamicResult.IsStable && !dynamicResult3.IsStable)) ? 1 : (-1));
                            # Если знаки устойчивости совпадают (оба устойчивы ИЛИ оба неустойчивы), то добавляем, иначе вычитаем
                            sign_multiplier = (
                                1.0
                                if (
                                    (dyn_result1.is_stable and dyn_result3.is_stable)
                                    or (
                                        not dyn_result1.is_stable
                                        and not dyn_result3.is_stable
                                    )
                                )
                                else -1.0
                            )

                            l_current += (
                                abs(l_unstable - l_stable) * 0.5 * sign_multiplier
                            )
                            # Ограничиваем диапазоном 0-100
                            l_current = max(0.0, min(100.0, l_current))
                            distance = l_current

                            iteration += 1
                            logger.info(
                                f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Бинарный поиск, итерация {iteration}: l_stable={l_stable:.2f}, l_unstable={l_unstable:.2f}, l_current={l_current:.2f}, distance={distance:.2f}"
                            )

                            rastr.set_line_for_uost_calc(
                                branch1_id, branch2_id, r_line, x_line, l_current
                            )
                            dyn_result3 = rastr.run_dynamic(ems=True)
                            logger.info(
                                f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Бинарный поиск, итерация {iteration}: результат устойчивости={dyn_result3.is_stable}"
                            )

                        if iteration >= max_iterations:
                            logger.warning(
                                f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Достигнуто максимальное количество итераций бинарного поиска ({max_iterations})"
                            )

                        logger.info(
                            f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Бинарный поиск завершен: distance={distance:.2f}, l_stable={l_stable:.2f}, l_unstable={l_unstable:.2f}"
                        )

                        # ДОБАВЛЕНО: Извлекаем значения r и x для обеих ветвей после бинарного поиска
                        # Эти значения соответствуют найденным остаточным напряжениям
                        begin_r = -1.0
                        begin_x = -1.0
                        end_r = -1.0
                        end_x = -1.0
                        try:
                            # Получаем r и x для первой ветви (начало линии)
                            begin_r = rastr.get_val("vetv", "r", branch1_id)
                            begin_x = rastr.get_val("vetv", "x", branch1_id)
                            # Получаем r и x для второй ветви (конец линии)
                            end_r = rastr.get_val("vetv", "r", branch2_id)
                            end_x = rastr.get_val("vetv", "x", branch2_id)
                            logger.info(
                                f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Параметры линии после бинарного поиска: begin_r={begin_r:.6f}, begin_x={begin_x:.6f}, end_r={end_r:.6f}, end_x={end_x:.6f}"
                            )
                        except Exception as e:
                            logger.warning(
                                f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Не удалось получить параметры линии после бинарного поиска: {e}"
                            )

                        # ДОБАВЛЕНО: Извлекаем значение шунта после бинарного поиска границы
                        logger.info(
                            f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Извлечение значения шунта КЗ после бинарного поиска: x_id={x_id}, r_id={r_id}, r_shunt={r_shunt}"
                        )
                        begin_shunt = -1.0
                        end_shunt = -1.0
                        try:
                            if x_id > 0:
                                # Получаем значение X шунта из действия
                                x_shunt_value = rastr.get_val(
                                    "DFWAutoActionScn", "Formula", x_id
                                )
                                logger.info(
                                    f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Получено значение X шунта из RASTR: x_shunt_value={x_shunt_value} (тип: {type(x_shunt_value)})"
                                )
                                if r_shunt == -1.0:
                                    # Только X (реактивное сопротивление)
                                    begin_shunt = (
                                        float(x_shunt_value) if x_shunt_value else -1.0
                                    )
                                    end_shunt = (
                                        begin_shunt  # Одно значение для обоих узлов
                                    )
                                    logger.info(
                                        f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Шунт (только X): begin_shunt={begin_shunt:.6f}, end_shunt={end_shunt:.6f}"
                                    )
                                else:
                                    # X и R (полное сопротивление)
                                    if r_id > 0:
                                        r_shunt_value = rastr.get_val(
                                            "DFWAutoActionScn", "Formula", r_id
                                        )
                                        logger.info(
                                            f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Получено значение R шунта из RASTR: r_shunt_value={r_shunt_value} (тип: {type(r_shunt_value)})"
                                        )
                                        x_val = (
                                            float(x_shunt_value)
                                            if x_shunt_value
                                            else 0.0
                                        )
                                        r_val = (
                                            float(r_shunt_value)
                                            if r_shunt_value
                                            else 0.0
                                        )
                                        # Модуль комплексного сопротивления
                                        z_mod_from_rastr = math.sqrt(
                                            r_val**2 + x_val**2
                                        )
                                        begin_shunt = z_mod_from_rastr
                                        end_shunt = z_mod_from_rastr
                                        logger.info(
                                            f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Шунт (X и R): x_val={x_val:.6f}, r_val={r_val:.6f}, z_mod_from_rastr={z_mod_from_rastr:.6f}, begin_shunt={begin_shunt:.6f}, end_shunt={end_shunt:.6f}"
                                        )
                                    else:
                                        begin_shunt = (
                                            float(x_shunt_value)
                                            if x_shunt_value
                                            else -1.0
                                        )
                                        end_shunt = begin_shunt
                                        logger.info(
                                            f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Шунт (только X, r_id=0): begin_shunt={begin_shunt:.6f}, end_shunt={end_shunt:.6f}"
                                        )
                            else:
                                logger.warning(
                                    f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] x_id={x_id}, не удалось извлечь значение шунта (x_id <= 0)"
                                )
                        except Exception as e:
                            logger.warning(
                                f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Не удалось получить значение шунта из RASTR после бинарного поиска: {e}"
                            )
                            logger.info(
                                f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Используем начальное значение z_mod={z_mod:.6f} как fallback"
                            )
                            # Используем начальное значение
                            begin_shunt = z_mod
                            end_shunt = z_mod
                    elif (
                        dyn_result1.is_success
                        and not dyn_result1.is_stable
                        and dyn_result2.is_success
                        and not dyn_result2.is_stable
                    ):
                        # Оба неустойчивы - увеличиваем шунт
                        logger.info(
                            f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Оба расчета неустойчивы, начинаем увеличение шунта"
                        )
                        distance = -1.0
                        # ИСПРАВЛЕНО: Убеждаемся, что оба значения - числа перед сравнением
                        ip_int = int(ip) if not isinstance(ip, int) else ip
                        node_kz_int = (
                            int(node_kz) if not isinstance(node_kz, int) else node_kz
                        )
                        rastr.set_line_for_uost_calc(
                            branch1_id,
                            branch2_id,
                            r_line,
                            x_line,
                            (99.9 if ip_int == node_kz_int else 0.1),
                        )

                        z_mod_new = (z_mod * 2.0) if z_mod > 0.1 else 1.0
                        z_mod_old = z_mod

                        logger.info(
                            f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Начальные значения: z_mod={z_mod:.4f}, z_mod_new={z_mod_new:.4f}, z_mod_old={z_mod_old:.4f}"
                        )

                        if r_shunt == -1.0:
                            rastr.change_rx_for_uost_calc(
                                x_id, z_mod_new * math.sin(z_angle)
                            )
                        else:
                            rastr.change_rx_for_uost_calc(
                                x_id,
                                z_mod_new * math.sin(z_angle),
                                r_id,
                                z_mod_new * math.cos(z_angle),
                            )

                        dyn_result4 = rastr.run_dynamic(ems=True)
                        logger.info(
                            f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Первый расчет с увеличенным шунтом: успех={dyn_result4.is_success}, устойчивость={dyn_result4.is_stable}"
                        )

                        iteration1 = 0
                        max_iterations1 = 50  # Максимум итераций для первого цикла
                        while (
                            dyn_result4.is_success
                            and not dyn_result4.is_stable
                            and iteration1 < max_iterations1
                        ):
                            z_mod_old = z_mod_new
                            z_mod_new += z_mod if z_mod > 0.1 else 1.0

                            logger.info(
                                f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Итерация {iteration1 + 1}: z_mod_old={z_mod_old:.4f}, z_mod_new={z_mod_new:.4f}"
                            )

                            if r_shunt == -1.0:
                                rastr.change_rx_for_uost_calc(
                                    x_id, z_mod_new * math.sin(z_angle)
                                )
                            else:
                                rastr.change_rx_for_uost_calc(
                                    x_id,
                                    z_mod_new * math.sin(z_angle),
                                    r_id,
                                    z_mod_new * math.cos(z_angle),
                                )

                            dyn_result4 = rastr.run_dynamic(ems=True)
                            logger.info(
                                f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Итерация {iteration1 + 1}: результат: успех={dyn_result4.is_success}, устойчивость={dyn_result4.is_stable}"
                            )
                            iteration1 += 1

                        if iteration1 >= max_iterations1:
                            logger.warning(
                                f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Достигнуто максимальное количество итераций ({max_iterations1}) для увеличения шунта"
                            )

                        if not dyn_result4.is_success:
                            logger.warning(
                                f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Расчет динамики не успешен после увеличения шунта, пропуск уточнения"
                            )
                        else:
                            logger.info(
                                f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Начало уточнения границы устойчивости: z_mod_old={z_mod_old:.4f}, z_mod_new={z_mod_new:.4f}"
                            )

                            # Уточнение границы
                            iteration2 = 0
                            max_iterations2 = 100  # Максимум итераций для второго цикла
                            prev_z_mod_old = None
                            prev_z_mod_new = None
                            stagnation_count = 0

                            while (
                                dyn_result4.is_success
                                and (
                                    not dyn_result4.is_stable
                                    or (1.0 - z_mod_old / z_mod_new) > 0.025
                                )
                                and iteration2 < max_iterations2
                            ):
                                # ИСПРАВЛЕНО: Проверка на застой - если значения не меняются
                                if (
                                    prev_z_mod_old is not None
                                    and prev_z_mod_new is not None
                                ):
                                    if (
                                        abs(z_mod_old - prev_z_mod_old) < 0.0001
                                        and abs(z_mod_new - prev_z_mod_new) < 0.0001
                                    ):
                                        stagnation_count += 1
                                        if stagnation_count >= 5:
                                            logger.warning(
                                                f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Обнаружен застой в уточнении границы (значения не меняются), прерываем цикл"
                                            )
                                            break
                                    else:
                                        stagnation_count = 0

                                prev_z_mod_old = z_mod_old
                                prev_z_mod_new = z_mod_new

                                # ИСПРАВЛЕНО: Проверка на равенство значений (как в C# - если num21 == num20, то num22 = 0)
                                if abs(z_mod_old - z_mod_new) < 0.0001:
                                    logger.warning(
                                        f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] z_mod_old и z_mod_new стали одинаковыми ({z_mod_old:.4f}), прерываем цикл уточнения"
                                    )
                                    break

                                z_step = (
                                    (z_mod_old - z_mod_new) * 0.5
                                    if dyn_result4.is_stable
                                    else (z_mod_new - z_mod_old) * 0.5
                                )
                                z_current = z_mod_new + z_step

                                logger.debug(
                                    f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Уточнение, итерация {iteration2 + 1}: z_step={z_step:.4f}, z_current={z_current:.4f}"
                                )

                                if r_shunt == -1.0:
                                    rastr.change_rx_for_uost_calc(
                                        x_id, z_current * math.sin(z_angle)
                                    )
                                else:
                                    rastr.change_rx_for_uost_calc(
                                        x_id,
                                        z_current * math.sin(z_angle),
                                        r_id,
                                        z_current * math.cos(z_angle),
                                    )

                                dyn_result4 = rastr.run_dynamic(ems=True)

                                if dyn_result4.is_stable:
                                    z_mod_new = z_current
                                else:
                                    z_mod_old = z_current

                                iteration2 += 1

                                # Логирование каждые 10 итераций
                                if iteration2 % 10 == 0:
                                    logger.info(
                                        f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Уточнение, итерация {iteration2}: z_mod_old={z_mod_old:.4f}, z_mod_new={z_mod_new:.4f}, устойчивость={dyn_result4.is_stable}, разница={abs(z_mod_old - z_mod_new):.4f}"
                                    )

                            if iteration2 >= max_iterations2:
                                logger.warning(
                                    f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Достигнуто максимальное количество итераций ({max_iterations2}) для уточнения границы"
                                )

                            logger.info(
                                f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Уточнение завершено: z_mod_old={z_mod_old:.4f}, z_mod_new={z_mod_new:.4f}, устойчивость={dyn_result4.is_stable}, итераций={iteration2}"
                            )

                            # ИСПРАВЛЕНО: Сохраняем финальное значение шунта в момент нахождения на границе устойчивости
                            z_mod_final = z_mod_new

                            # ДОБАВЛЕНО: Извлекаем значения r и x для обеих ветвей после уточнения границы
                            begin_r = -1.0
                            begin_x = -1.0
                            end_r = -1.0
                            end_x = -1.0
                            try:
                                # Получаем r и x для первой ветви (начало линии)
                                begin_r = rastr.get_val("vetv", "r", branch1_id)
                                begin_x = rastr.get_val("vetv", "x", branch1_id)
                                # Получаем r и x для второй ветви (конец линии)
                                end_r = rastr.get_val("vetv", "r", branch2_id)
                                end_x = rastr.get_val("vetv", "x", branch2_id)
                                logger.info(
                                    f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Параметры линии после уточнения: begin_r={begin_r:.6f}, begin_x={begin_x:.6f}, end_r={end_r:.6f}, end_x={end_x:.6f}"
                                )
                            except Exception as e:
                                logger.warning(
                                    f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Не удалось получить параметры линии после уточнения: {e}"
                                )

                            # ИСПРАВЛЕНО: Извлекаем значение шунта из RASTR в момент нахождения на границе устойчивости
                            logger.info(
                                f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Извлечение значения шунта КЗ после уточнения границы: x_id={x_id}, r_id={r_id}, r_shunt={r_shunt}, z_mod_final={z_mod_final:.6f}"
                            )
                            begin_shunt = -1.0
                            end_shunt = -1.0
                            try:
                                if x_id > 0:
                                    # Получаем значение X шунта из действия
                                    x_shunt_value = rastr.get_val(
                                        "DFWAutoActionScn", "Formula", x_id
                                    )
                                    logger.info(
                                        f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Получено значение X шунта из RASTR после уточнения: x_shunt_value={x_shunt_value} (тип: {type(x_shunt_value)})"
                                    )
                                    if r_shunt == -1.0:
                                        # Только X (реактивное сопротивление)
                                        begin_shunt = (
                                            float(x_shunt_value)
                                            if x_shunt_value
                                            else -1.0
                                        )
                                        end_shunt = (
                                            begin_shunt  # Одно значение для обоих узлов
                                        )
                                        logger.info(
                                            f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Шунт после уточнения (только X): begin_shunt={begin_shunt:.6f}, end_shunt={end_shunt:.6f}"
                                        )
                                    else:
                                        # X и R (полное сопротивление)
                                        if r_id > 0:
                                            r_shunt_value = rastr.get_val(
                                                "DFWAutoActionScn", "Formula", r_id
                                            )
                                            logger.info(
                                                f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Получено значение R шунта из RASTR после уточнения: r_shunt_value={r_shunt_value} (тип: {type(r_shunt_value)})"
                                            )
                                            x_val = (
                                                float(x_shunt_value)
                                                if x_shunt_value
                                                else 0.0
                                            )
                                            r_val = (
                                                float(r_shunt_value)
                                                if r_shunt_value
                                                else 0.0
                                            )
                                            # Модуль комплексного сопротивления
                                            z_mod_from_rastr = math.sqrt(
                                                r_val**2 + x_val**2
                                            )
                                            begin_shunt = z_mod_from_rastr
                                            end_shunt = z_mod_from_rastr
                                            logger.info(
                                                f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Шунт после уточнения (X и R): x_val={x_val:.6f}, r_val={r_val:.6f}, z_mod_from_rastr={z_mod_from_rastr:.6f}, begin_shunt={begin_shunt:.6f}, end_shunt={end_shunt:.6f}"
                                            )
                                        else:
                                            begin_shunt = (
                                                float(x_shunt_value)
                                                if x_shunt_value
                                                else -1.0
                                            )
                                            end_shunt = begin_shunt
                                            logger.info(
                                                f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Шунт после уточнения (только X, r_id=0): begin_shunt={begin_shunt:.6f}, end_shunt={end_shunt:.6f}"
                                            )
                                else:
                                    logger.warning(
                                        f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] x_id={x_id}, не удалось извлечь значение шунта после уточнения (x_id <= 0)"
                                    )
                            except Exception as e:
                                logger.warning(
                                    f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Не удалось получить значение шунта из RASTR после уточнения: {e}"
                                )
                                logger.info(
                                    f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Используем z_mod_final={z_mod_final:.6f} как fallback"
                                )
                                # Используем z_mod_final как резервное значение
                                begin_shunt = z_mod_final
                                end_shunt = z_mod_final

                            # ИСПРАВЛЕНО: Если система все еще неустойчива после всех итераций, продолжаем расчет с текущими значениями
                            if not dyn_result4.is_success:
                                logger.warning(
                                    f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Расчет динамики не успешен после уточнения, продолжаем с distance=-1.0"
                                )
                            elif not dyn_result4.is_stable:
                                logger.warning(
                                    f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Система все еще неустойчива после уточнения, продолжаем расчет"
                                )
                    else:
                        # Если не было уточнения границы (оба расчета были устойчивы или неустойчивы с самого начала)
                        logger.info(
                            f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Не было бинарного поиска или уточнения границы. Используем начальное значение шунта: z_mod={z_mod:.6f}"
                        )
                        begin_shunt = z_mod
                        end_shunt = z_mod
                        # Получаем текущие значения r и x для обеих ветвей
                        try:
                            begin_r = rastr.get_val("vetv", "r", branch1_id)
                            begin_x = rastr.get_val("vetv", "x", branch1_id)
                            end_r = rastr.get_val("vetv", "r", branch2_id)
                            end_x = rastr.get_val("vetv", "x", branch2_id)
                            logger.info(
                                f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Параметры линии (без бинарного поиска): begin_r={begin_r:.6f}, begin_x={begin_x:.6f}, end_r={end_r:.6f}, end_x={end_x:.6f}"
                            )
                        except Exception as e:
                            logger.warning(
                                f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Не удалось получить параметры линии: {e}"
                            )

                    # Получение остаточных напряжений
                    logger.info(
                        f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Начало получения остаточных напряжений: time_start={time_start:.6f}, ip={ip}, iq={iq}"
                    )
                    begin_uost = -1.0
                    end_uost = -1.0

                    logger.info(
                        f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Запуск финального динамического расчета для получения остаточных напряжений (ems=False, max_time={time_start + 0.02:.6f})"
                    )
                    dyn_result5 = rastr.run_dynamic(
                        ems=False, max_time=time_start + 0.02
                    )
                    logger.info(
                        f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Финальный расчет завершен: успех={dyn_result5.is_success}, устойчивость={dyn_result5.is_stable}"
                    )

                    if dyn_result5.is_success and dyn_result5.is_stable:
                        # ИСПРАВЛЕНО: Используем формат с пробелами и точное сравнение (как в C# строках 210-215)
                        logger.info(
                            f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Извлечение точек из exit файла для узлов ip={ip} и iq={iq}"
                        )
                        points_ip = rastr.get_points_from_exit_file(
                            "node", "vras", f"ny = {ip}"
                        )
                        points_iq = rastr.get_points_from_exit_file(
                            "node", "vras", f"ny = {iq}"
                        )
                        logger.info(
                            f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Получено точек для ip: {len(points_ip)}, для iq: {len(points_iq)}"
                        )

                        # ИСПРАВЛЕНО: Точное сравнение как в C# (k.X == time_start)
                        for point in points_ip:
                            if point.x == time_start:
                                begin_uost = point.y
                                logger.info(
                                    f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Найдено остаточное напряжение для узла ip={ip}: begin_uost={begin_uost:.2f} (время={point.x:.6f})"
                                )
                                break

                        for point in points_iq:
                            if point.x == time_start:
                                end_uost = point.y
                                logger.info(
                                    f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Найдено остаточное напряжение для узла iq={iq}: end_uost={end_uost:.2f} (время={point.x:.6f})"
                                )
                                break

                        if begin_uost == -1.0:
                            logger.warning(
                                f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Не найдено остаточное напряжение для узла ip={ip} в момент времени {time_start:.6f}"
                            )
                        if end_uost == -1.0:
                            logger.warning(
                                f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Не найдено остаточное напряжение для узла iq={iq} в момент времени {time_start:.6f}"
                            )
                    else:
                        logger.warning(
                            f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Финальный расчет не успешен или неустойчив, остаточные напряжения не получены"
                        )

                    # Сбор контролируемых величин
                    values_list = []
                    for kpr in self._kprs:
                        values_list.append(
                            Values(
                                id=kpr.id,
                                name=kpr.name,
                                value=rastr.get_val(kpr.table, kpr.col, kpr.selection),
                            )
                        )

                    logger.info(
                        f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}, СЦЕНАРИЙ {scn_idx + 1}] Расчет завершен: distance={distance:.2f}, begin_uost={begin_uost:.2f}, end_uost={end_uost:.2f}, begin_shunt={begin_shunt:.4f}, end_shunt={end_shunt:.4f}"
                    )

                    events_list.append(
                        UostEvents(
                            name=Path(scn.name).stem,
                            begin_node=ip,
                            end_node=iq,
                            np=np,
                            distance=distance,
                            begin_uost=begin_uost,
                            end_uost=end_uost,
                            begin_shunt=begin_shunt,
                            end_shunt=end_shunt,
                            begin_r=begin_r,
                            begin_x=begin_x,
                            end_r=end_r,
                            end_x=end_x,
                            values=values_list,
                        )
                    )

                    progress += 1
                    if self._progress_callback:
                        self._progress_callback(progress)

                    # ИСПРАВЛЕНО: Увеличиваем счетчик для следующего сценария (как num2 в C#)
                    new_node_counter += 1

                logger.info(
                    f"[РЕЖИМ {rgm_idx + 1}, ВАРИАНТ {vrn_idx + 1}] Обработано событий: {len(events_list)}"
                )

                uost_shems_list.append(
                    UostShems(
                        sheme_name=vrn.name, is_stable=is_stable, events=events_list
                    )
                )

            logger.info(
                f"[РЕЖИМ {rgm_idx + 1}] Обработано вариантов: {len(uost_shems_list)}"
            )

            results.append(
                UostResults(rg_name=Path(rgm.name).stem, uost_shems=uost_shems_list)
            )

        logger.info(
            f"Расчет остаточного напряжения завершен. Всего результатов: {len(results)}"
        )
        return results
