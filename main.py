from BayesNet import *
from BNReasoner import *


def main():
    dogNet = BayesNet()
    dogNet.load_from_bifxml(file_path= 'testing/lecture_example2.BIFXML')

    vars = dogNet.get_all_variables()
    #print(vars)
    print(dogNet.get_interaction_graph())
    dogNet.draw_structure()

    #for var in vars:
        #print(var)
        #print(dogNet.get_children(var))

    net = BNReasoner(dogNet)
    print(net.get_paths('X','O', []))


main()