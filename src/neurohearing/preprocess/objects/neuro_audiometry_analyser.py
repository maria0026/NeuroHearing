import pandas as pd
import os
from neurohearing.preprocess.objects.tonal_audiometry import TonalAudiometry

class NeurohearingAnalyser(TonalAudiometry):
        def __init__(self, path, 
                  tonal_suffix,
                  columnnames,
                  air_audiometry=["AirMask", "Air"],
                  bone_audiometry=["BoneMask", "Bone"],
                  vibro_audiometry=['VibroMask', 'Vibro']):
            super().__init__(path, tonal_suffix, columnnames, air_audiometry, bone_audiometry, vibro_audiometry)

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
            new_df = merged_df.loc[:, [self.pesel_column, self.date_column, 'IF_FIRST', 'L_BIAP', 'R_BIAP', 'L_HEARING_TYPE', 'P_HEARING_TYPE']]
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            new_df.to_csv(f'{output_path}audiometry_{self.tonal_suffix}_summarized.csv', index=False)
            print(f'Saving to {output_path}audiometry_{self.tonal_suffix}_summarized.csv completed.')