import neurohearing.common.tools as tools
from neurohearing.preprocess.objects.neuro_audiometry_analyser import NeurohearingAnalyser

def main():
    config = tools.load_config()
    tonaldataname=config["tonaldataname"]
    tonal_suffix = tonaldataname.split("_")[-1]
    datapath = config["dataprocesseddirectory"] + tonaldataname+'.csv'
    mri_datapath = config["datarawdirectory"]+ config['mri_dataname'] + '.csv'


    neurohearing_analyser = NeurohearingAnalyser(datapath, 
                                                 mri_datapath,
                                                tonal_suffix, 
                                                columnnames={'patient_number_columnname': config["patient_number_columnname"],
                                                            'pesel_columnname': config["pesel_columnname"],
                                                            'audiometry_earside_columnname': config['audiometry_earside_columnname'],
                                                            'date_column': config['date_column'],
                                                            'type_column': config['audiometry_type_columnname'],
                                                            'description_column': config['description_columnname'],
                                                            'genetic_patient_id_column': config['patient_identifier_columnname']
                                                            },
                                                air_audiometry=config['air_audiometry'],
                                                bone_audiometry=config['bone_audiometry'],
                                                vibro_audiometry=config['vibro_audiometry'])
    

    neurohearing_analyser.patients_dfs()
    neurohearing_analyser.choose_first_examination()
    neurohearing_analyser.create_dataframe_for_merging(config["datacalculationsdirectory"])
    neurohearing_analyser.create_disinct_datasets(config['Datasets'], config["datacalculationsdirectory"])
    #neurohearing_analyser.save_processed_df(config["datacalculationsdirectory"])


if __name__=="__main__":

    main()