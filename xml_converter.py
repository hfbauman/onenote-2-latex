#!/usr/bin/env python3
import os

def process_element(element):
    for child in element:
        if child.tag == onenote_namespace + "OEChildren":
            process_element(child)
        elif child.tag == onenote_namespace + "OE":
            if 'quickStyleIndex' in child.attrib and child.attrib['quickStyleIndex'] == '1':
                print("## " + child.find(onenote_namespace + "T").text)
            elif 'quickStyleIndex' in child.attrib and child.attrib['quickStyleIndex'] == '3':
                print("### " + child.find(onenote_namespace + "T").text)
            else:
                process_element(child)
        elif child.tag == onenote_namespace + "T":
            if child.text:
                print(child.text)


input_filename=current_directory = os.path.dirname(os.path.realpath(__file__))+os.sep+"Lecture 9.xml"
output_filename=current_directory+"Lecture 9 converted.md"

input_file = open(input_filename, "r", encoding="utf-8")
input = input_file.read()
input_file.close()

import xml.etree.ElementTree as ET

onenote_namespace = "{http://schemas.microsoft.com/office/onenote/2013/onenote}"

tree = ET.parse(input_filename)
root = tree.getroot()

for section in root:
    if section.tag == onenote_namespace + "Title":
        for child in section.iter():
            if child.tag == onenote_namespace + "T":
                print("# "+child.text)

    elif section.tag == onenote_namespace + "Outline":
        for attribute in section:
            process_element(attribute)