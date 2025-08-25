import pandas as pd

class TonalAudiometry():
    def __init__(self, path, mask_merging_columns=["PESEL", "UWAGI_DO_AUDIOMETRII_t"],
                 date_column="DATA_BADANIA_t",
                 audiometry_type={"TYP_AUDIOMETRII_t": [["BoneMask", "Bone"], ["AirMask", "Air"]]}):
        
        self.data = pd.read_csv(path, sep=None, engine='python')
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

        mini_dfs = []
        for _, group in self.data.groupby(group_columns):
            mini_dfs.append(group.reset_index(drop=True))

        for mini_df in mini_dfs:
            types = set(mini_df[type_col])
            for pair in pairs:
                if set(pair) <= types:
                    merged_row = mini_df.drop(columns=[type_col]) \
                    .agg(lambda x: x.iloc[0] if x.nunique() == 1 else list(x))
                    print(merged_row.columns)
                    #print(merged_row[['UWAGI_DO_AUDIOMETRII_t', 'TYP_AUDIOMETRII_t']])
                #merged_mini_dfs.append(merged_row.to_frame().T)
                #merged = True
                #break
                



