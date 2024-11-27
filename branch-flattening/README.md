# Branch Flattening for Solidity Code

Here we perform the branch flattening for 4 kinds of statements:

- if statement
- for statement
- while statement
- do-while statement

## Get the AST

First, we need to get the AST of the targeted Solidity source file. A simple way is to use the Solidity Compiler by giving the `--ast-compact-json` option. For example, we can get the AST of the `example.sol` file by running the following command:


```bash
solc example.sol --ast-compact-json > example_ast.json
```

## Solidity AST JSON

The Solidity AST JSON is a JSON file that contains the AST of the Solidity source file. The AST is a tree structure that represents the source code.

### VariableDeclarationStatement
'assignments', 'declarations', 'id', 'initialValue'

### VariableDeclaration
'constant', 'id', 'mutability', 'name', 'nameLocation', 'scope', 'stateVariable', 'storageLocation', 'typeDescriptions', 'typeName', 'visibility'

- `nodeType`: The type of the node, which is `VariableDeclaration`.
- `name`: The name of the variable.
- `value`: The value of the variable.


## Flattening Techniques

### `while` Statement

#### Structure
- condition: Expression
- body: Statement (usually Block)

#### Flattening



