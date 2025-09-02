import argparse
from neurohearing.preprocess.preprocessing_core import FileProcessor
import neurohearing.common.tools as tools


def main(args):

    config = tools.load_config()
    audiometry_datapath = config["datarawdirectory"] + config["dataname"] + '.xlsx'

    audiometry_types = tools.parse_list(args.audiometry_types) if args.audiometry_types else config["audiometry_types"]
    audiometry_map = tools.parse_map(args.audiometry_map) if args.audiometry_map else config["audiometry_map"]
    audiometry_dropcolumns = tools.parse_list(args.audiometry_dropcolumns) if args.audiometry_dropcolumns else config["audiometry_dropcolumns"]
    match_columns = tools.parse_list(args.match_columns) if args.match_columns else config["match_columns"]

    processor = FileProcessor(
        audiometry_datapath,
        audiometry_types=audiometry_types,
        audiometry_map=audiometry_map,
        audiometry_dropcolumns=audiometry_dropcolumns,
        match_columns = match_columns,
        output_path=config["datainterimdirectory"])
    
    processor.read_audiometry(config["pesel_columnname"])
    processor.read_patients(config["patients_sheetname"], config["pesel_columnname"])
    print("Reading completed")

    processor.filter_audiometry(config["description_column"])
    print("Filtering completed")
    print(processor.audiometries)

    processor.merge_audiometries(config["audiometry_type_columnname"], config["datainterimdirectory"])
    print("Merging completed")
    print(processor.audiometries)


if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Parser for audiometry data analyzer")
    parser.add_argument("--audiometry_types", help="Comma-separated list of audiometry sheet names")
    parser.add_argument("--audiometry_map", help="Comma-separated mapping 'SheetName=Key'")
    parser.add_argument("--audiometry_dropcolumns", help="Comma-separated list of columns to drop")
    parser.add_argument("--match_columns", help="Comma-separated list of key columns not to rename")
    args = parser.parse_args()
    main(args)