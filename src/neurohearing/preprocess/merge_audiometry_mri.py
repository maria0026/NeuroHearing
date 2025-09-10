import pandas as pd
import neurohearing.common.tools as tools
from neurohearing.preprocess.mri_morphometrics import MRI_morphometics
import argparse

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
                        help="Comma-separated list of audiometry sheet names")
    args = parser.parse_args()
    main(args)