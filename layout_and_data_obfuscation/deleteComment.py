import re

class DeleteComment:
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path
        self.content = self.open_file(self.input_path)

    def delete_single_comment(self, _content):
        pattern = r"//(?! SPDX-License-Identifier:).*?(\n|$)"
        return re.sub(pattern, "\n", _content, re.M)
    
    def delete_multiple_comment(self, _content):
        pattern = r"/\*((.)|((\r)?\n))*?\*/"
        return re.sub(pattern, "", _content, re.S)
    
    def delete_extra_empty_lines(self, _content):
        return re.sub(r"\n\s*\n+", "\n\n", _content)
    
    def delete(self):
        content = self.content
        content = self.delete_single_comment(content)
        content = self.delete_multiple_comment(content)
        content = self.delete_extra_empty_lines(content)
        return content

    def open_file(self, _path):
        with open(_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content

    def save_to_file(self, content):
        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.write(content)

def clean_and_save(input_file_path, output_file_path):
    deleter = DeleteComment(input_file_path, output_file_path)
    cleaned_data = deleter.delete()  
    deleter.save_to_file(cleaned_data)
    print(f"Comments have been deleted and saved to: {output_file_path}")


if __name__ == "__main__":
    input_file_path = input("Enter the path of the source file: ")  
    output_file_path = input("Enter the path where the output file should be saved: ")  
    clean_and_save(input_file_path, output_file_path)