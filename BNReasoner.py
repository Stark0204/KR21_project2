from typing import Union
from BayesNet import BayesNet
import pandas as pd
import numpy as np


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

    # TODO: This is where your methods should g

def marginalise(Q, E):
		
	result = pd.DataFrame()

	if not E:
		#If the evidence set is empty, and the probability table of single variable Q already exists, return that table
		if len(Q) == 1:
			if Q[0] in new_net.bn.get_all_cpts().keys():
				print('The table of Q already exists as a lone probability table \n')
				print(new_net.bn.get_all_cpts().get(Q[0]))
				return new_net.bn.get_all_cpts().get(Q[0])
		else:
			pass

	else:
		print('here1')
		#If E is not empty, but Q is a single variable and the CPT exists, return that table
		if len(Q) == 1:

			if Q[0] in new_net.bn.get_all_cpts().keys():
				
				for x in new_net.bn.get_all_cpts():
					index_list = list(new_net.bn.get_all_cpts().get(x).columns)
					index_list.remove('p')
					if index_list[-1] == Q[0]:
						index_list.remove(Q[0])

						for x in index_list:
							if x in E:
								index_list.remove(x)	
								E.remove(x)
							else:
								index_list.remove(x)

						if E:
							print('im here')
							print(new_net.bn.get_all_cpts().get(Q[0]))
							return(new_net.bn.get_all_cpts().get(Q[0]))


		
				#if Q:
				#	pass
							
		
		#1. check whether the CPT already exists 	DONE
		#2. if so, return that CPT		 	DONE
		#3. if not, multiply to find the full CPT	
		#4. sum out to retrive the PT of P(Q)
			
			

new_net = BNReasoner('/home/rik/Desktop/Jong_Master/Knowledge Representation/PGM/KR21_project2/testing/lecture_example2.BIFXML')
for x in new_net.bn.get_all_cpts():
	#print(new_net.bn.get_all_cpts().get(x))
	#print(new_net.bn.get_all_cpts().get(x))
	frame = new_net.bn.get_all_cpts().get(x)
	#print(new_net.bn.get_all_cpts().keys())
	print(frame)
	#if 'I' in new_net.bn.get_all_cpts().keys():
		#print('yes')
	#print('\n')

test_Q = []
test_Q.append('O')
test_E = []
test_E.append('Y')
test_E.append('X')

def chain_rule(all_tables, query_list):

	tables = new_net.bn.get_all_cpts()
	
	number_of_variables = len(new_net.bn.get_all_cpts())
	num_rows = 2**number_of_variables

	variables = []
			
	for key in new_net.bn.get_all_cpts().keys():
	 	variables.append(key)
	
	variables.append('p')
	num_rows = 32
	full_table = pd.DataFrame(index = range(num_rows), columns = variables)
	
	for x in range(len(variables)-1):
		for y in range(num_rows):
			if x == 0:
				if y < num_rows/2**(x+1):
					full_table.iloc[y][x] = False
				else:
					full_table.iloc[y][x] = True
			elif x == 1:
				if y < 8 or (y > 15 and y < 24):
					full_table.iloc[y][x] = False
				else:
					full_table.iloc[y][x] = True
				
			elif x == 2:
				if y < 4 or (y > 7 and y < 12) or (y > 15 and y < 20) or (y > 23 and y < 28):
					full_table.iloc[y][x] = False
				else:
					full_table.iloc[y][x] = True

			elif x == 3:
				if y in [0,1,4,5,8,9,12,13,16,17,20,21,24,25,28,29]:
					full_table.iloc[y][x] = False
				else:
					full_table.iloc[y][x] = True

			elif x == 4:
				if y % 2 == 0:
					full_table.iloc[y][x] = False
				else:
					full_table.iloc[y][x] = True


	#test_list = list(full_table.iloc[0])
	#print(test_list)

	for a in range(num_rows):
		value_list = list(full_table.iloc[a])
		value_list.remove(np.nan)
		print(value_list)
		probability = 1

		for x in new_net.bn.get_all_cpts():
			#print("x: ", x)
			current_cpt = new_net.bn.get_all_cpts().get(x)
			ndf = current_cpt[current_cpt[x] == full_table[x].iloc[a]]
			
			#print("shape: ", ndf.shape)
			if ndf.shape[0] == 1:

				probability *= ndf.iloc[0][ndf.shape[1]-1]
				#print('probability',probability)
				

			else:
				while ndf.shape[0] > 1:
					for y in variables:
						#print('y: ',y)
						#print('value: ',full_table[y].iloc[a])
						#print('index',ndf.co)
						if y in ndf.columns:
							#print('here')
							newdf = ndf[ndf[y] == full_table[y].iloc[a]]
							#print(ndf)
							#print(ndf.shape)
							if newdf.shape == ndf.shape:
								pass
							else:
								ndf=newdf
								break
						#print(ndf)
				probability *= ndf.iloc[0][ndf.shape[1]-1]
				#print('probability',probability)
		full_table['p'].iloc[a] = probability			

			
				
	print(full_table)
	s = full_table['p']
	s = s.sum()
	print(s)
		
		

	

chain_rule(new_net.bn.get_all_cpts(), test_Q)
#marginalise(test_Q, test_E)


	
#print(new_net.bn.get_all_cpts().values())

	
