'''
This code can be used to extract metadata from a PDF form following the DigLab layout.
Example:
    $ python diglab2ando.py  [pdf file]  [root data dir] -f [datafile1]  [datafile2] ... [datafileN]
Usage:
diglab2ando.py pdf_file root_data_dir [-f datafile1 ... datafileN]
    
    mandatory argument:
    pdf_form                      pdf form generated using the DigLaB tool used at INT
    root_data_dir                 root directory that follows the AnDO specifications, where the metadata
                                  and data will be stored
    
    optional argument:
    -f datafile1 ... datafileN    list of files containing various data to be included in the AnDO directory
'''


###
# 1. read diglab form with DICE and generate odml metadata
###

odml_data = 


###
# 2. create AnDO directory
###

from AnDOChecker.tools import AnDOGenerator

AnDOGenerator(info from odml_data, root_data_dir)


###
# 3. store the metadata extracted from the DigLab in the right place in the AnDO structure
###

# save a tsv file with odml_tables, that is called ses-YYYYMMDD_XXX_BBBB/metadata/diglab-YYYYMMDD_XXX_BBBB.tsv


###
# 4. store the data files (if provided) in the AnDO structure
###

# copy each of the datafile1, datafileN into ses-YYYYMMDD_XXX_BBBB/rawdata






