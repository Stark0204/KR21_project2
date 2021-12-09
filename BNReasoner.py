from typing import Union

import networkx as nx

from BayesNet import BayesNet
from copy import deepcopy
import matplotlib.pyplot as plt


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


    def d_sep(self, start: str, target: str, evidence: list):
        print("X = ", start, "  Y = ", target, "   Z =", evidence)
        BN_pruned = self.prune(evidence, dsepmode= True, start=start, target=target)

        intergraph = BN_pruned.get_interaction_graph()

        if nx.has_path(intergraph, start, target):
            return False
        else:
            return True







        # # Get (shortest) path
        # paths = []
        # paths.append(X)
        # x_child = copyNet.get_children(X)
        # if len(x_child == 0): return True

        # if Y in x_child:
        #     return False

        # while Y not in paths:

        #     for child in x_child:
        #         path_of_child = []
        #         path_of_child.append(child)
        #         children = copyNet.get_children(path_of_child)
        #         if len(children) > 0:
        #             if Y in children:
        #                 path_of_child.append(Y)
        #                 paths.append(path_of_child)
        #                 break


    

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


    def prune(self, evidence, dsepmode =False, start = None, target = None):
        BN_pruned = deepcopy(self.bn)
        BN_not_pruned = deepcopy(self.bn)

        # Cut outgoing edges from the evidence Z
        for i in evidence:
            trash = BN_pruned.get_children(i)

            for child in trash:
                edge = [i, child]
                BN_pruned.del_edge(edge)

            # Cut away the Z itself
            BN_pruned.del_var(i)

        var = BN_pruned.get_all_variables()

        # Take away every leaf node
        if dsepmode:
            for j in var:
                if len(BN_pruned.get_children(j)) == 0:
                    if target == j :
                            print("var equals target")
                    elif start == j:
                            print("var equals start")
                    else:
                        print("Deleting ", j)
                        BN_pruned.del_var(j)

        else:
            for j in var:
                if len(BN_pruned.get_children(j)) == 0:
                    print("Deleting ", j)
                    BN_pruned.del_var(j)

        BN_not_pruned.draw_structure()
        BN_pruned.draw_structure()
        return BN_pruned


    def order_min_degree(self):
        vars = self.bn.get_all_variables()
        edges = dict.fromkeys(vars, 0)

        for var in vars:
            neighbours = self.bn.get_neighbours(var)
            for neighbour in neighbours:

                edges[var] += 1

        edges_sorted = dict(sorted(edges.items(), key=lambda item: item[1]))
        order_min_degree = list(edges_sorted.keys())

        #sorted_values = sorted(edges.values())  # Sort the values
        #sorted_dict = {}
        # for i in sorted_values:
        #     for k in edges.keys():
        #         if edges[k] == i:
        #             sorted_dict[k] = edges[k]
        #             break

        print(edges)
        print(edges_sorted)
        print(order_min_degree)

        return(order_min_degree)
        #print(sorted_dict)


    def order_min_fill(self, return_dict = False):
        """
        Method to return the order of min fill
        Takes in self
        Output: dict containing the min_fill value per node
        """
        intergraph = self.bn.get_interaction_graph()
        nx.draw(intergraph, with_labels=True)
        plt.show()
        vars = intergraph.nodes
        print('vars = ', vars)
        min_fill = dict.fromkeys(vars, 0)

        for var in vars:
            neighbours = list(intergraph.neighbors(var))
            print('neighbours ', var, ' are ',neighbours)
            if len(neighbours) <=1:
                min_fill[var] = 0
                print('not enough neighbours,min_fill = 0')
                continue

            checked = []
            counter = 0

            # iterate over neighbours
            for neighbour in neighbours:

                # get the list of neighbours FROM THE NEIGHBOUR
                adj = list(intergraph.neighbors(neighbour))

                # delete the ones not bordering to var
                copy_neighbours = neighbours
                for i in copy_neighbours:
                    if i not in adj and i not in checked and i is not neighbour:
                        counter+= 1

                checked.append(neighbour)
            min_fill[var] = counter

        if return_dict: return min_fill
        
        print(min_fill)
        edges_sorted = dict(sorted(min_fill.items(), key=lambda item: item[1]))
        order_min_fill = list(edges_sorted.keys())
           
        return order_min_fill



    def order_min_fill(self):

        bn_copy = deepcopy(self.bn)
        intergraph = bn_copy.get_interaction_graph()
        vars = intergraph.nodes()

        print(vars)
        bn_copy.draw_structure()
        edges = dict.fromkeys(vars, 0)

        for var in vars:
            neighbours = bn_copy.get_neighbours(var)
            #print(neighbours)
            if neighbours == None:
                continue
            else:
                for neighbour in neighbours:
                    new_neighbours = neighbours.remove(neighbour)
                    print(new_neighbours)
                    if new_neighbours == None:
                        continue
                    else:
                        for end in new_neighbours:
                            if end in bn_copy.get_neighbours(neighbour):
                                continue
                            else:
                                bn_copy.add_edge([neighbour, end])
                                edges[var] += 1

        edges_sorted = dict(sorted(edges.items(), key=lambda item: item[1]))
        order_min_degree = list(edges_sorted.keys())




def main():

    print('starting MAIN...')
    test = BNReasoner("testing\lecture_example2.BIFXML" )
    test.bn.draw_structure()
    #print(test.d_sep("O", "I", ["Y", "X"]))
    print(test.order_min_degree())


    print(test.order_min_fill())









main()