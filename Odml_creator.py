'''
Extractor.py [-h] [-d] [-o FILE] pdf_form

# File: Extractor.py
# Project: DICE
# File Created: Thursday, 26th November 2020 2:47:01 pm
# Author: garcia.j (Jeremy.garcia@univ-amu.fr)
# -----
# Last Modified: Thursday, 26th November 2020 2:47:47 pm
# Modified By: garcia.j (Jeremy.garcia@univ-amu.fr)
# -----
# Copyright - 2020 MIT, Institut de neurosciences de la Timone
'''
from collections import defaultdict 
from argparse import ArgumentParser
import pprint
import json
import pprint
import odml
import json
from odml.tools import XMLWriter
from datetime import datetime
from collections import ChainMap

def parse_cli():
    """Load command line arguments"""
    parser = ArgumentParser(description='Dump the form contents of a PDF.')
    parser.add_argument('-d','--debug',action="store_true",
        help='PDF form to dump the contents of')
    parser.add_argument('file', metavar='pdf_form',
        help='PDF form to dump the contents of')
    parser.add_argument('-o', '--out', help='Write output to file',
        default=None, metavar='FILE')

    return parser.parse_args()

def get_all(data):
        """[summary]

        Args:
            data ([type]): [description]

        Returns:
            [type]: [description]

        TODO: maybe do this recursively
        """
        d = dict(data[0])
        for state in data:
            if isinstance(state,list):
                for i in state:
                    d.update(**i)
            else :
                d.update(**state)
        return d


def main():
    with open('data.dat') as f:
        data = json.load(f)

    pp = pprint.PrettyPrinter(indent=4,depth=6)
    MYodML = odml.Document()

    dic=get_all(data)

    MYodML.author = dic["userName"]
    MYodML.date = datetime.strptime(dic["dateSession"], "%d/%m/%Y").strftime("%Y-%m-%d")

    sec1 = odml.Section(name="Page1",
    definition="Page 1 of the diglab",)

    MYodML.append(sec1)

    for i in dic:
        if  ("_p2" not in i) :
            prop=odml.Property(name=i,
                            values= dic[i])
            MYodML["Page1"].append(prop)
    print(MYodML)

    filename = "viewable_document.xml"
   # pp.pprint(ff)
    XMLWriter(MYodML).write_file(filename, local_style=True)
        #
if __name__ == '__main__':
    main()
    