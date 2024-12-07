import re
import random

class SolidityVariableTransformer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.content = self.open_file()

    def open_file(self):
        with open(self.file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def save_file(self, output_path):
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(self.content)

    def find_integer_variables(self):
        # matches integer constant variable declarations
        pattern = r"(uint256|int256|uint|int)\s+constant\s+(\w+)\s*=\s*(\d+);"
        return re.findall(pattern, self.content)

    def find_boolean_variables(self):
        # matches boolean constant variable declarations
        pattern = r"(bool)\s+constant\s+(\w+)\s*=\s*(true|false);"
        return re.findall(pattern, self.content)

    def generate_integer_expression(self, value):
        # generates a random mathematical expression that evaluates to value
        terms = []
        remaining = value
        while remaining > 0:
            term = random.randint(1, remaining)
            terms.append(term)
            remaining -= term

        # random insertion of operators
        expression = str(terms[0])
        for term in terms[1:]:
            operator = random.choice(['+', '-', '*', '/'])
            if operator == '/':
                term = 1  # avoid zero or invalid divisions
            expression += f" {operator} {term}"
        
        # ensures the result of the expression is exactly the original value
        expression = f"({expression}) + {value - eval(expression)}"
        return expression

    def generate_boolean_expression(self, value):
        # generates a random logical expression that evaluates to value
        truth_value = (value.lower() == "true")  # convert string to boolean
        expression = "true" if truth_value else "false"

        for _ in range(random.randint(1, 3)):
            operator = random.choice(["&&", "||", "!"])
            if operator == "!":
                expression = f"({operator} {expression})"
            else:
                random_operand = "true" if random.choice([True, False]) else "false"
                expression = f"({expression} {operator} {random_operand})"

        # ensures the result of the expression matches the original value
        if truth_value:
            expression = f"({expression} || true)"
        else:
            expression = f"({expression} && false)"
        
        return expression

    def transform(self):
        # Transform integer variables
        integer_variables = self.find_integer_variables()
        for var_type, var_name, value in integer_variables:
            value = int(value)
            expression = self.generate_integer_expression(value)
            # replace integer constant declarations
            self.content = re.sub(
                fr"{var_type}\s+constant\s+{var_name}\s*=\s*{value};",
                f"{var_type} constant {var_name} = {expression};",
                self.content
            )

        # Transform boolean variables
        boolean_variables = self.find_boolean_variables()
        for var_type, var_name, value in boolean_variables:
            expression = self.generate_boolean_expression(value)
            # replace boolean constant declarations
            self.content = re.sub(
                fr"{var_type}\s+constant\s+{var_name}\s*=\s*{value};",
                f"{var_type} constant {var_name} = {expression};",
                self.content
            )

def variableTransformar(input_file_path, output_file_path):
    transformer = SolidityVariableTransformer(input_file_path)
    transformer.transform()
    transformer.save_file(output_file_path)
    print(f"Transformed file saved to: {output_file_path}")

# Example usage
# transformer = SolidityVariableTransformer('./example/example1.sol')
# transformer.transform()
# transformer.save_file('./example/example1_transformed.sol')
