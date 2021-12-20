from typing import Union
from BayesNet import BayesNet
import pandas as pd
import numpy as np
from copy import deepcopy
import statistics


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

	variables = []

	def mpe(self,Q,E):
		
		cpt = self.marginalise(Q,E)
		print(cpt[cpt.p == cpt.p.max()],'butt')

	def marginalise(self, Q, E):
			
		result = pd.DataFrame()

		if type(Q) == str:
			print('casting ',Q,' to list')
			temp = []
			temp.append(Q)
			Q = temp
		total = Q + E
		

		print('Query: ' + str(Q) + '')
		print('Evidence: ' + str(E) + '')

		if not Q:
			return self.marginalise(self.variables,E)

		q = Q[0]

		if E:
			print('\nEquation to find: Pr(' + str(total) + ') / Pr(' + str(E) + ')\n')
		else: 
			print('\nEquation to find: Pr(' + str(total) + ')\n')

		if not self.cpt_exists(Q,E).empty:

			print(self.cpt_exists(Q,E))
			return self.cpt_exists(Q,E)

		else:
			
			if not E:
				
				if len(Q) == 1: 
					
					variables_for_multiplication = list(self.bn.get_cpt(q).columns)
					variables_to_sum_out = deepcopy(variables_for_multiplication)
					variables_to_sum_out.remove(q)		
					check_list = deepcopy(variables_for_multiplication)		
					variables_for_multiplication.remove(q)
					variables_for_multiplication.remove('p')

					result = deepcopy(self.bn.get_cpt(q))

					for x in variables_for_multiplication:
						for y in self.bn.get_all_cpts().values():
							if x in y and not list(y.columns) == check_list:
								result = self.factor_multiplication(y, result)

					result = self.sum_out(result, Q)
					return result

				elif len(Q) > 1:

					result = self.marginalise(q,E)

					Q.remove(q)

					for x in Q:
						result = self.factor_multiplication(self.marginalise(x,E),result)

					return result


			elif E:	
				
				numerator_vars = Q + E

				print('Q+E =',numerator_vars)

				numerator = self.marginalise(numerator_vars, [])
				print('DONEHERE',numerator)
				denominator = self.marginalise(E, [])
				result = self.divide(numerator, denominator)		
				return result
						
				
				

	def cpt_exists(self, q_vars, evidence):
		
		Q = q_vars[0]
		
		if len(q_vars) > 1:
			print('No CPT exists for this query yet.\n')
			return pd.DataFrame()
		else:
		
			if not evidence:
				if len(self.bn.get_cpt(Q).columns) > 2:
					print('No CPT exists for this query yet.\n')		
					return pd.DataFrame()
				else:
					return self.bn.get_cpt(Q)
			else:
				evidence_list = list(self.bn.get_cpt(Q).columns)
				evidence_list.remove('p')
				evidence_list.remove(Q)
				
				if set(evidence_list) == set(evidence):	
					return self.bn.get_cpt(Q)
					
					
		print('No CPT exists for this query yet.\n')
		return pd.DataFrame()

	def divide (self, numerator, denominator):
		
		result = pd.DataFrame()				#Assign the dataframe that will be the final result of the division

		num_rows_num = numerator.shape[0]		#Save the number of rows of the CPT of the numerator
		num_rows_den = denominator.shape[0]		#Save the number of rows of the CPT of the denominator

		numerator_vars = list(numerator.columns)	#Saves the variables of the numerator into a list
		denominator_vars = list(denominator.columns)	#Saves the variables of the denominator into a list
		difference_vars = []				#This list contains the variables that are in the numerator but not the denominator
	
		print(numerator)
		print(denominator)
	
		print('Dividing :',numerator_vars,' by ',denominator_vars)

		for x in numerator_vars:
			if x not in denominator_vars:
				difference_vars.append(x)

		difference_vars.append('p')
		
		num_copy_check = deepcopy(numerator)				#Assign a list which is a copy of the numerator
		num_copy_check = num_copy_check.drop(columns=difference_vars)	#Remove from this list the vars that are not in the denominator

		den_copy_check = deepcopy(denominator)				#Assign a list which is a copy of the denominator
		den_copy_check = den_copy_check.drop(columns=['p'])		#Add the probability colum to this list
										#WHY: The result of this will be two lists, both of which only have columns of the same variables.
										#I can compare these lists and where the row values are the same I can divide the probability of the
		for x in range(num_rows_num):					#numerator in that row by the probability of the denominator in that row in the real CPT.
			for y in range(num_rows_den):
				if list(num_copy_check.iloc[x]) == (list(den_copy_check.iloc[y])):
					numerator.at[x,'p'] /= denominator.at[y,'p']
			


		return numerator

	
	def sum_out(self, table, query_list):
		
		sum_out_variables = list(table.columns)

		num_rows = 2**(len(sum_out_variables)-1)

		for x in query_list:
			if x in sum_out_variables:
				sum_out_variables.remove(x)
		sum_out_variables.remove('p')

		probless_table = table.drop(columns=['p'])


		for x in range(len(sum_out_variables)):
			print('Removing: ',sum_out_variables[x])
			table = table.drop(columns=[sum_out_variables[x]])	  #Remove the first variable to sum out

			probless_table = table.drop(columns=['p'])   #Create a table without probabilities for comparison

			for y in range(num_rows):			  #Loop through all rows
				for z in range(num_rows):                 #For each row, loop through all rows
					if y != z and probless_table.iloc[y].equals(probless_table.iloc[z]): #If not looking at the same row, and the rows are the same		
						
						table.at[y,'p'] += table.at[z,'p']		     #Sum the probabilities of the two rows
						
						table.iloc[z] = np.nan			     #Remove the lower row from the table
						
						probless_table.iloc[z] = np.nan
						break
				if table.shape[0] == num_rows/2:
					num_rows = int(num_rows/2)
					break	
			print_table = table.dropna()
			#print(print_table)			
		probless_table = probless_table.drop([1])
		table = table.dropna()

		print('Finished summing out: \n', table)
		return table

	def factor_multiplication(self,factor1, factor2):

		factor1_vars = list(factor1.columns)
		factor2_vars = list(factor2.columns)	

		print('Multiplying: ',factor1_vars, factor2_vars)

		length1 = len(list(factor1.columns))
		length2 = len(list(factor2.columns))
		
		main_factor = pd.DataFrame()
		other_factor = pd.DataFrame()
		main_factor_vars = []
		other_factor_vars = []

		if length1 >= length2:
		
			main_factor = factor1
			other_factor = factor2
			main_factor_vars = deepcopy(factor1_vars)
			other_factor_vars = deepcopy(factor2_vars)

			for x in factor1_vars:
				if x in factor2_vars:
					factor2_vars.remove(x)

			check_factor = deepcopy(factor2_vars)
	
		else:
			
			main_factor = factor2
			other_factor = factor1
			main_factor_vars = deepcopy(factor2_vars)
			other_factor_vars = deepcopy(factor1_vars)
		
			for x in factor2_vars:
				if x in factor1_vars:
					factor1_vars.remove(x)
		
			check_factor = deepcopy(factor1_vars)


		result_factor_vars = deepcopy(main_factor_vars)

		if check_factor:
			
			for x in check_factor:
				result_factor_vars.insert(0,x)
	
						
		result = self.create_cpt(result_factor_vars)

		main_factor_vars.remove('p')
		other_factor_vars.remove('p')

		num_rows = 2**(len(result_factor_vars)-1)

		#Now the actual multiplication occurs

		common_main = []
		common_other = []

		for x in result_factor_vars:
			if x in main_factor_vars:
				common_main.append(x)
			if x in other_factor_vars:
				common_other.append(x)

		other_factor =  other_factor.reset_index()
		main_factor = main_factor.reset_index()
			
		for x in range(num_rows):

			row_no_list = []
			row_no = 0
			
			for y in common_main:
				row_no_list += list(np.where(main_factor[y] == result.at[x,y])[0])

			row_no = statistics.mode(row_no_list)
			val1 = main_factor.at[row_no, 'p']
			row_no_list = []
			row_no = 0

			for y in common_other:
				row_no_list += list(np.where(other_factor[y] == result.at[x,y])[0])
			
			row_no = statistics.mode(row_no_list)
			
			val2 = other_factor.at[row_no, 'p']

			result.at[x, 'p'] = val1 * val2

		print('Finished multiplying: \n',result)
		return(result)

	def create_cpt(self,variables):

		print('Creating CPT from: ',variables,'\n')

		new_cpt = pd.DataFrame(columns=variables)
		
		num_vars = len(variables)
		num_rows = 2**(num_vars-1)

		for x in range(num_rows):
			new_cpt = new_cpt.append(pd.Series(), ignore_index=True)

		for x in range(num_vars-1):
			for y in range(0,num_rows, 2**(num_vars-2-x)):
				for z in range(2**(num_vars-2-x)):	     
					if y % 2**(num_vars-x-1) == 0:
						new_cpt.iat[y+z,x] = False
					else:
						new_cpt.iat[y+z,x] = True
		return new_cpt
			
def main():

	print('\nSTARTING...\n')
	
	test_Q = ['I']
	test_E = ['X','Y']
	x=0
	y=0

	test_net = BNReasoner('/home/rik/Desktop/Jong_Master/Knowledge Representation/PGM/KR21_project2/testing/lecture_example2.BIFXML')

	#test_net.bn.draw_structure()

	for key in test_net.bn.get_all_cpts().keys():
		test_net.variables.append(key)

	test_net.mpe(test_Q,test_E)
	
	#print(test_net.marginalise(test_Q, test_E))
	#print(test_net.variables)

main()

	
