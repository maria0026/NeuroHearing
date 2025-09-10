import pandas as pd
import neurohearing.common.tools as tools

class MRI_morphometics():
    def __init__(self,   
                path, 
                mri_suffix,
                config):
        
        self.pesel_columnname = config['pesel_columnname']
        self.date_column = config["date_column"]
        self.config = config
        self.mri_suffix = mri_suffix
        data_mri = pd.read_csv(path, sep=None, engine='python', dtype={self.pesel_columnname: str})
        self.data_mri = data_mri.rename(columns={"DataBadania": config['date_column'] + '_' + mri_suffix})
        

    def map_pesel(self, mapping_datapath):
        mapping = pd.read_csv(mapping_datapath, sep=None, engine='python', dtype={self.pesel_columnname: str})
        self.data_mri = pd.merge(self.data_mri, mapping, on="identifier")


    def merge_with_audiometry(self, data_audiometry):
        self.data_mri_audiometry_tonal = pd.merge(self.data_mri, data_audiometry, on=self.pesel_columnname)


    def choose_closest_examinations(self, tonal_suffix):
        data_mri_audiometry_tonal = tools.convert_to_datetime(self.data_mri_audiometry_tonal, self.date_column, self.mri_suffix)
        data_mri_audiometry_tonal = tools.convert_to_datetime(data_mri_audiometry_tonal, self.date_column, tonal_suffix)
        data_mri_audiometry_tonal[f'{self.mri_suffix}_{tonal_suffix}_date_diff'] = (data_mri_audiometry_tonal[f'{self.date_column}_{self.mri_suffix}'] -
                                                                                data_mri_audiometry_tonal[f'{self.date_column}_{tonal_suffix}']).abs()
        data_mri_audiometry_tonal_sorted = data_mri_audiometry_tonal.sort_values([self.pesel_columnname, f'{self.mri_suffix}_{tonal_suffix}_date_diff'])
        self.data_mri_audiometry_tonal_filtered = data_mri_audiometry_tonal_sorted.groupby(self.pesel_columnname).first().reset_index()

    def save_datasets(self, output_path_merged, output_datapath_mri):    
        self.data_mri_audiometry_tonal_filtered.to_csv(output_path_merged)
        train_mri = self.data_mri[~self.data_mri[self.pesel_columnname].isin(self.data_mri_audiometry_tonal_filtered[self.pesel_columnname])]
        train_mri.to_csv(output_datapath_mri)
