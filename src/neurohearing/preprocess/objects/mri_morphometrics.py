import neurohearing.common.tools as tools
import pandas as pd


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


    def filter_age(self, age_label_name):
        self.data_mri = self.data_mri[(self.data_mri[age_label_name] >= 0) & (self.data_mri[age_label_name] <= 100)].copy()


    def filter_zeros(self, filtering_threshold):
        zero_ratio = (self.data_mri == 0).sum() / len(self.data_mri)
        nan_ratio = self.data_mri.isna().sum() / len(self.data_mri)
        cols_to_keep = zero_ratio[(zero_ratio < filtering_threshold) & (nan_ratio < filtering_threshold)].index
        print(f"Kept {len(cols_to_keep)} columns out of {len(self.data_mri.columns)} after filtering zeros and NaNs")
        self.data_mri = self.data_mri[cols_to_keep].copy()


    def calculate_mean_in_ranges(self, age_label='age', age_ranges=[(0,5), (5,10), (10, 18), (18,65), (65,100)], exclude_cols=['hight', 'weight'] ):    
        self.data_mri = self.data_mri.drop(columns=["Unnamed: 0"] + exclude_cols)
        numeric_cols = self.data_mri.select_dtypes(include='number').columns

        self.data_mri['age_group'] = pd.cut(
            self.data_mri[age_label],
            bins=[r[0] for r in age_ranges] + [age_ranges[-1][1]],
            labels=[str(r) for r in age_ranges],
            include_lowest=True
        )

        grouped = self.data_mri.groupby('age_group')[numeric_cols].agg(['mean', 'std'])
        grouped.columns = [f"{col}_{stat}" for col, stat in grouped.columns]
        self.mean_std_age_ranges = grouped

        print(self.mean_std_age_ranges)


    def filter_outliers(self, age_label='age', n_std=6):
        if not hasattr(self, "mean_std_age_ranges"):
            raise ValueError("Run calculate_mean_in_ranges() before filter_outliers()")

        self.data_mri_original = self.data_mri.copy()
        numeric_cols = self.data_mri.select_dtypes(include='number').columns

        mask_total = pd.Series(True, index=self.data_mri.index)
        outliers_list = []

        for col in numeric_cols:
            if col != age_label:
                for age_group, group_df in self.data_mri.groupby('age_group', observed=True):
                    mean = self.mean_std_age_ranges.loc[age_group, f'{col}_mean']
                    std  = self.mean_std_age_ranges.loc[age_group, f'{col}_std']
                    difference = (group_df[col] - mean) / std
                    mask = (difference >= - n_std) & (difference <= n_std)

                    mask_total.loc[group_df.index] &= mask

                    outliers = group_df.loc[~mask, ['identifier', col]].copy()
                    outliers['difference_in_std'] = difference[~mask]
                    outliers['column'] = col
                    outliers_list.append(outliers)

        self.data_mri = self.data_mri[mask_total].copy()
        print("Outliers filtered using ±6σ rule.")

        return outliers_list

       
    def save_outliers(self, outliers_list, removed_ids_output_path="removed_identifiers.csv"):
        removed_df = pd.concat(outliers_list, ignore_index=True)
        removed_df = removed_df.dropna(subset=['difference_in_std'])
        removed_df = removed_df.loc[removed_df.groupby('identifier')['difference_in_std'].idxmax()]
        print(f"Removed identifiers: {len(removed_df)} before: {self.data_mri_original.shape} after: {self.data_mri.shape}")

        removed_df = removed_df[['identifier', 'column', 'difference_in_std']]
        removed_df = removed_df.sort_values(
            by='difference_in_std', 
            key=lambda x: x.abs(), 
            ascending=False
        )

        removed_df.to_csv(removed_ids_output_path, index=False)
        print(f"Removed identifiers saved to {removed_ids_output_path}")


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
        train_mri = self.data_mri[~self.data_mri[self.pesel_columnname].isin(self.data_mri_audiometry_tonal_filtered[self.pesel_columnname])].copy()
        #train_mri.drop(columns = self.pesel_columnname, inplace=True)   
        train_mri.to_csv(output_datapath_mri)
        #self.data_mri_audiometry_tonal_filtered.drop(columns = self.pesel_columnname, inplace=True)   
        self.data_mri_audiometry_tonal_filtered.to_csv(output_path_merged)


