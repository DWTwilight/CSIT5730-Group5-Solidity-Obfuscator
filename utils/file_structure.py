import re

from utils.expression import cal_expression


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


def get_structure(content):
    contract_pattern = re.compile(r"\bcontract\s+\w+\s*{")
    function_pattern = re.compile(
        r"\bfunction\s+\w+\s*\(.*?\)\s*(public|private|internal|external)?"
    )
    constructor_pattern = re.compile(
        r"\bconstructor\s*\(.*?\)\s*(public|private|internal|external)?"
    )
    modifier_pattern = re.compile(
        r"\bmodifier\s+\w+\s*\(.*?\)\s*(public|private|internal|external)?"
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
        elif re.search(modifier_pattern, line):
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
        if left == right > 0:
            return (start, i)
    return None


def between_if_else(content, start_, end_):
    if_ = 0
    else_ = 0
    for i in range(start_, end_):
        if_ += content[i].count("if")
        else_ += content[i].count("else")
        if else_ != if_:
            return True
    return False


def find_safe_positions(content, start_, end_):
    safe_lines = []
    left_ = 0
    right_ = 0
    stop = False
    for i in range(start_, end_):
        line = content[i]
        for s in line:
            if s == "}":
                right_ += 1
            if right_ > left_:
                stop = True
                break
            if s == "{":
                left_ += 1

        if stop:
            break
        if not in_round_brackets(content, i, end_) and not between_if_else(
            content, i, end_
        ):
            safe_lines.append(i)

        # if line.count("{") + line.count("}") == 0 and line.endswith(";\n"):
        #     if soft:
        #         safe_lines.append(i)
        #     else:
        #         # whether in a for loop or while loop
        #         if not in_loop(content, start_, func_start_):
        #             safe_lines.append(i)

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


def in_round_brackets(content, start_, end_):
    left_ = 0
    right_ = 0
    for i in range(start_, end_):
        left_ += content[i].count("(")
        right_ += content[i].count(")")
        if right_ != left_:
            return True
    return False


def in_view_function(content, func_start_):
    for i in range(func_start_, 0, -1):
        if " view" in content[i]:
            return True, i
        if "function" in content[i]:
            return False, -1

    return False, -1


def in_pure_function(content, func_start_):
    for i in range(func_start_, 0, -1):
        if " pure" in content[i]:
            return True, i
        if "function" in content[i]:
            return False, -1
    return False, -1


def is_array_declaration(array_name, line):
    # rf"(uint(\d*)?|int(\d*)?|bool)\[(.*)\](.*){array_name}"
    pattern = rf"(uint\d+|int\d+|bool)\[(.*)\]\s+(\w+)\s+({array_name});"
    return re.match(pattern, line.strip())


def is_constant_array_declaration(array_name, line):
    pattern = (
        rf"(uint\d+|int\d+|bool)\[(\d+)\]\s+(\w+)\s+({array_name})\s*=\s*\[(.*?)\];"
    )
    return re.match(pattern, line.strip())


def handle_nested_brackets(line, start):
    l = 0
    r = 0
    for i in range(start, len(line)):
        if line[i] == "[":
            l += 1
        elif line[i] == "]":
            r += 1
        if l > 0 and l == r:
            return i
    return None


def find_array(json_dict):
    array_list = []
    constant_dict = {}
    useful_nodes = find_useful_nodes(json_dict)

    for node in useful_nodes["var_nodes"]:
        constant_dict = find_constant_var(node, constant_dict)
        array_list += find_array_in_node(node, constant_dict)
    # print(constant_dict)
    for func in useful_nodes["function_nodes"]:
        array_list += find_array_in_function(func)
    return array_list, constant_dict


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


def find_constant_var(node, constant_dict):
    if node.get("nodeType", "") == "VariableDeclaration":
        var_name = node.get("name", "")
        c = node.get("constant", False)
        if (var_name != "") and c:
            value = node.get("value", {}).get("value", "")
            # directly assign value to the constant
            if value != "":
                if value in ["true", "false"]:
                    value = value.capitalize()
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
                value = cal_expression(left, right, op, constant_dict)
                constant_dict[var_name] = value

    return constant_dict


def get_array_length_by_typeString(node):
    type_string = node.get("typeDescriptions", {}).get("typeString", "")
    if type_string != "":
        lengths = extract_length_from_parentheses(type_string)
        array_name = node.get("name", "")
        if array_name and lengths:
            return {array_name: lengths}
    return None


def format_if_else(content):
    """
    Formats `if` and `else` statements in a file by adding braces and new lines if they are missing.

    Args:
        content: file content read by lines
    """

    formatted_content = []
    i = 0
    while i < len(content):
        line = content[i]
        stripped = line.strip()

        # Check for single-line if without braces
        if (
            stripped.startswith("if")
            and "return" in stripped
            and not stripped.endswith("{")
        ):
            # Extract condition and statement
            condition, statement = stripped.split("return", 1)
            formatted_content.append(condition.strip() + " {")  # Add opening brace
            formatted_content.append(
                " " * 4 + "return " + statement.strip()
            )  # Indented return statement
            formatted_content.append("}")  # Add closing brace
            i += 1  # Skip to the next line
            continue

        # Check for single-line else without braces
        elif (
            stripped.startswith("else")
            and "return" in stripped
            and not stripped.endswith("{")
        ):
            _, statement = stripped.split("return", 1)
            formatted_content.append("else {")  # Add opening brace
            formatted_content.append(
                " " * 4 + "return " + statement.strip()
            )  # Indented return statement
            formatted_content.append("}")  # Add closing brace
            i += 1  # Skip to the next line
            continue

        # Check for multi-line if/else without braces
        elif stripped.startswith("if") and not stripped.endswith("{"):
            formatted_content.append(stripped + " {")  # Add opening brace
            i += 1
            while i < len(content) and content[i].strip():  # Copy all following content
                formatted_content.append(" " * 4 + content[i].strip())
                i += 1
            formatted_content.append("}")  # Add closing brace
            continue

        elif stripped.startswith("else") and not stripped.endswith("{"):
            formatted_content.append("else {")  # Add opening brace
            i += 1
            while i < len(content) and content[i].strip():  # Copy all following content
                formatted_content.append(" " * 4 + content[i].strip())
                i += 1
            formatted_content.append("}")  # Add closing brace
            continue

        # Otherwise, copy the line as is
        formatted_content.append(line.rstrip())
        i += 1
    for i in range(len(formatted_content)):
        formatted_content[i] += "\n"
    return formatted_content
