
"""
Primera práctica de IA
Implementació de la classe Estat
Autors: Adrián Ruiz Vidal i Khaoula Ikkene
"""
import copy
import enum

from practica import joc
from practica.joc import Viatger, Accions

class pesos(enum.Enum):

    MOURE = 1
    BOTAR = 2
    POSAR_PARET = 4

class Estat:


    def __init__(self, parets, taulell, desti, agents: list[Viatger], nom, mida, cami=None):
        if cami is None:
            cami = []
        self.__taulell = taulell
        self.agents = agents
        self.__parets = parets
        self.desti = desti
        self.nom = nom
        self.__mida = mida
        self.cami = cami


    # Hacer hash de los atributos variables para la comparacion de estados
    def __hash__(self):
        return hash((
            # tuple(sorted(self.__parets)),  # Paredes
            self.desti,
            self.agents[self.nom],   # Posición del agente
        ))
    
    def __eq__(self, other):
        """Overrides the default implementation"""
        return (
            # tuple(sorted(self.__parets)) == tuple(sorted(other.__parets)) and
            self.agents[self.nom] == other.agents.get(self.nom) and
            self.desti == other.desti
        )

    def es_meta(self) -> bool:
        """
            Metode per verificar si l'agent esta en la posió de la meta
            """
        posAgent = self.agents[self.nom]
        posDesti = self.desti
        return posAgent == posDesti
    
    def es_valida(self, nova_posicio) -> bool:
        """
            Metode per verificar si la nova posicio calculada és dins el taullel i és lliure
            """
        return self.esta_dentro(nova_posicio) and self.esta_libre(nova_posicio)

    def esta_dentro(self, nova_posicio) -> bool:
        (x, y) = self.__mida
        pos_x, pos_y= nova_posicio
        return x > pos_x >= 0 and y > pos_y >= 0
    
    def esta_libre(self, nova_posicio) -> bool:
        pos_x, pos_y = nova_posicio

        return self.__taulell[pos_x][pos_y] == " " or nova_posicio == self.desti

    def generar_fills(self):
        fills = []
        moves = {
            Accions.MOURE: {
                "N": (0, -1),
                "O": (-1, 0),
                "S": (0, 1),
                "E": (1, 0),
            },
            Accions.BOTAR: {
                "N": (0, -2),
                "O": (-2, 0),
                "S": (0, 2),
                "E": (2, 0),
            }
        }

        # per les accions de moure i botar
        for accion, direcciones in moves.items():
            for index, mov in direcciones.items():
                # calculem la nova posició
                nova_posicio = tuple(map(sum, zip(self.agents[self.nom], mov)))
                # si és valida
                if self.es_valida(nova_posicio):
                    # Cream una nova copia de l'estat actual amb els nous canvis
                    nou_estat = Estat(
                        parets=self.__parets.copy(),
                        taulell=[row[:] for row in self.__taulell],  # Copia superficial de cada fila
                        desti=self.desti,
                        agents=self.agents.copy(),
                        nom=self.nom,
                        mida=self.__mida,
                        cami=self.cami[:] + [(accion, index)]
                    )

                    # marquem la nova posició com ocupada
                    nou_estat.__taulell[nova_posicio[0]][nova_posicio[1]] = "O"
                    # mourem l'agent, marcant la posició antica com a lliure
                    nou_estat.__taulell[self.agents[self.nom][0]][self.agents[self.nom][1]] = " "
                    nou_estat.agents[self.nom] = nova_posicio
                    # afegim
                    fills.append(nou_estat)

        # per les accions de tipus Posar paret
        for index, mov in moves[joc.Accions.MOURE].items():
            nova_posicio = tuple(map(sum, zip(self.agents[self.nom], mov)))
            # no podem posar parets en la posició de la diana
            if self.es_valida(nova_posicio) and nova_posicio != self.desti:
                # afegim la posició de la nova paret a la llista de parets
                nou_estat = Estat(
                    parets=self.__parets.copy() | {nova_posicio},
                    taulell=[row[:] for row in self.__taulell],
                    desti=self.desti,
                    agents=self.agents.copy(),
                    nom=self.nom,
                    mida=self.__mida,
                    cami=self.cami[:] + [(Accions.POSAR_PARET, index)]
                )
                # actualitzem el taullel
                nou_estat.__taulell[nova_posicio[0]][nova_posicio[1]] = "O"
                fills.append(nou_estat)

        return fills

    def __str__(self):
        # taulell_str = "\n".join(" ".join(fila) for fila in self.__taulell)
        taulell_coords = [
            (x, y) for x in range(len(self.__taulell))
            for y in range(len(self.__taulell[x])) if self.__taulell[x][y] != " "
        ]
        agents_str = ", ".join(f"{nom}: {pos}" for nom,
                               pos in self.agents.items())
        parets_str = ", ".join(str(paret) for paret in self.__parets)
        cami_str = " -> ".join(str(accion) for accion in self.cami)

        return (
            f"Estat del taulell:\n{taulell_coords}\n"
                f"Agents: {agents_str}\n"
                f"Parets: {parets_str}\n"
                f"Destí: {self.desti}\n"
                f"Camí recorregut: {cami_str}\n")


    def get_taulell(self):
        return self.__taulell

    def get_agents(self):
        return self.agents

    def get_parets(self):
        return self.__parets

    def get_desti(self):
        return self.desti

    def get_cami(self):
        return self.cami

    def get_nom(self):
        return self.nom

    def get_mida(self):
        return self.__mida