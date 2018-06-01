import numpy as np
import pandas as pd
import sys
sys.path.append("../code/")
from tensor import *
from sklearn.metrics import mean_squared_error

data = np.load("../notebook/data-2013-2017-observed-filtered.npy").item()
selected_appliance = ['use', 'air1', 'refrigerator1','furnace1', 'clotheswasher1', 'dishwasher1',  'microwave1']

def create_tensor(year, data):
    raw_data = data[year]
    homeids = list(raw_data.keys())
    tensor = np.zeros((len(homeids), 7, 12))
    for idx, hid in enumerate(homeids):
        for i, app in enumerate(selected_appliance):
            tensor[idx][i] = raw_data[hid][app].values.T
    return tensor

def get_train_test(tensor_1, tensor_2, random_seed):
    np.random.seed(random_seed)

    # get training and test_1 from tensor_1
    num = tensor_1.shape[0]
    index = np.random.choice(num, 9, False)
    train = tensor_1[index] 

    test_index = [x for x in np.array(range(num)) if x not in index]
    index = np.random.choice(test_index, 9, False)
    test_1 = tensor_1[index]

    # get test_2 from tensor2
    num = tensor_2.shape[0]
    index = np.random.choice(num, 9, False)
    test_2  = tensor_2[index]
    
    return train, test_1, test_2

def get_errors(year1, year2):
    
    errors = {}
    for test_set in ['same', 'diff']:
        errors[test_set] = {}
        for appliance in selected_appliance[1:]:
            errors[test_set][appliance] = {}
        
    for random_seed in range(20):

        print(random_seed)
        # between 2013 and 2014
        train, gt_test_same, gt_test_diff = get_train_test(all_tensor[year1], all_tensor[year2], random_seed)
        # gt_test_diff = all_tensor[year2]

        agg_test_same = gt_test_same.copy()
        agg_test_diff = gt_test_diff.copy()

        agg_test_same[:, 1:, :] = np.NaN
        agg_test_diff[:, 1:, :] = np.NaN

        # for the same year
        same_tensor = np.concatenate((train, gt_test_same))
        diff_tensor = np.concatenate((train, gt_test_diff))

        H_same, A_same, T_same = learn_HAT_adagrad(case, same_tensor, 3, 3, 5000, 0.1, dis=False, random_seed = 0)
        H_diff, A_diff, T_diff = learn_HAT_adagrad(case, diff_tensor, 3, 3, 5000, 0.1, dis=False, random_seed = 0)

        # calculate error
        pred_same = multiply_case(H_same, A_same, T_same, case)
        pred_diff = multiply_case(H_diff, A_diff, T_diff, case)

        pred_test_same = pred_same[train.shape[0]:]
        pred_test_diff = pred_diff[train.shape[0]:]

        for i in range(1, 7):
            # error on same year
            error_same = mean_squared_error(pred_test_same[:, i, :].reshape(1, -1), gt_test_same[:, i, :].reshape(1, -1))
            error_diff = mean_squared_error(pred_test_diff[:, i, :].reshape(1, -1), gt_test_diff[:, i, :].reshape(1, -1))
            errors['same'][selected_appliance[i]][random_seed] = np.sqrt(error_same)
            errors['diff'][selected_appliance[i]][random_seed] = np.sqrt(error_diff)
#             print(i, error_same, error_diff)
    return errors


year1, year2 = sys.argv[1:]
year1 = int(year1)
year2 = int(year2)

all_tensor = {}
for year in [2013, 2014, 2015, 2016, 2017]:
    all_tensor[year] = create_tensor(year, data)


case = 2

error = get_errors(year1, year2)

np.save("./error-{}-{}.npy".format(year1, year2), error)