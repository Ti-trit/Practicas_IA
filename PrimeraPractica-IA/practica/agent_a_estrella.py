"""
Primera práctica de IA
Implementació d'un algorisme de cerca informada; Algorisme A*
Autors: Adrián Ruiz Vidal i Khaoula Ikkene
"""
from typing import Tuple, Any

from base import agent, entorn
from practica import joc
from practica.joc import Accions, Viatger
from practica.estat import Estat
from queue import PriorityQueue


class EstatAEstrella(Estat):
    """
    Classe d'estat d'un agent A*, que té un atribut més: cost
    """
    def __init__(self, parets, taulell, desti, agents, nom, mida, cami, cost=0):
        super().__init__(parets, taulell, desti, agents, nom, mida, cami)
        self.__nom = self.get_nom()
        self.__cami = self.get_cami()
        self.__agents = self.get_agents()
        self.cost = cost 


    # Mateix que a Estat pero amb cost afegit per moviment
    def generar_fills(self):
        """
        Aquest metode es semblant al metode generar_fills de la classe Pare Estat
        Només canvia el tipus d'estat i ara calculem els costs dels estats en funció de les heuristiques i les accions fetes
        :return:
        """
        fills = []
        moves = {
            joc.Accions.MOURE: {
                "N": (0, -1),
                "O": (-1, 0),
                "S": (0, 1),
                "E": (1, 0),
            },
            joc.Accions.BOTAR: {
                "N": (0, -2),
                "O": (-2, 0),
                "S": (0, 2),
                "E": (2, 0),
            }
        }

        for accion, direcciones in moves.items():
            for index, mov in direcciones.items():
                nova_posicio = tuple(map(sum, zip(self.__agents[self.nom], mov)))

                if self.es_valida(nova_posicio):
                    nou_estat = EstatAEstrella(
                        parets=self.get_parets(),
                        agents=self.__agents.copy(),
                        taulell=[row[:] for row in self.get_taulell()],  # Copia superficial del taullel
                        desti=self.desti,
                        nom=self.__nom,
                        mida=self.get_mida(),
                        cami=self.__cami.copy()
                    )


                    # marquem la nova posició com ocupada
                    nou_estat.get_taulell()[nova_posicio[0]][nova_posicio[1]] = "O"
                    # mourem l'agent, marcant la posició antica com a lliure
                    nou_estat.get_taulell()[self.agents[self.nom][0]][self.agents[self.nom][1]] = " "
                    nou_estat.get_agents()[self.nom] = nova_posicio

                    nou_estat.get_cami().append((accion, index))

                    # Incrementar el coste según l'acció triada
                    if accion == Accions.MOURE:
                        nou_estat.cost += 1
                    else:
                        nou_estat.cost += 2

                    fills.append(nou_estat)

            # POSAR PARETS
        for index, mov in moves[Accions.MOURE].items():
            nova_posicio = tuple(map(sum, zip(self.__agents[self.__nom], mov)))

            if self.es_valida(nova_posicio) and nova_posicio != self.desti:
                # Crear una nueva instancia en lugar de deepcopy
                nou_estat = EstatAEstrella(
                    parets = self.get_parets(),
                    agents=self.__agents.copy(),
                    taulell=[row[:] for row in self.get_taulell()],  # Copia superficial de la matriz
                    desti=self.desti,
                    nom=self.__nom,
                    mida=self.get_mida(),
                    cami=self.__cami.copy()  # Copia superficial de la lista
                )

                nou_estat.get_parets().add(nova_posicio)
                nou_estat.get_taulell()[nova_posicio[0]][nova_posicio[1]] = "O"  
                nou_estat.get_cami().append((Accions.POSAR_PARET, index))
                nou_estat.cost += 4
                fills.append(nou_estat)

        return fills


class AgentAEstrella(Viatger):
    def __init__(self, nom: str, mida_taulell):
        super().__init__(nom, mida_taulell)
        self.__nom = nom
        self.__mida = mida_taulell
        self.__oberts = None
        self.__tancats = None
        self.__accions = None

    # L'id serveix per desempatar estats amb la mateixa heurística
    def heuristica(self, estat: EstatAEstrella, id: int) -> tuple[int | Any, int]:
        pos_x_agent = estat.get_agents()[estat.get_nom()][0]
        pos_y_agent = estat.get_agents()[estat.get_nom()][1]

        pos_x_desti = estat.get_desti()[0]
        pos_y_desti = estat.get_desti()[1]
        # Utilitzem la distància de Manhattan per a l'heurística
        manhattan = abs(pos_x_agent-pos_x_desti) + abs(pos_y_agent-pos_y_desti)

        # num_obstacles = 0
        # for paret in estat.get_parets():
        #     if min(pos_x_agent, estat.get_desti()[0]) <= paret[0] <= max(pos_x_agent, estat.get_desti()[0]) and \
        #             min(pos_y_agent, estat.get_desti()[1]) <= paret[1] <= max(pos_y_agent, estat.get_desti()[1]):
        #         num_obstacles += 1

        heur_total = manhattan+estat.cost
        # heur_total += num_obstacles
        return heur_total, id

    def obtenirEstat(self, tuple: dict) -> EstatAEstrella:
        """
        # Obtenir l'estat d'una tuple amb heurística
"""
        return tuple[1]

    def cerca(self, estat_inicial: EstatAEstrella) -> bool:

        self.__oberts = PriorityQueue()
        self.__tancats = set()
        exit = False
        self.__oberts.put(
            (self.heuristica(estat_inicial, 0), estat_inicial))

        i = 1   # id per afegir a la heurística
        while not self.__oberts.empty():
            tuple_actual = self.__oberts.get()
            estat_actual = self.obtenirEstat(tuple_actual)
            # si l'estat ja s'ha explorat, passem al seguent
            if estat_actual in self.__tancats:
                continue

            if estat_actual.es_meta():
                break

            for f in estat_actual.generar_fills():
                self.__oberts.put((self.heuristica(f, i), f))
                i += 1

            self.__tancats.add(estat_actual)

        if estat_actual.es_meta():
            self.__accions = estat_actual.get_cami()

            exit = True

        return exit

    def actua(self, percepcio: dict) -> Accions | tuple[Accions, str]:
        if self.__accions is None:
            estat_inicial = EstatAEstrella(
                percepcio["PARETS"], percepcio["TAULELL"], percepcio["DESTI"],
                percepcio["AGENTS"], self.__nom, self.__mida, cami=None)
            self.cerca(estat_inicial)

        if self.__accions:
            arrayAcc = self.__accions.pop(0)  # Sacar en formato cola (FIFO)

            return arrayAcc[0], arrayAcc[1]
        else:
            return Accions.ESPERAR
