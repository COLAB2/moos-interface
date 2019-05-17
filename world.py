import zmq
import math
import mine_layer
import time
from pyhop import *
import threading

class Vehicle:
    """
    attributes for the underwater vehicle
    """
    def __init__(self, cell, speed=0, direction=90, name="ship"):
        # format : cx.y
        self.cell = cell
        self.speed = speed
        self.direction = direction
        self.name = name


class Mine:
    """
    attributes for the mine detected
    """
    def __init__(self, x, y, label):
        self.x = x
        self.y = y
        self.label = label


class MoosWorld:
    """
    This class interfaces with moos
    """

    def __init__(self, state, init_enemy=False):
        # pyhop state
        self.world = state

        # initialize the cells of the grid with their corresponding way_points
        self.grid = self.calculate_grids()

        # initialize the enemy behavior as a thread
        if init_enemy:
            enemy_laying_mines = threading.Thread(target=self.enemy_movement)

        # initialize the socket connections
        self.declare_connections()

        # execute the thread
        enemy_laying_mines.start()

    def declare_connections(self):
        """
        Establish the socket connections required with moos
        :return:
        """

        # Zeromq connection with the moos for perception
        context = zmq.Context()
        self.subscriber = context.socket(zmq.SUB)
        self.subscriber_mine = context.socket(zmq.SUB)

        self.subscriber.setsockopt(zmq.SUBSCRIBE, '')
        self.subscriber_mine.setsockopt(zmq.SUBSCRIBE, '')

        self.subscriber.setsockopt(zmq.RCVTIMEO, 1)
        self.subscriber_mine.setsockopt(zmq.RCVTIMEO, 1)
        self.subscriber.setsockopt(zmq.CONFLATE, 1)

        self.subscriber.connect("tcp://127.0.0.1:5563")
        self.subscriber_mine.connect("tcp://127.0.0.1:5564")

        # Zeromq connection with the moos for action
        self.publisher = context.socket(zmq.PUB)
        self.publisher_mine = context.socket(zmq.PUB)
        self.publisher.bind("tcp://127.0.0.1:5560")
        self.publisher_mine.connect("tcp://127.0.0.1:5565")

        # Zeromq connection with the fisher (enemy) for action
        self.publisher_enemy = context.socket(zmq.PUB)
        self.publisher_enemy.bind("tcp://127.0.0.1:5592")

        # Zeromq connection with the fisher (enemy) for perception
        self.subscriber_enemy = context.socket(zmq.SUB)
        self.subscriber_enemy.setsockopt(zmq.SUBSCRIBE, '')
        self.subscriber_enemy.setsockopt(zmq.RCVTIMEO, 1)
        self.subscriber_enemy.connect("tcp://127.0.0.1:5590")

        # Zeromq connection with the fisher1 for perception
        self.subscriber_fisher1 = context.socket(zmq.SUB)
        self.subscriber_fisher1.setsockopt(zmq.SUBSCRIBE, '')
        self.subscriber_fisher1.setsockopt(zmq.RCVTIMEO, 1)
        self.subscriber_fisher1.connect("tcp://127.0.0.1:5593")

        # Zeromq connection with the fisher2 for perception
        self.subscriber_fisher2 = context.socket(zmq.SUB)
        self.subscriber_fisher2.setsockopt(zmq.SUBSCRIBE, '')
        self.subscriber_fisher2.setsockopt(zmq.RCVTIMEO, 1)
        self.subscriber_fisher2.connect("tcp://127.0.0.1:5596")

        # Zeromq connection with the fisher3 for perception
        self.subscriber_fisher3 = context.socket(zmq.SUB)
        self.subscriber_fisher3.setsockopt(zmq.SUBSCRIBE, '')
        self.subscriber_fisher3.setsockopt(zmq.RCVTIMEO, 1)
        self.subscriber_fisher3.connect("tcp://127.0.0.1:5599")

    def calculate_grids(self, grid_size=20, distance=20):
        """
        :param grid_size: dimensions of the grid
        :param distance: distance between each cell
        :return: returns the way_points associated with the grid
        """
        # this is the center point of the first cell in the grid
        start_point = [-131, 65]

        # to store the way_points associtated with the cell position
        grid = []

        x = start_point[0] - distance
        y = start_point[1] + distance
        # loop for the vertical grid i.e c00, c10, c20 ect.
        for i in range(0, grid_size):
            y = y - distance
            x = start_point[0] - distance
            # loop for the horizontal grid i.e c00, c01, c02
            row = []
            for j in range(0, grid_size):
                x = x + distance
                row.append([x, y])
            grid.append(row)

        return grid

    def calculate_cell(self, x, y):
        """
        :return: the exact cell
        """

        # calculates the euclidean distance between each cell and the vehicle coordinates
        # for faster processing this should be replaced with binary search algorithm
        for i in range(0, len(self.grid)):
            for j in range(0, len(self.grid)):
                euclidean_distance = math.sqrt((self.grid[i][j][0] - x) ** 2 + (self.grid[i][j][1] - y) ** 2)
                if euclidean_distance < 10:
                    return "c" + str(i) + "." + str(j)


    def update_agent(self, verbose=1):
        """
        :return: the remus state from the moos
        """
        try:
            remus_position = self.subscriber.recv()
        except:
            if verbose > 1:
                print ("connection not established .... Retrying ...")
            return self.update_agent()

        x, y, speed, direction = remus_position.split(",")
        x = float(x.split(":")[1])
        y = float(y.split(":")[1])
        speed = float(speed.split(":")[1])
        direction = float(direction.split(":")[1])

        if self.world.agent:
            self.world.agent.cell = self.calculate_cell(x, y)
            self.world.agent.speed = speed
            self.world.agent.direction = direction
        else:
            cell = self.calculate_cell(x, y)
            remus = Vehicle(cell, speed, direction, "remus")
            self.world.agent = remus

    def set_vehicle_parameters(self, vehicle_pos, name):
        """

        :param vehicle_pos: The string containing all the parameters of a vehicle
        :param name: the name of the vehicle
        :return: updates the parameters of the world
        """
        x, y, speed, direction = vehicle_pos.split(",")
        x = float(x.split(":")[1])
        y = float(y.split(":")[1])
        speed = float(speed.split(":")[1])
        direction = float(direction.split(":")[1])

        if name in self.world.vessels:
            self.world.vessels[name].cell = self.calculate_cell(x, y)
            self.world.vessels[name].speed = speed
            self.world.vessels[name].direction = direction
        else:
            cell = self.calculate_cell(x, y)
            vehicle = Vehicle(cell, speed, direction, name)
            self.world.vessels[name] = vehicle

    def get_vessel(self, subscriber, name):
        """

        :param subscriber: subscriber for fisher vessel
        :param name: name of the vessel
        :return:
        """

        try:
            fisher_pos = self.subscriber.recv()
            self.set_vehicle_parameters(fisher_pos, name)
        except:
            self.get_vessel(subscriber, name)

    def update_vessels(self, verbose=1):
        """
        :return: updating the dictionary with vessels
        """

        self.get_vessel(self.subscriber_fisher1, "fisher1")

        self.get_vessel(self.subscriber_fisher2, "fisher2")

        self.get_vessel(self.subscriber_fisher3, "fisher3")

        self.get_vessel(self.subscriber_enemy, "fisher4")


    def check_if_new_mine(self, mine):
        """
        :param mine: instance of the Mine class
        :return: boolean : checks if it is the new mine
        """
        for each in self.world.mines:
            if each.label == mine.label:
                return True

        return False


    def remove_mine(self, mine):
        """

        :param mine: instance of the mine
        :return: removes the mine from the dictionary
        """
        for each in self.world.mines:
            if each.label == mine.label:
                self.world.mines.remove(each)
                self.publisher_mine.send_multipart(
                    [b"M", str(mine.label)])


    def update_mines(self):
        """

        :return: Updates the dictionary if there are any mines
        """
        try:
            mine_report = self.subscriber_mine.recv()
            mine_x, mine_y, mine_label = mine_report.split(":")[1].split(",")
            mine_x = float(mine_x.split("=")[1])
            mine_y = float(mine_y.split("=")[1])
            mine_label = mine_label.split("=")[1]
            new_mine = Mine(mine_x, mine_y, mine_label)
            if self.check_if_new_mine(new_mine):
                self.world.mines.append()
        except:
            pass

    def update_world(self):
        """
        :return: the updated state from the moos
        """

        # updates the state of the remus
        self.update_agent()

        # updates the state of all the fisher vessels
        self.update_vessels()

        # if detected updates the state of the mines
        self.update_mines()

    def apply_agent_action(self, cell):
        """

        :param cell: The location of the cell remus should go to
        :return:
        """
        # get the grid indexes from the cell
        cell = cell.replace("c", "")
        cell = cell.split(".")
        row_index = int(cell[0])
        column_index = int(cell[1])
        point = self.grid[row_index][column_index]
        message = [b"M", b"point = " + str(point[0]) + "," + str(point[1]) + "# speed= 1.0"]
        time.sleep(0.1)
        self.publisher.send_multipart(message)
        time.sleep(0.1)
        self.publisher.send_multipart(message)

    def apply_enemy_action(self, cell):
        """

        :param cell: The location of the cell enemy should go to
        :return:
        """
        # get the grid indexes from the cell
        cell = cell.replace("c", "")
        cell = cell.split(".")
        row_index = int(cell[0])
        column_index = int(cell[1])
        point = self.grid[row_index][column_index]
        message = [b"M", b"point = " + str(point[0]) + "," + str(point[1]) + "# speed= 1.0"]
        time.sleep(0.1)
        self.publisher_enemy.send_multipart(message)
        time.sleep(0.1)
        self.publisher_enemy.send_multipart(message)

    def enemy_way_point_behavior(self, way_point):
        """
        :param way_point: List of way_points enemy should travel
        :return:
        """
        for each in way_point:
            time.sleep(0.1)
            self.apply_enemy_action(each)
            x=0
            y=0
            while not (self.calculate_cell(x, y) == each):
                try:
                    enemy_pos = self.subscriber_enemy.recv()
                    x, y, speed, direction = enemy_pos.split(",")
                    x = float(x.split(":")[1])
                    y = float(y.split(":")[1])
                except:
                    pass




    def enemy_movement(self):
        """
        The enemy movement and mine laying activity
        :return:
        """
        way_point = ["c2.19", "c3.19", "c4.19", "c4.18", "c4.17", "c4.16", "c5.16", "c5.15", "c5.14",
             "c5.13", "c5.12", "c5.11", "c5.10"]

        # travel to all the way_points (one by one)
        self.enemy_way_point_behavior(way_point)

        # lay mines
        cell = way_point[-1]
        cell = cell.replace("c", "")
        cell = cell.split(".")
        layer = mine_layer.Minelayer(self.grid[int(cell[0])][int(cell[1])])
        layer.send_message()

        # return to its original path
        while True:
            way_point.reverse()
            self.enemy_way_point_behavior(way_point)



def main():


    state = State('state')
    state.vessels = {}
    state.agent = {}
    state.mines = []
    # True parameter runs the thread for the movement of enemy
    w = MoosWorld(state, True)

    w.apply_agent_action("c5.8")

    '''
    To update the world (This updates dictionaries)
    w.update_world()
    
    To move remus
    w.apply_agent_action(cx.y)
    
    To remove mines
    w.remove_mine(mine)
    
    To adjust the way_points of the enemy vessel
    modify the list way_point from the function enemy_movement
    Note.. enemy_movement is a thread that runs when you initialize the MoosWorld
    

    '''


if __name__ == '__main__':
    main()