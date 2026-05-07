import math


class Atm:
    """
    Класс, описывающий банкомат.

    Статистические параметры:
    - mean_in, std_in: среднее и отклонение купюр, которые люди ВНОСЯТ в час.
    - mean_out, std_out: среднее и отклонение купюр, которые люди СНИМАЮТ в час.
    - capacity_in, capacity_out: максимальная вместимость бункеров приема и выдачи.

    Все средние значения — это количество банкнот (купюр) в час.
    Предполагаем, что это нормальное распределение.
    """

    def __init__(self, atm_id, lat, lon,
                 capacity_in, capacity_out,
                 mean_in, std_in,
                 mean_out, std_out,
                 current_in_level=0, current_out_level=0):
        self.atm_id = atm_id
        self.lat = lat  # Широта
        self.lon = lon  # Долгота

        # Параметры бункеров
        self.capacity_in = capacity_in
        self.capacity_out = capacity_out

        # Статистика ВНЕСЕНИЯ денег (пополнение бункера приема)
        self.mean_in = mean_in  # Среднее купюр в час
        self.std_in = std_in  # Стандартное отклонение

        # Статистика СНЯТИЯ денег (опустошение бункера выдачи)
        self.mean_out = mean_out  # Среднее купюр в час
        self.std_out = std_out  # Стандартное отклонение

        # Текущий уровень бункеров (сколько уже накопилось/осталось)
        self.current_in_level = current_in_level
        self.current_out_level = current_out_level

    def predict_level_after_hours(self, hours):
        """
        Прогноз уровня через заданное количество часов.
        Возвращает (предполагаемый_уровень_приема, предполагаемый_уровень_выдачи).

        Формула: текущий_уровень + (среднее_поступлений * часы) ± дисперсия.
        Для простоты используем +- 2 сигмы (95% доверительный интервал).
        """
        # Сколько купюр в среднем внесут за это время
        total_in_mean = self.mean_in * hours
        # Плюс "запас" на разброс (2 стандартных отклонения)
        total_in_worst = total_in_mean + 2 * self.std_in * math.sqrt(hours)

        # Сколько купюр в среднем снимут за это время
        total_out_mean = self.mean_out * hours
        # Минимальный уровень (худший случай для выдачи)
        total_out_worst = total_out_mean + 2 * self.std_out * math.sqrt(hours)

        predicted_in = self.current_in_level + total_in_worst
        predicted_out = self.current_out_level - total_out_worst

        return predicted_in, predicted_out

    def is_critical(self, hours_ahead=24):
        """
        Проверяет, находится ли банкомат в критическом состоянии.

        Критично, если:
        - Бункер приема заполнится > 90% (переполнение);
        - Бункер выдачи опустеет < 10% (пустой).
        """
        pred_in, pred_out = self.predict_level_after_hours(hours_ahead)

        in_fill_pct = (pred_in / self.capacity_in) * 100
        out_fill_pct = (pred_out / self.capacity_out) * 100

        if in_fill_pct > 90:
            return True, "RED_IN_OVERFLOW"
        if out_fill_pct < 10:
            return True, "RED_OUT_EMPTY"

        if in_fill_pct > 70 or out_fill_pct < 30:
            return True, "YELLOW"

        return False, "GREEN"

    def __repr__(self):
        return (f"Atm({self.atm_id}, "
                f"in={self.current_in_level}/{self.capacity_in}, "
                f"out={self.current_out_level}/{self.capacity_out})")