"""
Primera práctica de IA
Autors: Adrián Ruiz Vidal i Khaoula Ikkene
"""
from practica import agent, joc, agent_profunditat, agent_a_estrella, agent_MiniMax


def main():
    mida = (10,10)
    # mida = (8,8)
    # mida = (6,6)

    agents = [

        # agent_a_estrella.AgentAEstrella("A*", mida_taulell=mida)
        # agent_profunditat.AgentProfunditat("AgentProfunditat", mida_taulell=mida)
        #
        agent_MiniMax.AgentMiniMax("max", mida_taulell=mida),
        agent_MiniMax.AgentMiniMax("min", mida_taulell=mida)
    ]

    lab = joc.Laberint(agents, mida_taulell=mida)
    lab.comencar()


if __name__ == "__main__":
    main()
