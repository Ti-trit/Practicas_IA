"""
Primera práctica de IA
Implementació d'un algorisme de cerca no informada; primera cerca en profunditat
Autors: Adrián Ruiz Vidal i Khaoula Ikkene
"""
from practica.joc import Accions, Viatger
from practica.estat import Estat

class AgentProfunditat(Viatger):
    def __init__(self, nom: str, mida_taulell):
        super().__init__(nom, mida_taulell)
        self.__nom = nom
        self.__mida = mida_taulell
        self.__per_visitar = None
        self.__visitats = None
        self.__cami_exit = None


    def cerca(self, estat_inicial: Estat) -> bool:
        self.__per_visitar = [] #oberts
        self.__visitats = set() #tancats
        exit = False
        # afegim l'estat actual a la llista
        self.__per_visitar.append(estat_inicial)
        # mentre hi hagi estats per visitar
        while self.__per_visitar:
            # obtenim el primer estat de la llista
            estat_actual = self.__per_visitar.pop(-1)
            # si ja l'hem visitat, passem al seguent estat
            if estat_actual in self.__visitats:
                continue
            # si hem arribat a l'estat objectiu, aturem la cerca
            if estat_actual.es_meta():
                break
            #  obtenim els estats fills de l'estat actual
            # i els afegim a la llista d'estats per visitar
            for f in estat_actual.generar_fills():
                self.__per_visitar.append(f)

            # marquem l'estat actual com a visitat
            self.__visitats.add(estat_actual)

        # si l'estat actual és la meta,acaba el metode
        if estat_actual.es_meta():
            self.__cami_exit = estat_actual.cami
            exit = True

        return exit

    def actua(self, percepcio: dict) -> Accions | tuple[Accions, str]:
        # si no s'ha trobat una solucio, cream un estat inicial
        if self.__cami_exit is None:
            estat_inicial = Estat(
                percepcio["PARETS"], percepcio["TAULELL"], percepcio["DESTI"],
                percepcio["AGENTS"], self.__nom, self.__mida,)
            self.cerca(estat_inicial)

        # si l'algorisme ha trobat una solució, extraiem les accions una per una
        if self.__cami_exit:
            arrAcc = self.__cami_exit.pop(0)

            return arrAcc[0], arrAcc[1]
        else:
            return Accions.ESPERAR
