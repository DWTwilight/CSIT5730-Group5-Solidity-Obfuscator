from functools import reduce
import re
import utils

# s


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
        lengths = utils.extract_length_from_parentheses(type_string)
        array_name = node.get("name", "")
        if array_name and lengths:
            return {array_name: lengths}
    return None


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
    # print(constant_dict)
    for func in useful_nodes["function_nodes"]:
        array_list += find_array_in_function(func)
    return array_list, constant_dict


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
    structure = utils.get_structure(content)
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
        matches = utils.is_array_declaration(array_name, line)
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
        structure = utils.get_structure(content)
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
            matches = utils.is_array_declaration(array_name, line)
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
                end_ = utils.handle_nested_brackets(line, start)
                exp = line[start : end_ + 1]
                precise_match = re.search(pattern, exp)
                idx = precise_match.group(2)
                array_select_line = (
                    f"if({idx} < {array_name}Part1.length)\n"
                    + "{"
                    + line.replace(precise_match.group(), f"{array_name}Part1[{idx}]")
                    + "}\n"
                    + "else\n"
                    + "{"
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
        structure = utils.get_structure(content)
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
            matches = utils.is_constant_array_declaration(array_name, line)
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
                end_ = utils.handle_nested_brackets(line, start)
                exp = line[start : end_ + 1]
                precise_match = re.search(pattern, exp)
                idx = precise_match.group(2)
                array_select_line = (
                    f"{array_type} {array_name}PartValue;\n"
                    f"if({idx} < {array_name}Part1.length)\n"
                    + "{"
                    + f"{array_name}PartValue = {array_name}Part1[{idx}];"
                    + "}\n"
                    + "else\n"
                    + "{"
                    + f"{array_name}PartValue = {array_name}Part2[{idx}-{array_name}Part1.length];"
                    + "}\n"
                )
                content.insert(i, array_select_line)
                content[i + 1] = content[i + 1].replace(
                    precise_match.group(), f"{array_name}PartValue"
                )

    return content


def test_split_array(sol_file, ast_file):
    sol_str = utils.load_sol(sol_file)
    ast_json = utils.load_json(ast_file)
    array_list = find_array(ast_json)
    print(array_list)


if __name__ == "__main__":
    sol_file = "layout_jyh/my_testcase/simple_array.sol"
    ast_file = "layout_jyh/my_testcase/simple_array_output/simple_array.sol_json.ast"
    save_path = "/home/jyh/win_projects/CSIT5730-Group5-Solidity-Obfuscator/new_sols"
    filename = "new_array.sol"
    # test_split_array(sol_file, ast_file)
    content = utils.load_sol_lines(sol_file)
    ast_json = utils.load_json(ast_file)
    array_list, constant_dict = find_array(ast_json)
    for array in array_list:
        name = list(array.keys())[0]
        length = array[name]
        content = squeeze_array(content, name, length)
    content = split_array(content, array_list)
    content = split_constant_array(content, array_list)
    utils.save_sol_lines(content, save_path, filename)
