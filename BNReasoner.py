from typing import Union
from BayesNet import BayesNet
from copy import deepcopy


class BNReasoner:
    def __init__(self, net: Union[str, BayesNet]):
        """
        :param net: either file path of the bayesian network in BIFXML format or BayesNet object
        """
        if type(net) == str:
            # constructs a BN object
            self.bn = BayesNet()
            # Loads the BN from an BIFXML file
            self.bn.load_from_bifxml(net)
        else:
            self.bn = net

        self.paths_before = []

    # TODO: This is where your methods should go


    def d_sep(self, X, Y, Z):
        copyNet = deepcopy(self.bn)


        # Get (shortest) path
        paths = []
        paths.append(X)
        x_child = copyNet.get_children(X)
        if len(x_child == 0): return True

        if Y in x_child:
            return False

        while Y not in paths:

            for child in x_child:
                path_of_child = []
                path_of_child.append(child)
                children = copyNet.get_children(path_of_child)
                if len(children) > 0:
                    if Y in children:
                        path_of_child.append(Y)
                        paths.append(path_of_child)
                        break


        for var in Z:
            check_type()

    def get_paths(self, start, target, path_so_far):

        #if start in path_so_far: return (self, start, target, path_so_far)
        path_so_far.append(start)


        if start == target:
            print('yes')
            self.paths_before.append(path_so_far)
            return path_so_far


        neighbours = self.bn.get_neighbours(start)
        print('Neigbours = ', neighbours)

        neighbours = [x for x in neighbours if x not in path_so_far]
        print(path_so_far)
        print(neighbours)
        if len(neighbours) ==0: return None


        for neighbour in neighbours:
            #if self.get_paths(neighbour, target, path_so_far) is None:
            #    path_so_far.pop()
            if self.get_paths(neighbour, target, path_so_far) is not None:
                    return path_so_far



