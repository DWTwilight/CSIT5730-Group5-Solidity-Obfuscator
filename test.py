import os
import json
import argparse
import utils
from layout_ob import replace_var_name, add_variables
from dataflow_ob import split_array


def replace_var(sol_file, ast_file):
    sol_str = utils.load_sol(sol_file)
    ast_json = utils.load_json(ast_file)
    var_dict = utils.find_var(ast_json)
    print(f"Find Variables:{var_dict}")
    new_file = replace_var_name.replace_var(sol_str, list(var_dict.keys()))
    utils.save_sol(new_file, "new_sols", "new.sol")


def add_var(sol_file):
    n = 5  # insert times
    content = utils.load_sol_lines(sol_file)
    for _ in range(n):
        positions = add_variables.search_positions(content)
        content = add_variables.insert_codes(content, positions)
    utils.save_sol_lines(content, "new_sols", "new.sol")


def split_array(sol_file, ast_file):
    # test_split_array(sol_file, ast_file)
    content = utils.load_sol_lines(sol_file)
    ast_json = utils.load_json(ast_file)
    array_list, constant_dict = split_array.find_array(ast_json)
    for array in array_list:
        name = list(array.keys())[0]
        length = array[name]
        content = split_array.squeeze_array(content, name, length)
    content = split_array(content, array_list)
    content = split_array.split_constant_array(content, array_list)
    utils.save_sol_lines(content, "new_sols", "new.sol")


def sol_cmd(args):
    os.system(
        f"solc -o {args.new_output_path} --bin --ast-compact-json --asm {args.new_path}/{args.new_filename}"
    )


def main(args):
    args.save_new_file = os.path.join(args.new_path, args.new_filename)
    args.new_ast_file = os.path.join(args.new_output_path, f"{args.filename}_json.ast")
    split_array(args.sol_file, args.ast_file)
    sol_cmd(args)
    replace_var(args.save_new_file, args.args.new_ast_file)
    sol_cmd(args)
    add_var(args.save_new_file)
    sol_cmd(args)


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument(
        "--sol_file",
        "--sol",
        type=str,
        default="layout_jyh/my_testcase/simple_array.sol",
    )
    args.add_argument(
        "--ast_file",
        "--ast",
        type=str,
        default="layout_jyh/my_testcase/simple_array_output/simple_array.sol_json.ast",
    )
    args.add_argument("--new_path", "--np", type=str, default="new_sols")
    args.add_argument("--new_filename", "--nf", type=str, default="new.sol")
    args.add_argument("--new_output_path", "--nop", type=str, default="new_sols/output")
    args = args.parse_args()
    main(args)
