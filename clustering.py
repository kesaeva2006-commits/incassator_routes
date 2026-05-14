import numpy as np
from sklearn.cluster import KMeans
from atm import Atm


def cluster_atms(atms: list[Atm], n_clusters: int = 5) -> list[list[Atm]]:
    """
    Разделяет список банкоматов на n_clusters групп с помощью алгоритма KMeans.
    KMeans группирует точки (банкоматы) по близости координат (lat, lon),
    чтобы инкассация могла обслуживать ближайшие точки вместе.
    """

    # Если список пустой — возвращаем пустые кластеры
    if not atms:
        return [[] for _ in range(n_clusters)]

    # 1. Преобразуем список банкоматов в числовую матрицу координат
    # Формат: [[lat, lon], [lat, lon], ...]
    coords = np.array([[atm.lat, atm.lon] for atm in atms])

    # 2. Создаём модель KMeans
    # n_clusters — сколько групп хотим получить ( = числу инкассаторов)
    # random_state фиксирует результат (чтобы кластеры не менялись при запуске)
    kmeans = KMeans(
        n_clusters=n_clusters,
        random_state=42,
        n_init="auto"
    )

    # Обучаем модель и сразу получаем метки кластеров для каждой точки
    labels = kmeans.fit_predict(coords)

    # 3. Создаём список пустых кластеров
    clusters = [[] for _ in range(n_clusters)]

    # 4. Распределяем банкоматы по кластерам
    # label показывает, к какому кластеру относится каждый банкомат
    for atm, label in zip(atms, labels):
        clusters[label].append(atm)

    return clusters
