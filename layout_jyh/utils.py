import os
import json
import re
import string
import random
import hashlib


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


def load_sol_lines(sol_file):
    with open(sol_file, "r", encoding="utf-8") as f:
        return f.readlines()
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
    left = extract_expression(left)  # remove cracks(tuple expression)
    if "value" in left.keys():
        left = str(left["value"])
    elif "name" in left.keys():
        left = str(constant_dict[left["name"]])
    else:
        sub_left = left["leftExpression"]
        sub_op = left["operator"]
        sub_right = left["rightExpression"]
        left = str(cal_expression(sub_left, sub_right, sub_op, constant_dict))
    right = extract_expression(right)  # remove cracks(tuple expression)
    if "value" in right.keys():
        right = str(right["value"])
    elif "name" in right.keys():
        right = str(constant_dict[right["name"]])
    else:

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


def extract_length_from_parentheses(s):
    length_dict = []
    for i in range(len(s)):
        if s[i] == "[":
            for j in range(i, len(s)):
                if s[j] == "]":
                    if s[i + 1 : j] == "":
                        break
                    l = int(s[i + 1 : j])
                    length_dict.append(l)
                    break
    return length_dict


def generate_random_var():
    length = random.randint(5, 16)
    x = str(random.random())
    var = hashlib.md5(x.encode()).hexdigest()
    header = random.choice(string.ascii_lowercase)
    return header + var[: length - 1]


def generate_random_expression(declared_variables):
    # random operator numbers
    num_operations = random.randint(1, 3)

    # available operators
    operators = ["+", "-", "*", "/"]

    # init expression
    expression = random.choice(declared_variables)["name"]

    for _ in range(num_operations):
        operator = random.choice(operators)
        operand = random.choice(
            declared_variables + [{"name": random.randint(1, 10000)}]
        )["name"]
        if random.randint(1, 2) == 1:
            expression += f" {operator} {operand}"
        else:
            expression = f"{operand} {operator} " + expression

    # return
    return expression


def get_structure(content):
    contract_pattern = re.compile(r"\bcontract\s+\w+\s*{")
    function_pattern = re.compile(
        r"\bfunction\s+\w+\s*\(.*?\)\s*(public|private|internal|external)?"
    )
    constructor_pattern = re.compile(
        r"\bconstructor\s*\(.*?\)\s*(public|private|internal|external)?"
    )
    structure = {}
    for i in range(len(content)):
        line = content[i]
        if re.search(contract_pattern, line):
            start_line, end_line = find_end_brackets(content, i)
            structure[i] = {"type": "contract", "start": start_line, "end": end_line}
        elif re.search(function_pattern, line):
            start_line, end_line = find_end_brackets(content, i)
            structure[i] = {"type": "function", "start": start_line, "end": end_line}
            # print(content[start_line])
        elif re.search(constructor_pattern, line):
            start_line, end_line = find_end_brackets(content, i)
            structure[i] = {"type": "constructor", "start": start_line, "end": end_line}
    return structure


def find_end_brackets(content, start_line):
    left = 0
    right = 0
    found_first = False
    start = None
    for i in range(start_line, len(content)):
        line = content[i]
        left_ = line.count("{")
        if not found_first and left_ > 0:
            found_first = True
            start = i
        right_ = line.count("}")
        left += left_
        right += right_
        if left == right:
            return (start, i)
    return None


def find_safe_positions(content, start_, end_, func_start_, soft=True):
    safe_lines = []
    for i in range(start_, end_ + 1):
        line = content[i]
        if line.count("{") + line.count("}") == 0 and line.endswith(";\n"):
            if soft:
                safe_lines.append(i)
            else:
                # whether in a for loop or while loop
                if not in_loop(content, start_, func_start_):
                    safe_lines.append(i)

    return safe_lines


def get_current_function(functions, line):
    for func in functions:
        if func["start"] <= line <= func["end"]:
            return func
    return None


def in_loop(content, start_, func_start_):
    left_bracket = 0
    right_bracket = 0
    for i in range(start_, func_start_ - 1, -1):
        line = content[i]

        left_bracket += line.count("{")
        right_bracket += line.count("}")
    if left_bracket - right_bracket >= 2:
        return True
    else:
        return False


def in_view_function(content, func_start_):
    if " view " in content[func_start_]:
        return True
    else:
        return False


def is_array_declaration(array_name, line):
    pattern = rf"(\w+)\[(.*)?\](.*){array_name}"
    return re.match(pattern, line.strip())
