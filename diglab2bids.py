import re
import pathlib
import json
from bep032tools.generator.BEP032Generator import BEP032Data
from redcap_bridge.server_interface import download_records
from bep032tools.validator.BEP032Validator import is_valid


config_file = pathlib.Path(__file__).parent / 'config.json'
project_name = 'SimpleProject'


with open(config_file) as f:
    conf = json.load(f)

PROJECT_DEF = pathlib.Path(conf[project_name]['project_definition'])
OUTPUT_FOLDER = pathlib.Path(conf[project_name]['output_directory'])

if not OUTPUT_FOLDER.exists():
    OUTPUT_FOLDER.mkdir()


def get_metadata(conf, format):
    """
    Fetch all recorded metadata from the server
    Parameters
    ----------
    conf:

    format:

    Returns
    ----------
    """

    records_file = OUTPUT_FOLDER / f'records.{format}'
    download_records(records_file, conf / 'project.json', format=format)

    with open(records_file) as f:
        records = json.load(f)

    return records

def convert_to_bids(records, OUTPUT_FOLDER):
    """

    Parameters
    ----------
    records:

    OUTPUT_FOLDER:

    Returns
    ----------
    """
    for record_dict in records:
        sub_id, ses_id = get_sub_ses_ids(record_dict)
        gen = BEP032Data(sub_id, ses_id, modality='ephys')
        files = gen.generate_data_files()
        gen.register_data_files(files)
        gen.basedir = OUTPUT_FOLDER
        gen.generate_structure()
        files = gen.generate_metadata_files()
        gen.register_metadata_files(files)


        # generate_metadata_files(record_dict, gen.get_data_folder())


def get_sub_ses_ids(record_dict):
    """

    Parameters
    ----------
    record_dict:


    Returns
    ----------
    """
    sub_id = record_dict['guid']
    ses_id = f"{record_dict['date']}"

    for sep, key in zip(['id', 'c'], ['ses_number', 'ses_custom_field']):
        if key in record_dict:
            ses_id += f"{sep}{record_dict[key]}"

    # clean strings
    sub_id = re.sub(r'[\W_]+', '', sub_id)
    ses_id = re.sub(r'[\W_]+', '', ses_id)


    if ses_id.isalnum() and sub_id.isalnum():
        return sub_id, ses_id
    else:
        raise Exception("Record dict must only contain alphanumeric characters")


if __name__ == '__main__':
    # json way of the world
    rec = get_metadata(PROJECT_DEF, 'json')
    if not rec:
        raise ValueError(f'No records found for project {project_name}.')
    convert_to_bids(rec, OUTPUT_FOLDER)
    is_valid(OUTPUT_FOLDER)



# def convert(project_name, output_directory):
#     # open config , find project specifications
#     # use Diglabtools -> download_records -> 'records.csv' / 'records.json'
#     # make sure essential info is present (exp_name, date, session_id....)
#     # run andogenerator using essential infos
#     # (use andochecker)
#
#     """
#     :param pdf_form:
#     :param root_directory:
#     :return:
#     """
#
#     ###
#     # 1. read diglab form with Diglab Extractor and generate odml metadata
#     ###
#
#     metadata_collection = Extractor.load_form(pdf_form)
#
#     # assert essential AnDO information is present
#
#     def flatten_collection(collection):
#         '''
#         Merging individual dicts of list into single dictionary
#         Args:
#             collection: list of dictionaries. Only the first entry needs to be a list and is ignored.
#
#         Returns:
#             result: flattened dictionary
#         '''
#         if not isinstance(collection, list):
#             raise ValueError('Unexpected type of metadata collection. Expection an object of type `list`')
#
#         result = {}
#
#         if collection:
#             if not isinstance(collection[0], list):
#                 raise ValueError('Unexpected type of metadata collection. First entry is not of type `list`')
#             if not all([isinstance(i, dict) for i in collection[1:]]):
#                 raise ValueError('Unexpected type of metadata collection. All but first entry should be of type `dict`')
#
#             for item in collection[1:]:
#                 result.update(item)
#
#         return result
#
#     metadata_dict = flatten_collection(metadata_collection)
#
#     if 'dateSession' in metadata_dict and 'date' not in metadata_dict:
#         metadata_dict['date'] = metadata_dict['dateSession']
#
#     required_keys = ['expName', 'guid', 'date', 'sesNumber', 'customSesField']
#     params = {}
#     for req_key in required_keys:
#         if req_key in metadata_dict:
#             params[req_key] = metadata_dict[req_key]
#         else:
#             raise ValueError(f'DigLab form does not contain required key `{req_key}`.')
#
#     # TODO: Convert date to datetime object
#     ###
#     # 2. create AnDO directory
#     ###
#
#
#     # cheating for testing purposes only
#     # TODO: Remove this cheat
#     params['expName'] = 'MyCoolExperiment'
#     params['guid'] = '012345'
#
#
#     from ando.tools.generator.AnDOGenerator import AnDOSession
#
#     ses = AnDOSession(**params)
#     ses.generate_folders(root_directory)
#
#
#     ###
#     # 3. store the metadata extracted from the DigLab in the right place in the AnDO structure
#     ###
#
#     # save a tsv file with odml_tables, that is called ses-YYYYMMDD_XXX_BBBB/metadata/diglab-YYYYMMDD_XXX_BBBB.tsv
#
#
#     ###
#     # 4. store the data files (if provided) in the AnDO structure
#     ###
#
#     # copy each of the datafile1, datafileN into ses-YYYYMMDD_XXX_BBBB/rawdata
#
#
# def parse_cli():
#     """Load command line arguments"""
#     parser = ArgumentParser(description='Convert PDF DigLab Form to AnDO folder structure.')
#     parser.add_argument('file', metavar='pdf_form',
#         help='PDF form to read')
#     parser.add_argument('root_data_dir', help='Root directory to create AnDO structure',
#         default=None, metavar='root_dir')
#
#     return parser.parse_args()
#
# def main():
#     args = parse_cli()
#     convert(args.file, args.out)
#
# if __name__ == '__main__':
#     main()
#
#
#
#
# def cli():
#     """
#     Cli
#     """
#
#     parser = argparse.ArgumentParser(description='')
#     parser.add_argument('inputFile',
#                         help='Path to the input file csv one.')
#     parser.add_argument('--outputDirectory',
#                         help='Path to the output that contains the resumes.')
#     return parser
#
#

#
#
# def generate():
#     """
#     run andogenerator using essential infos
#     Parameters
#     ----------
#
#     Returns
#     ----------
#     """
#
# if __name__ == "__main__":
#
#     arg_parser = cli()
#     parsed_args = arg_parser.parse_args(sys.argv[1:])
#
#     if os.path.exists(parsed_args.inputDirectory):
#         csv_file = download(parsed_args.inputFile)
#         sub_id, ses_id =  get_info(csv_file)
#         generate(sub_id,ses_id,parsed_args.outputDirectory)
#         ando.is_valid(parsed_args.outputDirectory)
#




