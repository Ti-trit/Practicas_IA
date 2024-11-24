# -*- coding: utf-8 -*-
""" Mòdul que conté la classe abstracta Joc que permet generar múltiples jocs per ser emprats amb
agents intel·ligents.

Un joc és un objecte que conté alhora informació de com pintar-se i com realitzar les accions
indicades pels agents.

Creat per: Miquel Miró Nicolau (UIB), 2022
"""
import os

os.environ["SDL_VIDEO_WINDOW_POS"] = "%d,%d" % (100, 100)

import abc
import sys
import time
from abc import ABC

import pygame

from base import agent, entorn

fps_controller = pygame.time.Clock()


class HasPerdut(Exception):
    def __init__(self, msg=None) -> None:
        self.message = "Has perdut"

        if msg is not None:
            self.message += f": {msg}"

        super().__init__(self.message)


class Joc:
    def __init__(
        self,
        agents: list[agent.Agent],
        mida_pantalla: tuple[int, int] | None = None,
        title: str | None = None,
    ):
        self._mida_pantalla = mida_pantalla
        self._agents = agents
        self.__title = title
        self.__game_finished = False

        # self._game_window = None
        pygame.display.set_caption(self.__title)
        self._game_window = pygame.display.set_mode(self._mida_pantalla)

    def comencar(self) -> None:
        pygame.init()

        while True:
            fps_controller.tick(1)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self._draw()
            if not self.__game_finished:
                self._logica(self._agents)
            pygame.display.flip()

    @abc.abstractmethod
    def _draw(self):
        pass


    @abc.abstractmethod
    def percepcio(self) -> entorn.Percepcio:
        raise NotImplementedError

    @abc.abstractmethod
    def _aplica(self, accio: entorn.Accio, params=None, agent_actual=None):
        raise NotImplementedError

    def _logica(self, agents: list[agent.Agent]):
        for a in agents:
            accio = a.actua(percepcio=self.percepcio())
            if not isinstance(accio, tuple):
                accio = [accio]
            self._aplica(*accio, agent_actual=a)

    def set_game_status(self, finish: bool):
        self.__game_finished = finish


class JocNoGrafic(Joc, ABC):

    def __init__(self, agents: list[agent.Agent] | agent.Agent):
        if isinstance(agents, agent.Agent):
            agents = [agents]
        self._agents = agents

        super(JocNoGrafic, self).__init__(agents=agents, mida_pantalla=None, title=None)

    def comencar(self) -> None:
        while True:
            self._draw()
            self._logica(self._agents)
            time.sleep(0.25)
