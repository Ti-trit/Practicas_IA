import sys
sys.path.append('C:\\Users\\miquel\\Development\\ia2023')


import abc

from base import entorn

class Trampes(Exception):
    """Excepció aixecada quan l'usuari fa trampes."""

    def __init__(self) -> None:
        self.message = "Has fet trampes, no pots fer-ho"
        super().__init__(self.message)


class Agent:
    def __init__(self, long_memoria: int) -> None:
        self.__memoria_permesa = long_memoria
        self.__memoria = []

        self._posicio_pintar = None

    def get_memoria(self, temps: int) -> dict:
        """Retorna el que s'ha guardat fa tantes iteracions com temps passat per paràmetre.

        Args:
            temps: Enter, com a màxim pots accedir al nombre d'estats previ definits pel problema.
        Retorna:
            Informació guardada a la iteració indicada.
        """
        if temps > self.__memoria_permesa:
            raise Trampes

        mem = None

        if len(self.__memoria) > (temps - 1):
            mem = self.__memoria[len(self.__memoria) - temps]

        return mem

    def set_posicio(self, posicio: tuple) -> None:
        """ NO ES POT CRIDAR """
        self._posicio_pintar = posicio

    def set_memoria(self, info) -> None:
        self.__memoria.append(info)

    @abc.abstractmethod
    def actua(
        self, percepcio: entorn.Percepcio
    ) -> entorn.Accio | tuple[entorn.Accio, object]:
        raise NotImplementedError

    @abc.abstractmethod
    def pinta(self, display) -> None:
        raise NotImplementedError
