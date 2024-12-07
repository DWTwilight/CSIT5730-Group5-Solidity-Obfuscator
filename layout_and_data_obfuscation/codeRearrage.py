# import re
import regex as re
import random

def shuffle_and_indent_methods(sol_file_path, output_file_path):

    with open(sol_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    #Extract the header (pragma, SPDX, contract declaration)
    header_pattern = re.compile(r"(^[\s\S]*?)(contract\s+\w+\s*{)", re.DOTALL)
    header_match = header_pattern.search(content)

    if not header_match:
        print("No valid contract header found. Ensure the Solidity file has a valid contract declaration.")
        return

    header = header_match.group(1)
    contract_start = header_match.group(2)

    #Extract functions and modifiers
    method_pattern = re.compile(
        r"""
        (                           
            \bfunction\s+\w+\s*     
            \([^)]*\)\s*            
            (?:public|external|private|internal)?\s*  
            (?:view|pure|payable|onlyAdmin|returns|contractActive)?\s*       
            (?:contractActive|onlyAdmin|returns\s*\([^)]*\))?\s*  
            (?:returns\s*\([^)]*\))?\s*   
            {(?:[^{}]*|{(?:[^{}]*|{[^{}]*})*})*}                        
        )
        |
        (                           
            \breceive\s*\(\)\s*    
            (?:external)?\s*   
            (?:payable)?\s*           
            \s*{(?:[^{}]*|{(?:[^{}]*|{[^{}]*})*})*} 
        )
        |
        (                          
            \bmodifier\s+\w+\s*     
            \([^)]*\)?\s*          
            {(?:[^{}]*|{(?:[^{}]*|{[^{}]*})*})*}  
        )
        |
        (                          
            \bconstructor\s*\([^)]*\)\s* 
            {(?:[^{}]*|{(?:[^{}]*|{[^{}]*})*})*}
        )
        """,
        re.DOTALL | re.VERBOSE  
    )

    methods_modifiers = method_pattern.findall(content)

    # test
    # if methods_modifiers:
    #     print(f"Found {len(methods_modifiers)} methods:")
    #     for match in methods_modifiers:
    #         print(match)
    # else:
    #     print("No methods or modifiers were found. Ensure the Solidity file contains valid methods or modifiers.")


    methods_modifiers = [
        "".join(item).strip() for item in methods_modifiers if any(item)
    ]

    if not methods_modifiers:
        print("No methods or modifiers were found. Ensure the Solidity file contains valid methods or modifiers.")
        return

    #Remove matched functions and modifiers from content
    content_without_methods = method_pattern.sub("", content)

    #Find the contract body and closing brace
    contract_body_pattern = re.compile(r"(contract\s+\w+\s*{.*?)(})", re.DOTALL)
    contract_match = contract_body_pattern.search(content_without_methods)

    if not contract_match:
        print("Failed to find the contract body. Ensure the Solidity contract is properly formatted.")
        return

    contract_body = contract_match.group(1)
    closing_brace = contract_match.group(2)

    #Shuffle functions and modifiers randomly
    random.shuffle(methods_modifiers)

    #Format functions and modifiers with proper indentation
    formatted_methods_modifiers = "\n\n".join(
        "    " + "\n    ".join(item.strip().splitlines()) for item in methods_modifiers
    )
    
    #Format the contract body
    formatted_contract_body = re.sub(r"\n{2,}", "\n\n", contract_body.strip())

    #Combine into final contract
    final_contract = (
        f"{header.strip()}\n\n{formatted_contract_body}\n\n{formatted_methods_modifiers}\n\n{closing_brace}"
    )

    #Write to output file
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(final_contract)

    print(f"Methods and modifiers shuffled and saved to: {output_file_path}")

# example
# shuffle_and_indent_methods('./example/example1.sol', 'ShuffledSolidityFile1.sol')
