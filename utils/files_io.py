import os
import json
import re
import string
import random
import hashlib


def load_json(json_file):
    jsonStr = str()
    with open(json_file, "r", encoding="utf-8") as f:
        jsonStr = f.read()
    jsonDict = json.loads(jsonStr)
    return jsonDict


def load_sol(sol_file):
    with open(sol_file, "r", encoding="utf-8") as f:
        return f.read()
    return str()


def load_sol_lines(sol_file):
    with open(sol_file, "r", encoding="utf-8") as f:
        return f.readlines()
    return str()


def save_sol(sol_str, save_path, filename):
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    with open(os.path.join(save_path, filename), "w", encoding="utf-8") as f:
        f.write(sol_str)
    print(f"Generated {save_path}/{filename}")


def save_sol_lines(content, save_path, filename):
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    with open(os.path.join(save_path, filename), "w", encoding="utf-8") as f:
        for line in content:
            f.write(line)
    print(f"Generated {save_path}/{filename}")
