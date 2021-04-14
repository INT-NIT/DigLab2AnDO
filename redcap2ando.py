'''
This scripts can be used to extract metadata from a PDF form following the DigLab layout.
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

# use Diglabtools -> download_records -> 'records.csv' / 'records.json'
# make sure essential info is present (exp_name, date, session_id....)
# run andogenerator using essential infos
# (use andochecker)

from DigLabTools import


import Extractor

def convert(pdf_form, root_directory):
    """

    :param pdf_form:
    :param root_directory:
    :return:
    """

    ###
    # 1. read diglab form with Diglab Extractor and generate odml metadata
    ###

    metadata_collection = Extractor.load_form(pdf_form)

    # assert essential AnDO information is present

    def flatten_collection(collection):
        '''
        Merging individual dicts of list into single dictionary
        Args:
            collection: list of dictionaries. Only the first entry needs to be a list and is ignored.

        Returns:
            result: flattened dictionary
        '''
        if not isinstance(collection, list):
            raise ValueError('Unexpected type of metadata collection. Expection an object of type `list`')

        result = {}

        if collection:
            if not isinstance(collection[0], list):
                raise ValueError('Unexpected type of metadata collection. First entry is not of type `list`')
            if not all([isinstance(i, dict) for i in collection[1:]]):
                raise ValueError('Unexpected type of metadata collection. All but first entry should be of type `dict`')

            for item in collection[1:]:
                result.update(item)

        return result

    metadata_dict = flatten_collection(metadata_collection)

    if 'dateSession' in metadata_dict and 'date' not in metadata_dict:
        metadata_dict['date'] = metadata_dict['dateSession']

    required_keys = ['expName', 'guid', 'date', 'sesNumber', 'customSesField']
    params = {}
    for req_key in required_keys:
        if req_key in metadata_dict:
            params[req_key] = metadata_dict[req_key]
        else:
            raise ValueError(f'DigLab form does not contain required key `{req_key}`.')
    ###
    # 2. create AnDO directory
    ###



    from ando.tools.generator.AnDOGenerator import AnDOSession

    AnDOSession(**params)



    ###
    # 3. store the metadata extracted from the DigLab in the right place in the AnDO structure
    ###

    # save a tsv file with odml_tables, that is called ses-YYYYMMDD_XXX_BBBB/metadata/diglab-YYYYMMDD_XXX_BBBB.tsv


    ###
    # 4. store the data files (if provided) in the AnDO structure
    ###

    # copy each of the datafile1, datafileN into ses-YYYYMMDD_XXX_BBBB/rawdata


def parse_cli():
    """Load command line arguments"""
    parser = ArgumentParser(description='Convert PDF DigLab Form to AnDO folder structure.')
    parser.add_argument('file', metavar='pdf_form',
        help='PDF form to read')
    parser.add_argument('root_data_dir', help='Root directory to create AnDO structure',
        default=None, metavar='root_dir')

    return parser.parse_args()

def main():
    args = parse_cli()
    convert(args.file, args.out)

if __name__ == '__main__':
    main()




