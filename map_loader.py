import osmnx as ox
import os
import pickle

# Имя файла, в котором будем хранить кэш графа
CACHE_FILE = "moscow_graph.pkl"


def load_moscow_graph():
    """
    Загружает граф дорог Москвы.

    Логика:
    1. Если граф уже был скачан ранее → берём из кэша (быстро)
    2. Если нет → скачиваем с OpenStreetMap (медленно, но один раз)
    """

    # Проверяем, есть ли файл кэша
    if os.path.exists(CACHE_FILE):
        print("Найден кэш. Загружаем карту с диска...")

        # Загружаем объект графа из файла
        with open(CACHE_FILE, "rb") as f:
            G = pickle.load(f)

        print(f"Загружено: {len(G.nodes)} узлов, {len(G.edges)} рёбер")
        return G

    print("Скачиваем карту Москвы... (2-5 минут, только один раз)")

    # Скачиваем граф дорог Москвы по координатам
    G = ox.graph_from_bbox(
        north=55.95, south=55.55,
        east=37.95, west=37.30,
        network_type="drive",
        simplify=True
    )
    # Добавляем скорость движения на дорогах (км/ч)
    G = ox.add_edge_speeds(G)

    # Добавляем время проезда по каждому ребру (в секундах)
    G = ox.add_edge_travel_times(G)

    print("Сохраняем карту в кэш...")

    # Сохраняем граф в файл (кэшируем)
    with open(CACHE_FILE, "wb") as f:
        pickle.dump(G, f)

    print(f"Сохранено! Узлов: {len(G.nodes)}, рёбер: {len(G.edges)}")
    return G
