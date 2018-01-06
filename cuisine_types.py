import re
from lxml import etree as ET
import pprint
from collections import defaultdict

compile_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

list = []

# function to search strings for regex match
def audit_regex(attrib_types, tag_attrib, re, list):
    m = re.search(tag_attrib)
    if m:
        attrib_type = m.group()
        if type not in list:
            attrib_types[attrib_type].add(tag_attrib)

def elem_type(elem):
    return (elem.attrib['k'] == 'cuisine')

def audit(osmfile, regex):
    osm_file = open(osmfile, 'rb')
    attrib_types = defaultdict(set)

    for event, elem in ET.iterparse(osm_file, events=('start',)):
        if elem.tag == 'node' or elem.tag == 'way':
            for tag in elem.iter('tag'):
                if elem_type(tag):
                    audit_regex(attrib_types, tag.attrib['v'], regex, list)

    return attrib_types

auditregex = audit('livermore_ca_overpassAPI.osm', compile_re)

pprint.pprint(dict(auditregex))

