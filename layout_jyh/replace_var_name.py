import re
import random
import hashlib
import string
from layout_jyh import utils
from layout_jyh.utils import find_useful_nodes

value_types = ["uint", "int"]


def find_var_in_node(node):
    var_dict = {}
    if node.get("nodeType", "") == "VariableDeclaration":
        var_name = node.get("name", "")
        if var_name != "":
            string_type = node.get("typeDescriptions", {}).get("typeString", "")
            var_dict = var_dict.update({var_name: string_type})
    return var_dict


def find_var_in_statement(statement: list):
    var_dict = {}
    for dict_ in statement:
        if dict_.get("nodeType", "") == "VariableDeclarationStatement":
            for dict_var in dict_.get("declarations", []):
                if "name" in dict_var.keys():
                    string_type = dict_var.get("typeDescriptions", {}).get(
                        "typeString", ""
                    )
                    var_dict = var_dict.update({dict_var["name"]: string_type})
    return var_dict


def find_var_in_param(param: list):
    if param == {}:
        return {}
    var_dict = {}
    for dict_param in param.get("parameters", []):
        if "name" in dict_param.keys():
            string_type = dict_param.get("typeDescriptions", {}).get("typeString", "")
            if not var_dict:
                var_dict[dict_param["name"]] = string_type
            else:
                var_dict = var_dict.update({dict_param["name"]: string_type})
    return var_dict


def find_var_in_function(func):
    var_dict = {}
    var_statement = find_var_in_statement(func.get("body", {}).get("statements", []))
    if var_statement:
        var_dict = var_dict.update(var_statement)
    var_param = find_var_in_param(func.get("parameters", {}))
    if var_param:
        var_dict = var_dict.update(var_param)
    return var_dict


def find_var(json_dict):
    var_dict = {}
    useful_nodes = find_useful_nodes(json_dict)
    # print(useful_nodes["function_nodes"])
    for node in useful_nodes["var_nodes"]:
        var = find_var_in_node(node)
        if var:
            var_dict = var_dict.update(var)
    for node in useful_nodes["function_nodes"]:
        var = find_var_in_function(node)
        if var:
            var_dict = var_dict.update(var)
    return var_dict


def replace_var(sol_file: str, var_list: list):
    n = len(var_list)
    new_var_list = []
    # get new variables list.
    # make sure there are no repeated variables
    for i in range(n):
        new_var = utils.generate_random_var()
        while new_var in new_var_list:
            new_var = utils.generate_random_var()
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
