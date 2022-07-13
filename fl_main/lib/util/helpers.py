import json
import time
import pickle
import pathlib
import socket
import asyncio

# MAC address is used to generate IDs
from getmac import get_mac_address as gma
from typing import Dict, List, Any
from hashlib import sha256
from fl_main.lib.util.states import ClientState, IDPrefix


def set_config_file(config_type: str) -> str:
    # set the config file name
    module_path = pathlib.Path.cwd()
    config_file = f'{module_path}/setups/config_{config_type}.json'

    return config_file


def read_config(config_path: str) -> Dict[str, Any]:
    """
    Read a JSON configuration file to set up an aggregator
    :param config_path:
    :return: Dict[str,Any] - configs
    """
    with open(config_path) as jf:
        config = json.load(jf)
    return config


def generate_id() -> str:
    """
    Generate a system-wide unique ID based on
    MAC address and Instantiation time with a hash func (SHA256)
    :return: str - ID
    """
    macaddr = gma()
    in_time = time.time()

    raw = f'{macaddr}{in_time}'
    hash_id = sha256(raw.encode('utf-8'))
    return hash_id.hexdigest()


def generate_model_id(component_type: str, component_id: str, generation_time: float) -> str:
    """
    Generate a system-wide unique ID for a set of models based on
    (1) a component ID: the id of an entity that created the models and
    (2) generation time: the time the models were created.
    The ID is generated by a hash function (SHA256)
    :param component_type: str - a prefix indicating component type from IDPrefix
    :param component_id: str - ID of an entity that created the models
    :param generation_time: float - the time the models were created
    :return: str - Model ID
    """
    raw = f'{component_type}{component_id}{generation_time}'
    hash_id = sha256(raw.encode('utf-8'))
    return hash_id.hexdigest()


def compatible_data_dict_read(data_dict: Dict[str, Any]) -> List[Any]:
    # ID init
    # for compatibility with older versions
    if 'my_id' in data_dict.keys():
        id = data_dict['my_id']
    else:
        id = generate_id()

    if 'gene_time' in data_dict.keys():
        gene_time = data_dict['gene_time']
    else:
        gene_time = time.time()

    if 'models' in data_dict.keys():
        models = data_dict['models']
    else:
        models = data_dict

    if 'model_id' in data_dict.keys():
        model_id = data_dict['model_id']
    else:
        model_id = generate_model_id(IDPrefix.agent, id, gene_time)

    return id, gene_time, models, model_id


def save_model_file(data_dict: Dict[str, Any],
                    path: str,
                    name: str,
                    performance_dict: Dict[str, float] = dict()):
    """
    Save a given set of models into a local file
    :param data_dict: Dict[str,np.array] - model_id, models
    :param path: str - path to the directory
    :param name: str - model file name
    :param performance_dict: Dict[str,float] - each entry shows a pair of a model id and its performance
    :return:
    """
    data_dict['performance'] = performance_dict

    fname = f'{path}/{name}'
    with open(fname, 'wb') as f:
        pickle.dump(data_dict, f)


def load_model_file(path: str, name: str) -> (Dict[str, Any], Dict[str, float]):
    """
    Read a local model file and return the unpickled models
    :param path: str - path to the directory
    :param name: str - model file name
    :return: Dict[str,np.array] - models
    """
    fname = f'{path}/{name}'
    with open(fname, 'rb') as f:
        data_dict = pickle.load(f)

    performance_dict = data_dict.pop('performance')

    # data_dict only includes models
    return data_dict, performance_dict


def read_state(path: str, name: str) -> ClientState:
    """
    Read a local state file and return a Client state
    :param path: str - path to the directory
    :param name: str - model file name
    :return: ClientState - A state indicated in the file
    """
    fname = f'{path}/{name}'
    with open(fname, 'r') as f:
        st = f.read()

    # In case, the file is being written at a time,
    # Retry reading after 0.01 s
    if st == '':
        time.sleep(0.01)
        return read_state(path, name)

    return int(st)


def write_state(path: str, name: str, state: ClientState):
    """
    Change the state on the state file
    :param path: str - path to the directory
    :param name: str - model file name
    :param state: ClientState - A new Client state
    :return:
    """
    fname = f'{path}/{name}'
    with open(fname, 'w') as f:
        f.write(str(int(state)))


def get_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('1.1.1.1', 1))
        ip = s.getsockname()[0]
    except:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


def init_loop(func):
    """
    Start a loop function
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(asyncio.gather(func))
    loop.run_forever()
