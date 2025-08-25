import argparse
from neurohearing.preprocess.preprocessing_core import FileProcessor
from functools import reduce
import neurohearing.common.tools as tools


def main(args):

    config = tools.load_config()
    audiometry_datapath = config["datarawdirectory"] + config["dataname"] + '.xlsx'

    audiometry_types = tools.parse_list(args.audiometry_types)
    audiometry_map = tools.parse_map(args.audiometry_map) if args.audiometry_map else None
    audiometry_dropcolumns = tools.parse_list(args.audiometry_dropcolumns)
    match_columns = tools.parse_list(args.match_columns)

    processor = FileProcessor(
        audiometry_datapath,
        audiometry_types=audiometry_types,
        audiometry_map=audiometry_map,
        audiometry_dropcolumns=audiometry_dropcolumns,
        match_columns=match_columns,
        output_path=config["datainterimdirectory"])
    
    processor.read_audiometry()
    processor.read_patients()
    print("Reading completed")

    processor.filter_audiometry()
    print("Filtering completed")
    print(processor.audiometries)

    processor.merge()
    print("Merging completed")
    print(processor.audiometries)


if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Parser for audiometry data analyzer")
    parser.add_argument(
        "--audiometry_types",
        nargs="?",
        default="Audiometria_Tonalna,Audiometria_Slowna,Audiometria_Pole_Swobodne",
        help="Comma-separated list of audiometry sheet names",
        type=str
    )
    parser.add_argument(
        "--audiometry_map",
        nargs="?",
        default="Audiometria_Tonalna=tonal,Audiometria_Slowna=verbal,Audiometria_Pole_Swobodne=free_field",
        help="Comma-separated mapping 'SheetName=Key'",
        type=str
    )
    parser.add_argument(
        "--audiometry_dropcolumns",
        nargs="?",
        default="WYNIKI_POZOSTALE,WYKONUJACY_BADANIE,OPIS_BADANIA,id",
        help="Comma-separated list of columns to drop",
        type=str
    )
    parser.add_argument(
        "--match_columns",
        nargs="?",
        default="PESEL,NUMER_W_JEDNOSTCE,NUMER_HISTORII_CHOROBY",
        help="Comma-separated list of key columns not to rename",
        type=str
    )
    args = parser.parse_args()
    main(args)