import pyhop
from world import MoosWorld


def move(state, cell):
    """
    :param state: Pyhop state
    :param cell: the location in the grid of the format cx.y
    :return: pyhop state
    """
    world = MoosWorld(state)
    world.apply_agent_action(cell)

    # to allow remus to reach the specified location
    while not (state.agent.cell == cell):
        world.update_world()

    return state


def remove(state, mine):
    """

    :param state: Pyhop state
    :param mine: MoosWorld.Mine instance to be removed
    :return: the pyhop state
    """
    world = MoosWorld(state)
    world.remove_mine(mine)
    return state


def declare_ops():
    pyhop.declare_operators(move, remove)
