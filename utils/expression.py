import hashlib
import random
import string


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


def generate_random_var():
    length = random.randint(5, 16)
    x = str(random.random())
    var = hashlib.md5(x.encode()).hexdigest()
    header = random.choice(string.ascii_lowercase)
    return header + var[: length - 1]


def generate_random_expression(declared_variables, operators=["+", "-", "*"]):
    used_variables = []
    # random operator numbers
    num_operations = random.randint(1, 3)

    # init expression
    if declared_variables:
        expression = random.choice(declared_variables)["name"]
        used_variables.append(expression)
    else:
        expression = str(random.randint(1, 100))
    for _ in range(num_operations):
        operator = random.choice(operators)
        operand = random.choice(
            declared_variables + [{"name": random.randint(1, 10000)}]
        )["name"]
        if operand in declared_variables:
            used_variables.append(operand)
        if random.randint(1, 2) == 1:
            expression += f" {operator} {operand}"
        else:
            expression = f"{operand} {operator} " + expression

    # return
    return expression, used_variables
