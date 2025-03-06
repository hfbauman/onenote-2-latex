import os
from mathml2latex import mathml2latex

current_directory = os.path.dirname(os.path.realpath(__file__))+os.sep

input_filename=current_directory+"Lecture 9.md"
output_filename=current_directory+"Lecture 9 converted.md"

input_file = open(input_filename, "r", encoding="utf-8")
input = input_file.read()
input_file.close()
output = mathml2latex.convert(input)
output_file = open(output_filename, "w", encoding="utf-8")
output_file.write(output)
output_file.close()