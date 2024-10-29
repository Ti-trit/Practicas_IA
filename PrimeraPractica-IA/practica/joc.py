""" Labyrinth game. First practice.

Author: Miquel Miró Nicolau (UIB), 2024.
"""
import enum
import random
import warnings

import pygame

from base import agent as agent_lib
from base import entorn, joc


class TipusCas(enum.Enum):
    """ Enumerat, tipus de casella.

    """
    LLIURE = 0
    PARET = 1


class Accions(enum.Enum):
    """ Accions que es poden realitzar

    MOURE -> Pes 1
    BOTAR -> Pes 2
    POSAR_PARET -> Pes 4

    """
    MOURE = 0
    POSAR_PARET = 1
    BOTAR = 2
    ESPERAR = 3

    def __repr__(self):
        return self.name


class Viatger(agent_lib.Agent):
    PATH_IMG = "../assets/prova.png"

    def __init__(self, nom: str, mida_taulell: tuple[int, int] = (8, 8)):
        super().__init__(long_memoria=1)

        posicio = random.randint(0, mida_taulell[0] - 1), random.randint(
            0, mida_taulell[1] - 1
        )
        # posicio=(0,0)

        self.__posicio = posicio
        self.__nom = nom

    def pinta(self, display):
        pass

    def actua(self, percepcio: dict) -> Accions | tuple[Accions, object]:
        return Accions.ESPERAR

    @property
    def nom(self):
        return self.__nom

    @property
    def posicio(self):
        return self.__posicio

    @posicio.setter
    def posicio(self, val: tuple[int, int]):
        self.__posicio = val


class Casella:
    IMG_DESTI = "../assets/desti.png"
    SIZE = (50, 50)

    def __init__(
        self,
        tipus: TipusCas = TipusCas.LLIURE,
        agent: Viatger = None,
        desti: bool = False,
    ):
        self.__tipus = tipus
        self.__agent = agent
        self.__desti = desti

    def put_agent(self, agent):
        self.__agent = agent

        return self.__desti

    def pop_agent(self) -> agent_lib.Agent:
        age = self.__agent
        self.__agent = None

        return age

    def pop_desti(self):
        self.__desti = None

    def put_desti(self):
        self.__desti = True

    def put_paret(self):
        self.__tipus = TipusCas.PARET

    def is_accessible(self):
        return self.__tipus is TipusCas.LLIURE and self.__agent is None

    def is_desti(self) -> bool:
        return self.__desti

    def draw(self, window, x, y):
        pygame.draw.rect(
            window,
            pygame.Color(0, 0, 0),
            pygame.Rect(
                x * Casella.SIZE[0],
                y * Casella.SIZE[1],
                Casella.SIZE[0],
                Casella.SIZE[1],
            ),
            1 if self.__tipus is TipusCas.LLIURE else 0,
        )
        if self.__agent is not None:
            img = pygame.image.load(self.__agent.PATH_IMG)
            img = pygame.transform.scale(img, Casella.SIZE)
            window.blit(img, (x * Casella.SIZE[0], y * Casella.SIZE[1]))

        if self.__desti:
            img = pygame.image.load(Casella.IMG_DESTI)
            img = pygame.transform.scale(img, Casella.SIZE)
            window.blit(img, (x * Casella.SIZE[0], y * Casella.SIZE[1]))

    def simplifica(self):
        simple = " "
        if (
            self.__tipus is TipusCas.PARET
            or self.is_desti()
            or self.__agent is not None
        ):
            simple = "O"

        return simple


class Laberint(joc.Joc):
    MOVS = {
        "N": (0, -1),
        "O": (-1, 0),
        "S": (0, 1),
        "E": (1, 0),
    }

    def __init__(
        self,
        agents: list[Viatger],
        mida_taulell: tuple[int, int] = (12, 12),
        pos_final: tuple[int, int] = None,
        parets: str | set = None,
    ):
        super().__init__(
            agents,
            (mida_taulell[0] * Casella.SIZE[0], mida_taulell[1] * Casella.SIZE[1]),
            title="Pràctica 1",
        )
        self.__acabat = False

        self.__mida_taulell = mida_taulell
        self.__caselles = self.__generate_caselles()

        self.__agents = agents
        for a in self.__agents:
            x, y = a.posicio
            self.__caselles[x][y].put_agent(a)

        if pos_final is None:
            pos_final = (
                random.randint(0, mida_taulell[0] - 1),
                random.randint(0, mida_taulell[1] - 1),
            )
            # pos_final=(mida_taulell[0]-1, mida_taulell[1]-1)

        self.__desti = pos_final
        self.__caselles[pos_final[0]][pos_final[1]].put_desti()

        self.__parets = set()
        self.__afegeix_parets()

    def __generate_caselles(self) -> list[list[Casella]]:
        return [
            [Casella() for _ in range(self.__mida_taulell[1])]
            for _ in range(self.__mida_taulell[0])
        ]

    @property
    def size(self) -> int:
        return self.__mida_taulell[0] * self.__mida_taulell[1]

    def __afegeix_parets(self, parets: list[int] = None):
        """Afegeix les parets passades per paràmetre.

        Args:
            parets (llista d'enters): Posicions a on hi ha una paret.
        """
        if parets is None:
            parets = [i for i in range(self.size) if random.randint(0, 3) == 0]

        for paret in parets:
            x, y = paret // self.__mida_taulell[0], paret % self.__mida_taulell[0]
            if (
                (x * self.__mida_taulell[0] + y) in parets
                and not self.__caselles[x][y].is_desti()
                and self.__caselles[x][y].is_accessible()
            ):
                self.__caselles[x][y].put_paret()
                self.__parets.add((x, y))

    @property
    def pos_agents(self):
        posicions = {}
        for a in self.__agents:
            posicions[a.nom] = a.posicio

        return posicions

    @staticmethod
    def __obte_pos(pos_original: tuple[int, int], multiplicador: int, direccio: str):
        return (
            Laberint.MOVS[direccio][0] * multiplicador + pos_original[0],
            Laberint.MOVS[direccio][1] * multiplicador + pos_original[1],
        )

    def __pos_correcte(self, pos) -> bool:
        return (
            0 <= pos[0] < self.__mida_taulell[0]
            and 0 <= pos[1] < self.__mida_taulell[1]
        )

    def __moure_agent(
        self, direccio: str, agent_actual: Viatger, multiplicador: int = 1
    ):
        """Mou l'agent en la direcció indicada.

        Args:
            direccio (str): N,S,W,E. Els punts cardinals.
            agent_actual (Viatger): L'agent que realitza l'acció.
            multiplicador (int): Bot del moviment.
        """
        correcte = False

        pos_original = agent_actual.posicio
        pos_updated = self.__obte_pos(pos_original, multiplicador, direccio)

        if (
            self.__pos_correcte(pos_updated)
            and self.__caselles[pos_updated[0]][pos_updated[1]].is_accessible()
        ):
            self.__caselles[pos_original[0]][pos_original[1]].pop_agent()
            self.__caselles[pos_updated[0]][pos_updated[1]].put_agent(agent_actual)
            agent_actual.posicio = pos_updated
            correcte = True
        else:
            msg = f"Acció no possible a la casella {pos_updated} "
            pos_updated = pos_original
            warnings.warn(msg)

        return correcte, pos_updated

    def _aplica(
        self, accio: entorn.Accio, params=None, agent_actual: Viatger = None
    ) -> None:
        if not self.__acabat:
            if accio not in Accions:
                raise ValueError(f"Acció no existent en aquest joc: {accio}")

            if accio is Accions.MOURE or accio is Accions.BOTAR:
                if params not in ("N", "S", "E", "O"):
                    raise ValueError(f"Paràmetre {params} incorrecte per acció MOURE")
                _, pos_updated = self.__moure_agent(
                    params, agent_actual, int(accio is Accions.BOTAR) + 1
                )

                if self.__caselles[pos_updated[0]][pos_updated[1]].is_desti():
                    self.__caselles[pos_updated[0]][pos_updated[1]].pop_desti()
                    self.__acabat = True
                    print(f"L'agent {agent_actual.nom} ha guanyat")

            elif accio is Accions.POSAR_PARET:
                if params not in ("N", "S", "E", "O"):
                    raise ValueError(
                        f"Paràmetre {params} incorrecte per acció POSAR_PARET"
                    )
                pos_original = agent_actual.posicio
                pos_updated = self.__obte_pos(pos_original, 1, params)

                if (
                    self.__pos_correcte(pos_updated)
                    and self.__caselles[pos_updated[0]][pos_updated[1]].is_accessible()
                ):
                    self.__caselles[pos_updated[0]][pos_updated[1]].put_paret()
                    self.__parets.add(pos_updated)
                else:
                    msg = f"Acció no possible a la casella {pos_updated} "

                    warnings.warn(msg)

    def _draw(self) -> None:
        super()._draw()
        window = self._game_window
        window.fill(pygame.Color(255, 255, 255))

        for x, row in enumerate(self.__caselles):
            for y, cas in enumerate(row):
                cas.draw(window, x, y)

    def __simplify_caselles(self):
        return [[c.simplifica() for c in row] for row in self.__caselles]

    def percepcio(self) -> dict:
        # print(f"agents posicio {self.pos_agents}")
        return {
            "PARETS": self.__parets,
            "TAULELL": self.__simplify_caselles(),
            "DESTI": self.__desti,
            "AGENTS": self.pos_agents,
        }