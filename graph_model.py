import networkx as nx

class GraphModel:
    '''NetworkX graph wrapper'''

    def __init__(self):
        self.graph = nx.Graph()
    
    def add_edge(self, u, v, weight=1):
        '''Adds an edge between nodes u and v with an optional weight'''
        self.graph.add_edge(u, v, weight=weight)

    def shortest_path(self, start, target, weighted=True):
        '''Returns the shortest path as a '''
        w = 'weight' if weighted else None
        return nx.shortest_path(self.graph, start, target, weight=w)

    def shortest_path_length(self, start, target, weighted=True):
        '''Returns the cost of the shortest path'''
        w = 'weight' if weighted else None
        return nx.shortest_path_length(self.graph, start, target, weight=w)
