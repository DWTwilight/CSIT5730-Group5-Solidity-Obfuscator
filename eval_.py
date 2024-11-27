import json
from jsondiff import diff

f1 = "/home/jyh/win_projects/CSIT5730-Group5-Solidity-Obfuscator/layout_jyh/my_testcase/simple_array_output/simple_array.sol_json.ast"
f2 = "/home/jyh/win_projects/CSIT5730-Group5-Solidity-Obfuscator/new_sols/output/new_array.sol_json.ast"
with open(f1, "r", encoding="utf-8") as f:
    json1 = f.read()
with open(f2, "r", encoding="utf-8") as f:
    json2 = f.read()
ast_diff = diff(json1, json2)
print(ast_diff)
