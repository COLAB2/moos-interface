from pyhop import *
from world import MoosWorld

state = State('state')

# state.vessels contains the information about the fisher vessels
# format : state.vessels = {"fisher1" : world.Vehicle, "fisher2" : world.Vehicle}
state.vessels = {}

# state.agent contains the information about the remus (agent)
# format : state.agent = world.Vehicle
# this is not a dictionary don't be fooled by the initialization
state.agent = {}

# state.mines is the list contains the detected mines
# format : state.mines = [world.Mine, world.Mine, ...]
state.mines = []

# initialization of the MoosWorld
world = MoosWorld(state)

'''
To update the world (This updates dictionaries)
world.update_world()

To move remus
world.apply_agent_action(cx.y)

To remove mines
world.remove_mine(mine)

'''


def achieve_goals(state):
    """

    :param state: Pyhop state
    :return: To be decided
    """

    # updates the world
    world.update_world()



def declare_methods():
    declare_methods("achieve_goals", achieve_goals)