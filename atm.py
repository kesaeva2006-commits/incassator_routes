class Atm: # Класс, описывающий банкомат

    def __init__(self, atm_id: int, lat: float, lon: float,
                 capacity_in: int, capacity_out: int):
        """
        Конструктор класса — вызывается при создании объекта банкомата.

        :param atm_id: уникальный идентификатор банкомата
        :param lat: широта (географическая координата)
        :param lon: долгота (географическая координата)
        :param capacity_in: максимальная вместимость бункера приёма
        :param capacity_out: максимальная вместимость бункера выдачи
        """

        # Проверяем, что ёмкости бункеров заданы корректно
        # Они не могут быть нулевыми или отрицательными
        if capacity_in <= 0 or capacity_out <= 0:
            raise ValueError("Ёмкости бункеров должны быть больше 0")

        # Сохраняем переданные значения в объект (self — текущий объект)
        self.id = atm_id              # уникальный номер банкомата
        self.lat = lat                # широта ( для расчета расстояний)
        self.lon = lon                # долгота (для расчета расстояний)
        self.capacity_in = capacity_in    # максимальная вместимость бункера приема денег
        self.capacity_out = capacity_out  # максимальная вместимость бункера выдачи денег

    def needs_service(self) -> bool:
        """
        Проверяет, нужен ли банкомату инкассатор.

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
