from enum import Enum, IntEnum

class IDPrefix:
    agent = 'agent'
    aggregator = 'aggregator'
    db = 'database'

class ClientState(IntEnum):
    """
    Client states defined in the Agent specification
    """
    waiting_gm = 0
    training = 1
    sending = 2
    gm_ready = 3

class ModelType(Enum):
    """
    Types of ML models
    """
    local = 0
    cluster = 1

class DBMsgType(Enum):
    """
    Message types defined in the communication protocol between an aggregator and a database
    """
    push = 0
    get_list = 1
    get_models = 2

class AgentMsgType(Enum):
    """
    Message types defined in the communication protocol sent from an agent to an aggregator
    """
    participate = 0
    update = 1

class AggMsgType(Enum):
    """
    Message types defined in the communication protocol sent from an aggregator to an agent
    """
    welcome = 0
    sending_gm_models = 1

class ParticipateMSGLocation(IntEnum):
    """
    index indicator to read a participate message
    """
    msg_type = 0
    agent_id = 1
    model_id = 2
    lmodels = 3
    init_flag = 4
    sim_flag = 5
    exch_socket = 6
    gene_time = 7
    meta_data = 8
    agent_ip = 9

class DBPushMsgLocation(IntEnum):
    """
    index indicator to read a push message
    """
    msg_type = 0
    component_id = 1
    round = 2
    model_type = 3
    models = 4
    model_id = 5
    gene_time = 6
    meta_data = 7
    req_id_list = 8

class GMDistributionMsgLocation(IntEnum):
    """
    index indicator to read a global models distribution message
    """
    msg_type = 0
    aggregator_id = 1
    model_id = 2
    round = 3
    global_models = 4