class Atm: # Класс, описывающий банкомат

    def __init__(self, atm_id: int, lat: float, lon: float,
                 capacity_in: int, capacity_out: int,
                 mean_in: float = 0, std_in: float = 0,
                 mean_out: float = 0, std_out: float = 0):
        """
        Конструктор класса — вызывается при создании объекта банкомата.

        :param atm_id: уникальный идентификатор банкомата
        :param lat: широта (географическая координата)
        :param lon: долгота (географическая координата)
        :param capacity_in: максимальная вместимость бункера приёма
        :param capacity_out: максимальная вместимость бункера выдачи
        :param mean_in: среднее количество внесённых купюр в час
        :param std_in: отклонение внесений (разброс)
        :param mean_out: среднее количество снятых купюр в час
        :param std_out: отклонение снятий
        """

        # Проверяем, что ёмкости бункеров заданы корректно
        # Они не могут быть нулевыми или отрицательными
        if capacity_in <= 0 or capacity_out <= 0:
            raise ValueError("Ёмкости бункеров должны быть больше 0")

        # БАЗОВЫЕ ПАРАМЕТРЫ
        # Сохраняем переданные значения в объект (self — текущий объект)
        self.id = atm_id              # уникальный номер банкомата
        self.lat = lat                # широта ( для расчета расстояний)
        self.lon = lon                # долгота (для расчета расстояний)
        self.capacity_in = capacity_in    # максимальная вместимость бункера приема денег
        self.capacity_out = capacity_out  # максимальная вместимость бункера выдачи денег


        # ТЕКУЩЕЕ СОСТОЯНИЕ БАНКОМАТА
        # сколько уже накопилось в бункере приема
        self.current_in = 0

        # сколько осталось в бункере выдачи (начинаем с полного)
        self.current_out = capacity_out

        # СТАТИСТИКА
        self.mean_in = mean_in
        self.std_in = std_in
        self.mean_out = mean_out
        self.std_out = std_out

    def needs_service(self) -> bool:
        """
        Проверяет, нужен ли банкомату инкассатор.
        Условия:
        - если бункер приема заполнен более чем на 90%
        - если бункер выдачи опустел ниже 10%

        :return: True — нужен, False — не нужен
        """
        # Если бункер приёма переполнен (>= 90%)
        if self.current_in >= self.capacity_in * 0.9:
            return True

        # Если бункер выдачи почти пуст (<= 10%)
        if self.current_out <= self.capacity_out * 0.1:
            return True

        # Иначе всё хорошо
        return False

    def __repr__(self):
        """Читаемый вид объекта для логов и отладки."""
        return (f"Atm(id={self.id}, lat={self.lat:.4f}, lon={self.lon:.4f}, "
                f"cap_in={self.capacity_in}, cap_out={self.capacity_out})")

    def predict_level_after_hours(self, hours: float) -> tuple:
        """
        Прогнозирует уровень бункеров через заданное количество часов.

        Формула: текущий_уровень + (среднее × часы) ± 2 сигмы.
        Используем ± 2 сигмы для 95% доверительного интервала.

        :param hours: через сколько часов делаем прогноз
        :return: (предполагаемый_уровень_приема, предполагаемый_уровень_выдачи)
        """
        import math

        # Сколько купюр в среднем внесут за это время
        total_in_mean = self.mean_in * hours
        # Плюс "запас" на разброс (2 стандартных отклонения)
        total_in_worst = total_in_mean + 2 * self.std_in * math.sqrt(hours)

        # Сколько купюр в среднем снимут за это время
        total_out_mean = self.mean_out * hours
        # Худший случай для выдачи
        total_out_worst = total_out_mean + 2 * self.std_out * math.sqrt(hours)

        # Прогнозируемые уровни
        predicted_in = self.current_in + total_in_worst
        predicted_out = self.current_out - total_out_worst

        return predicted_in, predicted_out

    def is_critical(self, hours_ahead: float = 24) -> tuple:
        """
        Определяет статус критичности банкомата.

        :param hours_ahead: на сколько часов вперёд делаем прогноз (по умолчанию 24)
        :return: (is_critical: bool, status: str)
                 status может быть:
                 - "RED_IN_OVERFLOW" — бункер приёма переполнится (>90%)
                 - "RED_OUT_EMPTY" — бункер выдачи опустеет (<10%)
                 - "YELLOW" — внимание (приём >70% или выдача <30%)
                 - "GREEN" — всё в норме
        """
        pred_in, pred_out = self.predict_level_after_hours(hours_ahead)

        # Процент заполненности бункера приёма
        in_pct = (pred_in / self.capacity_in) * 100 if self.capacity_in > 0 else 0

        # Процент заполненности бункера выдачи
        out_pct = (pred_out / self.capacity_out) * 100 if self.capacity_out > 0 else 100

        # Проверяем критические состояния
        if in_pct > 90:
            return True, "RED_IN_OVERFLOW"
        if out_pct < 10:
            return True, "RED_OUT_EMPTY"
        if in_pct > 70 or out_pct < 30:
            return True, "YELLOW"

        return False, "GREEN"

    # ============================================================
    # НОВЫЕ МЕТОДЫ ДЛЯ СПРИНТА 3
    # ============================================================

    def predict_inflow(self, hours: float) -> float:
        """
        Прогноз поступлений в бункер приёма через N часов.

        Формула: текущий_уровень + среднее_поступлений × часы + 2σ√часы

        :param hours: через сколько часов делаем прогноз
        :return: прогнозируемый уровень бункера приёма
        """
        import math
        total_in_mean = self.mean_in * hours
        total_in_worst = total_in_mean + 2 * self.std_in * math.sqrt(hours)
        return self.current_in + total_in_worst

    def predict_outflow(self, hours: float) -> float:
        """
        Прогноз выдач из бункера выдачи через N часов.

        Формула: текущий_уровень - (среднее_снятий × часы + 2σ√часы)

        :param hours: через сколько часов делаем прогноз
        :return: прогнозируемый остаток в бункере выдачи
        """
        import math
        total_out_mean = self.mean_out * hours
        total_out_worst = total_out_mean + 2 * self.std_out * math.sqrt(hours)
        return self.current_out - total_out_worst

    def get_risk_level(self, hours_ahead: float = 24) -> str:
        """
        Определяет уровень риска банкомата.

        :param hours_ahead: на сколько часов вперёд прогноз
        :return: "RED" — критично (>90% приёма или <10% выдачи)
                 "YELLOW" — внимание (>70% приёма или <30% выдачи)
                 "GREEN" — норма
        """
        pred_in = self.predict_inflow(hours_ahead)
        pred_out = self.predict_outflow(hours_ahead)

        in_pct = (pred_in / self.capacity_in) * 100 if self.capacity_in > 0 else 0
        out_pct = (pred_out / self.capacity_out) * 100 if self.capacity_out > 0 else 100

        if in_pct > 90 or out_pct < 10:
            return "RED"
        if in_pct > 70 or out_pct < 30:
            return "YELLOW"
        return "GREEN"

    def update_levels(self, hours_passed: float):
        """
        Обновляет текущие уровни бункеров после прошедшего времени.
        Вызывается в конце каждого дня для пересчёта перед следующим днём.

        :param hours_passed: сколько часов прошло (обычно 24)
        """
        import math
        # Обновляем бункер приёма (люди внесли деньги)
        total_in = self.mean_in * hours_passed
        self.current_in = min(self.capacity_in, self.current_in + total_in)

        # Обновляем бункер выдачи (люди сняли деньги)
        total_out = self.mean_out * hours_passed
        self.current_out = max(0, self.current_out - total_out)
