import re
from layout_jyh import utils
from layout_jyh.replace_var_name import find_var


def find_constant_var(node, constant_dict):
    if node.get("nodeType", "") == "VariableDeclaration":
        var_name = node.get("name", "")
        c = node.get("constant", False)
        if (var_name != "") and c:
            value = node.get("value", {}).get("value", "")
            # directly assign value to the constant
            if value != "":
                constant_dict[var_name] = eval(value)
            # assign another var to the constant
            elif node.get("value", {}).get("name", ""):
                assign_var = node["value"]["name"]
                constant_dict[var_name] = constant_dict[assign_var]
            # use expression to assign the constant
            else:
                node = node["value"]
                left = node["leftExpression"]
                op = node["operator"]
                right = node["rightExpression"]
                value = utils.cal_expression(left, right, op, constant_dict)
                constant_dict[var_name] = value

    return constant_dict


def get_array_length_by_typeString(node):
    type_string = node.get("typeDescriptions", {}).get("typeString", "")
    if type_string != "":
        return utils.extract_length_from_parentheses(type_string)


def get_array_length(node, constant_dict):
    array_list = []
    array_name = node.get("name", "")
    array_length_dict = node["typeName"].get("length", {})
    # the length can be a number or a constant expression
    array_length_dict = utils.extract_expression(array_length_dict)
    if not array_length_dict:
        return array_list
    if array_length_dict.get("value", ""):
        array_list.append({array_name: int(array_length_dict.get("value", ""))})
    elif array_length_dict.get("name", ""):
        array_list.append(
            {array_name: constant_dict[array_length_dict.get("name", "")]}
        )
    else:

        left = array_length_dict["leftExpression"]
        op = array_length_dict["operator"]
        right = array_length_dict["rightExpression"]
        value = utils.cal_expression(left, right, op, constant_dict)
        array_list.append({array_name: value})


def find_array_in_node(node, constant_dict=None):
    array_list = []
    if node.get("nodeType", "") == "VariableDeclaration":
        var_name = node.get("name", "")
        if var_name != "":
            if node.get("typeName", {}):
                if node["typeName"].get("nodeType", "") == "ArrayTypeName":
                    # array_list += get_array_length(node, constant_dict)
                    # use type string to get length
                    length_dict = get_array_length_by_typeString(node)
                    if length_dict:
                        array_list.append(length_dict)
    return array_list


def find_array_in_function(func):
    array_list = []

    return array_list


def find_array(json_dict):
    array_list = []
    constant_dict = {}
    useful_nodes = utils.find_useful_nodes(json_dict)

    for node in useful_nodes["var_nodes"]:
        constant_dict = find_constant_var(node, constant_dict)
        array_list += find_array_in_node(node, constant_dict)
    print(constant_dict)
    for func in useful_nodes["function_nodes"]:
        array_list += find_array_in_function(func)
    return array_list
