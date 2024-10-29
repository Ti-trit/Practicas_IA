"""
Primera práctica de IA
Implementació d'un algorisme de cerca informada; MiniMax amb poda alpha-beta
Autors: Adrián Ruiz Vidal i Khaoula Ikkene
"""
import copy
import time

from fontTools.ttLib.ttVisitor import visit
from numpy.f2py.symbolic import as_ge
from scipy.ndimage import maximum

from practica.joc import Accions, Viatger
from practica.estat import Estat, pesos

global inicio
torn = 1 #comença el jugador max

class EstatMiniMax(Estat):
    def __init__(self, parets, taulell, desti, agents: list[Viatger], nom, mida, cami=None):
        super().__init__(parets, taulell, desti, agents, nom, mida, cami)
        self.nom = self.get_nom()
        self.cami = self.get_cami()
        self.agents = self.get_agents()
        self.parets = self.get_parets()
        self.taulell = self.get_taulell()
        self.heuristica = self.get_heuristica()

    def __hash__(self):
        return hash((
            tuple(self.parets),  # Paredes
            tuple(tuple(row) for row in self.taulell),# Convertir la matriz a una tupla de tuplas
            self.desti,
            self.agents[self.nom],  # Posición del agente
        ))

    def __eq__(self, other):
        """Overrides the default implementation"""
        return (

            tuple(self.parets) == tuple(other.parets) and
                self.agents[self.nom] == other.agents.get(self.nom) and
                self.desti == other.desti and
                self.taulell == other.taulell
        )

    def get_heuristica(self):
        global torn
        pos_agent1 = self.agents[self.nom]
        index = next(agent for agent in self.agents if agent != self.nom)
        pos_enemic = self.agents[index]

        # Calcular las distancias a la meta
        distancia_meta = sum(abs(a - b) for a, b in zip(pos_agent1, self.desti))
        distancia_enemic = sum(abs(a - b) for a, b in zip(pos_enemic, self.desti))


        # quants parets hi ha entre l'agent i l'estat meta?
        num_obstacles = 0
        for paret in self.parets:
            if min(pos_agent1[0], self.desti[0]) <= paret[0] <= max(pos_agent1[0], self.desti[0]) and \
                    min(pos_agent1[1], self.desti[1]) <= paret[1] <= max(pos_agent1[1], self.desti[1]):
                num_obstacles += 1

        # total d'accions que són de tipus POSAR_PARET
        num_parets = sum(1 for action in self.cami if action == Accions.POSAR_PARET)

        # si és el torn de max, ha de prioritzar arribar el primer a la meta
        if torn == 1:
            self.heuristica = distancia_meta + num_obstacles
        else:
            self.heuristica = -(distancia_meta + num_obstacles)-num_parets


        return self.heuristica

    def pos_valida(self, nova_posicio) -> bool:
        # Comprobar si la posición está fuera de los límites del tablero
        if not (0 <= nova_posicio[0] < len(self.taulell) and 0 <= nova_posicio[1] < len(self.taulell[0])):
            return False

        # Comprobar si ya hay una pared en esa posición
        if nova_posicio in self.parets:
            return False

        # Comprobar si la posición está ocupada por algún agente
        for pos in self.agents.values():
            if nova_posicio == pos:
                return False

        # Comprobar si la posición es el destino
        if nova_posicio == self.desti:
            return False

        # Si ninguna de las condiciones anteriores se cumple, la posición es válida
        return True

    def generar_fills(self):
        fills = []
        movs = {

                "N": (0, -1),
                "O": (-1, 0),
                "S": (0, 1),
                "E": (1, 0),
            }

        movs2 = {
            "N": (0, -2),
            "O": (-2, 0),
            "S": (0, 2),
            "E": (2, 0),
        }

        # per les accions de MOURE
        for index, mov in movs.items():
            nova_posicio = tuple(map(sum, zip(self.agents[self.nom], mov)))

            if self.es_valida(nova_posicio):
                nou_estat = EstatMiniMax(
                    parets=self.parets.copy(),
                    taulell=[row[:] for row in self.taulell],
                    desti=self.desti,
                    agents=self.agents.copy(),
                    nom=self.nom,
                    mida=self.get_mida(),
                    cami=self.cami[:] + [(Accions.MOURE, index)]
                    )
                # marquem la nova posició com ocupada
                nou_estat.taulell[nova_posicio[0]][nova_posicio[1]] = "O"
                # mourem l'agent, marcant la posició antica com a lliure
                nou_estat.taulell[self.agents[self.nom][0]][self.agents[self.nom][1]] = " "
                # actualitzar la posició de l'agent
                nou_estat.agents[self.nom] = nova_posicio
                fills.append(nou_estat)
        # botar
        for index, mov in movs2.items():
            nova_posicio = tuple(map(sum, zip(self.agents[self.nom], mov)))

            if self.es_valida(nova_posicio):
                nou_estat = EstatMiniMax(
                    parets=self.parets.copy(),
                    taulell=[row[:] for row in self.taulell],
                    desti=self.desti,
                    agents=self.agents.copy(),
                    nom=self.nom,
                    mida=self.get_mida(),
                    cami=self.cami[:] + [(Accions.BOTAR, index)]
                )

                # marquem la nova posició com ocupada
                nou_estat.taulell[nova_posicio[0]][nova_posicio[1]] = "O"
                # mourem l'agent, marcant la posició antica com a lliure
                nou_estat.taulell[self.agents[self.nom][0]][self.agents[self.nom][1]] = " "
                nou_estat.agents[self.nom] = nova_posicio
                fills.append(nou_estat)

        # para la acción de poner paredes
        for index, mov in movs.items():
            nova_posicio = tuple(map(sum, zip(self.agents[self.nom], mov)))

            # Verificar si la posición es válida
            if  self.pos_valida(nova_posicio) :

            # Crear una copia del tablero y de las paredes

                nou_taulell = [row[:] for row in self.taulell]
                nou_parets = self.parets.copy()
                nou_taulell[nova_posicio[0]][nova_posicio[1]] = "O"
                nou_parets.add(nova_posicio)

                nou_estat = EstatMiniMax(
                    parets=nou_parets,
                    taulell=nou_taulell,
                    desti=self.desti,
                    agents=self.agents.copy(),
                    nom=self.nom,
                    mida=self.get_mida(),
                    cami=self.cami[:] + [(Accions.POSAR_PARET, index)]
                )

                fills.append(nou_estat)

        return fills




class AgentMiniMax(Viatger):
    def __init__(self, nom: str, mida_taulell):
        super().__init__(nom, mida_taulell)
        self.__nom = nom
        self.__mida = mida_taulell
        self.__cami = None
        self.maximum_depth =3
        self.oberts= None
        self.__visitats = None



    @staticmethod
    def torn_de_max() -> bool:
        """
        Metode per anar alternant els torns entre l'agent MAX i MIN
        torn =1 --> torn de max
        """
        global torn
        if torn == 1:
            torn = 0
            return True
        else:
            torn = 1
            return False



    def cerca(self, estat: EstatMiniMax, alpha, beta, torn_max: bool, profunditat: int):
        global punt_fill, fill
        if estat.es_meta():

            return estat, (1 if not torn_max else -1)

        if profunditat >= self.maximum_depth:

            return estat,estat.heuristica

        valor = None
        self.oberts.append(estat)
        # no vam guardant les puntuacions dels estats fills, sino que amb una variable que es va actualitzant
        # vam guardant la millor puntuació segons cada torn
        for fill in estat.generar_fills():
            if fill in self.oberts or fill in self.__visitats:
                continue


            punt_fill = self.cerca(fill, alpha, beta, not torn_max, profunditat + 1)
            self.__visitats.add(punt_fill)
            # self.num_tancats+=1
            if torn_max:
                if valor is None or punt_fill[1] > valor:
                    valor = punt_fill[1]
                    if profunditat == 0:
                        # si hem arribat al nivell més alt, hem de retornar l'acció triada

                        self.__cami = fill.cami[0]
                    #     actualitzem el valor de alpha en el torn de max
                    alpha = valor
            else:
                if valor is None or punt_fill[1] < valor:
                    valor = punt_fill[1]
                    # si hem arribat al nivell més alt, hem de retornar l'acció triada
                    if profunditat == 0:
                        self.__cami = fill.cami[0]

                    beta = valor

            if alpha >= beta:
                # pruning, fo fa falta explorar més
                break

        self.oberts.pop(-1)

        if valor is None:
            return estat, estat.heuristica
        else:
            return estat, valor


    def actua(self, percepcio: dict) -> Accions | tuple[Accions, str]:
        # reiniciar els conjunts

        self.oberts= []
        self.__visitats= set()

        estat_inicial = EstatMiniMax(
            percepcio["PARETS"], percepcio["TAULELL"], percepcio["DESTI"],
            percepcio["AGENTS"], self.__nom, self.__mida,
        )
        if estat_inicial.es_meta():
            return Accions.ESPERAR

        turno = self.torn_de_max()
        self.cerca(estat_inicial, alpha=-float('inf'), beta=float('inf'), torn_max=turno, profunditat=0)
        if self.__cami is None:
            return Accions.ESPERAR
        else:
            return self.__cami