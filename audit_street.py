import re
from lxml import etree as ET
import pprint
from collections import defaultdict

lower = re.compile(r'^([a-z]|_)*$')  
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')  
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

accepted_street_names = ["Avenue", "Boulevard", "Commons", "Court", "Drive", "Lane", "Parkway", "Place", "Road", "Square", "Street", "Trail", "West", "East", "North", "South", "Terrace", "Loop", "Common", "Way", "Circle"]


def audit_street_type(street_types, street_name, regex, accepted_street_names):
    '''
    group all street_name into street_type variable.  If street_name not in our 
    aacepted_street_name variable we add the street name.

    '''
    m = regex.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in accepted_street_names:
            street_types[street_type].add(street_name)

def is_street_name(elem):
    # the key element tag we're searching for
	return (elem.attrib['k'] == 'addr:street')

def audit(osmfile, regex):
   
	osm_file = open(osmfile, 'rb')
	street_types = defaultdict(set)

    # for loop and parse all node's and way's for tag elements from our is_street_name
    # function and return the values of all k:v pair not in our accepted_steet_name variable
	for event, elem in ET.iterparse(osm_file, events=('start',)):
		if elem.tag == 'node' or elem.tag == 'way':
			for tag in elem.iter('tag'):
				if is_street_name(tag):
					audit_street_type(street_types, tag.attrib['v'], regex, accepted_street_names)

	return street_types

street_types = audit('livermore_ca_overpassAPI.osm', street_type_re)

pprint.pprint(dict(street_types))

# Begin updating street names
def update_name(name, mapping, regex):
    # mapping out the correct 
    m = regex.search(name)
    if m:
        street_type = m.group()
        if street_type in mapping_street:
            name = re.sub(regex, mapping[street_type], name)
            
        return name

# mapping for abbreviations
mapping_street = {'St': 'Street',
          'St.': 'Street',
          'Ave': 'Avenue',
          'Rd.': 'Road',
          'Ave': 'Avenue',
          'Blvd': 'Boulvard',
          'Dr': 'Drive',
          'Pkwy': 'Parkway',
          'Rd': 'Road',
          'Ct': 'Court',}

# confirm corrections were made
for street_type, ways in street_types.items():
    for name in ways:
        better_name = update_name(name, mapping, street_type_re)
        print(name, "=>", better_name)


# City Name Audit

compile_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
list = []


    # function to search strings to group regex matches and add to our list of city name
def audit_regex(attrib_types, tag_attrib, re, list):
    m = re.search(tag_attrib)
    if m:
        attrib_type = m.group()
        if type not in list:
            attrib_types[attrib_type].add(tag_attrib)


def elem_type(elem):
    return (elem.attrib['k'] == 'addr:city')


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


# the function above update_name takes the mapping_street variable and updates the street names.  The function below adds to the updated street names and uses the mapping_city variable to update the correct city names.  

def update(name, mapping, regex):
    m = regex.search(name)
    if m:
        type = m.group()
        if type in mapping_city:
            name = re.sub(regex, mapping[auditregex], name)

    return name


mapping_city = {'livermore': 'Livermore',
           'pleasanton': 'Pleasanton',
           'Dulin': 'Dublin'}

for auditregex, ways in auditregex.items():
    for name in ways:
        better_name = update(name, mapping, compile_re)
        print(name, '=>', better_name)

# create json file to import into MonogoDB

from datetime import datetime

CREATED = ['version', 'changeset', 'timestamp', 'user', 'uid']

def shape_element(element):
    node = {}
    if element.tag == 'node' or element.tag == 'way':
        node['type'] = element.tag
        
        for attrib in element.attrib:
            
            if attrib in CREATED:
                if 'created' not in node:
                    node['created'] = {}
                if attrib == 'timestamp':
                    node['created'][attrib] = datetime.strptime(element.attrib[attrib], '%Y-%m-%dT%H:%M:%SZ')
                else:
                    node['created'][attrib] = element.get(attrib)
                    
            if attrib in ['lat', 'lon']:
                lat = float(element.attrib.get('lat'))
                lon = float(element.attrib.get('lon'))
                node['pos'] = [lat, lon]
                
            else:
                node[attrib] = element.attrib.get(attrib)
                
        for tag in element.iter('tag'):
            key = tag.attrib['k']
            value = tag.attrib['v']
            if not problemchars.search(key):
                
                if lower_colon.search(key) and key.find('addr') == 0:
                    if 'address' not in node:
                        node['address'] = {}
                    sub_attr = key.split(':')[1]
                    if is_street_name(tag):
                        better_name = update_name(name, mapping, street_type_re)
                        node['address'][sub_attr] = better_name
                    else:
                        node['address'][sub_attr] = value
                        
                elif not key.find('addr') == 0:
                    if key not in node:
                        node[key] = value
                else:
                    node['tag:' + key] = value
                    
            for nd in element.iter('nd'):
                 if 'node_refs' not in node:
                        node['node_refs'] = []
                        node['node_refs'].append(nd.attrib['ref'])
            return node
        else:
            return None

import json
from bson import json_util

def process_map(file_in, pretty = False):
    file_out = '{0}.json'.format(file_in)
    with open(file_out, 'w') as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                if pretty:
                    fo.write(json.dumps(el, indent=2, default=json_util.default)+'\n')
                else:
                    fo.write(json.dumps(el, default=json_util.default) + '\n')
                    

process_map('livermore_ca_overpassAPI.osm')
