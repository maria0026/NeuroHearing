from neurohearing.preprocess.tonal_audiometry import TonalAudiometry
import neurohearing.common.tools as tools

def main():

    config = tools.load_config()
    tonal_audiometry_datapath = config["datainterimdirectory"] + config["tonaldataname"] + '.csv'

    tonal_audiometry_processor = TonalAudiometry(tonal_audiometry_datapath)
    tonal_audiometry_processor.merge_mask()

if __name__=="__main__":
    main()