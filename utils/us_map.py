import pandas as pd
import geopandas as gpd

def transform_geometries(df, x, y, scale, rotate):
    """
    Transform geometries in dataframe
    """
    df.loc[:, "geometry"] = df.geometry.translate(yoff=y, xoff=x)
    center = df.dissolve().centroid.iloc[0]
    df.loc[:, "geometry"] = df.geometry.scale(xfact=scale, yfact=scale, origin=center)
    df.loc[:, "geometry"] = df.geometry.rotate(rotate, origin=center)
    return df

def adjust_maps(df):
    """
    Move Alaska and Hawaii to bottom of continental US
    """
    df_main_land = df[~df.STATEFP.isin(["02", "15"])]
    df_alaska = df[df.STATEFP == "02"]
    df_hawaii = df[df.STATEFP == "15"]

    df_alaska = transform_geometries(df_alaska, 1300000, -4900000, 0.5, 32)
    df_hawaii = transform_geometries(df_hawaii, 5400000, -1500000, 1, 24)

    return pd.concat([df_main_land, df_alaska, df_hawaii])

def main(path: str="data/cb_2018_us_state_500k"):
    """
    Return dataframe of adjusted US map 
    """
    states = gpd.read_file(path)

    # Remove Puerto Rico, American Samoa, United States Virgin Islands, Guam, Commonwealth of the Northern Mariana Islands
    states = states[~states.STATEFP.isin(["72", "69", "60", "66", "78"])]
    # Center map on the continental US
    states = states.to_crs("ESRI:102003")

    # Move Alaska and Hawaii into place
    states = adjust_maps(states)
    return states

