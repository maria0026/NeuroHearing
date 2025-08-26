import pandas as pd

class TonalAudiometry():
    def __init__(self, path, mask_merging_columns=["PESEL", "UWAGI_DO_AUDIOMETRII_t"],
                 date_column="DATA_BADANIA_t",
                 audiometry_type={"TYP_AUDIOMETRII_t": [["Bone", "BoneMask"], ["Air", "AirMask"]]}):
        
        self.data = pd.read_csv(path, sep=None, engine='python', dtype={"PESEL": str})
        self.mask_merging_columns = mask_merging_columns
        self.date_column = date_column
        self.audiometry_type = audiometry_type

    def merge_mask(self):

        self.data[self.date_column] = pd.to_datetime(self.data[self.date_column])
        self.data['date_year_month_day'] = (
            self.data[self.date_column].dt.year.astype(str) + "-" +
            self.data[self.date_column].dt.month.astype(str) + "-" +
            self.data[self.date_column].dt.day.astype(str)
        )

        group_columns = self.mask_merging_columns + ['date_year_month_day']
        type_col = list(self.audiometry_type.keys())[0]

        pairs = [p for sublist in self.audiometry_type[type_col] for p in [sublist]]

        #mini_df for each patient and each ear
        mini_dfs = []
        for _, group in self.data.groupby(group_columns):
            mini_dfs.append(group.reset_index(drop=True))

        for mini_df in mini_dfs:

            types = set(mini_df[type_col])
            for pair in pairs:
                if set(pair) <= types:
                    row_first = mini_df[mini_df[type_col] == pair[0]].iloc[0]
                    row_second = mini_df[mini_df[type_col] == pair[1]].iloc[0]
                    merged_row = row_first.combine_first(row_second)

                    #update values with merged from masking and not masking
                    idx_first = mini_df[mini_df[type_col] == pair[0]].index[0]
                    mini_df.loc[idx_first] = merged_row
                    #delete second row
                    mini_df = mini_df[mini_df[type_col] != pair[1]]

            #filter vibro
            mini_df = mini_df[~mini_df[type_col].str.contains("Vibro", na=False)]
            mini_df = mini_df[~mini_df[type_col].str.contains("szumy", na=False)]
            #cols = mini_df.filter(like='WYNIK').columns
            #print(mini_df[list(cols) + ['UWAGI_DO_AUDIOMETRII_t', 'TYP_AUDIOMETRII_t']])



