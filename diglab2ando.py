
import pathlib
import json
from ando.tools.generator.AnDOGenerator import AnDOData
from redcap_bridge.server_interface import download_records

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

    Returns
    ----------
    """

    records_file = OUTPUT_FOLDER / f'records.{format}'
    download_records(records_file, conf / 'project.json', format=format)

    with open(records_file) as f:
        records = json.load(f)

    return records

def convert_to_bids(records, OUTPUT_FOLDER):

    for record_dict in records:
        sub_id, ses_id = get_sub_ses_ids(record_dict)
        gen = AnDOData(sub_id, ses_id, modality='ephys')
        gen.register_data_files(get_data_file())
        gen.basedir = OUTPUT_FOLDER
        gen.generate_structure()
        gen.generate_data_files(mode='move')

        generate_metadata_files(record_dict, gen.get_data_folder())


def get_sub_ses_ids(record_dict):
    sub_id = record_dict['guid']
    # TODO: This still needs to be tweaked to only contain alphanumeric characters
    ses_id = record_dict['date'] + record_dict['ses_number'] + record_dict['ses_custom_field']

    return sub_id, ses_id


def get_data_file():
    # TODO: this needs to be replaced by a project-specific
    #  functions that converts the data to nix and provides the path to the nix
    #  file
    dummy_nix_file = OUTPUT_FOLDER / 'dummy_file.nix'
    if not dummy_nix_file.exists():
        dummy_nix_file.touch()
    return dummy_nix_file


def generate_metadata_files(record_dict, save_dir):
    # TODO: this needs to generate the basic BIDS metadata files and
    # these can then be rearranged into the right location by the ando generator
    filename = f'sub-{record_dict["guid"]}_ses-{record_dict["date"]}_ephys.json'
    with open(save_dir / filename, 'w') as f:
        json.dump(record_dict, f)


if __name__ == '__main__':
    # json way of the world
    rec = get_metadata(PROJECT_DEF, 'json')
    if not rec:
        raise ValueError(f'No records found for project {project_name}.')
    convert_to_bids(rec, OUTPUT_FOLDER)


# def get_info(path_to_csv_file):
#     """
#     Make sure essential info is present (exp_name, session_id)
#     Parameters
#     ----------
#     path_to_csv_file: str
#         Path to config file
#
#
#     Returns
#     ----------
#     str
#         ses_id string
#     str
#         sub_id string
#     """
#     with open(path_to_csv_file, 'r') as read_obj:
#         csv_reader = reader(read_obj)
#         for row in csv_reader:
#             try:
#                 sub_id = row["sub_id"]
#                 ses_id = row["ses_id"]
#             except KeyError:
#                 print(f"key not found.")
#         return sub_id, ses_id

#
#
#
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




