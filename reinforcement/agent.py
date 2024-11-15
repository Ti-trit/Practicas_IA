import logging
import random

import numpy as np

from base import entorn
from reinforcement.abstractmodel import AbstractModel
from reinforcement.joc import Status, Action


class AgentQ(AbstractModel):
    """Tabular Q-learning prediction model.

    For every state (here: the agents current location ) the value for each of the actions is
    stored in a table.The key for this table is (state + action). Initially all values are 0.
    When playing training games after every move the value in the table is updated based on
    the reward gained after making the move. Training ends after a fixed number of games,
    or earlier if a stopping criterion is reached (here: a 100% win rate).
    """

    default_check_convergence_every = (
        5  # by default check for convergence every # episodes
    )

    def __init__(self, game, **kwargs):
        """Create a new prediction model for 'game'.

        Args:
            game (Maze): Maze game object
            kwargs: model dependent init parameters
        """
        super().__init__(game, name="QTableModel")
        self.Q = {}  # table with value for (state, action) combination

    def q(self, state):
        """Get q values for all actions for a certain state."""
        # Si estado es de tipo array lo convierte a una tupla simple
        if type(state) is np.ndarray:
            state = tuple(state.flatten())

        q_aprox = np.zeros(len(self.environment.actions))
        i = 0
        for action in self.environment.actions:
            if (state, action) in self.Q:
                q_aprox[i] = self.Q[(state, action)]
            i += 1
        return q_aprox

    def actua(self, percepcio) -> entorn.Accio | tuple[entorn.Accio, object]:
        """Policy: choose the action with the highest value from the Q-table. Random choice if
        multiple actions have the same (max) value.

        Args:
            percepcio: game state
        Returns:
            selected action
        """
        q = self.q(percepcio["POS"])

        actions = np.nonzero(q == np.max(q))[
            0
        ]  # get index of the action(s) with the max value
        return random.choice(actions)

    def pinta(self, display) -> None:
        pass

    def predict(self, state):
        """ Policy: choose the action with the highest value from the Q-table.
        Random choice if multiple actions have the same (max) value.

        Args:
            state (np.array): Game state

        Returns:
            Action. Selected action
        """
        q = self.q(state)

        actions = np.nonzero(q == np.max(q))[
            0
        ]  # get index of the action(s) with the max value
        return self.environment.actions[random.choice(actions)]

    def print_Q(self):
        """ Print Q table.

        Prints two matrices:
            1. Q-Values Matrix: Maximum Q-value for each state.
            2. Policy Matrix: Optimal action to take in each state based on the maximum Q-value.

        Rows represent the y-coordinate, and columns represent the x-coordinate.

        Author: Dylan Luigi Canning.
        """
        # Extract all unique states from the Q-table
        states = set(state for (state, action) in self.Q.keys())

        if not states:
            print("Q-table is empty.")
            return

        # Determine the grid dimensions
        xs = [s[0] for s in states]
        ys = [s[1] for s in states]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        # Calculate grid size
        width = max_x - min_x + 1
        height = max_y - min_y + 1

        # Initialize the Q-values matrix with None
        Q_matrix = np.full((height, width), None, dtype=object)

        # Initialize the Policy matrix with None
        Policy_matrix = np.full((height, width), None, dtype=object)

        # Populate the Q-values and Policy matrices
        for state in states:
            x, y = state
            # Get all Q-values for the current state across all possible actions
            actions_q = {
                action: self.Q.get((state, action), 0.0)
                for action in self.environment.actions
            }

            if actions_q:
                # Determine the maximum Q-value for the current state
                max_q = max(actions_q.values())
                # Find all actions that have the maximum Q-value
                max_actions = [action for action, q in actions_q.items() if q == max_q]
                # Choose one action randomly among those with the max Q-value
                best_action = random.choice(max_actions)
            else:
                max_q = 0.0
                best_action = '-'

            # Adjust indices if states do not start at (0,0)
            matrix_y = y - min_y  # Row index
            matrix_x = x - min_x  # Column index

            Q_matrix[matrix_y][matrix_x] = max_q
            Policy_matrix[matrix_y][matrix_x] = AgentQ._action_to_symbol(best_action)

        # Convert None to a placeholder (e.g., '-') for better readability
        Q_matrix_display = np.where(Q_matrix == None, '-', Q_matrix)
        Policy_matrix_display = np.where(Policy_matrix == None, '-', Policy_matrix)

        # Print the Q-values matrix
        print("Q-Table Maximum Values (Rows: Y-axis, Columns: X-axis):")
        for row in Q_matrix_display:
            row_display = ""
            for cell in row:
                if cell == '-':
                    row_display += f"{cell:^6} "  # Center the placeholder
                else:
                    row_display += f"{cell:6.2f} "  # Format Q-values to two decimal places
            print(row_display)
        print()  # Add an empty line for better readability

        # Print the Policy matrix
        print("Policy Matrix (Rows: Y-axis, Columns: X-axis):")
        for row in Policy_matrix_display:
            row_display = ""
            for cell in row:
                row_display += f"{cell:^6} "  # Center the action symbol or placeholder
            print(row_display)

    @staticmethod
    def _action_to_symbol(action):
        """
        Converts an Action enum member to a single-character symbol for easier visualization.

        Args:
            action (Action): The Action enum member (e.g., Action.MOVE_UP).

        Returns:
            str: A single-character symbol representing the action.
        """
        action_mapping = {
            Action.MOVE_LEFT: '←',
            Action.MOVE_RIGHT: '→',
            Action.MOVE_UP: '↑',
            Action.MOVE_DOWN: '↓',
        }
        return action_mapping.get(action, '?')  # '?' for undefined actions

    def train(
            self,
            discount,
            exploration_rate,
            learning_rate,
            episodes,
            stop_at_convergence=False,
    ):
        """ Train the model

        Args:
            stop_at_convergence: stop training as soon as convergence is reached.

        Hyperparameters:
            discount (float): (gamma) preference for future rewards (0 = not at all, 1 = only)
            exploration_rate (float): exploration rate reduction after each random step
                                (<= 1, 1 = no at all)
            learning_rate (float): preference for using new knowledge (0 = not at all, 1 = only)
            episodes (int): number of training games to play

        Returns:
            Int, datetime: number of training episodes, total time spent
        """

        # variables for reporting purposes
        cumulative_reward = 0
        cumulative_reward_history = []
        win_history = []

        # start_time = datetime.now()

        # training starts here
        for episode in range(1, episodes + 1):

            state = self.environment.reset()

            # choose action epsilon greedy
            if np.random.random() < exploration_rate:
                action = random.choice(self.environment.actions)
            else:
                action = self.predict(state)

            while True:
                next_state, reward, status = self.environment._aplica(action)
                cumulative_reward += reward

                # choose next action epsilon greedy
                if np.random.random() < exploration_rate:
                    next_action = random.choice(self.environment.actions)
                else:
                    next_action = self.predict(next_state)

                if (
                        state,
                        action,
                ) not in self.Q.keys():  # ensure value exists for (state, action)
                    # to avoid a KeyError
                    self.Q[(state, action)] = 0.0

                if (
                        next_state,
                        next_action,
                ) not in self.Q.keys():  # ensure value exists for (state, action)
                    # to avoid a KeyError
                    self.Q[(next_state, next_action)] = 0.0

                # DINS POLÍTICA!
                next_Q = self.Q[(next_state, next_action)]

                self.Q[(state, action)] = self.Q[(state, action)] + learning_rate * (
                        reward + discount * next_Q - self.Q[(state, action)]
                )

                if status in (
                        Status.WIN,
                        Status.LOSE,
                ):  # terminal state reached, stop episode
                    break

                state = next_state
                action = next_action

            cumulative_reward_history.append(cumulative_reward)

            logging.info(
                "episode: {:d}/{:d} | status: {:4s} | e: {:.5f}".format(
                    episode, episodes, status.name, exploration_rate
                )
            )
        """
            if episode % check_convergence_every == 0:
                # check if the current model does win from all starting cells
                # only possible if there is a finite number of starting states
                w_all, win_rate = self.environment.check_win_all(self)
                win_history.append((episode, win_rate))
                if w_all is True and stop_at_convergence is True:
                    logging.info("won from all start cells, stop learning")
                    break
        """

        logging.info("episodes: {:d}".format(episode))

        return cumulative_reward_history, win_history, episode
