from datetime import datetime
from data.supplemental_english import GOVERNMENT_CODES, REGION_CODES
import pandas as pd


def get_government_series():
    gov_series = set()
    special_gov_series = {}
    for key in GOVERNMENT_CODES:
        gov_series.add((key[0], key[2]))
        if key[1] != (0, 999):
            if ((key[0], key[2])) not in special_gov_series:
                special_gov_series[(key[0], key[2])] = []
            special_gov_series[(key[0], key[2])].append(key[1])
    return gov_series, special_gov_series

def get_region(region_code):
    for region in REGION_CODES:
        for code in REGION_CODES[region]:
            if code == region_code:
                return region
    return "NAN"

def get_plate_info(plate):
    series1 = plate[0]
    serial_number = plate[1:4]
    series2 = plate[4:6]
    region_code = plate[6:]
    
    '''
    We want to get:
    + region
    + series number
    + is it government plate or not
    + is it forbidden to buy
    + does it have advantage
    + category
    '''
    gov_series, special_gov_series = get_government_series()
    series = series1 + series2
    info = {} 
    if (series, region_code) not in gov_series:
        info["government_plate"] = 0
        info["serial_number"] = serial_number
        info["forbidden_to_buy"] = 0
        info["have_advantage"] = 0 
        info["significance_level"] = 0
        info["region"] = get_region(region_code)
        info["category"] = "Normal plate"
    else:
        series_range = (0, 999)
        if (series, region_code) in special_gov_series:
            for r in special_gov_series[(series, region_code)]:
                if int(r[0]) <= int(serial_number) <= int(r[1]):
                    series_range = r
                    break
        if (series, series_range, region_code) not in GOVERNMENT_CODES:
            info["government_plate"] = 0
            info["forbidden_to_buy"] = 0
            info["have_advantage"] = 0
            info["significance_level"] = 0
            info["category"] = "Normal plate"
        else:
            info["government_plate"] = 1 
            info["forbidden_to_buy"] = GOVERNMENT_CODES[(series, series_range, region_code)][1]
            info["have_advantage"] = GOVERNMENT_CODES[(series, series_range, region_code)][2]
            info["significance_level"] = GOVERNMENT_CODES[(series, series_range, region_code)][3]
            info["category"] = GOVERNMENT_CODES[(series, series_range, region_code)][0]
        info["serial_number"] = serial_number
        info["region"] = get_region(region_code)
        
    return info

def get_datetime(timestamp):
    # Get the year, month, date, before midday and after midday:
    # eg. 2024-12-26 00:00:00
    info = {}
    dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
    info["year"] = dt.year
    info["month"] = dt.month
    info["day"] = dt.day
    info["before_midday"] = 1 if dt.hour < 12 else 0
    return info

def create_new_features(df):
    df = df.join(df['plate'].apply(get_plate_info).apply(pd.Series))
    df = df.join(df['date'].apply(get_datetime).apply(pd.Series))
    return df

