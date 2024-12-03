import argparse
import re
import os
import sys

parent_dir = os.path.abspath(".")
print(parent_dir)
sys.path.append(parent_dir)

from utils import files_io, file_structure, expression


value_types = ["uint", "int"]


def find_var_in_node(node):
    var_dict = {}
    if node.get("nodeType", "") == "VariableDeclaration":
        var_name = node.get("name", "")
        if var_name != "":
            string_type = node.get("typeDescriptions", {}).get("typeString", "")
            if var_dict:
                var_dict.update({var_name: string_type})
            else:
                var_dict[var_name] = string_type
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
                    var_dict.update({dict_var["name"]: string_type})
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
                var_dict.update({dict_param["name"]: string_type})
    return var_dict


def find_var_in_function(func):
    var_dict = {}
    var_statement = find_var_in_statement(func.get("body", {}).get("statements", []))
    if var_statement:
        var_dict = var_dict.update(var_statement)
    var_param = find_var_in_param(func.get("parameters", {}))
    if var_param:
        if var_dict:
            var_dict.update(var_param)
        else:
            var_dict = var_param
    return var_dict


def find_var(json_dict):
    var_dict = {}
    useful_nodes = file_structure.find_useful_nodes(json_dict)
    # print(useful_nodes["function_nodes"])
    for node in useful_nodes["var_nodes"]:
        var = find_var_in_node(node)
        if var:
            if var_dict:
                var_dict.update(var)
            else:
                var_dict = var
    for node in useful_nodes["function_nodes"]:
        var = find_var_in_function(node)
        if var:
            if var_dict:
                var_dict.update(var)
            else:
                var_dict = var
    return var_dict


def replace_var(sol_file: str, var_list: list):
    n = len(var_list)
    new_var_list = []
    # get new variables list.
    # make sure there are no repeated variables
    for i in range(n):
        new_var = expression.generate_random_var()
        while new_var in new_var_list:
            new_var = expression.generate_random_var()
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


def main(args):
    sol_str = files_io.load_sol(args.sol_file)
    ast_json = files_io.load_json(args.ast_file)
    var_dict = find_var(ast_json)
    array_list, constant_dict = file_structure.find_array(ast_json)
    print(f"Find Variables:{var_dict}, Find Arrays: {array_list}")
    new_file = replace_var(
        sol_str, list(var_dict.keys()) + [list(array.keys())[0] for array in array_list]
    )
    files_io.save_sol(new_file, args.output_path, args.output_filename)


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--sol_file", "--sol", type=str, default="examples/example.sol")
    args.add_argument(
        "--ast_file", "--ast", type=str, default="examples/output/example.sol_json.ast"
    )
    args.add_argument("--output_path", "--np", type=str, default="./tmp")
    args.add_argument(
        "--output_filename", "--nf", type=str, default="replace_variables.sol"
    )
    # args.add_argument(
    #     "--new_output_path", "--nop", type=str, default="./tmp/solc_output"
    # )
    args.add_argument("--n", type=int, help="number of new variables", default=5)
    args = args.parse_args()
    main(args)
