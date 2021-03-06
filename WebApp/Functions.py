import numpy as np
import pandas as pd
from sklearn.neighbors.kde import KernelDensity
from sklearn import preprocessing
from operator import itemgetter
import copy


def model_overview(pre_proc_file):
	pre_data = pd.read_csv(pre_proc_file).values

	total_count = pre_data.shape[0]
	
	changes_count = 0
	key_count = 0

	tp_count = 0
	fp_count = 0

	tn_count = 0
	fn_count = 0

	for sample in pre_data:

		if sample[2]== "TP":
			tp_count += 1

		elif sample[2]== "FP":
			fp_count += 1
 
		elif sample[2] == "TN":
			tn_count += 1

		elif sample[2] == "FN":
			fn_count += 1


		if sample[3] > 0:
			key_count += 1

		if sample[4] > 0:
			changes_count += 1


	# print("-- Model Summary --")

	# print("Total # of samples:", total_count)
	# print()
	# print("True Positive:",tp_count)
	# print("False Positive:",fp_count)
	# print("True Negative:",tn_count)
	# print("False Negative:",fn_count)
	# print()
	# print("Key Features:",key_count)
	# print("Changes",changes_count)



def separate_bins_feature(feat_column,special_case = False):
	no_bins = 10

	if special_case:
		# -- Solves the two special cases --
		max_val = 7
		min_val = 0
		single_bin = 1

	else:
		# -- All other cases --
		feat_column = feat_column.flatten()
		two_std = 2*np.std(feat_column)
		avg_val = np.mean(feat_column)

		# -- Finding the Range --
		if (avg_val - two_std < 0):
			min_val = 0
		else:
			min_val = round((avg_val - two_std),0)
		max_val = round((avg_val + two_std),0)

		# -- Creating the Bins --
		single_bin = (max_val - min_val) // no_bins
		if (single_bin == 0):
			single_bin = 1
	
	centre = min_val + (single_bin // 2)
	floor = min_val
	ceil = min_val + single_bin

	ranges = []
	bins = np.zeros(10)
	new_col = np.zeros(feat_column.shape[0])
	new_col_vals = np.zeros(feat_column.shape[0])

	for i in range(no_bins):
		range_str = ""
		if (centre <= max_val):
			for val_i in range(feat_column.shape[0]):
					if (i == 0):
						range_str = "x < " + str(ceil)
						if (feat_column[val_i] < ceil):
							new_col[val_i] = i
							new_col_vals[val_i] = centre

					elif (i == no_bins-1) or ((centre + single_bin) > max_val):
						range_str = str(floor) + " < x"
						if (feat_column[val_i] >= floor):
							new_col[val_i] = i
							new_col_vals[val_i] = centre

					else:
						range_str = str(floor) +" < x < " + str(ceil)
						if ((ceil > feat_column[val_i]) and (feat_column[val_i] >= floor)):
							new_col[val_i] = i
							new_col_vals[val_i] = centre
			bins[i] = centre
			ranges.append(range_str)
		
		else:
			bins[i] = -1
			ranges.append("-1")


		floor += single_bin
		ceil += single_bin
		centre += single_bin

	return bins, new_col, new_col_vals, ranges

def divide_data_bins(data, special=[]):
    no_feat = data.shape[1]
    bins_centred = []
    X_pos_array = []
    in_vals = []
    
    for i in range(no_feat):
        # Handles special case
        bins, new_col, val = separate_bins_feature(data[:,i].flatten(),(i in special))[:3]
        
        in_vals.append(val)
        bins_centred.append(bins)
        X_pos_array.append(new_col)
        
    # Convert to numpy array
    in_vals = np.array(in_vals).transpose()
    bins_centred = np.array(bins_centred)
    X_pos_array = (np.array(X_pos_array)).transpose() 

    return bins_centred, X_pos_array, in_vals

def prepare_for_analysis(filename):
	data_array = pd.read_csv(filename,header=None).values

	# -- Removes the columns with all -9 values -- 
	row_no = 0 
	for row in data_array:
		for col_i in range(1,row.shape[0]):
			if (row[col_i] == -9):
				remove = True
			else:
				remove = False
				break

		if remove:
			data_array = np.delete(data_array, row_no, 0)

		else:
			row_no += 1

	return data_array

def sample_transf(X):
    trans_dict = {}
    my_count = 0
    for sample in range(10459):
        if X[sample][0] != -9:
            trans_dict[str(sample)] = my_count
            my_count += 1
        else:
            trans_dict[str(sample)] = -9

    return trans_dict


def occurance_counter(pre_proc_file):
	# --- Finds how many changes and anchors there are in ratio form ---
	pre_data = pd.read_csv(pre_proc_file).values

	count_array = np.zeros((23,4))
	ratio_array = np.zeros((23,4))
	total = 0


	for sam in range(pre_data.shape[0]):
		total += 1
		for anc in range(5,9):
			col = pre_data[sam][anc]
			if col >= 0:
				if pre_data[sam][1] > 0.5:
					count_array[col][0] += 1
				else: 
					count_array[col][1] += 1

		for chn in range(9,14):
			col = pre_data[sam][chn]
			if col >= 0:

				if pre_data[sam][chn+5] >= 0:
					count_array[col][2] += 1
				else:
					count_array[col][3] += 1
	
	ratio_array = count_array				
	# ratio_array = count_array/total			
	# for i in range(ratio_array.shape[1]):
	# 	ratio_array
	return ratio_array

def my_combinations(target,data,limit):
	# --- Finds the mathematical combinations using recursion ---
	result = []
	for i in range(len(data)):
		new_target = copy.copy(target)
		new_data = copy.copy(data)
		new_target.append(data[i])
		new_data = data[i+1:]
		if (4 >= len(new_target) >= limit):
			result.append(new_target)
		result += my_combinations(new_target,new_data,limit)
	return result

def combination_finder(pre_proc_file,cols_lst,anchs):
	# --- Finds all the combinations with the desired columns --- 

	# print(cols_lst)
	pre_data = pd.read_csv(pre_proc_file).values
	all_combinations = {}

	samples_list = []

	for sample in range(pre_data.shape[0]):

		cur_lst = []

		if (anchs):
			range_val = range(5,9)
		else:
			range_val = range(9,14)
		for c in range_val:
			val = pre_data[sample][c]
			if (val < 0 or len(cur_lst) > 5):
				break
			cur_lst.append(val)

		if (set(cols_lst).issubset(cur_lst)):
			new_key = ','.join(str(x) for x in cols_lst)
			if new_key in all_combinations:
				all_combinations[new_key] += 1
			else:
				all_combinations[new_key] = 1

			left_over = [x for x in cur_lst if (x not in cols_lst)]

			if len(left_over) > 0:
				possible_combs = my_combinations([],left_over,0)

			# -- Add the leftovers -- 
				for ending in possible_combs:
					sorted_cols = sorted(cols_lst+ending)
					new_key = ','.join(str(x) for x in sorted_cols)
					if new_key in all_combinations:
						all_combinations[new_key] += 1
					else:
						all_combinations[new_key] = 1


	tuple_result = []
	for one_case in all_combinations:
		lst_case = one_case.split(',')
		tuple_result.append((lst_case,all_combinations[one_case]))
		tuple_result = sorted(tuple_result, key=itemgetter(1), reverse=True)

	final_result = []
	for item_pair in tuple_result:
		string_result = [int(x) for x in item_pair[0]]
		final_result.append(string_result)

	return final_result

def ids_with_combination(pre_proc_file,cols_lst,anchs):
	# --- Finds all the combinations with the desired columns --- 

	# print(cols_lst)
	pre_data = pd.read_csv(pre_proc_file).values
	all_combinations = {}

	samples_list = []

	for sample in range(pre_data.shape[0]):

		cur_lst = []

		if (anchs):
			range_val = range(5,9)
		else:
			range_val = range(9,14)
		for c in range_val:
			val = pre_data[sample][c]
			if (val < 0 or len(cur_lst) > 5):
				break
			cur_lst.append(val)

		if (set(cols_lst).issubset(cur_lst)):
			samples_list.append(pre_data[sample][0])

	return samples_list

def changes_generator(pre_proc_file,desired_cols):
	# --- Generates the list of lists needed for D3 visualisation ---
	# --- Also outputs list of sample lists needed for global vis --- 

	total_change_no = 2826

	pre_data = pd.read_csv(pre_proc_file).values

	global_samples = []

	all_changes = []
	all_counts = []
	all_per = []

	no_of_cols = len(desired_cols)
	changes_lst = [0]*(no_of_cols) #Last column is count

	matches = 0

	# -- Finding all the change combinations --
	for sam in range(pre_data.shape[0]):
		for test in range(9,14):
			if (pre_data[sam][test] in desired_cols):
				changes_lst[matches] = pre_data[sam][test+5]
				matches += 1

				if (matches == no_of_cols):
					if (changes_lst in all_changes):
						idx = all_changes.index(changes_lst)
						all_counts[idx] += 1
						global_samples[idx].append(pre_data[sam][0])
					else:
						all_changes.append(changes_lst)
						all_counts.append(1)
						all_per.append(int(np.round(pre_data[sam][1],0)))

						global_samples.append([pre_data[sam][0]])

		# - Resets changes list -
		changes_lst = [0]*no_of_cols
		matches = 0


	if (all_changes == []):
		return None

	# --- Sorting by counts ---
	sorted_changes = []
	sorted_counts = []
	sorted_per = []	
	sorted_global = []

	keySort = np.argsort(all_counts)[::-1]

	for key in keySort:
		sorted_changes.append(all_changes[key])
		sorted_counts.append(all_counts[key])
		sorted_per.append(all_per[key])
		sorted_global.append(global_samples[key])

	all_changes = sorted_changes
	all_counts = sorted_counts
	all_per	= sorted_per
	global_samples = sorted_global

	names = ["External Risk Estimate", 
                      "Months Since Oldest Trade Open",
                      "Months Since Last Trade Open",
                      "Average Months in File",
                      "Satisfactory Trades",
                      "Trades 60+ Ever",
                      "Trades 90+ Ever",
                      "% Trades Never Delq.",
                      "Months Since Last Delq.",
                      "Max Delq. Last 12M",
                      "Max Delq. Ever",
                      "Total Trades",
                      "Trades Open Last 12M",
                      "% Installment Trades",
                      "Months Since Most Recent Inq",
                      "Inq Last 6 Months",
                      "Inq Last 6 Months exl. 7 days",
                      "Revolving Burden",
                      "Installment Burden",
                      "Revolving Trades w/ Balance:",
                      "Installment Trades w/ Balance",
                      "Bank Trades w/ High Utilization Ratio",
                      "% Trades w/ Balance"]

	total_count = np.sum(all_counts)
	all_dicts = []
	# for i in range(all_counts.shape[0]):
	for i in range(len(all_counts)):
		single_dicts = []
		single_change = all_changes[i]

		for n in range(len(single_change)):
			result = {}
			result["name"] = names[desired_cols[n]]
			result["label"] = "Ft." + str(n+1)
			result["inc_change"] = int(single_change[n])
			result["occ"] = float(np.round((all_counts[i]/total_count),2))
			result["number_of"] = float(np.round((all_counts[i])))
			result["total_ratio"] = float(np.round((total_count/total_change_no),2))
			result["total_no"] = float(np.round((total_count)))
			result["per"] = float(all_per[i])
			result["id_list"] = global_samples[i]

			single_dicts.append(result)

		all_dicts.append(single_dicts)

	global_samples = list(global_samples)
	# print("--- Global ---")
	# print(global_samples)
	return [all_dicts, global_samples]
	# return all_dicts

def anchor_generator(pre_proc_file, all_data_file, anchs_lst):
	pre_data = pd.read_csv(pre_proc_file).values
	all_data = pd.read_csv(all_data_file,header=None).values[:,1:]

	samples_list = []

	# -- A list of sample IDs which are used to draw global explanations --
	good_samples = []
	bad_samples = []

	good_ones = []
	bad_ones = []

	# -- Find samples with the desired anchs -- 

	for sample in range(pre_data.shape[0]):
		test_case = []
		for test in range(5,9):
			if (pre_data[sample][test] < 0):
				break
			test_case.append(pre_data[sample][test])

		if (set(anchs_lst).issubset(test_case)):
			samples_list.append(pre_data[sample][0])
			if ((pre_data[sample][1])> 0.5):
				good_ones.append(pre_data[sample])
			else:
				bad_ones.append(pre_data[sample])


	good_ones = np.array(good_ones)
	bad_ones = np.array(bad_ones)

	# -- Sort the List -- 
	if good_ones.shape[0] != 0:
		good_ones = good_ones[(-good_ones[:,1]).argsort()]

	if bad_ones.shape[0] != 0:
		bad_ones = bad_ones[bad_ones[:,1].argsort()]


	names = ["External Risk Estimate", 
                      "Months Since Oldest Trade Open",
                      "Months Since Last Trade Open",
                      "Average Months in File",
                      "Satisfactory Trades",
                      "Trades 60+ Ever",
                      "Trades 90+ Ever",
                      "% Trades Never Delq.",
                      "Months Since Last Delq.",
                      "Max Delq. Last 12M",
                      "Max Delq. Ever",
                      "Total Trades",
                      "Trades Open Last 12M",
                      "% Installment Trades",
                      "Months Since Most Recent Inq",
                      "Inq Last 6 Months",
                      "Inq Last 6 Months exl. 7 days",
                      "Revolving Burden",
                      "Installment Burden",
                      "Revolving Trades w/ Balance:",
                      "Installment Trades w/ Balance",
                      "Bank Trades w/ High Utilization Ratio",
                      "% Trades w/ Balance"]
	

	names_dicts = []
	# -- Creating Labels Dictionary -- 
	for col_ind in range(len(anchs_lst)):
		one_dict = {}
		one_dict["name"] = names[anchs_lst[col_ind]]
		one_dict["label"] = col_ind + 1
		names_dicts.append(one_dict)

	# -- Create Dictionaries
	squares_dicts = []
	good_dicts = []
	for row in good_ones:
		one_dict = {}

		one_dict["per"] = row[1]
		one_dict["id"] = row[0]

		good_samples.append(row[0])

		good_dicts.append(one_dict)
		squares_dicts.append(one_dict)
		
	bad_dicts = []
	for row in bad_ones:
		one_dict = {}

		one_dict["per"] = row[1]
		one_dict["id"] = row[0]
		bad_samples.append(row[0])

		bad_dicts.append(one_dict)
		squares_dicts.append(one_dict)

	# return names_dicts,squares_dicts,good_samples,bad_samples
	# return names_dicts,squares_dicts
	return names_dicts, good_dicts, bad_dicts, good_samples, bad_samples

def prep_for_D3_global(pre_proc_file,all_data_file,samples,bins_centred,positions,transform):

	names = ["External Risk Estimate", 
                      "Months Since Oldest Trade Open",
                      "Months Since Last Trade Open",
                      "Average Months in File",
                      "Satisfactory Trades",
                      "Trades 60+ Ever",
                      "Trades 90+ Ever",
                      "% Trades Never Delq.",
                      "Months Since Last Delq.",
                      "Max Delq. Last 12M",
                      "Max Delq. Ever",
                      "Total Trades",
                      "Trades Open Last 12M",
                      "% Installment Trades",
                      "Months Since Most Recent Inq",
                      "Inq Last 6 Months",
                      "Inq Last 6 Months exl. 7 days",
                      "Revolving Burden",
                      "Installment Burden",
                      "Revolving Trades w/ Balance:",
                      "Installment Trades w/ Balance",
                      "Bank Trades w/ High Utilization Ratio",
                      "% Trades w/ Balance"]

	pre_data = pd.read_csv(pre_proc_file).values
	all_data = pd.read_csv(all_data_file,header=None).values[:,1:]

	final_data = []

	
	for s in samples:

		s -= 1
		single_dict_list = []
		for i in range(all_data.shape[1]):
			result = {}
			result["name"] = names[i]
			result["incr"] = 0 
			result["per"] = pre_data[s][1]
			result["anch"] = 0

			val = all_data[s][i].round(0)
			change = val

	        # -- Identify Anchors --
			for an in range(5,9):
				col = pre_data[s][an]
				if (i == col):
					result["anch"] = 1

			# -- Find Change -- 
			for a in range(9,14):
				col = pre_data[s][a]
				if (i == col):

					new_sample_ind = int(transform[str(s)])
					idx = positions[new_sample_ind][col]
					increments = pre_data[s][a+5]
					change = bins_centred[i][int(idx+increments)]



			max_bin = np.max(bins_centred[i])
			min_bin = np.min(bins_centred[i])

			if (min_bin == -1):
				min_bin = 0

			if (max_bin < 10):
				max_bin = 10

			scl_val = ((val-min_bin)/(max_bin-min_bin)).round(2)
			scl_change = ((change-min_bin)/(max_bin-min_bin)).round(2)

			if (scl_val < 0 ):
				scl_val = 0
			if (scl_change < 0):
				scl_change = 0

			result["val"] = int(val)
			result["scl_val"] = float(scl_val)
			result["change"] = int(change)
			result["scl_change"] = float(scl_change)

			single_dict_list.append(result)
			
		final_data.append(single_dict_list)

	return final_data

def prep_for_D3_aggregation(pre_proc_file,all_data_file,samples,bins_centred,positions,transform,sort = False):

	names = ["External Risk Estimate", 
                      "Months Since Oldest Trade Open",
                      "Months Since Last Trade Open",
                      "Average Months in File",
                      "Satisfactory Trades",
                      "Trades 60+ Ever",
                      "Trades 90+ Ever",
                      "% Trades Never Delq.",
                      "Months Since Last Delq.",
                      "Max Delq. Last 12M",
                      "Max Delq. Ever",
                      "Total Trades",
                      "Trades Open Last 12M",
                      "% Installment Trades",
                      "Months Since Most Recent Inq",
                      "Inq Last 6 Months",
                      "Inq Last 6 Months exl. 7 days",
                      "Revolving Burden",
                      "Installment Burden",
                      "Revolving Trades w/ Balance:",
                      "Installment Trades w/ Balance",
                      "Bank Trades w/ High Utilization Ratio",
                      "% Trades w/ Balance"]
                      
	pre_data = pd.read_csv(pre_proc_file).values
	all_data = pd.read_csv(all_data_file,header=None).values[:,1:]

	final_data = []

	
	for s in samples:
		s -= 1
		single_dict_list = []
		for i in range(all_data.shape[1]):
			result = {}
			result["name"] = names[i]
			result["incr"] = 0 

			if pre_data[s][1] > 0.5:
				result["dec"] = 1
			else:
				result["dec"] = 0

			val = all_data[s][i].round(0)
			change = val

	        # -- Identify Anchors --
			for an in range(5,9):
				col = pre_data[s][an]
				if (i == col):
					result["anch"] = 1

			# -- Find Change -- 
			for a in range(9,14):
				col = pre_data[s][a]
				if (i == col):

					new_sample_ind = int(transform[str(s)])
					idx = positions[new_sample_ind][col]
					increments = pre_data[s][a+5]
					change = bins_centred[i][int(idx+increments)]



			max_bin = np.max(bins_centred[i])
			min_bin = np.min(bins_centred[i])

			if (min_bin == -1):
				min_bin = 0

			if (max_bin < 10):
				max_bin = 10

			scl_val = ((val-min_bin)/(max_bin-min_bin)).round(2)
			scl_change = ((change-min_bin)/(max_bin-min_bin)).round(2)

			if (scl_val < 0 ):
				scl_val = 0
			if (scl_change < 0):
				scl_change = 0

			result["scl_val"] = float(scl_val)
			result["scl_change"] = float(scl_change)

			single_dict_list.append(result)
			
		final_data.append(single_dict_list)

	# return final_data
	final_data = np.array(final_data)
	# return(final_data.tolist())
	
	# -- Sorting based on the number of arrows -- 
	if sort == True:
		count_list = np.zeros((final_data.shape[1],))
		for c in range(final_data.shape[1]):
			col = final_data[:,c]
			count = 0
			for sample in col:
				if sample['scl_val'] != sample['scl_change']:
					count += 1

			count_list[c] = count

		keySort = np.argsort(count_list)[::-1]

		final_result = np.array([])

		for key in keySort:
			if final_result.any() == False:
				final_result = final_data[:,key].reshape(-1,1)
			else:
				final_result = np.append(final_result,final_data[:,key].reshape(-1,1), axis = 1)

		return final_result.tolist()
	
	else:
		return final_data.tolist()

def populate_violin_plot(pos_array, id_list, transform, monot=False,):

	names = ["External Risk Estimate", 
				"Months Since Oldest Trade Open",
				"Months Since Last Trade Open",
				"Average Months in File",
				"Satisfactory Trades",
				"Trades 60+ Ever",
				"Trades 90+ Ever",
				"% Trades Never Delq.",
				"Months Since Last Delq.",
				"Max Delq. Last 12M",
				"Max Delq. Ever",
				"Total Trades",
				"Trades Open Last 12M",
				"% Installment Trades",
				"Months Since Most Recent Inq",
				"Inq Last 6 Months",
				"Inq Last 6 Months exl. 7 days",
				"Revolving Burden",
				"Installment Burden",
				"Revolving Trades w/ Balance:",
				"Installment Trades w/ Balance",
				"Bank Trades w/ High Utilization Ratio",
				"% Trades w/ Balance"]

	monot_array = np.array([1,1,1,1,1,0,0,1,1,1,1,-1,0,-1,1,0,0,0,0,-1,-1,0,-1])

	all_graphs = []

	total_length = pos_array.shape[0]
	id_length = id_list.shape[0]

	for col in range(pos_array.shape[1]):

		# -- Creating 10 empty dictionaries -- 
		single_graph = []

		for i in range(10):
			single_graph.append({'bin':str(i+1), "left":0, "right":0})


		# -- Incramenting total counts --
		column = pos_array[:,col]

		for bin_no in column:
			single_graph[9-int(bin_no)]['right'] += 1


		# -- Incramenting relative counts -- 
		for id_no in id_list:
			id_no = int(transform[str(id_no)])

			to_incrament = 9-column[id_no-1]   # CHECK IF THIS IS CORRECT!!!
			single_graph[int(to_incrament)]['left'] += 1  # assuming 1 indexing


		all_graphs.append(single_graph)


	# -- Scaling the graphs with relative sizes -- 
	for each_graph in all_graphs:
		max_left = 0
		max_right = 0

		for pos in each_graph:
			if pos['right'] > max_right:
				max_right = pos['right']

			if pos['left'] > max_left:
				max_left = pos['left']

		
		for pos in each_graph:
			pos['right'] = pos['right']/max_right
			pos['left'] = pos['left']/max_left


	return all_graphs




def kernel_density(X,samples,transform):

	all_kernels = []
	partial_kernels = []


	# --- Identifying sample densities --- 
	transformed_samples = []
	for s in samples:
		transformed_samples.append(int(transform[str(s)]))

	filtered_X = X[transformed_samples]

	col_mean, col_median, sam_mean, sam_median = [], [], [], []

	for c in range(X.shape[1]):

		# --- Isolate feature column --- 
		col = X[:,c]  # All samples
		sam = filtered_X[:,c]  # Select samples


		# --- Set paramaters --- 
		max_val = max(10,np.amax(col))
		min_val = min(0,np.amin(col))
		scale = max_val+1 - min_val

		fineness = 1000


		# --- Reshaping --- 
		col = np.reshape(col, (col.shape[0],1))
		sam = np.reshape(sam, (sam.shape[0],1))

		X_axis = np.linspace(min_val,max_val,fineness)[:, np.newaxis]


		# --- Estimate density --- 
		kde_col = KernelDensity(kernel='gaussian', bandwidth=scale/20).fit(col)
		kde_sam = KernelDensity(kernel='gaussian', bandwidth=scale/20).fit(sam)
		log_dens_col = kde_col.score_samples(X_axis)
		log_dens_sam = kde_sam.score_samples(X_axis)

		kernel_col = np.exp(log_dens_col)
		kernel_sam = np.exp(log_dens_sam)


		# --- Normalize and Convert --- 
		min_max_scaler = preprocessing.MinMaxScaler(copy=True, feature_range=(0, 1))

		kernel_col = np.reshape(kernel_col, (kernel_col.shape[0],1))
		kernel_sam = np.reshape(kernel_sam, (kernel_sam.shape[0],1))

		kernel_col = min_max_scaler.fit_transform(kernel_col)
		kernel_sam = min_max_scaler.fit_transform(kernel_sam)


		kernel_col = [0]+kernel_col.flatten().tolist()+[0]
		kernel_sam = [0]+kernel_sam.flatten().tolist()+[0]


		# # --- Needed to optimize graph --- 
		# kernel_col.append(0)
		# kernel_sam.append(0)

		all_kernels.append(kernel_col)
		partial_kernels.append(kernel_sam)

		

		# --- Estimate statistics values --- 
		col_mean.append(np.mean(col))
		col_median.append(np.median(col))
		
		sam_mean.append(np.mean(sam))
		sam_median.append(np.median(sam))


	return all_kernels, partial_kernels, sam_median, col_median




def all_kernel_densities(X):

	names = ["External Risk Estimate", 
			"Months Since Oldest Trade Open",
			"Months Since Last Trade Open",
			"Average Months in File",
			"Satisfactory Trades",
			"Trades 60+ Ever",
			"Trades 90+ Ever",
			"% Trades Never Delq.",
			"Months Since Last Delq.",
			"Max Delq. Last 12M",
			"Max Delq. Ever",
			"Total Trades",
			"Trades Open Last 12M",
			"% Installment Trades",
			"Months Since Most Recent Inq",
			"Inq Last 6 Months",
			"Inq Last 6 Months exl. 7 days",
			"Revolving Burden",
			"Installment Burden",
			"Revolving Trades w/ Balance:",
			"Installment Trades w/ Balance",
			"Bank Trades w/ High Utilization Ratio",
			"% Trades w/ Balance"]

	all_kernels = []

	col_mean, col_median = [], []

	for c in range(X.shape[1]):

		# --- Isolate feature column --- 
		col = X[:,c]  # All samples


		# --- Set paramaters --- 
		max_val = max(10,np.amax(col))
		min_val = min(0,np.amin(col))
		scale = max_val+1 - min_val
		fineness = 1000

		# --- Reshaping --- 
		col = np.reshape(col, (col.shape[0],1))
		X_axis = np.linspace(min_val,max_val,fineness)[:, np.newaxis]

		# --- Estimate density --- 
		kde_col = KernelDensity(kernel='gaussian', bandwidth=scale/20).fit(col)
		log_dens_col = kde_col.score_samples(X_axis)
		kernel_col = np.exp(log_dens_col)

		# --- Normalize and Convert --- 
		min_max_scaler = preprocessing.MinMaxScaler(copy=True, feature_range=(0, 1))

		kernel_col = np.reshape(kernel_col, (kernel_col.shape[0],1))
		kernel_col = min_max_scaler.fit_transform(kernel_col)

		kernel_col = [0]+kernel_col.flatten().tolist()+[0]

		# --- Single Dictionary --- 

		one_dict = {'name':names[c], 'data':kernel_col}
		
		all_kernels.append(one_dict)

		# --- Estimate statistics values ---

		med_val = np.median(col)/(max_val-min_val)
		mean_val = np.mean(col)/(max_val-min_val) 
		
		col_mean.append(mean_val)
		col_median.append(med_val)

	

	return all_kernels, col_median, col_mean

def specific_kernel_densities(X,samples,transform):
	partial_kernels = []

	names = ["External Risk Estimate", 
			"Months Since Oldest Trade Open",
			"Months Since Last Trade Open",
			"Average Months in File",
			"Satisfactory Trades",
			"Trades 60+ Ever",
			"Trades 90+ Ever",
			"% Trades Never Delq.",
			"Months Since Last Delq.",
			"Max Delq. Last 12M",
			"Max Delq. Ever",
			"Total Trades",
			"Trades Open Last 12M",
			"% Installment Trades",
			"Months Since Most Recent Inq",
			"Inq Last 6 Months",
			"Inq Last 6 Months exl. 7 days",
			"Revolving Burden",
			"Installment Burden",
			"Revolving Trades w/ Balance:",
			"Installment Trades w/ Balance",
			"Bank Trades w/ High Utilization Ratio",
			"% Trades w/ Balance"]

	# --- Identifying sample densities --- 
	transformed_samples = []
	for s in samples:
		transformed_samples.append(int(transform[str(s)]))

	filtered_X = X[transformed_samples]

	sam_mean, sam_median = [], []

	for c in range(X.shape[1]):

		# --- Isolate feature column --- 
		col = X[:,c]  # All samples
		sam = filtered_X[:,c]  # Select samples


		# --- Set paramaters --- 
		max_val = max(10,np.amax(col))
		min_val = min(0,np.amin(col))
		scale = max_val+1 - min_val

		fineness = 1000

		# --- Reshaping --- 
		sam = np.reshape(sam, (sam.shape[0],1))

		X_axis = np.linspace(min_val,max_val,fineness)[:, np.newaxis]


		# --- Estimate density --- 
		kde_sam = KernelDensity(kernel='gaussian', bandwidth=scale/20).fit(sam)
		log_dens_sam = kde_sam.score_samples(X_axis)

		kernel_sam = np.exp(log_dens_sam)


		# --- Normalize and Convert --- 
		min_max_scaler = preprocessing.MinMaxScaler(copy=True, feature_range=(0, 1))

		kernel_sam = np.reshape(kernel_sam, (kernel_sam.shape[0],1))

		kernel_sam = min_max_scaler.fit_transform(kernel_sam)

		kernel_sam = [0]+kernel_sam.flatten().tolist()+[0]


		# --- Single Dictionary --- 

		one_dict = {'name':names[c], 'data':kernel_sam}
		
		partial_kernels.append(one_dict)

		# --- Estimate statistics values ---

		med_val = np.median(sam)/(max_val-min_val)
		mean_val = np.mean(sam)/(max_val-min_val) 
		
		sam_mean.append(mean_val)
		sam_median.append(med_val)


	return partial_kernels, sam_median, sam_mean



if __name__ == '__main__':
    vals = pd.read_csv("static/data/final_data_file.csv", header=None).values
    X = vals[:,1:]
    y = vals[:,0]

    vals_no_9 = prepare_for_analysis("static/data/final_data_file.csv")
    X_no_9 = vals_no_9[:,1:]

    no_samples, no_features = X.shape


    bins_centred, X_pos_array, init_vals = divide_data_bins(X_no_9,[9,10])
    # density_array = scaling_data_density(X_no_9, bins_centred)
    # print(len(density_array))

    proj_samples = [x+1 for x in range(1000)]

    trans = sample_transf(X)

    # prep_for_D3_aggregation("static/data/pred_data_x.csv","static/data/final_data_file.csv", proj_samples, bins_centred, X_pos_array, trans, True)
    # result = populate_violin_plot(X_pos_array, np.array([1,2,3,4,5,6,7]),trans)

    # all_den, select_den, all_median , select_median = kernel_density(X_no_9, [1,2,3,4,5],trans)   # Density Code!!
    all_den, all_median, all_mean = all_kernel_densities(X_no_9)
    select_den, select_median, select_mean = specific_kernel_densities(X_no_9, [1,2,3,4,5],trans)

    # count_total = occurance_counter("static/data/pred_data_x.csv")
    # sample_transf()

