
import json
import requests
import requests_cache
import networkx as nx 
import matplotlib.pyplot as plt
import pprint
from prettytable import PrettyTable

pp = pprint.PrettyPrinter(indent=2)

def write_json(filepath, data, encoding='utf-8', ensure_ascii=False, indent=2):
    """Serializes object as JSON. Writes content to the provided filepath.

    Parameters:
        filepath (str): the path to the file
        data (dict)/(list): the data to be encoded as JSON and written to the file
        encoding (str): name of encoding used to encode the file
        ensure_ascii (str): if False non-ASCII characters are printed as is; otherwise
                            non-ASCII characters are escaped.
        indent (int): number of "pretty printed" indention spaces applied to encoded JSON

    Returns:
        None
    """

    with open(filepath, 'w', encoding=encoding) as file_obj:
        json.dump(data, file_obj, ensure_ascii=ensure_ascii, indent=indent)

CACHE_FILENAME = "cache.json"
def open_cache():
    ''' opens the cache file if it exists and loads the JSON into
    the FIB_CACHE dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    Parameters
    ----------
    None
    Returns
    -------
    The opened cache
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
        return cache_dict

def save_cache(cache_dict):
    ''' saves the current state of the cache to disk
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close() 


class Drugs():
    ''' The Drugs class

     Attributes:
    ------------
    rxcui: RxCUI is a unique, unambiguous identifier that is assigned to an individual drug entity in RxNorm and used to
      relate to all things associated with that drug.
    name: RxNorm concept name
    synonym: Short or "Tallman" RxNorm synonym
    tty: indicate generic and branded drug names at different levels of specificity
    json: the json file of the drug called

       '''
    def __init__(self, rxcui=None, name=None, synonym=None, tty=None, json=None):
        self.json = json
        if json is None:
            self.rxcui = rxcui
            self.name = name
            self.synonym = synonym
            self.tty = tty
        else:
            self.rxcui = json['rxcui']
            self.name = json['name']
            self.synonym = json['synonym']
            self.tty = json['tty']
            
    def drug_rxcui(self):
        return (f"RXCUI: {self.rxcui} -- Name: {self.name} ")

# class Interaction():
#     def __init__(self, rxcui=None, name=None, synonym=None, tty=None, json=None):



# Meds = []
while True:
    Meds = []
    continue_adding = True
    while continue_adding:
        #request user drug name input for RXCUI drug indentification. 
        user_input = input("Enter a medication for drug interaction identification or quit: \n")
        if user_input == 'quit'.lower():
                print('Thank you, have a nice day.')
                break
        else:
            if user_input.isalpha():
                test = 'https://rxnav.nlm.nih.gov/REST/drugs.json?name='
                search = user_input
                # search = 'warfarin'
                test_url = test+search
                response = requests.get(test_url).json()
                # print(response.content)
                data = response['drugGroup']['conceptGroup']
                # write_json('warfarin_RXNorm.json', data)

                #loop through data returned from API call
                for dicts in data:
                    if len(dicts.keys()) > 1:
                        for info in dicts['conceptProperties']:
                            drug = Drugs(json=info)
                            if drug not in Meds:
                                Meds.append(drug)   
            
            cache_me = []
            for a in Meds:
                cache_me.append((a.__dict__))
            save_cache(cache_me)
            
            cache = open_cache
            for med in Meds:
                if cache:
                    print(med.drug_rxcui())
    # print(Meds)    
    
    # rxcuis identified in the previous API calls will be entered for drug interaction identification    
    rxcuis_input = input("Please enter the rxcui drug codes for drug interaction identification (separated by space): \n")
    rxcuis = rxcuis_input.strip().split()
    #print(rxcuis)
    rxcuis_str = "+".join(rxcuis)
    #print(rxcuis_str)
    if rxcuis_str:
    # print(rxcuis_str)
        api_url = ' https://rxnav.nlm.nih.gov/REST/interaction/list.json?rxcuis='
        search = rxcuis_str
        interaction_url = api_url+search
        # print(interaction_url)
        response = requests.get(interaction_url).json()
        data = response['fullInteractionTypeGroup']
        # print(data)
        # print(response.content)
        # write_json('triple_interaction.json', data)

    vertex_list = []
    for group_interaction in data:
        for interaction in group_interaction["fullInteractionType"]:
            # print(interaction)
            # print(interaction['interactionPair'])
            for interaction_pair in interaction['interactionPair']:
                # print(interaction_pair)
                drug1 = interaction_pair['interactionConcept'][0]['minConceptItem']['name']
                drug2 = interaction_pair['interactionConcept'][1]['minConceptItem']['name']
                severity = interaction_pair['severity']
                description = interaction_pair['description']
                vertex_list.append([drug1, drug2, severity, description])
    # print(vertex_list)

    #create a drug interaction table                     
    table = PrettyTable()
    table.field_names = ["Drug 1", "Drug 2", "Severity", "Description"]

    #add data to the table
    for vertex in vertex_list:
        table.add_row(vertex)
    print(table)

    #create an empty network graph
    G = nx.Graph()
    for edge in vertex_list:
        drug1 = edge[0]
        drug2 = edge[1]
        severity = edge[2]
        description = edge[3]
        G.add_edge(drug1, drug2, severity=severity, description=description)

    # Set the node size based on the severity of each drug
    for node in G.nodes:
        severity = None
        for _, _, data in G.edges(node, data=True):
            if 'severity' in data:
                severity = data['severity']
                break
        if severity == 'high':
            G.nodes[node]['node_size'] = 800
        elif severity == 'moderate':
            G.nodes[node]['node_size'] = 500
        elif severity == 'low':
            G.nodes[node]['node_size'] = 300
        else:
            G.nodes[node]['node_size'] = 100

    # Draw the graph
    pos = nx.spring_layout(G)
    node_sizes = [data['node_size'] for _, data in G.nodes(data=True)]
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes)
    nx.draw_networkx_edges(G, pos)
    nx.draw_networkx_labels(G, pos)
    plt.axis('off')
    plt.show()         