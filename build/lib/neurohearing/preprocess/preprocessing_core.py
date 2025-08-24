import pandas as pd
import os

class FileProcessor:
    def __init__(self, path, audiometry_types=['Audiometria_Tonalna', 'Audiometria_Slowna', 'Audiometria_Pole_Swobodne'], 
                audiometry_map = {'Audiometria_Tonalna': 'tonal',
                                   'Audiometria_Slowna': 'verbal',
                                   'Audiometria_Pole_Swobodne': 'free_field'},
                audiometry_dropcolumns = ["WYNIKI_POZOSTALE", "WYKONUJACY_BADANIE", "OPIS_BADANIA", "id"],
                match_columns = ["PESEL", "NUMER_W_JEDNOSTCE", "NUMER_HISTORII_CHOROBY"],
                output_path="data/interim"):
        
        self.f = pd.ExcelFile(path, engine='openpyxl')
        self.audiometry_types = audiometry_types
        self.audiometry_map = audiometry_map
        self.audiometry_dropcolumns = audiometry_dropcolumns
        self.match_columns = match_columns
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        self.output_path = output_path
        
        self.audiometries = {}

        
    def read_audiometry(self):
        exclude_cols = self.match_columns + self.audiometry_dropcolumns
        for sheet in self.f.sheet_names:
            for audiometry_type in self.audiometry_types:
                if sheet == audiometry_type:
                    try:
                        df = self.f.parse(sheet, dtype={"PESEL": str})
                        #give different names for all columns except the matching ones and columns to drop
                        df = df.rename(columns={col: f"{col}_{self.audiometry_map[sheet][0]}" for col in df.columns if col not in exclude_cols})
                        self.audiometries[self.audiometry_map[sheet]] = df
                        print(f'{self.audiometry_map[sheet]} audiometry reading completed')
                    except ValueError as e:
                        print(f"Nie udało się wczytać arkusza '{sheet}': {e}")


    def read_patients(self):
        for sheet in self.f.sheet_names:
            if sheet == 'Pacjenci':
                self.df_patients = self.f.parse(sheet, dtype={"PESEL": str})


    def filter_audiometry(self):
        for key, df in self.audiometries.items():
            df = df[df["OPIS_BADANIA"].isnull()]
            df = df.drop(
                columns=self.audiometry_dropcolumns
            )
            self.audiometries[key] = df
            
    def merge(self):
        
        for key, df in self.audiometries.items():
            df_merged = pd.merge(
            self.df_patients,
            df,
            on=self.match_columns,
            how="left"
            )
            df_merged = df_merged[~df_merged[f'NAZWA_AUDIOMETRII_{key[0]}'].isnull()]
            self.audiometries[key] = df_merged
            df_merged.to_csv(f'{self.output_path}/audiometry_{key}.csv')
