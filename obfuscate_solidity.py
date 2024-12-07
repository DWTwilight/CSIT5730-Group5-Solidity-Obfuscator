import re
import random
import string
import base64

class SolidityObfuscator:
    def __init__(self):
        self.name_mapping = {}
        self.var_counter = 0
        self.error_messages = set()
        self.keywords = {
            'contract', 'function', 'mapping', 'address', 'uint256', 'string',
            'private', 'public', 'view', 'returns', 'constructor', 'event',
            'indexed', 'require', 'msg', 'sender', 'emit', 'selfdestruct',
            'payable', 'memory', 'storage', 'calldata', 'struct', 'modifier',
            'internal', 'external', 'pure', 'bytes', 'bytes32', 'bool', 'uint',
            'int', 'interface', 'using', 'for', 'true', 'false', 'new', 'delete',
            'if', 'else', 'while', 'for', 'do', 'break', 'continue', 'return',
            'value', 'gas', 'block', 'timestamp', 'now', 'this', 'super',
            'assembly', 'constant', 'anonymous', 'virtual', 'override', 'revert',
            'assert', 'enum', 'library', 'constructor', 'fallback',
            'receive', 'event', 'error', 'import', 'from', 'pragma'
        }
        self.builtin_properties = {
            'length', 'push', 'pop', 'shift', 'unshift', 'delete', 'keccak256',
            'abi', 'encodePacked', 'encodeWithSignature', 'transfer', 'call',
            'delegatecall', 'balance', 'gasleft', 'blockhash', 'coinbase',
            'timestamp', 'number', 'difficulty', 'gaslimit', 'basefee',
            'chainid', 'selfbalance', 'prevrandao', 'nonce'
        }

    def generate_random_name(self, length=8):
        return ''.join(random.choices(string.ascii_letters, k=length))

    def get_mapped_name(self, original_name):
        if original_name not in self.name_mapping:
            self.name_mapping[original_name] = f"v{self.generate_random_name()}"
        return self.name_mapping[original_name]

    def encode_string(self, s):
        return base64.b64encode(s.encode()).decode()

    def detect_error_messages(self, content):
        require_pattern = r'require\s*\([^,]+,\s*"([^"]+)"\)'
        require_messages = re.findall(require_pattern, content)
        revert_pattern = r'revert\s*\(\s*"([^"]+)"\s*\)'
        revert_messages = re.findall(revert_pattern, content)
        assert_pattern = r'assert\s*\([^,]+,\s*"([^"]+)"\)'
        assert_messages = re.findall(assert_pattern, content)
        self.error_messages = set(require_messages + revert_messages + assert_messages)

    def preserve_header(self, content):
        lines = content.split('\n')
        header_lines = []
        remaining_lines = []
        for line in lines:
            if '// SPDX-License-Identifier:' in line or 'pragma solidity' in line:
                header_lines.append(line)
            else:
                remaining_lines.append(line)
        return '\n'.join(header_lines), '\n'.join(remaining_lines)

    def find_variable_declarations(self, content):
        variables = set()
        mapping_pattern = r'\bmapping\s*\([^)]+\)\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*;'
        mappings = re.findall(mapping_pattern, content)
        variables.update(mappings)
        state_var_pattern = r'\b(uint\d+|int\d+|bool|string|address|bytes\d+|bytes32)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:=.*)?;'
        state_vars = re.findall(state_var_pattern, content)
        for var in state_vars:
            var_name = var[1]
            variables.add(var_name)
        func_param_pattern = r'\bfunction\s+\w+\s*\(([^)]*)\)'
        func_params = re.findall(func_param_pattern, content)
        for params in func_params:
            param_list = params.split(',')
            for param in param_list:
                parts = param.strip().split()
                if len(parts) >= 2:
                    var_name = parts[-1]
                    if var_name not in self.keywords and var_name not in self.builtin_properties and not var_name.startswith('_') and not var_name.isupper():
                        variables.add(var_name)
        return_pattern = r'\breturns\s*\(([^)]*)\)'
        returns = re.findall(return_pattern, content)
        for ret in returns:
            ret_list = ret.split(',')
            for ret_var in ret_list:
                parts = ret_var.strip().split()
                if len(parts) == 2:
                    var_name = parts[-1]
                    if var_name not in self.keywords and var_name not in self.builtin_properties and not var_name.startswith('_') and not var_name.isupper():
                        variables.add(var_name)
                elif len(parts) == 1:
                    continue
        struct_pattern = r'struct\s+\w+\s*\{([^}]+)\}'
        structs = re.findall(struct_pattern, content, re.DOTALL)
        for struct_body in structs:
            member_pattern = r'\b(?:uint\d+|int\d+|bool|string|address|bytes\d+|bytes32)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*;'
            members = re.findall(member_pattern, struct_body)
            variables.update(members)

        return variables

    def obfuscate_variables(self, content):
        variables = self.find_variable_declarations(content)
        variables = {var for var in variables if var not in self.keywords and var not in self.builtin_properties}
        for var in variables:
            if var not in self.name_mapping:
                self.name_mapping[var] = self.get_mapped_name(var)
        sorted_vars = sorted(self.name_mapping.keys(), key=lambda x: -len(x))
        string_pattern = r'\".*?\"|\'.*?\''
        parts = re.split(string_pattern, content)
        strings = re.findall(string_pattern, content)
        for i in range(len(parts)):
            for var in sorted_vars:
                parts[i] = re.sub(r'\b{}\b'.format(re.escape(var)), self.name_mapping[var], parts[i])
        new_content = ""
        for i in range(len(parts)):
            new_content += parts[i]
            if i < len(strings):
                new_content += strings[i]

        return new_content

    def obfuscate_data_map(self, content):
        mapping_pattern = r'\bmapping\s*\([^)]+\)\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*;'
        mappings = re.findall(mapping_pattern, content)
        for mapping_name in mappings:
            if mapping_name not in self.name_mapping:
                self.name_mapping[mapping_name] = self.get_mapped_name(mapping_name)
            content = re.sub(r'\b{}\b'.format(re.escape(mapping_name)), self.name_mapping[mapping_name], content)
        return content

    def obfuscate_strings(self, content):
        string_pattern = r'\"([^"]*)\"'

        def replace_string(match):
            message = match.group(1)
            if message in self.error_messages:
                return f'"{message}"'
            else:
                encoded = self.encode_string(message)
                return f'"{encoded}"'

        content = re.sub(string_pattern, replace_string, content)
        return content

    def check_code_format(self, content):
        brackets = {
            '{': '}',
            '(': ')',
            '[': ']'
        }
        stack = []
        for i, char in enumerate(content):
            if char in brackets:
                stack.append(char)
            elif char in brackets.values():
                if not stack:
                    raise SyntaxError(f"Unmatched closing bracket: {char} at position {i}")
                expected = brackets[stack.pop()]
                if char != expected:
                    raise SyntaxError(f"Mismatched brackets: expected {expected}, got {char} at position {i}")

        if stack:
            raise SyntaxError(f"Unclosed brackets: {stack}")

        return content

    def obfuscate(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        header, content = self.preserve_header(content)
        self.detect_error_messages(content)
        content = self.obfuscate_data_map(content)
        content = self.obfuscate_variables(content)
        content = self.obfuscate_strings(content)
        try:
            self.check_code_format(content)
        except SyntaxError as e:
            print("错误")

        final_content = f"{header}\n\n{content}"
        output_path = file_path.replace('.sol', '_obfuscated.sol')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_content)

        return output_path


if __name__ == "__main__":
    obfuscator = SolidityObfuscator()
    output_file = obfuscator.obfuscate("contract.sol")
    print(f"混淆代码保存在: {output_file}")
