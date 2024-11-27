import json
import os
from typing import Optional, List
from utils import gen_dintinct_labels


class FlatteningContext:
    def __init__(self, path: str, from_sol: bool = False):
        if from_sol:
            self.ast = self.__from_sol(path)
        else:
            with open(path, "r") as f:
                try:
                    self.ast = json.load(f)
                except json.JSONDecodeError as e:
                    raise Exception(f"Failed to parse JSON file: {e.msg}")

        # Traverse the AST and find the maximum id
        self.max_id = 0
        self.__preprocess(self.ast)

    def __from_sol(self, path: str) -> dict:
        """
        Parse the solidity source code and return the AST JSON.
        """
        import subprocess

        # Check if dir is a legal file path
        if not os.path.isfile(path):
            raise FileNotFoundError(f"File {path} does not exist")

        # Run solc to generate AST JSON
        result = subprocess.run(
            ["solc", "--ast-compact-json", path], capture_output=True, text=True
        )

        if result.returncode != 0:
            raise Exception(f"Solc compilation failed: {result.stderr}")

        # Parse the JSON output
        try:
            ast_json = json.loads(result.stdout[result.stdout.index("{") :])
            return ast_json
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse solc AST output as JSON: {e.msg}")

    def __preprocess(self, node):
        """
        Get the maximum `id` and remove all the `src` fields.
        """
        if not isinstance(node, dict) or "nodeType" not in node:
            return

        self.max_id = max(self.max_id, node["id"])
        node.pop("src")

        for _, value in node.items():
            if isinstance(value, dict):
                self.__preprocess(value)
            elif isinstance(value, list):
                for item in value:
                    self.__preprocess(item)

    def __new_id(self) -> int:
        self.max_id += 1
        return self.max_id

    def __new_node(
        self, node_type: str, force_id: Optional[int] = None, **kwargs
    ) -> dict:
        """
        Create a new node. Generate a new id if `force_id` is not provided.
        """
        node = {
            "nodeType": node_type,
            "id": self.__new_id() if force_id is None else force_id,
        }

        for k, v in kwargs.items():
            node[k] = v

        return node

    def __new_decl_uint256(
        self, name: str, scope_id: int, value: Optional[int] = None
    ) -> dict:
        """
        Create a new `VariableDeclarationStatement` node to declare a single `uint256` variable.
        Fields except for `id` and `nodeType`:
            - `assignments`: `[ids of VariableDeclaration]`
            - `declarations`: `[VariableDeclaration]`
            - `initialValue`: `str` (optional)
        """
        node = self.__new_node("VariableDeclarationStatement")
        node["declarations"] = [
            {
                "constant": False,
                "id": self.__new_id(),
                "mutability": "mutable",
                "name": name,
                "nodeType": "VariableDeclaration",
                "scope": scope_id,
                "stateVariable": False,
                "storageLocation": "default",
                "typeDescriptions": {
                    "typeIdentifier": "t_uint256",
                    "typeString": "uint256",
                },
                "typeName": {
                    "id": self.__new_id(),
                    "name": "uint256",
                    "nodeType": "ElementaryTypeName",
                    "typeDescriptions": {
                        "typeIdentifier": "t_uint256",
                        "typeString": "uint256",
                    },
                },
                "visibility": "internal",
            }
        ]
        node["assignments"] = [node["declarations"][0]["id"]]
        if value is not None:
            value_str = str(value)
            node["initialValue"] = {
                "hexValue": "".join([hex(int(c))[2:] for c in value_str]),
                "id": self.__new_id(),
                "isConstant": False,
                "isLValue": False,
                "isPure": True,
                "kind": "number",
                "lValueRequested": False,
                "nodeType": "Literal",
                "typeDescriptions": {
                    "typeIdentifier": f"t_rational_{value_str}_by_1",
                    "typeString": f"int_const {value_str}",
                },
                "value": value_str,
            }
        return node

    def __new_literal_true(self) -> dict:
        return {
            "hexValue": "74727565",
            "id": self.__new_id(),
            "isConstant": False,
            "isLValue": False,
            "isPure": True,
            "kind": "bool",
            "lValueRequested": False,
            "nodeType": "Literal",
            "typeDescriptions": {"typeIdentifier": "t_bool", "typeString": "bool"},
            "value": "true",
        }

    def __new_block(self, statements: List[dict] = []) -> dict:
        return self.__new_node("Block", statements=statements)

    def __new_if_statement(
        self, condition: dict, true_body: dict, false_body: Optional[dict] = None
    ) -> dict:
        node = self.__new_node("IfStatement", condition=condition, trueBody=true_body)
        if false_body is not None:
            node["falseBody"] = false_body
        return node

    def __new_reference_identifier(self, referenced_declaration: dict) -> dict:
        """
        Create a new `Identifier` node to reference a variable. \\
        Params:
            - `referencedDeclaration`: `VariableDeclaration`
        """
        assert referenced_declaration["nodeType"] == "VariableDeclaration"
        return {
            "id": self.__new_id(),
            "name": referenced_declaration["name"],
            "nodeType": "Identifier",
            "overloadedDeclarations": [],
            "referencedDeclaration": referenced_declaration["id"],
            "typeDescriptions": referenced_declaration["typeDescriptions"].deepcopy(),
        }

    def __new_equal_operation_uint256(self, left: dict, right: dict) -> dict:
        return {
            "commonType": {"typeIdentifier": "t_uint256", "typeString": "uint256"},
            "id": self.__new_id(),
            "isConstant": False,
            "isLValue": False,
            "isPure": False,
            "lValueRequested": False,
            "leftExpression": left.deepcopy(),
            "nodeType": "BinaryOperation",
            "operator": "==",
            "rightExpression": right.deepcopy(),
            "typeDescriptions": {"typeIdentifier": "t_bool", "typeString": "bool"},
        }

    def flatten_if(self, node: dict):
        assert node["nodeType"] == "IfStatement"
        raise NotImplementedError()

    def flatten_for(self, node: dict):
        assert node["nodeType"] == "ForStatement"

        condition = node["condition"]
        pre = node["pre"]
        post = node["post"]
        body_statements = node["body"]["statements"]
        assert isinstance(body_statements, list)

        raise NotImplementedError()

    def flatten_while(self, node: dict):
        assert node["nodeType"] == "WhileStatement"

        old_while = node.deepcopy()

        # Make the original WhileStatement a Block
        node.pop("body")
        node.pop("condition")
        node["id"] = self.__new_id()
        node["nodeType"] = "Block"
        node["statements"] = []

        condition_label, body_label, break_label = gen_dintinct_labels(3)

        # Declare a state variable, initialize it with the continue label
        # TODO: set a random name for the state variable, and make sure it's not used in other places
        node["statements"].append(
            self.__new_decl_uint256("state_var", node["id"], condition_label)
        )

        # Create the dispatcher, the outer layer of which is a loop
        dispatcher = self.__new_node(
            "WhileStatement", condition=self.__new_literal_true()
        )
        dispatcher["body"] = self.__new_block()

        # Create the branches for the dispatcher
        state_var_ref = self.__new_reference_identifier(dispatcher["statements"][0]["declarations"][0])
        
    def flatten_dowhile(self, node: dict):
        assert node["nodeType"] == "DoWhileStatement"

        raise NotImplementedError()

    def flatten_block(self, node: dict):
        assert node["nodeType"] == "Block"

        raise NotImplementedError()
