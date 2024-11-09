import re
import random
import hashlib
import string

from layout_jyh.utils import find_useful_nodes


def find_var_in_node(node):
    var_list = []
    if node.get("nodeType", "") == "VariableDeclaration":
        var_name = node.get("name", "")
        if var_name != "":
            var_list.append(var_name)
    return var_list


def find_var_in_statement(statement: list):
    var_list = []
    for dict_ in statement:
        if dict_.get("nodeType", "") == "VariableDeclarationStatement":
            for dict_var in dict_.get("declarations", []):
                if "name" in dict_var.keys():
                    var_list.append(dict_var["name"])
    return var_list


def find_var_in_param(param: list):
    if param == {}:
        return []
    var_list = []
    for dict_param in param.get("parameters", []):
        if "name" in dict_param.keys():
            var_list.append(dict_param["name"])
    return var_list


def find_var_in_function(func):
    var_list = []
    var_list += find_var_in_statement(func.get("body", {}).get("statements", []))
    var_list += find_var_in_param(func.get("parameters", {}))
    return var_list


def find_var(json_dict):
    var_list = []
    useful_nodes = find_useful_nodes(json_dict)
    # print(useful_nodes["function_nodes"])
    for node in useful_nodes["var_nodes"]:
        var_list += find_var_in_node(node)
    for node in useful_nodes["function_nodes"]:
        var_list += find_var_in_function(node)
    return list(set(var_list))


def generate_random_var():
    length = random.randint(5, 16)
    x = str(random.random())
    var = hashlib.md5(x.encode()).hexdigest()
    header = random.choice(string.ascii_lowercase)
    return header + var[: length - 1]


def replace_var(sol_file: str, var_list: list):
    n = len(var_list)
    new_var_list = []
    # get new variables list.
    # make sure there are no repeated variables
    for i in range(n):
        new_var = generate_random_var()
        while new_var in new_var_list:
            new_var = generate_random_var()
        print(new_var)
        new_var_list.append(new_var)
    for i in range(n):
        var = var_list[i]
        # regex for old var.
        # make sure it is not part of another variable.
        pattern = rf"(?<![a-zA-Z0-9_]){re.escape(var)}(?![a-zA-Z0-9_])"
        new_var = new_var_list[i]
        sol_file = re.sub(pattern, new_var, sol_file)
    return sol_file
