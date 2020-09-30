#!/usr/bin/env python
# coding: utf-8

# In[4]:


import pandas as pd
import numpy as np
import itertools
from collections import Counter

from scipy import stats
from statsmodels.stats import weightstats as stests
from scipy.stats import ttest_ind
from scipy.stats import mannwhitneyu

import matplotlib.pyplot as plt
import pylab as pl

import pickle


# In[5]:


def data_preprocessing(data):
    print('Data preprocessing starts...')
    print('Data preprocessing done!')
    col_list = data._get_numeric_data().columns
    for col in col_list:
        data[col].replace(np.NaN,data[col].mean())
    return data


# <h1>Conflict Trivia</h1>

# In[6]:


def conflict_create_subgroups(data, attribute_list, prune_threshold):
    print('    Conflict create subgroups started...')
    prune_subgroup = []
    unique_list = []
    subgroup_list = []
    subgroup_type_value_list = []
    attribute_unique_value_list = []
    all_subgroup_list = []
    prune_subgroup_list = []
    number_list = [i for i in range(len(attribute_list))]
    for i in range(len(attribute_list)):
        all_combination_list = list(itertools.combinations(number_list, i+1))
        for all_combination in all_combination_list:
            modified_data = data.copy()
            combination_list = []
            attribute_type_list = []
            for all_combination_value in all_combination:
                unique_list  = data[attribute_list[all_combination_value]].unique()
                for prune in prune_subgroup:
                    for each_prune in prune:
                        if each_prune in unique_list:
                            unique_list = np.delete(unique_list, np.where(unique_list == each_prune))
                combination_list.append(unique_list)
                attribute_type_list.append(attribute_list[all_combination_value])
            subgroup_list = list(itertools.product(*combination_list))
            subgroup_list.sort()
            prune_subgroup_list = []
            for subgroup in subgroup_list:
                i = 0
                modified_data = data.copy()
                for each_subgroup in subgroup:
                    modified_data = modified_data[modified_data[attribute_type_list[i]] == each_subgroup]
                    i = i + 1
                if(modified_data.shape[0] >= prune_threshold):
                    prune_subgroup_list.append(list(subgroup))
                else:
                    prune_subgroup.append(list(subgroup))
            for subgroup in prune_subgroup_list:
                subgroup_type_value_list.append([attribute_type_list, subgroup])
    print('    Conflict create subgroups done!')
    return subgroup_type_value_list


# In[7]:


def conflict_check_interestingness(subgroup1, subgroup2):
    pval_array = [0, 0, 0]
    ##################Z-Test##################
    ztest, pval1 = stests.ztest(subgroup1, subgroup2, value=0, alternative='two-sided')
    pval_array[0] = pval1
    #################T-Test##################
    ttest, pval2 = ttest_ind(subgroup1, subgroup2)
    pval_array[1] = pval2
    ##############Mann Whiteney U Test############
    stat, pval3 = mannwhitneyu(subgroup1, subgroup2)
    pval_array[2] = pval3
    #########################################
    return pval_array


# In[8]:


def conflict_export_results(result_df):
    print('    Conflict export results started...')
    conflict_trivia_df = pd.DataFrame(columns = ['Trivia'])
    conflict_trivia_evidence_df = pd.DataFrame(columns = ['Overl_dist_graph', 'Stats', 'Test_stats'])
    for i in range(result_df.shape[0]):

        trivia = result_df.iloc[i]

        trivia_string = "Subgroup " + str(trivia['Subgroup1'][1]) + " is interesting."
        row_dict1 = {'Trivia' : trivia_string}
        conflict_trivia_df = conflict_trivia_df.append(row_dict1, ignore_index=True)

        subgroup_list = trivia['Subgroup1_list']
        complement_list = trivia['Subgroup2_list']
        subgroup_stats_dict = {'count':len(subgroup_list), 'mean':np.mean(subgroup_list), 'median':np.median(subgroup_list), 'var':np.var(subgroup_list), 'std':np.std(subgroup_list)}
        complement_stats_dict = {'count':len(complement_list), 'mean':np.mean(complement_list), 'median':np.median(complement_list), 'var':np.var(complement_list), 'std':np.std(complement_list)}
        test_stats_dict = {'ztest':trivia['Z-Test'], 'ttest':trivia['T-Test'], 'mwutest':trivia['Mann Whiteney U Test']}
        row_dict2 = {'Overl_dist_graph':[subgroup_list, complement_list], 'Stats':[subgroup_stats_dict, complement_stats_dict], 'Test_stats':test_stats_dict}
        conflict_trivia_evidence_df = conflict_trivia_evidence_df.append(row_dict2, ignore_index=True)
                
    print('    Conflict export results done!')
    return conflict_trivia_df, conflict_trivia_evidence_df


# In[9]:


def find_confict_trivia(data, attribute_list, measure_list, heuristic_list, heuristic_threshold_list):
    print('Conflict trivia starts...')
    result_df = pd.DataFrame(columns = ['Subgroup1', 'Subgroup2', 'Subgroup1_list', 'Subgroup2_list', 'Z-Test', 'T-Test', 'Mann Whiteney U Test', 'Score'])
    measure_column = measure_list[0]
    size_threshold = heuristic_threshold_list[0]
    total_subgroup_count = 0
    interesting_subgroup_count = 0

    subgroup_list = conflict_create_subgroups(data, attribute_list, size_threshold)
    total_subgroup_count = len(subgroup_list)

    print('    Conflict check interestingness started...')
    for subgroup in subgroup_list:
        total_list = list(data[measure_column])

        subgroup_dataframe = data.copy()
        attribute_list1, attribute_value_list1 = subgroup
        for i in range(len(attribute_list1)):
            subgroup_dataframe = subgroup_dataframe[subgroup_dataframe[attribute_list1[i]] == attribute_value_list1[i]]
        subgroup_list = list(subgroup_dataframe[measure_column])
        
        subgroup_count = DecrementCounter(subgroup_list)
        complement_list = [x for x in total_list if not subgroup_count.decrement(x)]

        pval_array = conflict_check_interestingness(subgroup_list, complement_list)
#         combined_statistic, combined_pvalue = stats.combine_pvalues(pval_array, method='fisher', weights=None)
        count = 0;
        for pval in pval_array:
            if(pval < 0.05):
                count += 1
        if(count >= 2):
            interesting_subgroup_count += 1
            subgroup1 = subgroup
            subgroup2 = 'Complement'
            ztest = round(pval_array[0], 2)
            ttest = round(pval_array[1], 2)
            mwutest = round(pval_array[2], 2)
#             score = round(combined_pvalue, 2)
            score = count
            row_dict = {'Subgroup1' : subgroup1, 'Subgroup2' : subgroup2, 'Subgroup1_list' : subgroup_list, 'Subgroup2_list' : complement_list, 'Z-Test' : ztest, 'T-Test' : ttest, 'Mann Whiteney U Test' : mwutest, 'Score' : score}
            result_df = result_df.append(row_dict, ignore_index=True)
    print('    Conflict check interestingness done!')

    conflict_trivia_df, conflict_trivia_evidence_df = conflict_export_results(result_df)
            
    print('Conflict trivia done!')
    return conflict_trivia_df, conflict_trivia_evidence_df

class DecrementCounter(Counter):
    def decrement(self,x):
        if self[x]:
            self[x] -= 1
            return True
        return False


# <hr>

# <h1>Comparison Trivia</h1>

# In[10]:


def comparison_create_subgroups(data, attribute_list):
    all_subgroup_list = []
    for i in range(len(attribute_list)):
        unique_list = data[attribute_list[i]].unique()
        unique_length = len(unique_list) if len(unique_list) < 3 else 3
        all_combination_list = []
        for j in range(unique_length):
            all_combination_list.extend(map(list,(itertools.combinations(unique_list, j+1))))
        all_subgroup_list.append([attribute_list[i] , all_combination_list])
    return all_subgroup_list


# In[11]:


def comparison_check_interstingness(data, attribute_list, measure_list, subgroup_list, class_attribute, identifier_attribute):
    calculate_measure_dataframe = pd.DataFrame(columns=['Identifier','Identifier_class','Category','Subgroup1','Subgroup2','Measure','Factor','No. of groups','Subgroup1_list','Subgroup2_list'])
    for i in range(len(subgroup_list)):
        sub_list = subgroup_list[i][1]
        for j in range(len(sub_list)):
            subgroup1 = sub_list[j]
            if(len(subgroup1) == 1):
                for k in range(j+1 ,len(sub_list)):
                    if(sub_list[j][0] not in sub_list[k]):
                        subgroup2 = sub_list[k]
                        for measure in measure_list:
                            no_of_groups = len(subgroup2)
                            category = subgroup_list[i][0]
                            factor, subgroup1_list, subgroup2_list, flip = calculate_measure(data, subgroup1, subgroup2, measure, category)
                            if (factor > 500):
                                if (flip == 0):
                                    row_dict = {'Identifier':identifier_attribute, 'Identifier_class':class_attribute, 'Category':category, 'Subgroup1':subgroup1, 'Subgroup2':subgroup2, 'Measure':measure, 'Factor':factor, 'No. of groups':no_of_groups, 'Subgroup1_list':subgroup1_list, 'Subgroup2_list':subgroup2_list}
                                else:
                                    row_dict = {'Identifier':identifier_attribute, 'Identifier_class':class_attribute, 'Category':category, 'Subgroup1':subgroup2, 'Subgroup2':subgroup1, 'Measure':measure, 'Factor':factor, 'No. of groups':no_of_groups, 'Subgroup1_list':subgroup1_list, 'Subgroup2_list':subgroup2_list}
                                calculate_measure_dataframe = calculate_measure_dataframe.append(row_dict, ignore_index=True)
    return calculate_measure_dataframe

def calculate_measure(data, subgroup1, subgroup2, measure, category):
    subgroup1_dataframe =pd.DataFrame(columns=list(data.columns))
    subgroup2_dataframe =pd.DataFrame(columns=list(data.columns))
    for i in range(len(subgroup1)):
        subgroup1_dataframe = subgroup1_dataframe.append(data[data[category] == subgroup1[i]])
    for i in range(len(subgroup2)):
        subgroup2_dataframe = subgroup2_dataframe.append(data[data[category] == subgroup2[i]])     
    subgroup1_total = subgroup1_dataframe[measure].sum(axis = 0)
    subgroup1_count = subgroup1_dataframe.shape[0]
    subgroup1_operation_value = subgroup1_total / subgroup1_count
    subgroup2_total = subgroup2_dataframe[measure].sum(axis = 0)
    subgroup2_count = subgroup2_dataframe.shape[0]
    subgroup2_operation_value = subgroup2_total / subgroup2_count
    if (subgroup2_operation_value // subgroup1_operation_value > 0):
        score = subgroup2_operation_value // subgroup1_operation_value 
        flip = 0
        return score, list(subgroup1_dataframe[measure]), list(subgroup2_dataframe[measure]), flip
    else :
        score = subgroup1_operation_value // subgroup2_operation_value
        flip = 1
        return score, list(subgroup2_dataframe[measure]), list(subgroup1_dataframe[measure]), flip


# In[12]:


def comparison_export_result(result_df):
    print('    Comparison export results started...')
    comparison_trivia_df = pd.DataFrame(columns = ['Trivia'])
    comparison_trivia_evidence_df = pd.DataFrame(columns = ['Overl_dist_graph', 'Stats'])
    for i in range(result_df.shape[0]):

        trivia = result_df.iloc[i]

        trivia_string = 'For ' + trivia['Identifier_class'] + ' ' + trivia['Measure'] + ' of ' + str(trivia['Subgroup1']) + ' is ' + str(trivia['Factor']) + ' times of ' + trivia['Measure'] + ' of ' + str(trivia['Subgroup2']) 
        row_dict1 = {'Trivia' : trivia_string}
        comparison_trivia_df = comparison_trivia_df.append(row_dict1, ignore_index=True)

        subgroup1_list = trivia['Subgroup1_list']
        subgroup2_list = trivia['Subgroup2_list']
        subgroup1_stats_dict = {'count':len(subgroup1_list), 'mean':np.mean(subgroup1_list), 'median':np.median(subgroup1_list), 'var':np.var(subgroup1_list), 'std':np.std(subgroup1_list)}
        subgroup2_stats_dict = {'count':len(subgroup2_list), 'mean':np.mean(subgroup2_list), 'median':np.median(subgroup2_list), 'var':np.var(subgroup2_list), 'std':np.std(subgroup2_list)}
        row_dict2 = {'Overl_dist_graph':[subgroup1_list, subgroup2_list], 'Stats':[subgroup1_stats_dict, subgroup2_stats_dict]}
        comparison_trivia_evidence_df = comparison_trivia_evidence_df.append(row_dict2, ignore_index=True)
                
    print('    Comparison export results done!')
    return comparison_trivia_df, comparison_trivia_evidence_df 


# In[13]:


def find_comparison_trivia(data, attribute_list, measure_list, identifier_attribute):
    print('Comparison trivia starts...')
    identifier_attribute_unique_list = data[identifier_attribute].unique()
    df_list = []
    print('    Comparison create subgroups started...')
    print('    Comparison check interestingness started...')
    for class_attribute in identifier_attribute_unique_list:
        class_attribute_data = data[data[identifier_attribute] == class_attribute]
        sub_list = comparison_create_subgroups(class_attribute_data, attribute_list)
        final_dataframe = comparison_check_interstingness(class_attribute_data, attribute_list, measure_list, sub_list, class_attribute, identifier_attribute)
        final_dataframe = final_dataframe.sort_values(by ='Factor' , ascending=False).reset_index(drop=True)
        df_list.append(final_dataframe)
    result_df = pd.DataFrame(columns = df_list[0].columns)
    print('    Comparison create subgroups done!')
    print('    Comparison check interestingness done!')
    for df in df_list:
        result_df = result_df.append(df, ignore_index=True)
    comparison_trivia_df, comparison_trivia_evidence_df = comparison_export_result(result_df)
    print('Comparison trivia done!')
    return comparison_trivia_df, comparison_trivia_evidence_df
    #return


# <hr>

# <h1>Export results</h1>

# In[16]:


def find_trivia(file_name, conflict_attribute_list, comparison_attribute_list, measure_list, heuristic_list, heuristic_threshold_list, identifier_attribute):
    print('Trivia finding starts...')
    data = pd.read_csv(file_name)
    data = data_preprocessing(data)
    conflict_trivia_df, conflict_trivia_evidence_df = find_confict_trivia(data, conflict_attribute_list, measure_list, heuristic_list, heuristic_threshold_list)
    comparison_trivia_df, comparison_trivia_evidence_df = find_comparison_trivia(data, comparison_attribute_list, measure_list, identifier_attribute)
    final_dict = {'conflict_trivia_df':conflict_trivia_df,
                  'conflict_trivia_evidence_df':conflict_trivia_evidence_df,
                  'comparison_trivia_df':comparison_trivia_df,
                  'comparison_trivia_evidence_df':comparison_trivia_evidence_df}
    with open('trivia_output2.pickle', 'wb') as handle:
        pickle.dump(final_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print('Data exporting done!')
    print('Trivia finding done!')
    return 'trivia_output2.pickle'

# In[17]:

def Analysis(filename):
    #file_name = "trivia_input.csv"
    file_name = filename
    conflict_attribute_list = ['ProdDescr', 'Plant', 'Vendor', 'RespUserPurGrp', 'POPurMethod', 'Requisitioner']
    comparison_attribute_list = ['POPurMethod']
    measure_list = ['PricePerUnit']
    heuristic_list = ['Size']
    heuristic_threshold_list = [100] 
    identifier_attribute = 'Plant'

    pickle_file = find_trivia(file_name, conflict_attribute_list, comparison_attribute_list, measure_list, heuristic_list, heuristic_threshold_list, identifier_attribute)

    return 1

# In[18]:


#with open('trivia_output2.pickle', 'rb') as handle:
#    b = pickle.load(handle)
#b


# In[ ]:




