from functools import reduce
import re
import argparse
import os
import sys

parent_dir = os.path.abspath(".")
print(parent_dir)
sys.path.append(parent_dir)

from utils import files_io, file_structure, expression


def get_array_length(node, constant_dict):
    array_list = []
    array_name = node.get("name", "")
    array_length_dict = node["typeName"].get("length", {})
    # the length can be a number or a constant expression
    array_length_dict = file_structure.extract_expression(array_length_dict)
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
        value = expression.cal_expression(left, right, op, constant_dict)
        array_list.append({array_name: value})


def squeeze_array(content, array_name, length):
    """lengths: variables -> numbers;
    multi dimensional array -> one dimension;

    Args:
        content (list): lines of the file
        array_name (str): current array name
        lengths (list): lengths of each dimension
        constant_list (list): list of declared constants
    Returns:
        list: updated content
    """
    # one-dimensional arrays don't need to be squeezed
    structure = file_structure.get_structure(content)
    functions_start = [
        structure[i]["start"]
        for i in structure.keys()
        if structure[i]["type"] == "function"
    ]
    for i in range(len(content)):
        # skip in parameters
        if i in functions_start:
            continue
        # set current line
        line = content[i]
        # whether it's the declaration line
        matches = file_structure.is_array_declaration(array_name, line)
        # replace content
        if matches:
            l = reduce(lambda x, y: x * y, length)
            old_pattern = r"\[([^\]]*)\](\[[^\]]*\])*"
            old = re.search(old_pattern, line)
            if old:
                old = old[0]
            content[i] = content[i].replace(old, f"[{l}]")
            # skip this line
            continue
            # if it's not the declaration line
            # array pattern
            # assignment or comparison(at the left side)(ignore bool type which is considered later)
        old_idx, new_idx = generate_new_idx(line, array_name, length)
        if old_idx and new_idx:
            content[i] = content[i].replace(old_idx, new_idx)
    return content


def generate_new_idx(line, array_name, length):
    pattern = rf"({array_name})\[([^\]]*)\](\[[^\]]*\])*"
    matches = re.search(pattern, line)
    # there is no this array
    if not matches:
        return None, None
    # matches
    dimensions = re.findall(r"\[([^\]]*)\]", matches.group())
    new_idx = dimensions[-1]
    for j in range(len(length) - 1):
        new_idx = f"({dimensions[-j-2]})*{length[-j-2]}+" + new_idx
    new_idx = f"{array_name}[{new_idx}]"
    # new_array = f"{array_name}[{new_idx}]"
    return matches.group(), new_idx


def split_array(content, array_list):
    for array in array_list:
        array_name = list(array.keys())[0]
        structure = file_structure.get_structure(content)
        functions_start = [
            structure[i]["start"]
            for i in structure.keys()
            if structure[i]["type"] == "function"
        ]
        array_type = None
        for i in range(len(content)):
            # skip in parameters
            if i in functions_start:
                continue
            # set current line
            line = content[i]
            # whether it's the declaration line
            matches = file_structure.is_array_declaration(array_name, line)
            # replace content
            if matches:
                array_type = matches.group(1)  # 数组类型
                length = int(matches.group(2))  # 原数组长度
                visibility = matches.group(3)  # 可见性修饰符
                name = matches.group(4)  # 数组名
                new_l_1 = length // 2
                new_l_2 = length - new_l_1
                content[i] = (
                    f"{array_type}[{new_l_1}] {visibility} {array_name}Part1;\n"
                    + f"{array_type}[{new_l_2}] {visibility} {array_name}Part2;\n "
                )
                # skip this line
                continue
            if not array_type:
                continue
            if f"{array_name}.length" in line:
                content[i] = content[i].replace(
                    f"{array_name}.length",
                    f"({array_name}Part1.length+{array_name}Part2.length)",
                )
            # normal use of the array
            pattern = rf"({array_name})\[(.*)\]"
            matches = re.search(pattern, line)
            if matches:
                start = matches.span()[0]
                end_ = file_structure.handle_nested_brackets(line, start)
                exp = line[start : end_ + 1]
                precise_match = re.search(pattern, exp)
                idx = precise_match.group(2)
                array_select_line = (
                    f"if({idx} < {array_name}Part1.length)\n"
                    + "{\n"
                    + line.replace(precise_match.group(), f"{array_name}Part1[{idx}]")
                    + "}\n"
                    + "else\n"
                    + "{\n"
                    + line.replace(
                        precise_match.group(),
                        f"{array_name}Part2[{idx}-{array_name}Part1.length]",
                    )
                    + "}\n"
                )
                content[i] = array_select_line

    return content


def split_constant_array(content, constant_array_list):
    for array in constant_array_list:
        array_name = list(array.keys())[0]
        length = array[array_name]
        structure = file_structure.get_structure(content)
        functions_start = [
            structure[i]["start"]
            for i in structure.keys()
            if structure[i]["type"] == "function"
        ]
        array_type = None
        length = None
        for i in range(len(content)):
            # skip in parameters
            if i in functions_start:
                continue
            # set current line
            line = content[i]
            # whether it's the declaration line
            matches = file_structure.is_constant_array_declaration(array_name, line)
            # replace content
            if matches:
                array_type = matches.group(1)  # 数组类型
                length = int(matches.group(2))  # 原数组长度
                visibility = matches.group(3)  # 可见性修饰符
                name = matches.group(4)  # 数组名
                values = matches.group(5).strip()  # 数组值（可能包含空格）
                values_list = [v.strip() for v in values.split(",")]
                mid = len(values_list) // 2
                part1 = ", ".join(values_list[:mid])
                part2 = ", ".join(values_list[mid:])

                # 构造新的数组声明
                part1_code = (
                    f"{array_type}[{mid}] {visibility} {name}Part1 = [{part1}];\n"
                )
                part2_code = f"{array_type}[{len(values_list) - mid}] {visibility} {name}Part2 = [{part2}];\n"
                content[i] = f"    {part1_code}    {part2_code}"
                continue

            if not array_type:
                continue
            if f"{array_name}.length" in line:
                content[i] = content[i].replace(
                    f"{array_name}.length",
                    f"({array_name}Part1.length+{array_name}Part2.length)",
                )
            pattern = rf"({array_name})\[(.*)\]"
            matches = re.search(pattern, line)
            if matches:
                start = matches.span()[0]
                end_ = file_structure.handle_nested_brackets(line, start)
                exp = line[start : end_ + 1]
                precise_match = re.search(pattern, exp)
                idx = precise_match.group(2)
                array_select_line = (
                    f"{array_type} {array_name}PartValue;\n"
                    f"if({idx} < {array_name}Part1.length)\n"
                    + "{\n"
                    + f"{array_name}PartValue = {array_name}Part1[{idx}];\n"
                    + "}\n"
                    + "else\n"
                    + "{\n"
                    + f"{array_name}PartValue = {array_name}Part2[{idx}-{array_name}Part1.length];\n"
                    + "}\n"
                )
                content.insert(i, array_select_line)
                content[i + 1] = content[i + 1].replace(
                    precise_match.group(), f"{array_name}PartValue"
                )

    return content


def test_split_array(sol_file, ast_file):
    sol_str = files_io.load_sol(sol_file)
    ast_json = files_io.load_json(ast_file)
    array_list = file_structure.find_array(ast_json)
    print(array_list)


def main(args):
    # test_split_array(sol_file, ast_file)
    content = files_io.load_sol_lines(args.sol_file)
    content = file_structure.format_if_else(content)
    ast_json = files_io.load_json(args.ast_file)
    array_list, constant_dict = file_structure.find_array(ast_json)
    for array in array_list:
        name = list(array.keys())[0]
        length = array[name]
        content = squeeze_array(content, name, length)
    content = split_array(content, array_list)
    content = split_constant_array(content, array_list)
    files_io.save_sol_lines(content, args.output_path, args.output_filename)


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--sol_file", "--sol", type=str)
    args.add_argument(
        "--ast_file", "--ast", type=str, default="examples/output/example.sol_json.ast"
    )
    args.add_argument("--output_path", "--np", type=str, default="./tmp")
    args.add_argument("--output_filename", "--nf", type=str, default="split_array.sol")
    args = args.parse_args()
    print(f"Processing File: {args.sol_file}")
    main(args)
