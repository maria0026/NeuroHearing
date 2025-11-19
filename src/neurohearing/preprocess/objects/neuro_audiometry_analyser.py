import pandas as pd
import os
from neurohearing.preprocess.objects.tonal_audiometry import TonalAudiometry

class NeurohearingAnalyser(TonalAudiometry):
        def __init__(self, path,
                      mri_path,
                  tonal_suffix,
                  columnnames,
                  air_audiometry=["AirMask", "Air"],
                  bone_audiometry=["BoneMask", "Bone"],
                  vibro_audiometry=['VibroMask', 'Vibro']):
            super().__init__(path, tonal_suffix, columnnames, air_audiometry, bone_audiometry, vibro_audiometry)
            self.data_mri = pd.read_csv(mri_path, sep=None, engine='python', dtype={self.pesel_column: str})


        def choose_first_examination(self):
            id = 0
            for i, mini_df in enumerate(self.mini_dfs):
                id_new = mini_df[self.patient_number_columnname].values[0]
                #print(id, id_new)
                if id_new == id:
                    self.mini_dfs[i]['IF_FIRST'] = 0
                else:
                    self.mini_dfs[i]['IF_FIRST'] = 1
                id = id_new


        def create_dataframe_for_merging(self, output_path):
            for i, mini_df in enumerate(self.mini_dfs):
                ears_grouped = {g: d for g, d in mini_df.groupby("EAR_SIDE")}
                for ear in self.ears:
                    if ear not in ears_grouped:
                        continue

                    group = ears_grouped[ear]
                    biap_values = group['BIAP'].dropna()
                    if biap_values.empty:
                        self.mini_dfs[i][f'{ear}_BIAP'] = None
                    else:
                        self.mini_dfs[i][f'{ear}_BIAP'] = biap_values.iloc[0]

                    hearing_type_vals = group['HEARING_TYPE'].dropna()

                    if hearing_type_vals.empty:
                        self.mini_dfs[i][f'{ear}_HEARING_TYPE'] = None
                    else:
                        self.mini_dfs[i][f'{ear}_HEARING_TYPE'] = hearing_type_vals.iloc[0]

                    
                indeks = mini_df.index[0]
                self.mini_dfs[i] = mini_df.iloc[[indeks]]

            merged_df = pd.concat(self.mini_dfs, ignore_index=True)
            merged_df[self.date_column] = merged_df[self.date_column].dt.strftime("%d.%m.%Y %H:%M")
            self.new_df = merged_df.loc[:, [self.pesel_column, self.date_column, 'IF_FIRST', 'L_BIAP', 'P_BIAP', 'L_HEARING_TYPE', 'P_HEARING_TYPE']]
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            self.new_df.to_csv(f'{output_path}audiometry_{self.tonal_suffix}_summarized.csv', index=False)
            print(f'Saving to {output_path}audiometry_{self.tonal_suffix}_summarized.csv completed.')


        def create_disinct_datasets(self, hearing_loss_dict, output_path):
            for loss_type, rules in hearing_loss_dict.items():
    
                df_filtered = self.new_df[(self.new_df['L_BIAP']==rules[0]) & (self.new_df['P_BIAP']==rules[1])]
                df_filtered[self.pesel_column] = df_filtered[self.pesel_column].astype(str)
                self.data_mri[self.pesel_column] = self.data_mri[self.pesel_column].astype(str)

                mri_audiometry = pd.merge(self.data_mri, df_filtered, on=self.pesel_column)
                mri_audiometry.to_csv(f'{output_path}mri_audiometry_{loss_type}.csv', index=False)
                print(f'Saving to {output_path}audiometry_mri.csv completed.')
