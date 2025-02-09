import streamlit as st
import pandas as pd
from datetime import datetime


def clean_group_data(df):



    df = pd.read_excel(df, header=[3], index_col=[0])

    unnamed_cols = [col for col in df.columns if 'Unnamed' in str(col)]
    if unnamed_cols:
        df = df.drop(columns=unnamed_cols, inplace=False)

    # Reset index and set up base DataFrame
    df.reset_index(inplace=True)



    df_group_data = df.iloc[58:]
    df_group_data.reset_index(inplace=True)
    df_group_data = df_group_data.iloc[1:-2]
    df_group_data.dropna(subset=df_group_data.columns[1:], how='all', inplace=True)

    df_group_data = df_group_data.T
    
    df_group_data = df_group_data.reset_index()

    df_group_data.columns = df_group_data.iloc[1]

    df_group_data = df_group_data[2:]
    df_group_data = df_group_data.drop_duplicates()

    df_group_data.columns.values[0] = 'DATE'



    df_group_data.columns = df_group_data.columns.str.strip()
    df_group_data['DATE'] = pd.to_datetime(df_group_data['DATE'], format='%m/%d/%Y')
    cleaned_groups = df_group_data

    return cleaned_groups
 