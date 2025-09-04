import argparse
from neurohearing.preprocess.tonal_audiometry import TonalAudiometry
import neurohearing.common.tools as tools

def main():

    config = tools.load_config()
    tonaldataname=config["tonaldataname"]
    tonal_suffix = tonaldataname.split("_")[-1]
    tonal_audiometry_datapath = config["datainterimdirectory"] + tonaldataname + '.csv'

    tonal_audiometry_processor = TonalAudiometry(tonal_audiometry_datapath, 
                                                 tonal_suffix, 
                                                 match_columnnames=config['match_columns'],
                                                 columnnames={'pesel_columnname': config["pesel_columnname"],
                                                                'audiometry_earside_columnname': config['audiometry_earside_columnname'],
                                                                'date_column': config['date_column'],
                                                                'type_column': config['audiometry_type_columnname']
                                                               },
                                                 audiometry_pairs=[["BoneMask", "Bone"], ["AirMask", "Air"]]
                                                 )
    tonal_audiometry_processor.patients_dfs()
    tonal_audiometry_processor.merge_mask()

    PTA2_columns = config["pta_columns"]["PTA2"]
    PTA4_columns = config["pta_columns"]["PTA4"]
    hfPTA_columns = config["pta_columns"]["hfPTA"]
    
    tonal_audiometry_processor.calculate_pta(PTA2_columns, PTA4_columns, hfPTA_columns)
    tonal_audiometry_processor.save_processed_df(config["dataprocesseddirectory"])

if __name__=="__main__":
    main()