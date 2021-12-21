from typing import Union
from BayesNet import BayesNet
import pandas as pd
import numpy as np
from copy import deepcopy
import statistics
import networkx as nx
import matplotlib.pyplot as plt
import random
import sys

#Code:
#MAP/MPE @Rik 
#DONERandom ordering Rik
#Test cases per algorithm Rik
#Perform Queries Use Case Rik
#Push BN generator to GitHub @Trenki


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
	instantiations = []
	elim_order = []


	def mpe(self, Q, E):
		if Q:
			cpt = self.marginalise(Q, E,self.elim_order)
		else:
			remaining_vars = deepcopy(self.variables)
			vars_to_remove = []
			for x in self.variables:
				if x in E:
					vars_to_remove.append(x)
			for x in vars_to_remove:
				remaining_vars.remove(x)
				
			cpt = self.marginalise(remaining_vars,E,self.elim_order)
		print(cpt[cpt.p == cpt.p.max()])

	def process_instantiation(self,given, truth_value):
		
		if not instantiations:
			return None
	
		given_cpt = self.bn.get_cpt(given)
		print(given_cpt)

		
		for x in self.bn.get_all_cpts().values():
			num_rows = x.shape[0]
			if given in list(x.columns):
				for y in range(num_rows):
					if x.at[y, given] == truth_value:
						x.iloc[y] = np.nan
				x = x.dropna()
				cpt_var_list = list(x.columns)
				len_cpt_list = len(cpt_var_list)
				self.bn.update_cpt(cpt_var_list[len_cpt_list-2],x)
				#print('LOOK',self.bn.get_cpt(given))
				#print(x)
						
					
					

	def marginalise(self, Q, E, elim_order):
		result = pd.DataFrame()

		for q in Q:
			if '-' in q:
				if q.replace('-','').upper() == q.replace('-',''):
					pass
				elif q.replace('-','').upper() in self.variables:
					self.instantiations.append(q)
					index = Q.index(q)
					Q[index] = q.replace('-','').upper()
					q = q.replace('-','').upper()
			if q not in self.variables and q.upper() not in self.variables:
				sys.exit('Query list invalid: Variable ' + str(q.upper()) + ' does not exist within the network')
			if q in self.variables:
				pass
			elif q.upper() in self.variables:
				index = Q.index(q)
				Q[index] = q.upper()
				self.instantiations.append(q)

		if type(Q) == str:
			print('casting ', Q, ' to list')
			temp = []
			temp.append(Q)
			Q = temp
		total = Q + E

		print('Query: ' + str(Q) + '')
		print('Evidence: ' + str(E) + '')

		if not Q:
			return self.marginalise(self.variables, E)

		q = Q[0]

		if E:
			print('\nEquation to find: Pr(' + str(total) + ') / Pr(' + str(E) + ')\n')
		else:
			print('\nEquation to find: Pr(' + str(total) + ')\n')

		if not self.cpt_exists(Q, E).empty:

			print(self.cpt_exists(Q, E))
			return self.cpt_exists(Q, E)

		else:

			if not E:

				if len(Q) == 1:

					variables_for_multiplication = list(self.bn.get_cpt(q).columns)

					check_list = deepcopy(variables_for_multiplication)
					variables_for_multiplication.remove(q)
					variables_for_multiplication.remove('p')

					print('rand', variables_for_multiplication)

					order = deepcopy(elim_order)
					vars_for_removal = []


					for x in order:
						if x not in variables_for_multiplication:
							vars_for_removal.append(x)

					for x in vars_for_removal:
						order.remove(x)

					print('elim: ', order)

					result = deepcopy(self.bn.get_cpt(q))

					for x in order:
						print('this is x: ',x)							#In the given elimination order:
						for y in self.bn.get_all_cpts().values():			#Iterate the cpts we have
							if x in list(y.columns) and not list(y.columns) == check_list and x in variables_for_multiplication: 
								result = self.factor_multiplication(y, result)	#Multiply the current cpt by 
						if x in variables_for_multiplication:
							variables_for_multiplication.remove(x)
						sum_out = variables_for_multiplication + list(q)
						
						result = self.sum_out(result, sum_out)
						
					
					return result

				elif len(Q) > 1:

					result = self.marginalise(q, E, self.elim_order)

					Q.remove(q)

					for x in Q:
						result = self.factor_multiplication(self.marginalise(x, E, self.elim_order), result)

					return result


			elif E:

				numerator_vars = Q + E

				print('Q+E =', numerator_vars)

				numerator = self.marginalise(numerator_vars, [], self.elim_order)
				denominator = self.marginalise(E, [], self.elim_order)
				result = self.divide(numerator, denominator)
				return result


	def cpt_exists(self, q_vars, evidence):
		Q = q_vars[0]

		if len(q_vars) > 1:
			print('No CPT exists for this query yet1.\n')
			return pd.DataFrame()
		else:

			if not evidence:
				if len(self.bn.get_cpt(Q).columns) > 2:
					print('No CPT exists for this query yet2.\n')
					return pd.DataFrame()
				else:
					return self.bn.get_cpt(Q)
			else:
				evidence_list = list(self.bn.get_cpt(Q).columns)
				evidence_list.remove('p')
				evidence_list.remove(Q)

				if set(evidence_list) == set(evidence):
					return self.bn.get_cpt(Q)

		print('No CPT exists for this query yet3.\n')
		return pd.DataFrame()


	def divide(self, numerator, denominator):
		
		numerator.reset_index(drop=True, inplace=True)
		denominator.reset_index(drop=True, inplace=True)


		result = pd.DataFrame()  # Assign the dataframe that will be the final result of the division

		num_rows_num = numerator.shape[0]  # Save the number of rows of the CPT of the numerator
		num_rows_den = denominator.shape[0]  # Save the number of rows of the CPT of the denominator

		numerator_vars = list(numerator.columns)  # Saves the variables of the numerator into a list
		denominator_vars = list(denominator.columns)  # Saves the variables of the denominator into a list
		difference_vars = []  # This list contains the variables that are in the numerator but not the denominator

		print(numerator)
		print(denominator)

		print('Dividing :', numerator_vars, ' by ', denominator_vars)

		for x in numerator_vars:
			if x not in denominator_vars:
				difference_vars.append(x)

		difference_vars.append('p')

		num_copy_check = deepcopy(numerator)  # Assign a list which is a copy of the numerator
		num_copy_check = num_copy_check.drop(
			columns=difference_vars)  # Remove from this list the vars that are not in the denominator

		den_copy_check = deepcopy(denominator)  # Assign a list which is a copy of the denominator
		den_copy_check = den_copy_check.drop(columns=['p'])  # Add the probability colum to this list
		# WHY: The result of this will be two lists, both of which only have columns of the same variables.
		# I can compare these lists and where the row values are the same I can divide the probability of the
		for x in range(num_rows_num):  # numerator in that row by the probability of the denominator in that row in the real CPT.
			for y in range(num_rows_den):
				if list(num_copy_check.iloc[x]) == (list(den_copy_check.iloc[y])):
					numerator.at[x, 'p'] /= denominator.at[y, 'p']

		return numerator


	def sum_out(self, table, query_list):

		#table is the cpt to sum out from
		#query_list is the variables not to sum out
		sum_out_variables = list(table.columns)

		num_rows = 2 ** (len(sum_out_variables) - 1)

		for x in query_list:
			if x in sum_out_variables:
				sum_out_variables.remove(x)
		if 'p' in sum_out_variables:

			sum_out_variables.remove('p')

		probless_table = table.drop(columns=['p'])

		for x in range(len(sum_out_variables)):
			print('Removing: ', sum_out_variables[x])
			table = table.drop(columns=[sum_out_variables[x]])  # Remove the first variable to sum out

			probless_table = table.drop(columns=['p'])  # Create a table without probabilities for comparison

			for y in range(num_rows):  # Loop through all rows
				for z in range(num_rows):  # For each row, loop through all rows
					if y != z and probless_table.iloc[y].equals(
							probless_table.iloc[z]):  # If not looking at the same row, and the rows are the same

						table.reset_index(drop=True, inplace=True)
						table.at[y, 'p'] += table.at[z, 'p']  # Sum the probabilities of the two rows

						table.iloc[z] = np.nan  # Remove the lower row from the table

						probless_table.iloc[z] = np.nan
						break
				if table.shape[0] == num_rows / 2:
					num_rows = int(num_rows / 2)
					break
			print_table = table.dropna()
		# print(print_table)
		probless_table = probless_table.drop([1])
		table = table.dropna()

		print('Finished summing out: \n', table)
		return table


	def factor_multiplication(self, factor1, factor2):
		factor1_vars = list(factor1.columns)
		factor2_vars = list(factor2.columns)

		print('Multiplying: ', factor1_vars, factor2_vars)

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
				result_factor_vars.insert(0, x)

		result = self.create_cpt(result_factor_vars)

		main_factor_vars.remove('p')
		other_factor_vars.remove('p')

		num_rows = 2 ** (len(result_factor_vars) - 1)

		# Now the actual multiplication occurs

		common_main = []
		common_other = []

		for x in result_factor_vars:
			if x in main_factor_vars:
				common_main.append(x)
			if x in other_factor_vars:
				common_other.append(x)

		other_factor = other_factor.reset_index()
		main_factor = main_factor.reset_index()

		for x in range(num_rows):

			row_no_list = []
			row_no = 0

			for y in common_main:
				row_no_list += list(np.where(main_factor[y] == result.at[x, y])[0])

			row_no = statistics.mode(row_no_list)
			val1 = main_factor.at[row_no, 'p']
			row_no_list = []
			row_no = 0

			for y in common_other:
				row_no_list += list(np.where(other_factor[y] == result.at[x, y])[0])

			row_no = statistics.mode(row_no_list)

			val2 = other_factor.at[row_no, 'p']

			result.at[x, 'p'] = val1 * val2

		print('Finished multiplying: \n', result)
		return (result)


	def create_cpt(self, variables):
		print('Creating CPT from: ', variables, '\n')

		new_cpt = pd.DataFrame(columns=variables)

		num_vars = len(variables)
		num_rows = 2 ** (num_vars - 1)

		for x in range(num_rows):
			new_cpt = new_cpt.append(pd.Series(), ignore_index=True)

		for x in range(num_vars - 1):
			for y in range(0, num_rows, 2 ** (num_vars - 2 - x)):
				for z in range(2 ** (num_vars - 2 - x)):
					if y % 2 ** (num_vars - x - 1) == 0:
						new_cpt.iat[y + z, x] = False
					else:
						new_cpt.iat[y + z, x] = True
		return new_cpt


	paths_before = []


	def d_sep(self, start: str, target: str, evidence: list):
		print("X = ", start, "  Y = ", target, "   Z =", evidence)
		BN_pruned = self.prune(evidence, dsepmode=True, start=start, target=target)

		intergraph = BN_pruned.get_interaction_graph()

		if nx.has_path(intergraph, start, target):
			return False
		else:
			return True


		def get_paths(self, start, target, path_so_far):
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
		if len(neighbours) == 0: return None

		for neighbour in neighbours:
			# if self.get_paths(neighbour, target, path_so_far) is None:
			#    path_so_far.pop()
			if self.get_paths(neighbour, target, path_so_far) is not None:
				return path_so_far


	def prune(self, evidence, dsepmode=False, start=None, target=None):
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
					if target == j:
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

		# sorted_values = sorted(edges.values())  # Sort the values
		# sorted_dict = {}
		# for i in sorted_values:
		#     for k in edges.keys():
		#         if edges[k] == i:
		#             sorted_dict[k] = edges[k]
		#             break

		#print(edges)
		print(edges_sorted)
		#print(order_min_degree)

		return (order_min_degree)


	# print(sorted_dict)


	def order_min_fill(self, return_dict=False):
		"""
		Method to return the order of min fill
		Takes in self
		Output: dict containing the min_fill value per node
		"""
		intergraph = self.bn.get_interaction_graph()
		#nx.draw(intergraph, with_labels=True)
		plt.show()
		vars = intergraph.nodes
		print('vars = ', vars)
		min_fill = dict.fromkeys(vars, 0)

		for var in vars:
			neighbours = list(intergraph.neighbors(var))
			print('neighbours ', var, ' are ', neighbours)
			if len(neighbours) <= 1:
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
						counter += 1

				checked.append(neighbour)
			min_fill[var] = counter

		if return_dict: return min_fill

		print(min_fill)
		edges_sorted = dict(sorted(min_fill.items(), key=lambda item: item[1]))
		order_min_fill = list(edges_sorted.keys())

		return order_min_fill

	def order_random(self):
		random_order = deepcopy(self.variables)
		random.shuffle(random_order)
		return random_order

def main():
	print('\nSTARTING...\n')

	test_Q = ['X']
	test_E = ['Y']
	x = 0
	y = 0

	test_net = BNReasoner(
		'/home/rik/Desktop/Jong_Master/Knowledge Representation/PGM/KR21_project2/testing/lecture_example2.BIFXML')

	# test_net.bn.draw_structure()

	test_net.variables = test_net.bn.get_all_variables()
	test_net.elim_order = test_net.order_random()
	

	print(test_net.mpe(test_Q, test_E))
	#print('MIN_FILL')
	#print(test_net.order_min_fill())
	#print('MIN_DEGREE')
	#print(test_net.order_min_degree())

main()
