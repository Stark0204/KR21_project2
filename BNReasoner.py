from typing import Union
from BayesNet import BayesNet
import pandas as pd
import numpy as np
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

    # TODO: This is where your methods should go

new_net = BayesNet()
new_net.load_from_bifxml('/home/rik/Desktop/Jong_Master/Knowledge Representation/PGM/KR21_project2/testing/lecture_example2.BIFXML')

variables = []

def marginalise(Q, E):
		
	result = pd.DataFrame()

	if not E:
		#If the evidence set is empty, and the probability table of single variable Q already exists, return that table
		if len(Q) == 1 : #and not Q[0].getparents()
			if Q[0] in new_net.get_all_cpts().keys():
				print('The table of Q already exists as a lone probability table \n')
				print(new_net.get_all_cpts().get(Q[0]))
				return new_net.get_all_cpts().get(Q[0])
		else:
			sum_out(new_net.get_all_cpts(), Q) #This is a temporary solution as summing out, which works

	else:
		print('here1')
		#If E is not empty, but Q is a single variable and the CPT exists, return that table
		if len(Q) == 1:

			if Q[0] in new_net.get_all_cpts().keys():
				
				for x in new_net.get_all_cpts():
					index_list = list(new_net.get_all_cpts().get(x).columns)
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
							print(new_net.get_all_cpts().get(Q[0]))
							return(new_net.get_all_cpts().get(Q[0]))


def sum_out(all_tables, query_list):

	tables = new_net.get_all_cpts()
	
	number_of_variables = len(new_net.get_all_cpts())
	num_rows = 2**number_of_variables

	global variables

	sum_out_variables = deepcopy(variables)
	for x in query_list:
		if x in sum_out_variables:
			sum_out_variables.remove(x)
	
	num_rows = 2**(len(variables))
	variables.append('p')
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


	for a in range(num_rows):
		value_list = list(full_table.iloc[a])
		value_list.remove(np.nan)
		print(value_list)
		probability = 1

		for x in new_net.get_all_cpts():

			current_cpt = new_net.get_all_cpts().get(x)
			ndf = current_cpt[current_cpt[x] == full_table[x].iloc[a]]
			
			if ndf.shape[0] == 1:

				probability *= ndf.iloc[0][ndf.shape[1]-1]

			else:
				while ndf.shape[0] > 1:
					for y in variables:
						if y in ndf.columns:

							newdf = ndf[ndf[y] == full_table[y].iloc[a]]
							if newdf.shape == ndf.shape:
								pass
							else:
								ndf=newdf
								break

				probability *= ndf.iloc[0][ndf.shape[1]-1]

		full_table['p'].iloc[a] = probability			


	#probless_table = full_table.drop(columns=['p'])

	for x in sum_out_variables:
		full_table = full_table.drop(columns=[x])	  #Remove the first variable to sum out
		probless_table = full_table.drop(columns=['p'])   #Create a table without probabilities for comparison

		for y in range(num_rows):			  #Loop through all rows
			for z in range(num_rows):                 #For each row, loop through all rows
				if y != z and probless_table.iloc[y].equals(probless_table.iloc[z]): #If not looking at the same row, and the rows are the same
					full_table['p'][y] += full_table['p'][z]		     #Sum the probabilities of the two rows
					full_table = full_table.drop([z])			     #Remove the lower row from the table
					break
			if full_table.shape[0] == num_rows/2:
				num_rows = int(num_rows/2)
				break	
					
	probless_table = probless_table.drop([1])
	print(full_table)

	return full_table

def elimination(query_variables, evidence_variables, ordered_variables):
	print('NOT DONE YET')

def main():

	test_Q = ['X']
	test_E = []

	new_net.draw_structure()

	for key in new_net.get_all_cpts().keys():
		variables.append(key)
	
	marginalise(test_Q, test_E)

main()

	
