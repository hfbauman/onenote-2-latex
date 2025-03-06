#!/usr/bin/env python3
import os
from mathml2latex import mathml2latex
import re
import sys

onenote_namespace = "{http://schemas.microsoft.com/office/onenote/2013/onenote}"

def process_element(element,output):
    for child in element:
        if child.tag == onenote_namespace + "OEChildren":
            process_element(child,output)
        elif child.tag == onenote_namespace + "OE":
            if 'quickStyleIndex' in child.attrib and child.attrib['quickStyleIndex'] == '1':
                # print("## " + child.find(onenote_namespace + "T").text)
                output.write("## " + child.find(onenote_namespace + "T").text + "\n")
            elif 'quickStyleIndex' in child.attrib and child.attrib['quickStyleIndex'] == '3':
                # print("### " + child.find(onenote_namespace + "T").text)
                output.write("### " + child.find(onenote_namespace + "T").text + "\n")
            else:
                process_element(child,output)
        elif child.tag == onenote_namespace + "T":
            if child.text:
                #Preprocess to remove xml tags
                text = re.sub(r'<span.*?>|</span>', '', child.text)
                text = re.sub(r'<span\nlang=en-US>', '', text)
                text = text.replace('&nbsp;', ' ')

                # print(mathml2latex.convert(text))
                output.write(mathml2latex.convert(text)+"\n")

def main(input_filename, output_filename):
    input_file = open(input_filename, "r", encoding="utf-8")
    input = input_file.read()
    input_file.close()

    import xml.etree.ElementTree as ET

    tree = ET.parse(input_filename)
    root = tree.getroot()

    with open(output_filename, 'w') as output:
        for section in root:
            if section.tag == onenote_namespace + "Title":
                for child in section.iter():
                    if child.tag == onenote_namespace + "T":
                        output.write("# " + child.text + "\n")

            elif section.tag == onenote_namespace + "Outline":
                for attribute in section:
                    process_element(attribute,output)

current_directory = os.path.dirname(os.path.realpath(__file__))+os.sep
input_filename=current_directory +"Lecture 9.xml"
output_filename=current_directory+"Lecture 9 converted.md"