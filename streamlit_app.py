import streamlit as st
import pandas as pd
import logging
import io


st.title("Generate Potentials Information")
st.write('Upload hitlist, and 21day .xlsx files')

if 'clean_dfs' not in st.session_state:
    st.session_state.clean_dfs = {}

hitlist_file = st.file_uploader('Hitlist:', type='.xlsx')
if hitlist_file is not None:
    hitlist_df = pd.read_excel(hitlist_file)


drop_list = ['COL1', 'EVENT_DAY', 'BOOKING_NAME', 'Distro?', 'BOOK_ID', 'CONTACT_FULL_NAME',
             'BOOKING_STATUS', 'PHONE_NO', 'CF_CONTACT_NAME', 'CF_ACCT_AGENT_NAME',
             'CF_PHONE_NO', 'CAT_OWNER_CODE', 'EVENT_LINK_ID', 'SETUP_SETDOWN_TIME',
             'SC_TRANSLATION_GEMTRANSLATION_', 'DATE_SORT_COLUMN', 'GTD', 'ACT', 'RESORT', 'Column1']

EVENT_TYPE_KEEP = ['BKFB', 'LNCB', 'OTHR', 'BKFT', 'RECM', 'REBE', 'DINB', 'RECH', 'DINR', 'RECE']
BREAKFAST_EVENTS = ['BKFB', 'BKFT']
LUNCH_EVENTS = ['LNCB']
DINNER_EVENTS = ['DINB', 'DINR', 'OTHR', 'RECM', 'REBE', 'RECH', 'RECE']
    

def clean_hitlist_data(df):

    df.drop(columns=[col for col in drop_list if col in df.columns], inplace=True)

    def event_filter(df):
        filtered_events = df[df['EV_TYPE'].isin(EVENT_TYPE_KEEP)]
        filtered_events = filtered_events[filtered_events['ACCOUNT_NAME'] != 'Fairmont Scottsdale/In House Functions']
        filtered_events = filtered_events[filtered_events['ACCOUNT_NAME'] != 'Fairmont Scottsdale Princess']
        filtered_events = filtered_events[
            filtered_events['ACCOUNT_NAME'].notna() & (filtered_events['ACCOUNT_NAME'] != 'N/A')]
        return filtered_events

    def get_max_event_details(events, event_types):
        filtered_events = events[events['EV_TYPE'].isin(event_types)]
        if not filtered_events.empty:
            max_event = filtered_events.loc[filtered_events['ATTENDEES'].idxmax()]
            return {
                'type': max_event['EV_TYPE'],
                'time': max_event['TIME'],
                'location': max_event['FUNC_SPACE'],
                'attendees': filtered_events['ATTENDEES'].sum()
            }
        return {'type': '', 'time': '', 'location': '', 'attendees': 0}

    def clean_hitlist(df):
        filtered_events = event_filter(df)
        summary_by_day = []

        for day in filtered_events['DATE'].unique():
            day_events = filtered_events[filtered_events['DATE'] == day]
            for account in day_events['ACCOUNT_NAME'].unique():
                account_events = day_events[day_events['ACCOUNT_NAME'] == account]

                # Calculate event details
                breakfast_details = get_max_event_details(account_events, BREAKFAST_EVENTS)
                lunch_details = get_max_event_details(account_events, LUNCH_EVENTS)
                dinner_details = get_max_event_details(account_events, DINNER_EVENTS)

                summary_by_day.append({
                    'DATE': day,
                    'ACCOUNT_NAME': account,
                    'BREAKFAST_ATTENDEES': breakfast_details['attendees'],
                    'BREAKFAST_TYPE': breakfast_details['type'],
                    'BREAKFAST_TIME': breakfast_details['time'],
                    'BREAKFAST_LOCATION': breakfast_details['location'],
                    'LUNCH_ATTENDEES': lunch_details['attendees'],
                    'LUNCH_TYPE': lunch_details['type'],
                    'LUNCH_TIME': lunch_details['time'],
                    'LUNCH_LOCATION': lunch_details['location'],
                    'DINNER_ATTENDEES': dinner_details['attendees'],
                    'DINNER_TYPE': dinner_details['type'],
                    'DINNER_TIME': dinner_details['time'],
                    'DINNER_LOCATION': dinner_details['location'],
                })

        # Convert summary to DataFrame
        summary_df = pd.DataFrame(summary_by_day)
        column_order = ['DATE', 'ACCOUNT_NAME', 'BREAKFAST_ATTENDEES', 'BREAKFAST_TYPE',
                        'BREAKFAST_TIME', 'BREAKFAST_LOCATION', 'LUNCH_ATTENDEES',
                        'LUNCH_TYPE', 'LUNCH_TIME', 'LUNCH_LOCATION', 'DINNER_ATTENDEES',
                        'DINNER_TYPE', 'DINNER_TIME', 'DINNER_LOCATION']
        summary_df = summary_df[column_order]
        summary_df['DATE'] = pd.to_datetime(summary_df['DATE']).dt.strftime('%m/%d/%Y')

        return summary_df

    try:
        cleaned_hitlist = clean_hitlist(df)
        return cleaned_hitlist

    except Exception as e:
        logging.error(f"Error processing hitlist data: {e}")
        # Confirm missing/partial return data:
        print({'error': 'Failed to process hitlist data.'})


forecast_file = st.file_uploader('Forecast:', type='.xlsx')
if forecast_file is not None:
    forecast_df = pd.read_excel(forecast_file, header=[3], index_col=[0])
    unnamed_cols = [col for col in forecast_df.columns if 'Unnamed' in str(col)]
    if unnamed_cols:
        forecast_df = forecast_df.drop(columns=unnamed_cols, inplace=False)

    # Reset index and set up base DataFrame
    forecast_df.reset_index(inplace=True)
    

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

def clean_group_data(df):

    date_format = '%m/%d/%Y'

    cleaned_groups = df.iloc[59:-2]
    cleaned_groups.dropna(subset=cleaned_groups.columns[1:], how='all', inplace=True)
    cleaned_groups = cleaned_groups.T
    cleaned_groups.reset_index(inplace=True)
    cleaned_groups.columns = cleaned_groups.iloc[0]
    cleaned_groups = cleaned_groups.iloc[1:]
    cleaned_groups.columns.values[0] = 'DATE'
    cleaned_groups['DATE'] = pd.to_datetime(cleaned_groups['DATE'], errors='coerce')
    cleaned_groups['DATE'] = cleaned_groups['DATE'].dt.strftime(date_format)

    return cleaned_groups


if st.button('Process Files'):
    cleaned_hitlist = clean_hitlist_data(hitlist_df)
    st.session_state.clean_dfs['Hitlist'] = cleaned_hitlist
    cleaned_forecast = clean_forecast_data(forecast_df)
    st.session_state.clean_dfs['Forecast'] = cleaned_forecast
    cleaned_groups = clean_group_data(forecast_df)
    st.session_state.clean_dfs['Group Rooms'] = cleaned_groups


def combine_dfs(dict):
    file_name = 'Potentials_Data.xlsx'
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for sheet_name, df in dict.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        writer.close()
        output.seek(0)

        return output.getvalue(), file_name

if st.button('Generate .xlsx export'):
    file_content, file_name = combine_dfs(st.session_state.clean_dfs)
    st.download_button(
        label='Download File',
        data=file_content,
        file_name=file_name,
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
  













            






             


        

        




    




