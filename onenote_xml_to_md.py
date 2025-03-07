#!/usr/bin/env python3
import os
from mathml2latex import mathml2latex
from mathml2latex.unicode_map import unicode_map
import re
import sys

onenote_namespace = "{http://schemas.microsoft.com/office/onenote/2013/onenote}"

def process_text(text):
    #Preprocess to remove xml tags
    text = re.sub(r'<span.*?>|</span>', '', text)
    text = re.sub(r'<span\nlang=en-US>', '', text)
    text = re.sub(r'<br>', '', text)
    text = text.replace('&nbsp;', ' ')

    text = mathml2latex.convert(text)

    # Sometimes the unicode characters are not included by OneNote in the XML file
    for utf_code, latex_code in unicode_map.items():
        utf_code = utf_code.encode('utf-8').decode('unicode_escape')
        text = text.replace(utf_code, latex_code)

    # Remove any remaining xml tags, usually font and color tags
    text = re.sub(r'<span.*?>', '', text, flags=re.DOTALL)
    
    return text


def process_element(element,output):
    for child in element:
        if child.tag == onenote_namespace + "OEChildren":
            process_element(child,output)
        elif child.tag == onenote_namespace + "OE":
            if 'quickStyleIndex' in child.attrib and child.attrib['quickStyleIndex'] == '1':
                text = child.find(onenote_namespace + "T").text
                if text!=None:
                    text = process_text(text)
                    # Prevents math lines from being accidentally rendered as a title
                    if text.startswith("$$"):
                        output.write(text + "\n\n")
                    else:
                        output.write("## " + text + "\n\n")
            elif 'quickStyleIndex' in child.attrib and child.attrib['quickStyleIndex'] == '3':
                text = child.find(onenote_namespace + "T").text
                if text!=None:
                    text = text.replace('&nbsp;', ' ')
                    output.write("### " + mathml2latex.convert(text) + "\n\n")
            elif child.find(onenote_namespace + "List"):
                list_element = child.find(onenote_namespace + "List")
                number_element=list_element.find(onenote_namespace + "Number")
                text_element = child.find(onenote_namespace + "T")

                if text_element.text and number_element!=None:
                    number = number_element.attrib["text"]
                    text = process_text(text_element.text)
                    
                    # Prevent centering of math lines if they are in a list
                    text=text.replace("$$", "$")

                    output.write(number +" "+ text + "\n\n")
            else:
                process_element(child,output)
        elif child.tag == onenote_namespace + "T":
            if child.text:
                text = process_text(child.text)

                output.write(text+"\n\n")

def convert(input_filename, output_filename):
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

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python xml_converter.py <input_file> <output_file>")
        sys.exit(1)

    input_filename = sys.argv[1]
    output_filename = sys.argv[2]

    convert(input_filename, output_filename)