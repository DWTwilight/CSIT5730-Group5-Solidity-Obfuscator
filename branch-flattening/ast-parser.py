import json

with open('./branch-flattening/examples/example1_ast.json') as f:
    ast = json.load(f)

node_types = set()

def get_node_types(node: dict):    
    if 'nodeType' not in node:
        return
    
    node_types.add(node['nodeType'])

    if (node['nodeType'] == 'BinaryOperation'):
        #print(node)
        print(node.keys())
        #print(node['body'].keys())

    for k, v in node.items():
        if isinstance(v, dict):
            get_node_types(v)
        elif isinstance(v, list):
            for i in v:
                if isinstance(i, dict):
                    get_node_types(i)

get_node_types(ast)
print(node_types)