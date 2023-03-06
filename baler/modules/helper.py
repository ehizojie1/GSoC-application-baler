import argparse
import os
import pickle
import sys

import numpy
import pandas
import torch

from modules import training, plotting, data_processing
from dataclasses import dataclass
import importlib

def get_arguments():
    parser = argparse.ArgumentParser(
        prog="baler.py",
        description="""Baler is a machine learning based compression tool for big data.\n
Baler has three running modes:\n
\t1. Derivation: Using a configuration file and a "small" input dataset, Baler derives a machine learning model optimized to compress and decompress your data.\n
\t2. Compression: Using a previously derived model and a large input dataset, Baler compresses your data and outputs a smaller compressed file.\n
\t3. Decompression: Using a previously compressed file as input and a model, Baler decompresses your data into a larger file.""",
        epilog="Enjoy!",
    )
    parser.add_argument(
        "--mode",
        type=str,
        required=False,
        help="train, compress, decompress, plot, info",
    )
    parser.add_argument(
        "--project", type=str, required=False, help="Name of new project"
    )

    args = parser.parse_args()
    if not args.mode or (args.mode != "new_project" and not args.project):
        parser.print_usage()
        exit(1)
    if args.mode == "new_project":
        config = None
    else:
        config = configClass
        importlib.import_module(f"projects.{args.project}.{args.project}_config").set_config(config)
    return config, args.mode, args.project


def create_new_project(project_name: str, base_path: str = "projects") -> None:
    project_path = os.path.join(base_path, project_name)
    if os.path.exists(project_path):
        print(f"The project {project_path} already exists.")
        return

    required_directories = [
        "compressed_output",
        "decompressed_output",
        "plotting",
        "training",
        "model",
    ]
    os.makedirs(project_path)
    with open(os.path.join(project_path, f"{project_name}_config.py"), "w") as f:
        print(project_path)
        f.write(create_default_config(project_name))
    with open(os.path.join(project_path, f"{project_name}_preprocessing.py"), "w") as f:
        print(project_path)
        f.write(create_default_config(project_name))
    with open(os.path.join(project_path, f"{project_name}_analysis.py"), "w") as f:
        print(project_path)
        f.write(create_default_config(project_name))
    for directory in required_directories:
        os.makedirs(os.path.join(project_path, directory))


@dataclass
class configClass:
    input_path          : str
    compression_ratio   : float
    epochs              : int
    early_stopping      : bool
    lr_scheduler        : bool
    patience            : int
    min_delta           : int
    model_name          : str
    custom_norm         : bool
    l1                  : bool
    reg_param           : float
    RHO                 : float
    lr                  : float
    batch_size          : int
    save_as_root        : bool
    test_size           : float

def create_default_config(project_name) -> str:
    return f'''
def set_config(c):
    c.input_path          = "data/{project_name}/{project_name}.pickle"
    c.path_before_pre_processing = "data/example/example.root"
    c.compression_ratio   = 2.0
    c.epochs              = 5
    c.early_stopping      = True
    c.lr_scheduler        = False
    c.patience            = 100
    c.min_delta           = 0
    c.model_name          = "george_SAE"
    c.custom_norm         = False
    c.l1                  = True
    c.reg_param             = 0.001
    c.RHO                 = 0.05
    c.lr                  = 0.001
    c.batch_size          = 512
    c.save_as_root        = True
    c.test_size           = 0.15
'''

def create_default_preprocessing(project_name) -> str:
    return f'''

    '''

def create_default_analysis(project_name) -> str:
    return f'''

    '''


def to_pickle(data, path):
    with open(path, "wb") as handle:
        pickle.dump(data, handle)

def from_pickle(path):
    with open(path, 'rb') as handle:
        return pickle.load(handle)


def model_init(model_name):
    # This is used when we don't have saved model parameters.
    ModelObject = data_processing.initialise_model(model_name)
    return ModelObject


def data_loader(data_path):
    return data_processing.load_data(data_path)


def numpy_to_tensor(data):
    if isinstance(data, pandas.DataFrame):
        data = data.to_numpy()

    return torch.from_numpy(data)


def normalize(data, custom_norm, cleared_col_names):
    data = numpy.apply_along_axis(
        data_processing.normalize, axis=0, arr=data, custom_norm=custom_norm
    )
    df = data_processing.numpy_to_df(data, cleared_col_names)
    return df


def process(data_path,test_size):
    df = data_processing.load_data(data_path)
    cleared_col_names = data_processing.get_columns(df)
    normalization_features = data_processing.find_minmax(df)
    number_of_columns = len(data_processing.get_columns(df))

    train_set, test_set = data_processing.split(
        df, test_size=test_size, random_state=1
    )
    return train_set, test_set, number_of_columns, normalization_features, cleared_col_names


def renormalize(data, true_min_list, feature_range_list):
    return data_processing.renormalize_func(data, true_min_list, feature_range_list)


def train(model, number_of_columns, train_set, test_set, project_path, config):
    return training.train(
        model, number_of_columns, train_set, test_set, project_path, config
    )


def plot(project_path):
    plotting.plot(project_path)


def loss_plotter(path_to_loss_data, output_path, config):
    return plotting.loss_plot(path_to_loss_data, output_path, config)


def model_saver(model, model_path):
    return data_processing.save_model(model, model_path)


def detach(tensor):
    return tensor.cpu().detach().numpy()


def compress(model_path, config):
    # Give the encoding function the correct input as tensor
    data = data_loader(config.input_path)
    cleared_col_names = data_processing.get_columns(data)
    number_of_columns = len(data_processing.get_columns(data))
    try:
        config.latent_space_size = int(number_of_columns//config.compression_ratio)
        config.number_of_columns = number_of_columns
    except AttributeError:
        assert(number_of_columns==config.number_of_columns)
    data_before = numpy.array(data)
    data = normalize(data, config.custom_norm, cleared_col_names)
    
    # Initialise and load the model correctly.
    ModelObject = data_processing.initialise_model(config.model_name)
    model = data_processing.load_model(
        ModelObject,
        model_path=model_path,
        n_features=number_of_columns,
        z_dim=config.latent_space_size,
    )
    data_tensor = numpy_to_tensor(data).to(model.device)

    compressed = model.encode(data_tensor)
    return compressed, data_before, cleared_col_names


def decompress(model_path, input_path, model_name):

    # Load the data & convert to tensor
    data = data_loader(input_path)
    latent_space_size = len(data[0])
    modelDict = torch.load(str(model_path))
    number_of_columns = len(modelDict[list(modelDict.keys())[-1]])


    # Initialise and load the model correctly.
    ModelObject = data_processing.initialise_model(model_name)
    model = data_processing.load_model(
        ModelObject,
        model_path=model_path,
        n_features=number_of_columns,
        z_dim=latent_space_size,
    )
    data_tensor = numpy_to_tensor(data).to(model.device)
    decompressed = model.decode(data_tensor)
    return decompressed


def to_root(data_path, cleared_col_names, save_path):
    if isinstance(data_path, pickle.Pickler):
        df, Names = data_processing.pickle_to_df(file_path=data_path)
        return data_processing.df_to_root(df, Names, save_path)
    elif isinstance(data_path, pandas.DataFrame):
        return data_processing.df_to_root(
            data_path, save_path=save_path
        )
    elif isinstance(data_path, numpy.ndarray):
        df = data_processing.numpy_to_df(data_path, cleared_col_names)
        df_names = df.columns
        return data_processing.df_to_root(df, col_names=df_names, save_path=save_path)


def get_device():
    device = None
    if torch.cuda.is_available():
        dev = "cuda:0"
        device = torch.device(dev)
    else:
        dev = "cpu"
        device = torch.device(dev)
    return device
