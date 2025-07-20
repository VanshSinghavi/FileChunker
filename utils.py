import random

def select_random_replicas(all_nodes, primary_node, replication_factor):
    """
    Selects a random set of nodes for chunk replication.
    
    :param all_nodes: List of all available nodes.
    :param replication_factor: Number of replicas to create.
    :return: List of selected nodes for replication.
    """
    eligible_nodes = [node for node in all_nodes if node != primary_node]
    if len(eligible_nodes) < replication_factor:
        raise ValueError("Not enough nodes available for replication.")
    return random.sample(eligible_nodes, replication_factor-1)