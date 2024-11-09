import os
import json
import math


def load_json(json_file):
    jsonStr = str()
    with open(json_file, "r", encoding="utf-8") as f:
        jsonStr = f.read()
    jsonDict = json.loads(jsonStr)
    return jsonDict


def load_sol(sol_file):
    with open(sol_file, "r", encoding="utf-8") as f:
        return f.read()
    return str()


def save_sol(sol_str, save_path, filename):
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    with open(os.path.join(save_path, filename), "w", encoding="utf-8") as f:
        f.write(sol_str)
    print(f"Generated {save_path}/{filename}")


def find_useful_nodes(json_dict):
    var_nodes = []
    function_nodes = []
    node = json_dict.get("nodes", "")
    if node:
        for d in node:
            if d.get("nodeType", "") == "ContractDefinition":
                for dict_ in d.get("nodes", {}):
                    if dict_.get("nodeType", "") == "VariableDeclaration":
                        var_nodes.append(dict_)
                    elif dict_.get("nodeType", "") == "FunctionDefinition":
                        function_nodes.append(dict_)
    return {"var_nodes": var_nodes, "function_nodes": function_nodes}


def cal_expression(left, right, op, constant_dict):
    """Recursively calculate the value of the expression.
    Can only handle simple binary operators: +,-,*,/,%,**.
    Ignore "immutable"

    Args:
        left (dict): leftExpression
        right (dict): rightExpression
        op (str): BinaryOperation
        constant_dict (dict): known values of constants
    """
    if "value" in left.keys():
        left = str(left["value"])
    elif "name" in left.keys():
        left = str(constant_dict[left["name"]])
    else:
        # if left.get("nodeType", "") == "TupleExpression":
        #     left = left["components"][0]
        left = extract_expression(left)
        sub_left = left["leftExpression"]
        sub_op = left["operator"]
        sub_right = left["rightExpression"]
        left = str(cal_expression(sub_left, sub_right, sub_op, constant_dict))
    if "value" in right.keys():
        right = str(right["value"])
    elif "name" in right.keys():
        right = str(constant_dict[right["name"]])
    else:
        # if right.get("nodeType", "") == "TupleExpression":
        #     right = right["components"][0]
        right = extract_expression(right)
        sub_left = right["leftExpression"]
        sub_op = right["operator"]
        sub_right = right["rightExpression"]
        right = str(cal_expression(sub_left, sub_right, sub_op, constant_dict))
    expression = f"{left} {op} {right}"
    n = int(eval(expression))
    assert n >= 0, "Error: arithmetic underflow"
    return n


def extract_expression(expression):
    while expression.get("nodeType", "") == "TupleExpression":
        expression = expression["components"][0]
    return expression
