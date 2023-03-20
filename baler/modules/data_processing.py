import json
import pickle

import numpy as np
import pandas as pd
import torch
import uproot
import uproot3
from sklearn.model_selection import train_test_split

from modules import helper
from modules import models
from modules import data_processing

def save_model(model, model_path: str) -> None:
    return torch.save(model.state_dict(), model_path)


def initialise_model(model_name):
    model_object = getattr(models, model_name)
    return model_object


def load_model(model_object, model_path, n_features, z_dim):
    device = helper.get_device()
    model = model_object(device, n_features, z_dim)

    # Loading the state_dict into the model
    model.load_state_dict(torch.load(str(model_path)), strict=False)
    return model


def numpy_to_df(array, cleared_col_names):
    if np.shape(array)[1] == 4:
        col_names = ["comp1", "comp2", "comp3", "comp4"]
    else:
        col_names = cleared_col_names
    df = pd.DataFrame(array, columns=col_names)

    return df


def load_data(data_path: str):
    df = pd.read_pickle(data_path)
    return df


def find_minmax(data):
    data = np.array(data)
    data = list(data)
    true_max_list = np.apply_along_axis(np.max, axis=0, arr=data)
    true_min_list = np.apply_along_axis(np.min, axis=0, arr=data)

    feature_range_list = true_max_list - true_min_list

    normalization_features = pd.DataFrame(
        {"True min": true_min_list, "Feature Range": feature_range_list}
    )
    return normalization_features


#defining custom_norm function
#def custom_normalization(data):
#    pt_div = 1.2
#    pt_sub = 1.3
#    phi_div = 3
#    eta_div = 5
#    m_div = 1.8
#    m_add = 1

#    data['fPt'] = data['fPt'] #(np.log10(data['fPt']) - pt_sub) / pt_div
#    data['fPhi'] = data['fPhi'] / phi_div
#    data['fEta'] = data['fEta'] / eta_div
#    data['fM'] = np.log10(data['fM'] + m_add) / m_div
#    data['m_EmEnergy'] = np.log10(data['m_EmEnergy'] + m_add) / m_div
#    data['m_HadEnergy'] = np.log10(data['m_HadEnergy'] + m_add) / m_div
#    data['m_InvisibleEnergy'] = np.log10(data['m_InvisibleEnergy'] + m_add) / m_div
#    data['m_AuxiliaryEnergy'] = np.log10(data['m_AuxiliaryEnergy'] + m_add) / m_div
    
#    data = np.array(data)

#    return data

def normalize(data, custom_norm):
    print('data_p.py func normalize')
    print(data)
    data = np.array(data)
    if custom_norm:
        #pass #to use the custom_norm, un comment the next line and commnent this line
        #data = custom_normalization(data)
        gen_mean = np.mean(data)
        true_min = np.min(data)
        true_max = np.max(data)
        gen_std = np.std(data)
        gen_var = (gen_std)**2
        half_std = gen_std/2
        gen_mean_by2 = 2*gen_mean 
        gen_std_by2 = 2*gen_std
        feature_range = true_max - true_min
        data = [((i - gen_std) / feature_range ) for i in data]
        data = np.array(data)
    elif not custom_norm:
        true_min = np.min(data)
        true_max = np.max(data)
        feature_range = true_max - true_min
        data = [((i - true_min) / feature_range) for i in data]
        data = np.array(data)
    return data


def split(df, test_size, random_state):
    return train_test_split(df, test_size=test_size, random_state=random_state)


def renormalize_std(data, true_min, feature_range):
    data = list(data)
    data = [((i * feature_range) + true_min) for i in data]
    data = np.array(data)
    return data


def renormalize_func(norm_data, min_list, range_list):
    norm_data = np.array(norm_data)
    renormalized = [
        renormalize_std(norm_data, min_list[i], range_list[i])
        for i in range(len(min_list))
    ]
    renormalized_full = [(renormalized[i][:, i]) for i in range(len(renormalized))]
    renormalized_full = np.array(renormalized_full).T
    return renormalized_full


def get_columns(df):
    return list(df.columns)


def pickle_to_df(file_path):
    load_data(file_path)
    # From pickle to df:
    with open(file_path, "rb") as handle:
        data = pickle.load(handle)
        df = pd.DataFrame(data, columns=names)
        return df, names


def df_to_root(df, save_path):
    col_names = data_processing.get_columns(df)
    with uproot3.recreate(save_path) as tree:
        for i in range(len(col_names)):
            tree[col_names[i]] = uproot3.newtree({col_names[i]: "float64"})
            tree[col_names[i]].extend({col_names[i]: df[col_names[i]].to_numpy()})


def RMS_function(response_norm):
    square = np.square(response_norm)
    MS = square.mean()
    RMS = np.sqrt(MS)
    return RMS
