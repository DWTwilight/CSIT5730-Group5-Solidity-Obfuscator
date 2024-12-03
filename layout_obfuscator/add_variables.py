import os
import sys

parent_dir = os.path.abspath(".")
print(parent_dir)
sys.path.append(parent_dir)

import argparse
from utils import files_io, expression, file_structure
import re
import random


# 获取父级目录路径


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
            if "for" in line or "while" in line:
                continue
            var_type = match.group(1)  # type
            is_constant = bool(match.group(2))
            var_name = match.group(3)  #
            insert_points[i] = {
                "type": var_type,
                "is_constant": is_constant,
                "name": var_name,
            }
    # structure = utils.get_structure(content)

    return insert_points


def declare_new_variable(content):
    insert_points = search_positions(content)
    structure = file_structure.get_structure(content)
    # random select a line
    line_number = random.sample(list(insert_points.keys()), k=1)[0]
    blocks = [
        structure[i] for i in structure.keys() if structure[i]["type"] != "contract"
    ]
    if line_number <= blocks[0]["start"]:
        before_block = True
        declared_variables = [
            v
            for k, v in insert_points.items()
            if (k < min(blocks[0]["start"], line_number))
        ]
        new_variable = generate_useless_variable(declared_variables)
        code_line = (
            f"{new_variable["type"]} {new_variable["name"]} = {new_variable["value"]};"
        )
    else:
        before_block = False
        select_function = file_structure.get_current_function(blocks, line_number)
        while not select_function:
            line_number += 1
            select_function = file_structure.get_current_function(blocks, line_number)
        line_number = random.randint(select_function["start"], select_function["end"])
        if file_structure.in_round_brackets(
            content, line_number, select_function["end"]
        ):
            return False, (content, before_block, None, line_number)
        declared_variables = [
            v
            for k, v in insert_points.items()
            if (k < min(blocks[0]["start"], line_number))
        ]

        # print("current", line_number)

        new_variable = generate_useless_variable(declared_variables)
        code_line = (
            f"{new_variable["type"]} {new_variable["name"]} = {new_variable["value"]};"
        )
        # print("assign", line_number, code_line)
    content.insert(line_number + 1, f"{code_line}\n")
    return True, (content, before_block, new_variable, line_number + 1)


def use_new_variables(content, before_block, new_variable, start_line):
    insert_points = search_positions(content)
    structure = file_structure.get_structure(content)
    # random select a line
    line_number = start_line
    blocks = [
        structure[i] for i in structure.keys() if structure[i]["type"] != "contract"
    ]
    select_function = {}
    if not blocks:
        return content, -1
    if before_block:
        select_function = random.sample(blocks, k=1)[0]
    else:
        select_function = file_structure.get_current_function(blocks, line_number + 1)
    # if the function is too simple, skip
    if not select_function or select_function["end"] == select_function["start"]:
        return content, -1
    # else
    safe_lines = file_structure.find_safe_positions(
        content,
        max(line_number + 1, select_function["start"] + 1),
        select_function["end"],
    )
    if len(safe_lines) == 0:
        # directly skip
        return content, -1
    in_view, l = file_structure.in_view_function(content, select_function["start"])
    if in_view:
        content[l] = content[l].replace("view", " ")
    in_pure, l = file_structure.in_pure_function(content, select_function["start"])
    if in_pure:
        content[l] = content[l].replace("pure", " ")
    line_number = random.sample(safe_lines, k=1)[0]
    # line_number - 1: a new line is added
    # if new variable's type is bool, skip this step.
    if new_variable is None:
        return content, -1
    if new_variable.get("type", "") == "bool":
        code_line = f"{new_variable['name']} = !{new_variable['name']};"
        # print(line_number, new_variable["name"], before_block)
    else:
        declared_variables = [
            v
            for k, v in insert_points.items()
            if (k < min(blocks[0]["start"], line_number - 1))
            and (v["type"] == new_variable["type"])
        ]
        new_exp, used_v = expression.generate_random_expression(
            declared_variables, operators=["+", "*"]
        )
        code_line = f"{new_variable['name']} = {new_variable['type']}({new_exp});"
        # print(line_number, new_variable["name"], "=", new_exp, before_block)
    content.insert(line_number, f"{code_line}\n")

    return content, line_number


def insert_codes(content):

    # new variables declaration
    # declared variables: global or in the same function.

    # FIRST: assign new variables
    flag, (content, before_block, new_variable, assign_line) = declare_new_variable(
        content
    )

    # SECOND: add random expressions for the new variable
    # re-generate structure since the content is changed
    # print(flag)
    if flag:
        content, use_line = use_new_variables(
            content, before_block, new_variable, assign_line
        )
        # print("declaration:", assign_line, "use:", use_line)
    return flag, content


def generate_useless_variable(declared_variables):
    v_type = random.sample(VAR_LIST, k=1)[0]
    v_name = expression.generate_random_var()
    used_variables = []
    if v_type == "bool":
        # bool type
        if random.randint(1, 10) == 1:
            v_value = "false"
        else:
            v_value = "true"
    else:
        # filter variables
        declared_variables = [v for v in declared_variables if v["type"] == v_type]
        if len(declared_variables) >= 2:
            # use_variable = random.sample(declared_variables, k=3)
            v_value, v_used = expression.generate_random_expression(declared_variables)
            v_value = str(v_value)
            used_variables += v_used
        else:
            v_value = str(random.randint(0, 1000000))

    return {
        "type": v_type,
        "name": v_name,
        "value": v_value,
        "used_variables": used_variables,
    }


def main(args):
    # print(args.sol_file)
    content = files_io.load_sol_lines(args.sol_file)
    for i in range(args.n):
        flag, content = insert_codes(content)

    if not os.path.exists(args.output_path):
        os.makedirs(args.output_path)
    with open(
        os.path.join(args.output_path, args.output_filename),
        "w",
    ) as f:
        for line in content:
            f.write(line)


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--sol_file", "--sol", type=str, default="examples/example.sol")
    args.add_argument("--ast_file", "--ast", type=str)
    args.add_argument("--output_path", "--np", type=str, default="./tmp")
    args.add_argument(
        "--output_filename", "--nf", type=str, default="add_variables.sol"
    )
    # args.add_argument(
    #     "--new_output_path", "--nop", type=str, default="./tmp/solc_output"
    # )
    args.add_argument("--n", type=int, help="number of new variables", default=5)
    args = args.parse_args()
    print(f"Processing File: {args.sol_file}")
    main(args)
