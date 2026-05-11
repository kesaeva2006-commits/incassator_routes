class Atm:
    def __init__(self, id, lat, lon, capacity_in, capacity_out):
        self.id = id
        self.lat = lat
        self.lon = lon
        self.capacity_in = capacity_in
        self.capacity_out = capacity_out
        self.current_in = 0
        self.current_out = capacity_out

    def needs_service(self):
        return self.current_in >= self.capacity_in or self.current_out <= 0
