#!/usr/bin/env python3
"""
A simple Python script to convert a OneNote XML file to Markdown.
MathML content (embedded in the text as CDATA or comments) is left unchanged.
Usage: python convert.py <input_xml_file>
"""

import sys
import xml.etree.ElementTree as ET

# Define the OneNote namespace used in the XML
NS = {'one': 'http://schemas.microsoft.com/office/onenote/2013/onenote'}

def get_text(elem):
    """Recursively collect text (including CDATA) from an element."""
    parts = []
    if elem.text:
        parts.append(elem.text)
    for child in elem:
        parts.append(get_text(child))
        if child.tail:
            parts.append(child.tail)
    return ''.join(parts)

def process_oe(oe, indent=0):
    """
    Process a one:OE element to Markdown.
    Uses the attribute 'quickStyleIndex' to decide on Markdown formatting.
    If a one:List child is present, a bullet list is assumed.
    MathML sections in the text are left as is.
    """
    md = ""
    qs = oe.get('quickStyleIndex', "2")  # default to paragraph style

    # Determine Markdown prefix based on quickStyleIndex:
    # Index 0 and 1 will be taken as top-level headers; index 3 as secondary header.
    if qs in ("0", "1"):
        prefix = "# "
    elif qs == "3":
        prefix = "## "
    else:
        prefix = ""

    # Check if this OE is part of a list; if so, use a bullet and indent.
    if oe.find('one:List', NS) is not None:
        bullet = "- "
        prefix = "  " * indent + bullet
    else:
        prefix = "  " * indent + prefix

    # Get the text from the one:T element (this will include any MathML embedded)
    t_elem = oe.find('one:T', NS)
    text = get_text(t_elem).strip() if t_elem is not None else ""

    # Build the Markdown for this element
    md += prefix + text + "\n"

    # Process any nested one:OEChildren elements recursively
    oe_children = oe.find('one:OEChildren', NS)
    if oe_children is not None:
        for child in oe_children.findall('one:OE', NS):
            md += process_oe(child, indent=indent+1)
    return md

def convert_xml_to_markdown(xml_file):
    """
    Converts the OneNote XML file to Markdown.
    Extracts the page title and then processes each outline.
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()
    md = ""

    # Extract the page title from one:Title/one:OE/one:T (if available)
    title_elem = root.find('one:Title/one:OE/one:T', NS)
    if title_elem is not None and title_elem.text:
        md += "# " + title_elem.text.strip() + "\n\n"

    # Process each one:Outline element and its children (one:OE)
    for outline in root.findall('.//one:Outline', NS):
        for oe in outline.findall('one:OE', NS):
            md += process_oe(oe) + "\n"
    return md

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python convert.py <input_xml_file>")
        sys.exit(1)
    input_file = sys.argv[1]
    markdown = convert_xml_to_markdown(input_file)
    print(markdown)
