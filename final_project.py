
import json
import requests
import requests_cache
import networkx as nx 
import matplotlib.pyplot as plt
import pprint

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




while True:
    Meds = []
    user_input = input("Enter a medication for drug interaction identification: \n")
    if user_input.isalpha():
        test = 'https://rxnav.nlm.nih.gov/REST/drugs.json?name='
        search = user_input
        # search = 'warfarin'
        test_url = test+search
        response = requests.get(test_url).json()
        data = response['drugGroup']['conceptGroup']
        write_json('warfarin_RXNorm.json', data)

        for dicts in data:
            if len(dicts.keys()) > 1:
                for info in dicts['conceptProperties']:
                    Meds.append(Drugs(json=info))   
        
        cache_me = []
        for a in Meds:
            cache_me.append((a.__dict__))
        save_cache(cache_me)
        
        cache = open_cache
        for med in Meds:
            if cache:
                print(med.drug_rxcui())
        
        new_input = input("Please enter another medication for drug interaction identification with first entry. \n")
        if new_input.isalpha():
            user_input = new_input
        while True:
            yes_no_input = input("Do you still want to add other medications for drug interaction testing? \n")
            if yes_no_input.lower() == "yes":
                new_input_two = input("Please add medication. \n")
                if new_input_two.isalpha():
                    user_input = new_input_two
                # else: 
                #     continue

#new_input = input("Please enter another medication to test the drug interaction with: \n") 
    # while True:
    #     rxcui_input = input("Please enter the rxcui drug code for drug indentification: \n")
    #     if rxcui_input.isnumeric():
    #         print(rxcui_input)
    #         api_url = 'https://rxnav.nlm.nih.gov/REST/interaction/interaction.json?rxcui='
    #         search = rxcui_input
    #         interaction_url = api_url+search
    #         response = requests.get(interaction_url).json()
    #         data = response
    #         print(data)
                

requests_cache.install_cache('api_cache')
response = requests.get('https://rxnav.nlm.nih.gov/REST/interaction/list.json?rxcuis=207106+152923+656659')
data = response.json()["fullInteractionTypeGroup"]
# print(data)


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
print(vertex_list)




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