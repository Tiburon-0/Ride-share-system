import math
import networkx as nx


class Location:

    '''Intializes Location class
    Node ID must be an integer'''

    def __init__(self, node):
        self._node = node

    def __str__(self):
        '''User-friendly display for Location class'''
        return f"Node: {self._node}"

    # Getter methods

    def get_node(self):
        '''Returns node_id'''
        return self._node

    # Distance calculation

    def distance_to(self, graph, starting_location, target_location, weight=None):
        '''Returns the distance between specified points using Djikstra's algorithm'''
        distance = nx.shortest_path_length(graph, starting_location, target_location, weight)
        return distance


class RiderLocation(Location):
    def __str__(self):
        '''User friendly display for RiderLocation subclass'''
        return f"RiderLocation:{self._node}"


class DriverLocation(Location):
    def __str__(self):
        '''User friendly display for DriverLocation subclass'''
        return f"DriverLocation:{self._node}"
