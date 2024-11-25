import os
import json
from layout_jyh.utils import load_json, load_sol, save_sol
from layout_jyh.replace_var_name import find_var, replace_var
from layout_jyh.split_array import find_array


def test_replace_var(sol_file, ast_file):
    sol_str = load_sol(sol_file)
    ast_json = load_json(ast_file)
    var_dict = find_var(ast_json)
    print(f"Find Variables:{var_dict}")

    new_file = replace_var(sol_str, list(var_dict.keys()))
    save_sol(new_file, "new_sols", "new.sol")


def test_split_array(sol_file, ast_file):
    sol_str = load_sol(sol_file)
    ast_json = load_json(ast_file)
    array_list = find_array(ast_json)
    print(array_list)


if __name__ == "__main__":
    sol_file = "layout_jyh/my_testcase/simple_array.sol"
    ast_file = "layout_jyh/my_testcase/simple_array_output/simple_array.sol_json.ast"
    # test_split_array(sol_file, ast_file)
    # print(var_list)
    test_replace_var(sol_file, ast_file)
