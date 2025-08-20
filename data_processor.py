import pandas as pd

class FileProcessor:
    def __init__(self, path, audiometry_types=['Audiometria_Tonalna', 'Audiometria_Slowna', 'Audiometria_Pole_Swobodne'], 
                 audiometry_map = {'Audiometria_Tonalna': 'tonal',
                                   'Audiometria_Slowna': 'verbal',
                                   'Audiometria_Pole_Swobodne': 'free_field'}):
        
        self.f = pd.ExcelFile(path, engine='openpyxl')
        self.audiometry_types = audiometry_types
        self.audiometry_map = audiometry_map
        self.audiometries = {}
        
    def read_audiometry(self):

        for sheet in self.f.sheet_names:
            for audiometry_type in self.audiometry_types:
                if sheet == audiometry_type:
                    try:
                        self.audiometries[self.audiometry_map[sheet]] = self.f.parse(sheet)
                        print(f'{self.audiometry_map[sheet]} audiometry reading completed')
                    except ValueError as e:
                        print(f"Nie udało się wczytać arkusza '{sheet}': {e}")

    def filter_audiometry(self):

        for key, df in self.audiometries.items():
            df = df[df["OPIS_BADANIA"].isnull()]
            df = df.drop(
                columns=["WYNIKI_POZOSTALE", "WYKONUJACY_BADANIE", "OPIS_BADANIA"]
            )
            self.audiometries[key] = df
            
    def read_patients(self):
        for sheet in self.f.sheet_names:
            if sheet == 'Pacjenci':
                self.df_patients = self.f.parse(sheet)
