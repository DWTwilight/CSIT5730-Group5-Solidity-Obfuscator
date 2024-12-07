import sys
import deleteComment, codeRearrage, disruptFormat
import variableTransformar


if len(sys.argv) != 3:
    print("Usage: python test.py <input_file_path> <output_file_path>")
    sys.exit(1)

input_file_path = sys.argv[1]
output_file_path = sys.argv[2]

deleteComment.clean_and_save(input_file_path, output_file_path)
variableTransformar.variableTransformar(output_file_path, output_file_path)
codeRearrage.shuffle_and_indent_methods(output_file_path, output_file_path)

disruptFormat.process_file(output_file_path, output_file_path, 0.5)