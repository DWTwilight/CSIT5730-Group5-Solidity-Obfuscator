import utils
import re
import random

VAR_LIST = ["bool", "uint128", "uint256", "int128", "int256"]


def search_positions(content):
    # Regular Expression
    # search insert position
    var_pattern = r"(uint256|int256|address|bool|)\s+(constant\s+)?(\w+)\s*="
    insert_points = {}
    for i in range(len(content)):
        line = content[i]
        match = re.search(var_pattern, line)

        if match:
            var_type = match.group(1)  # 类型
            is_constant = bool(match.group(2))  # 是否有 constant 修饰符
            var_name = match.group(3)  # 变量名
            insert_points[i] = {
                "type": var_type,
                "is_constant": is_constant,
                "name": var_name,
            }
    # structure = utils.get_structure(content)

    return insert_points


def insert_codes(content, insert_points):
    structure = utils.get_structure(content)
    line_number = random.sample(list(insert_points.keys()), k=1)[0]
    # new variables declaration
    declared_variables = [v for k, v in insert_points.items() if (k < line_number)]
    new_variable = generate_useless_variable(declared_variables)
    functions = [
        structure[i] for i in structure.keys() if structure[i]["type"] == "function"
    ]
    if line_number <= functions[0]["start"]:
        before_function = True
        code_line = (
            f"{new_variable["type"]} {new_variable["name"]} = {new_variable["value"]};"
        )
    else:
        before_function = False
        select_function = utils.get_current_function(functions, line_number + 1)
        safe_lines = utils.find_safe_positions(
            content,
            line_number + 1,
            select_function["end"],
            select_function["start"],
            soft=False,
        )
        if len(safe_lines) == 0:
            # directly skip
            return content
        # print("current", line_number)
        line_number = random.sample(safe_lines, k=1)[0]
        # print("after", line_number)
        if utils.in_view_function(content, select_function["start"]):
            content[select_function["start"]] = content[
                select_function["start"]
            ].replace(" view ", " ")
        code_line = (
            f"{new_variable["type"]} {new_variable["name"]} = {new_variable["value"]};"
        )
    content.insert(line_number + 1, f"{code_line}\n")
    # add random expressions for the new variable
    # re-generate structure since the content is changed

    structure = utils.get_structure(content)
    functions = [
        structure[i] for i in structure.keys() if structure[i]["type"] == "function"
    ]
    select_function = {}
    if before_function:
        select_function = random.sample(functions, k=1)[0]
    else:
        select_function = utils.get_current_function(functions, line_number + 1)
    # if the function is too simple, skip
    if not select_function or select_function["end"] == select_function["start"]:
        return content
    # else
    safe_lines = utils.find_safe_positions(
        content,
        max(line_number + 2, select_function["start"]),
        select_function["end"],
        select_function["start"],
    )
    if len(safe_lines) == 0:
        # directly skip
        return content
    if utils.in_view_function(content, select_function["start"]):
        content[select_function["start"]] = content[select_function["start"]].replace(
            " view ", " "
        )
    line_number = random.sample(safe_lines, k=1)[0]
    # line_number - 1: a new line is added
    # if new variable's type is bool, skip this step.
    if new_variable["type"] == "bool":
        code_line = f"{new_variable['name']} = !{new_variable['name']}"
        print(line_number, new_variable["name"])
    else:
        declared_variables = [
            v
            for k, v in insert_points.items()
            if (k < line_number - 1) and (v["type"] == new_variable["type"])
        ]
        new_exp = generate_useless_expression(declared_variables)
        code_line = f"{new_variable['name']} = {new_variable['type']}({new_exp});"
        content.insert(line_number, f"{code_line}\n")
        print(line_number, new_variable["name"], "=", new_exp)
    return content


def generate_useless_variable(declared_variables):
    v_type = random.sample(VAR_LIST, k=1)[0]
    v_name = utils.generate_random_var()
    if v_type == "bool":
        # bool type
        if random.randint(1, 10) == 1:
            v_value = "false"
        else:
            v_value = "true"
    else:
        # filter variables
        declared_variables = [v for v in declared_variables if v["type"] == v_type]
        if declared_variables and len(declared_variables) >= 2:
            # use_variable = random.sample(declared_variables, k=3)
            v_value = str(utils.generate_random_expression(declared_variables))

        else:
            v_value = str(random.randint(0, 1000000))

    return {"type": v_type, "name": v_name, "value": v_value}


def generate_useless_expression(declared_variables):

    if declared_variables and len(declared_variables) >= 2:
        # use_variable = random.sample(declared_variables, k=3)
        v_value = str(utils.generate_random_expression(declared_variables))

    else:
        v_value = str(random.randint(0, 1000000))
    return v_value


if __name__ == "__main__":
    sol_file = "/home/jyh/win_projects/CSIT5730-Group5-Solidity-Obfuscator/layout_jyh/my_testcase/sample.sol"

    ast_file = "/home/jyh/win_projects/CSIT5730-Group5-Solidity-Obfuscator/layout_jyh/my_testcase/sample_output/sample.sol_json.ast"
    n = 5  # insert times
    content = utils.load_sol_lines(sol_file)
    for _ in range(n):
        positions = search_positions(content)
        content = insert_codes(content, positions)
    with open(
        "/home/jyh/win_projects/CSIT5730-Group5-Solidity-Obfuscator/new_sols/new.sol",
        "w",
    ) as f:
        for line in content:
            f.write(line)
