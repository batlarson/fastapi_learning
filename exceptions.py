class ActivoNoEncontradoError(Exception):
    def __init__(self, ticker: str):
        self.ticker = ticker


class PrecioNoDisponibleError(Exception):
    def __init__(self, ticker: str):
        self.ticker = ticker


