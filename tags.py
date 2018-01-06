from lxml import etree as ET
import pprint
from collections import defaultdict

osm_file = open('livermore_ca_overpassAPI.osm', 'rb')

def count_tags(filename): # provide a file to parse
    
    counts = defaultdict(int) # variable as dictionary for top element tags and their occurrences
    for line in ET.iterparse(filename): # parsing file line by line 
        current = line[1].tag 
        counts[current] += 1 # adding 1 to every reoccuring tag count
    return counts

print(count_tags(osm_file))
