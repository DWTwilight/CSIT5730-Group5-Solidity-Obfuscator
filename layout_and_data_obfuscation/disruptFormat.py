import re
import sys
from random import random

class disruptFormat:

	def __init__(self, input_file_path):
		self.input_file_path = input_file_path
		self.content = self.open_file(self.input_file_path)

	def open_file(self, file_path):
		with open(file_path, 'r', encoding='utf-8') as f:
			return f.read()

	def save_to_file(self, content, output_file_path):
		with open(output_file_path, 'w', encoding='utf-8') as f:
			f.write(content)

	def reSubT(self, _content):
		pattern = r"\t"
		return re.sub(pattern, " ", _content)

	def reSubN(self, _content):
		pattern = r"\n"
		return re.sub(pattern, "\t", _content)

	def reSubS(self, _content):
		pattern = r"(\s){1,}"
		return re.sub(pattern, "\n", _content)

	def disrupt(self, _prob):
		nowContent = self.content
		if random() < _prob:
			nowContent = self.reSubT(nowContent)
		nowContent = self.reSubN(nowContent)
		if random() < _prob:
			nowContent = self.reSubS(nowContent)
		return nowContent

	def process_and_save(self, output_file_path, prob):
		disrupted_content = self.disrupt(prob)
		self.save_to_file(disrupted_content, output_file_path)
		print(f"Processed content has been saved to: {output_file_path}")


def process_file(input_file_path, output_file_path, prob):
	disruptor = disruptFormat(input_file_path)
	disruptor.process_and_save(output_file_path, prob)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python disruptFormat.py <input_file_path> <output_file_path> <probability>")
        sys.exit(1)

    input_file_path = sys.argv[1]
    output_file_path = sys.argv[2]
    try:
        prob = float(sys.argv[3])
        if not (0 <= prob <= 1):
            raise ValueError("Probability must be a float between 0 and 1.")
    except ValueError as e:
        print(f"Invalid probability value: {e}")
        sys.exit(1)

    # Call the process_file function
    process_file(input_file_path, output_file_path, prob)
