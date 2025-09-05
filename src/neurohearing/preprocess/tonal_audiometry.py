import pandas as pd
import os

class TonalAudiometry():
    def __init__(self, 
                  path, 
                  tonal_suffix,
                  match_columnnames, 
                  columnnames,
                  air_audiometry=["AirMask", "Air"],
                  bone_audiometry=["BoneMask", "Bone"]):
        
        for key, value in columnnames.items():
            if value not in match_columnnames:
                columnnames[key] = value + '_' + tonal_suffix

        self.pesel_columnname = columnnames['pesel_columnname']
        self.data = pd.read_csv(path, sep=None, engine='python', dtype={self.pesel_columnname: str})

        self.earside_col = columnnames['audiometry_earside_columnname']
        self.date_column = columnnames['date_column']
        self.type_col = columnnames['type_column']

        self.tonal_suffix = tonal_suffix
        self.air_audiometry = air_audiometry
        self.bone_audiometry = bone_audiometry

    def patients_dfs(self):
        self.data[self.date_column] = pd.to_datetime(self.data[self.date_column])
        self.data['date_year_month_day'] = (
            self.data[self.date_column].dt.year.astype(str) + "-" +
            self.data[self.date_column].dt.month.astype(str) + "-" +
            self.data[self.date_column].dt.day.astype(str)
        )

        self.group_columns = [self.pesel_columnname, self.earside_col] + ['date_year_month_day']

        #mini_df for each patient and each ear
        self.mini_dfs = []
        for _, group in self.data.groupby(self.group_columns):
            self.mini_dfs.append(group.reset_index(drop=True))

        print(f'Created {len(self.mini_dfs)} dataframes for each patient and each ear.')


    def merge_mask(self):
        pairs = self.air_audiometry + self.bone_audiometry

        for i, mini_df in enumerate(self.mini_dfs):

            types = set(mini_df[self.type_col])
            for pair in pairs:
                if set(pair) <= types:
                    row_first = mini_df[mini_df[self.type_col] == pair[0]].iloc[0]
                    row_second = mini_df[mini_df[self.type_col] == pair[1]].iloc[0]
                    merged_row = row_first.combine_first(row_second)

                    #update values with merged from masking and not masking
                    idx_first = mini_df[mini_df[self.type_col] == pair[0]].index[0]
                    mini_df.loc[idx_first] = merged_row
                    #delete second row
                    mini_df = mini_df[mini_df[self.type_col] != pair[1]]

            #filter vibro
            mini_df = mini_df[~mini_df[self.type_col].str.contains("Vibro", na=False)]
            mini_df = mini_df[~mini_df[self.type_col].str.contains("szumy", na=False)]

            self.mini_dfs[i] = mini_df
            #cols = mini_df.filter(like='WYNIK').columns
            #print(mini_df[list(cols) + ['UWAGI_DO_AUDIOMETRII_tonal', 'TYP_AUDIOMETRII_tonal']])

        print(f'Merging rows completed.')


    def calculate_pta(self, PTA2_columns, PTA4_columns, hf_columns):

        PTA2_columns = [col + "_" + self.tonal_suffix for col in PTA2_columns]
        PTA4_columns = [col + "_" + self.tonal_suffix for col in PTA4_columns]
        hf_columns = [col + "_" + self.tonal_suffix for col in hf_columns]

        for i, mini_df in enumerate(self.mini_dfs):
            mini_df['PTA2'] = mini_df[PTA2_columns].mean(axis=1)
            #mini_df['PTA4'] = mini_df[PTA4_columns].mean(axis=1)
            mini_df['hfPTA'] = mini_df[hf_columns].mean(axis=1)
            self.mini_dfs[i] = mini_df
        
        print('PTA calculation completed.')
    

    def save_processed_df(self, output_path):
        merged_df = pd.concat(self.mini_dfs, ignore_index=True)
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        merged_df.to_csv(f'{output_path}audiometry_{self.tonal_suffix}.csv', index=False)
        print(f'Saving to {output_path}audiometry_{self.tonal_suffix}.csv completed.')


    def select_better_air_pta(self):

        #column names for grouping
        two_ear_group_columns = self.group_columns.copy()
        two_ear_group_columns.remove(self.earside_col)

        merged_df = pd.concat(self.mini_dfs, ignore_index=True)
        rows = []
        
        for _, group in merged_df.groupby(two_ear_group_columns):
            air = group[group[self.type_col].isin(self.air_audiometry)].copy()
            air['ear_side'] = air[self.earside_col].str.extract(r"(lewego|prawego)")
            air['ear_side'] = air['ear_side'].map({"lewego": "L", "prawego": "P"})

            row_min_pta2 = air.nsmallest(1, 'PTA2')
            if not row_min_pta2.empty:
                row_min_pta2 = row_min_pta2.iloc[0]
            else:
                row_min_pta2 = None 

            row_min_hfPTA = air.nsmallest(1, 'hfPTA')
            if not row_min_hfPTA.empty:
                row_min_hfPTA = row_min_hfPTA.iloc[0]
            else:
                row_min_hfPTA = None

            rows.append({
                self.pesel_columnname: str(group[self.pesel_columnname].values[0]),
                'PTA2': row_min_pta2['PTA2'] if row_min_pta2 is not None else None,
                'earside_PTA2': row_min_pta2['ear_side'] if row_min_pta2 is not None else None,
                'hfPTA': row_min_hfPTA['hfPTA'] if row_min_hfPTA is not None else None,
                'earside_hfPTA': row_min_hfPTA['ear_side'] if row_min_hfPTA is not None else None,
                self.date_column: group['date_year_month_day'].values[0]
            })
        self.final_mri_df = pd.DataFrame(rows)
        #print(final_df)

    def save_processed_to_mri_df(self, output_path):
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        self.final_mri_df.to_csv(f'{output_path}audiometry_{self.tonal_suffix}_mri.csv', index=False)
        print(f'Saving to {output_path}audiometry_{self.tonal_suffix}_mri.csv completed.')

