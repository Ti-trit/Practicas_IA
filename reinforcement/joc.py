from enum import Enum, IntEnum
from xml.sax.handler import property_dom_node

import numpy as np
import pygame
import random

from base import joc, entorn


class Cell(IntEnum):
    EMPTY = 0  # indicates empty cell where the agent can move to
    OCCUPIED = 1  # indicates cell which contains a wall and cannot be entered
    CURRENT = 2  # indicates current cell of the agent


class Action(IntEnum):
    MOVE_LEFT = 0
    MOVE_RIGHT = 1
    MOVE_UP = 2
    MOVE_DOWN = 3


class Status(Enum):
    WIN = 0
    LOSE = 1
    PLAYING = 2


class Laberint(joc.Joc):
    """
    A maze with walls. An agent is placed at the start cell and must find the exit cell by moving
    through the maze.
    """

    actions = [
        Action.MOVE_LEFT,
        Action.MOVE_RIGHT,
        Action.MOVE_UP,
        Action.MOVE_DOWN,
    ]  # all possible actions

    reward_exit = 10.0  # reward for reaching the exit cell
    penalty_move = (
        -0.05
    )  # penalty for a move which did not result in finding the exit cell
    penalty_visited = -0.25  # penalty for returning to a cell which was visited earlier
    penalty_impossible_move = (
        -0.75
    )  # penalty for trying to enter an occupied cell or moving out

    # of the maze

    def __init__(
        self,
        agents=None,
        maze=None,
        start_cell=(0, 0),
        exit_cell=(6, 6),
        mostra_cami=False,
    ):
        """Create a new maze game

        Args:
            agent (QTableModel): Agent to solve the maze (optional).
            maze (numpy.array): 2D array containing empty cells (= 0) and cells occupied
                with walls (= 1) (optional).
            start_cell (tuple): starting cell for the agent in the maze (optional, else upper left)
            exit_cell (tuple): exit cell which the agent has to reach (optional, else lower
                right)
        """
        super().__init__(agents, (8 * 50, 8 * 50), title="Laberint reforç")
        if maze is None:
            maze = np.array(
                [
                    [0, 1, 0, 0, 0, 0, 0, 0],
                    [0, 1, 0, 1, 0, 1, 0, 0],
                    [0, 1, 0, 1, 1, 0, 1, 0],
                    [0, 1, 0, 1, 0, 0, 0, 0],
                    [0, 1, 0, 1, 0, 1, 0, 0],
                    [0, 0, 0, 1, 0, 1, 1, 1],
                    [0, 1, 1, 0, 0, 0, 0, 0],
                    [0, 1, 0, 0, 0, 1, 0, 0],
                ]
            )  # 0 = free, 1 = occupied

        self.__maze = maze
        self.__minimum_reward = (
            -0.5 * self.__maze.size
        )  # stop game if accumulated reward
        # is below this threshold

        nrows, ncols = self.__maze.shape

        self.__exit_cell = (ncols - 1, nrows - 1) if exit_cell is None else exit_cell

        self.__start_cell = self.__previous_cell = self.__current_cell = start_cell
        self.__total_reward = 0.0  # accumulated reward
        self.__visited = set()  # a set() only stores unique values
        self.__mostra_cami = mostra_cami

    def _aplica(self, accio: entorn.Accio, params=None, agent_actual=None):
        """Move the agent according to 'action' and return the new state, reward and game status.

        Args:
            accio: the agent will move in this direction
            params:
            agent_actual:

        Returns:
            state, reward, status
        """

        reward = self.__execute(accio)
        self.__total_reward += reward

        status = self.__status()
        state = self.percepcio()

        if status is not Status.PLAYING:
            self.set_game_status(True)

        return state["POS"], reward, status

    # Reinicia la salida del agente a una nueva posición aleatoria válida
    def reset(self):
        start_cell = (random.randint(0, 7), random.randint(0, 7)) 
        while not self.esValid(start_cell):
            start_cell = (random.randint(0, 7), random.randint(0, 7))
        self.__previous_cell = self.__current_cell = start_cell
        self.__total_reward = 0.0  # accumulated reward
        self.__visited = set()  # a set() only stores unique values
        self.set_game_status(False)

        return start_cell
    
    # Comprueba que la posición inicial del agente sea válida
    def esValid(self, cell):
        new_cell = (cell[1],cell[0])    # Cambiar fila por columna
        # Comprobar si no es pared o meta o inicio no posible (0,0)
        return self.__maze[new_cell] == 0 and new_cell != self.__exit_cell and new_cell != self.__start_cell

    def __execute(self, action):
        """Execute action and collect the reward or penalty.

        Args:
            action: direction in which the agent will move

        Returns:
            Float: reward or penalty which results from the action
        """
        possible_actions = self.__possible_actions(self.__current_cell)

        if not possible_actions:
            reward = (
                self.__minimum_reward - 1
            )  # cannot move anywhere, force end of game

        elif action in possible_actions:
            col, row = self.__current_cell
            if action == Action.MOVE_LEFT:
                col -= 1
            elif action == Action.MOVE_UP:
                row -= 1
            if action == Action.MOVE_RIGHT:
                col += 1
            elif action == Action.MOVE_DOWN:
                row += 1

            self.__previous_cell = self.__current_cell
            self.__current_cell = (col, row)

            reward = self.__calculate_reward()

            self.__visited.add(self.__current_cell)
        else:
            reward = (
                Laberint.penalty_impossible_move
            )  # penalty for trying to enter an occupied
            # cell or move out of the maze

        return reward

    def __calculate_reward(self):
        if self.__current_cell == self.__exit_cell:
            reward = Laberint.reward_exit  # maximum reward when reaching the exit cell
        elif self.__current_cell in self.__visited:
            reward = (
                Laberint.penalty_visited
            )  # penalty when returning to a cell which was
            # visited earlier
        else:
            reward = (
                Laberint.penalty_move
            )  # penalty for a move which did not result in finding
            # the exit cell
        return reward

    def __possible_actions(self, cell: tuple[int, int]):
        """Create a list with all possible actions from 'cell', avoiding the maze's edges and
        walls.

        Args:
            cell (tuple): location of the agent (optional, else use current cell)

        Returns:
            list: all possible actions
        """
        col, row = cell

        possible_actions = Laberint.actions.copy()  # initially allow all

        # now restrict the initial list by removing impossible actions
        nrows, ncols = self.__maze.shape
        if row == 0 or (row > 0 and self.__maze[row - 1, col] == Cell.OCCUPIED):
            possible_actions.remove(Action.MOVE_UP)
        if row == nrows - 1 or (
            row < nrows - 1 and self.__maze[row + 1, col] == Cell.OCCUPIED
        ):
            possible_actions.remove(Action.MOVE_DOWN)

        if col == 0 or (col > 0 and self.__maze[row, col - 1] == Cell.OCCUPIED):
            possible_actions.remove(Action.MOVE_LEFT)
        if col == ncols - 1 or (
            col < ncols - 1 and self.__maze[row, col + 1] == Cell.OCCUPIED
        ):
            possible_actions.remove(Action.MOVE_RIGHT)

        return possible_actions

    def __status(self):
        """Return the game status.

        :return Status: current game status (WIN, LOSE, PLAYING)
        """
        if self.__current_cell == self.__exit_cell:
            return Status.WIN

        if (
            self.__total_reward < self.__minimum_reward
        ):  # force end of game after too much loss
            return Status.LOSE

        return Status.PLAYING

    def percepcio(self):
        """Return the state of the maze: the agent current location

        Returns:
            {'POS': numpy.array [1][2]: agents current location}
        """

        pos = self.__current_cell
        return {"POS": pos}

    def set_agent(self, agent):
        self._agents = agent

    @property
    def maze(self):
        return self.__maze

    @maze.setter
    def maze(self, maze):
        self.__maze = maze

    def _draw(self):
        super()._draw()
        window = self._game_window
        window.fill(pygame.Color(255, 255, 255))

        for x, row in enumerate(self.__maze):
            for y, cas in enumerate(row):
                self.draw_casella(y, x, self.__maze[x][y] == 1)

    def draw_casella(self, x, y, buida=True):
        if (x, y) in self.__visited and self.__mostra_cami:
            pygame.draw.rect(
                self._game_window,
                pygame.Color(255, 235, 245),
                pygame.Rect(x * 50, y * 50, 50, 50),
                0,
            )
        else:
            pygame.draw.rect(
                self._game_window,
                pygame.Color(0, 0, 0),
                pygame.Rect(x * 50, y * 50, 50, 50),
                0 if buida else 1,
            )

        if self.__current_cell[0] == x and self.__current_cell[1] == y:
            img = pygame.image.load("../assets/prova.png")
            img = pygame.transform.scale(img, (50, 50))
            self._game_window.blit(img, (x * 50, y * 50))

        if self.__exit_cell[0] == x and self.__exit_cell[1] == y:
            img = pygame.image.load("../assets/desti.png")
            img = pygame.transform.scale(img, (50, 50))
            self._game_window.blit(img, (x * 50, y * 50))
