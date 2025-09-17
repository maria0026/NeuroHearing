import neurohearing.common.tools as tools
from neurohearing.preprocess.objects.mri_morphometrics import MRI_morphometics
import pandas as pd
import argparse
import os

def main(args):
    config = tools.load_config()
    tonaldataname = config["tonaldataname"]
    tonal_suffix = tonaldataname.split("_")[-1]
    mri_suffix = "mri"

    processed_tonal_audiometry_datapath = config["dataprocesseddirectory"] + tonaldataname + '_' + mri_suffix +'.csv'
    data_audiometry = pd.read_csv(processed_tonal_audiometry_datapath, sep=None, engine='python', dtype={config["pesel_columnname"]: str})

    mri_mrophometric_datapath = config["datarawdirectory"] + config["mri_dataname"] + '.csv'
    mri_morpohometrics = MRI_morphometics(mri_mrophometric_datapath,
                                          mri_suffix,
                                          config)
    
    mapping_datapath = config["datarawdirectory"] + config["mapping"] + '.csv'
    mri_morpohometrics.map_pesel(mapping_datapath)
    mri_morpohometrics.filter_age(args.label_name)
    mri_morpohometrics.filter_zeros(args.zeros_filtering_threshold)
    
    removed_ids_output_path = config["resultsdirectory"] + args.mri_removed_identifiers + '.csv'
    if not os.path.exists(config["resultsdirectory"]):
        os.makedirs(config["resultsdirectory"])

    mri_morpohometrics.filter_outliers(n_std=6, removed_ids_output_path=removed_ids_output_path)

    mri_morpohometrics.merge_with_audiometry(data_audiometry)
    mri_morpohometrics.choose_closest_examinations(tonal_suffix)

    output_path_merged = config["dataprocesseddirectory"] + args.mri_audiometry_merged_filename +'.csv'
    output_path_mri = config["dataprocesseddirectory"] +  config["mri_dataname"] + '.csv'

    mri_morpohometrics.save_datasets(output_path_merged, output_path_mri)


if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Parser for audiometry data analyzer")
    parser.add_argument("--mri_audiometry_merged_filename", 
                        nargs="?", 
                        default="audiometry_tonal_mri_merged",
                        help="Filename for audiometry mri merged")
    parser.add_argument("--label_name",
                        nargs="?",
                        default="age",
                        help="Predicted parameters, list", 
                        type=str)
    parser.add_argument("--zeros_filtering_threshold",
                        nargs="?",
                        default=0.2,
                        help="If column has zeros number larger than this threshold it will be deleted")
    parser.add_argument("--mri_removed_identifiers", 
                        nargs="?", 
                        default="removed_identifiers",
                        help="Filename for audiometry mri merged")
    args = parser.parse_args()
    main(args)