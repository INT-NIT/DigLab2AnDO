import shutil
import argparse
import re

import bep032tools.validator.BEP032Validator

try:
    import pandas as pd

    HAVE_PANDAS = True
except ImportError:
    HAVE_PANDAS = False
from bep032tools.validator.BEP032Validator import build_rule_regexp
from bep032tools.rulesStructured import RULES_SET
from bep032tools.generator.utils import *
from bep032tools.generator.BEP032Generator import BEP032Data

METADATA_LEVELS = {i: r['authorized_metadata_files'] for i, r in enumerate(RULES_SET)}
METADATA_LEVEL_BY_NAME = {build_rule_regexp(v)[0]: k for k, values in METADATA_LEVELS.items() for v
                          in values}

# TODO: These can be extracted from the BEP032Data init definition. Check out the
# function inspection options
ESSENTIAL_CSV_COLUMNS = ['sub_id', 'ses_id']
OPTIONAL_CSV_COLUMNS = ['tasks', 'runs']


class BEP032TemplateData(BEP032Data):
    """
    Representation of a BEP032 Data, as specified by in the
    [ephys BEP](https://bids.neuroimaging.io/bep032)

    The BEP032Data object can track multiple realizations of `split`, `run`, `task` but only a
    single realization of `session` and `subject`, i.e. to represent multiple `session` folders,
    multiple BEP032Data objects are required. To include multiple realizations of tasks
    or runs, call the `register_data` method for each set of parameters separately.

    Parameters
    ----------
    sub_id : str
        subject identifier, e.g. '0012' or 'j.s.smith'
    ses-id : str
        session identifier, e.g. '20210101' or '007'
    tasks : str
        task identifier of data files
    runs : str
        run identifier of data files
    """

    def __init__(self, sub_id, ses_id, diglab_df=None, project_name=None):
        super().__init__(sub_id, ses_id, modality='ephys')
        self.diglab_df = diglab_df
        self.project_name = project_name

    def generate_metadata_file_participants(self, output):
        assert self.sub_id == self.diglab_df['guid'].values[0]
        participant_df = pd.DataFrame([['sub-' + self.sub_id]], columns=['participant_id'])
        if not output.with_suffix('.tsv').exists():
            save_tsv(participant_df, output)

    def generate_metadata_file_tasks(self, output):
        # here we want to call save_json and save_tsv()
        pass

    def generate_metadata_file_dataset_description(self, output):
        dataset_dict = {
            "Name": self.project_name,
            "BIDSVersion": "1.6.0",
            "License": "CC BY 4.0",
            "Authors": self.diglab_df['user'].to_list(),
            "Acknowledgements": "TBA",
            "HowToAcknowledge": "TBA",
            "Funding": ["TBA"],
            "ReferencesAndLinks": "TBA",
            "EthicsApprovals": self.diglab_df['ethical_protocol_id'].to_list()
        }
        save_json(dataset_dict, output)

    def generate_metadata_file_sessions(self, output):
        session_df = pd.DataFrame([
            ['ses-' + self.ses_id, '2009-06-15T13:45:30', '120']],
            columns=['session_id', 'acq_time', 'systolic_blood_pressure'])
        if not output.with_suffix('.tsv').exists():
            save_tsv(session_df, output)

    def generate_metadata_file_probes(self, output):
        probes_df = pd.DataFrame([
            ['e380a', 'multi-shank', 0, 'iridium-oxide', 0, 0, 0, 'circle', 20],
            ['e380b', 'multi-shank', 1.5, 'iridium-oxide', 0, 100, 0, 'circle', 20],
            ['t420a', 'tetrode', 3.6, 'iridium-oxide', 0, 200, 0, 'circle', 20],
            ['t420b', 'tetrode', 7, 'iridium-oxide', 500, 0, 0, 'circle', 20]],
            columns=['probe_id', 'type', 'coordinate_space', 'material', 'x', 'y', 'z', 'shape',
                     'contact_size'])
        save_tsv(probes_df, output)

    def generate_metadata_file_channels(self, output):
        channels_df = pd.DataFrame([
            # [129, 1, 'neuronal', 'mV', 30000, 30, 'good'],
            # [130, 3, 'neuronal', 'mV', 30000, 30, 'good'],
            # [131, 5, 'neuronal', 'mV', 30000, 30, 'bad'],
            # [132, 'n/a', 'sync_pulse', 'V', 1000, 1, 'n/a']
            ],
            columns=['channel_id', 'contact_id', 'type', 'units', 'sampling_frequency', 'gain',
                     'status'])
        save_tsv(channels_df, output)

    def generate_metadata_file_contacts(self, output):
        contact_df = pd.DataFrame([
            # [1, 'e380a', 0, 1.1, 'iridium-oxide', 0, 0, 0, 'circle', 20],
            # [2, 'e380a', 0, 1.5, 'iridium-oxide', 0, 100, 0, 'circle', 20],
            # [3, 'e380a', 0, 3.6, 'iridium-oxide', 0, 200, 0, 'circle', 20],
            # [4, 'e380a', 1, 7, 'iridium-oxide', 500, 0, 0, 'circle', 20],
            # [5, 'e380a', 1, 7, 'iridium-oxide', 500, 100, 0, 'circle', 20],
            # [6, 'e380a', 1, 7, 'iridium-oxide', 500, 200, 0, 'circle', 20]
            ],
            columns=['contact_id', 'probe_id', 'shank_id', 'impedance', 'material', 'x', 'y', 'z',
                     'shape', 'contact_size'])
        save_tsv(contact_df, output)

    def _get_compressed_choices(self, question_label, active_value=1):
        # extract columns belonging to this question (if it's a multiple choice question)
        question_df = self.diglab_df.filter(regex=f'{question_label}___\w', axis=1)
        # shorten column names and only use choices as column labels
        question_df.columns = question_df.columns.str.replace(f'{question_label}___', '')
        # extract choices that contain 'active' (selected) value
        choices = question_df.columns[(question_df.values==active_value)[0]].to_list()
        return choices

    def generate_metadata_file_ephys(self, output):
        # extract selected modalities
        modalities = self._get_compressed_choices('modality')
        trialbeh = self._get_compressed_choices('subject_behaviour')
        posttrialbeh = self._get_compressed_choices('subject_behaviour_2')
        rewardfluidtype = self._get_compressed_choices('reward_fluid_type')

        if self.diglab_df['reward_fluid_type_other'].values[0]:
            rewardfluidtype += self.diglab_df['reward_fluid_type_other'].values

        rewardothertype = self._get_compressed_choices('reward_other')


        ephys_dict = {
            # "PowerLineFrequency": 50,
            # "PowerLineFrequencyUnit": "Hz",
            # "Manufacturer": "OpenEphys",
            # "ManufacturerModelName": "OpenEphys Starter Kit",
            # "ManufacturerModelVersion": "",
            # "SamplingFrequency": 30000,
            # "SamplingFrequencyUnit": "Hz",
            # "Location": "Institut de Neurosciences de la Timone, Faculté de Médecine, 27, "
            #             "Boulevard Jean Moulin, 13005 Marseille - France",
            # "Software": "Cerebus",
            # "SoftwareVersion": "1.5.1",
            "Creator": self.diglab_df['user'].values[0],
            # "Maintainer": "John Doe jr.",
            # "Procedure": {
            #     "Pharmaceuticals": {
            #         "isoflurane": {
            #             "PharmaceuticalName": "isoflurane",
            #             "PharmaceuticalDoseAmount": 50,
            #             "PharmaceuticalDoseUnit": "ug/kg/min",
            #         },
            #         "ketamine": {
            #             "PharmaceuticalName": "ketamine",
            #             "PharmaceuticalDoseAmount": 0.1,
            #             "PharmaceuticalDoseUnit": "ug/kg/min",
            #         },
            #     },
            # },
            "Comments": self.diglab_df['comments_exp'].values[0],
            "SessionNumber": self.diglab_df['ses_number'].values[0],
            "Subject": {
                "Weight": self.diglab_df['weight'].values[0],
                "WeightUnit": 'kg',
                "Comments": self.diglab_df['comments_subject'].values[0],
                "SubjectBehaviour": trialbeh,
                "PostTrialSubjectBehaviour": posttrialbeh,
            },
            "SpecialEvents": {},
            "Modalities": modalities,
            "Setup": {
                "Comments": self.diglab_df['comments_setup'].values[0]
            },
            "Rewards": {
                "FluidType": rewardfluidtype,
                "OtherType": rewardothertype,
            },
            "DigLab": {
                "record_id": self.diglab_df['record_id'].values[0],
                # TODO: Fix test dataset
                # "diglab_version": self.diglab_df['provenance_diglabtools_version'].values[0],
                # "redcap_form_version": self.diglab_df['redcap_form_version'].values[0],
            }
        }

        for id in range(3):
            if self.diglab_df[f'special_event_{id}'].values[0]:
                ephys_dict["SpecialEvents"][id] = {
                    "Comment": self.diglab_df[f'special_event_{id}'].values[0],
                    "Time": self.diglab_df[f'special_event_time_{id}'].values[0]
                }

        save_json(ephys_dict, output)

    def generate_metadata_file_scans(self, output):
        # extract data quality value
        quality = self._get_compressed_choices('data_quality')

        for key in self.data.keys():
            filename = f'ephys/sub-{self.sub_id}_ses-{self.ses_id}'
            if key:
                filename += key
            filename += '.nix'
            runs_df = pd.DataFrame([[
                filename,
                self.diglab_df['date'].values[0]],
                self.diglab_df['exp_name'].values[0],
                self.diglab_df['stimulation___yes'].values[0],
                self.diglab_df['subject_behaviour_multi___yes'].values[0],
                self.diglab_df['time_last_trial'].values[0],
                quality,
                self.diglab_df['incomplete_session___yes'].values[0],
                self.diglab_df['reward_fluid'].values[0],
                'ml',
                self.diglab_df['reward_fluid_additional'].values[0]
                ],
                columns=['filename', 'acq_date', 'exp_name', 'stimulation', 'post_trial_data',
                         'time_last_trial', 'data_quality', 'incomplete_session', 'fluid_reward',
                         'fluid_reward_unit', 'additional_fluid_reward'])
            save_tsv(runs_df, output)

    def validate(self):
        """
        Validate the generated structure using the BEP032 validator

        Parameters
        ----------
        output_folder: str
            path to the folder to validate

        Returns
        ----------
        bool
            True if validation was successful. False if it failed.
        """
        bep032tools.validator.BEP032Validator.is_valid(self.basedir)


def create_file(source, destination, mode):
    """
    Create a file at a destination location

    Parameters
    ----------
    source: str
        Source location of the file.
    destination: str
        Destination location of the file.
    mode: str
        File creation mode. Valid parameters are 'copy', 'link' and 'move'.

    Raises
    ----------
    ValueError
        In case of invalid creation mode.
    """
    if mode == 'copy':
        shutil.copy(source, destination)
    elif mode == 'link':
        os.link(source, destination)
    elif mode == 'move':
        shutil.move(source, destination)
    else:
        raise ValueError(f'Invalid file creation mode "{mode}"')


def extract_structure_from_csv(csv_file):
    """
    Load csv file that contains folder structure information and return it as pandas.datafram.

    Parameters
    ----------
    csv_file: str
        The file to be loaded.

    Returns
    -------
    pandas.dataframe
        A dataframe containing the essential columns for creating an BEP032 structure
    """
    if not HAVE_PANDAS:
        raise ImportError('Extraction of bep032 structure from csv requires pandas.')

    df = pd.read_csv(csv_file, dtype=str)

    # ensure all fields contain information
    if df.isnull().values.any():
        raise ValueError(f'Csv file contains empty cells.')

    # standardizing column labels
    # df = df.rename(columns=LABEL_MAPPING)

    # Check is the header contains all required names
    if not set(ESSENTIAL_CSV_COLUMNS).issubset(df.columns):
        raise ValueError(f'Csv file ({csv_file}) does not contain required information '
                         f'({ESSENTIAL_CSV_COLUMNS}). '
                         f'Accepted column names are specified in the BEP.')

    return df


def generate_struct(csv_file, pathToDir):
    """
    Create structure with csv file given in argument
    This file must contain a header row specifying the provided data. Accepted titles are
    defined in the BEP.
    Essential information of the following attributes needs to be present.
    Essential columns are 'sub_id' and 'ses_id'.

    Parameters
    ----------
    csv_file: str
        Csv file that contains a list of directories to create.
    pathToDir: str
        Path to directory where the directories will be created.
    """

    df = extract_structure_from_csv(csv_file)

    df = df[ESSENTIAL_CSV_COLUMNS]
    test_data_files = [Path('empty_ephys.nix')]
    for f in test_data_files:
        f.touch()

    for session_kwargs in df.to_dict('index').values():
        session = BEP032TemplateData(**session_kwargs)
        session.basedir = pathToDir
        session.generate_structure()
        session.register_data_files(*test_data_files)
        session.organize_data_files(mode='copy')
        session.generate_all_metadata_files()

    # cleanup
    for f in test_data_files:
        if f.exists():
            f.unlink()


def main():
    """

    Notes
    ----------

    Usage via command line: BEP032Generator.py [-h] pathToCsv pathToDir

    positional arguments:
        pathToCsv   Path to your csv file

        pathToDir   Path to your folder

    optional arguments:
        -h, --help  show this help message and exit
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('pathToCsv', help='Path to your csv file')
    parser.add_argument('pathToDir', help='Path to your folder')

    # Create two argument groups

    args = parser.parse_args()

    # Check if directory exists
    if not os.path.isdir(args.pathToDir):
        print('Directory does not exist:', args.pathToDir)
        exit(1)
    generate_struct(args.pathToCsv, args.pathToDir)


if __name__ == '__main__':
    main()
