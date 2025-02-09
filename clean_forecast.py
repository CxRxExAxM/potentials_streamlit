import streamlit as st
import pandas as pd
from datetime import datetime



def pivot_and_clean(df, keep_rows):

    date_format = '%m/%d/%Y'
    cleaned_df = df.iloc[keep_rows].T.reset_index()
    cleaned_df.columns = cleaned_df.iloc[0]
    cleaned_df = cleaned_df[1:]
    cleaned_df.columns.values[0] = 'DATE'
    cleaned_df.columns = cleaned_df.columns.str.strip()
    cleaned_df['DATE'] = pd.to_datetime(cleaned_df['DATE'], errors='coerce')
    cleaned_df['DATE'] = cleaned_df['DATE'].dt.strftime(date_format)
    return cleaned_df


def clean_forecast_data(df):

    # Split forecast data sections
    df_hotel_data = df.loc[:22]
    df_privado_data = df.loc[23:39]
    df_fg_data = df.loc[40:56]

    # Rows to keep for each forecast section
    keep_hotel_rows = [4, 5, 12, 11, 14, 15, 16, 17]
    keep_privado_rows = [3, 4, 11]
    keep_fg_rows = [3, 4, 11]

    # Clean and pivot each section
    hotel_t = pivot_and_clean(df_hotel_data, keep_hotel_rows)
    hotel_v = pivot_and_clean(df_privado_data, keep_privado_rows)
    hotel_fg = pivot_and_clean(df_fg_data, keep_fg_rows)

    # Merge all forecast sections on DATE
    cleaned_forecast = pd.merge(hotel_t, hotel_v, on='DATE', how='outer', suffixes=('', '_priv'))
    cleaned_forecast = pd.merge(cleaned_forecast, hotel_fg, on='DATE', how='outer', suffixes=('', '_fg'))

    return cleaned_forecast
 
