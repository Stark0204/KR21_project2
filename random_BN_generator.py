from BayesNet import BayesNet
from typing import Dict
from BNReasoner import *
import pandas as pd
import random
import itertools



def generate_random_net(n: int) -> BayesNet:

    net=BayesNet()
    
    nodes=list(range(1,n+1))

    edges = []
    for i in range(1, n):
        children=[]
        num_childs = random.randint(1, 3)
        for j in range(num_childs):
            x = random.randint(i+1, n)
            if x in children:
                continue
            children.append(x)
        [edges.append((i,c)) for c in children]

    edge_string=[(str(t[0]),str(t[1])) for t in edges]
    

    final_dic=dict.fromkeys([str(n) for n in nodes])

    for n in nodes:

        parents=[]
        for j in edges:
            if n in j and n == j[1]:
                parents.append(j[0])

        col_names = parents #first the parents
        col_names.append(n) #then the node its self to have it on the right
        #creating a cpt from colums
        
        worlds = [list(i) for i in itertools.product([True, False], repeat=len(col_names))]
        result_cpt = pd.DataFrame(worlds, columns=[str(i) for i in col_names])
        result_cpt['p']=0
        
        for i in range(0,len(result_cpt),2) :
            p=random.uniform(0,1)
            result_cpt.loc[i, 'p']=p
            result_cpt.loc[i+1, 'p']=1-p

        final_dic.update({str(n): result_cpt})

    net.create_bn(final_dic.keys(), edge_string,final_dic)
    
    return net