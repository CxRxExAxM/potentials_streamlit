import streamlit as st
import pandas as pd
import logging



drop_list = ['COL1', 'EVENT_DAY', 'BOOKING_NAME', 'Distro?', 'BOOK_ID', 'CONTACT_FULL_NAME',
             'BOOKING_STATUS', 'PHONE_NO', 'CF_CONTACT_NAME', 'CF_ACCT_AGENT_NAME',
             'CF_PHONE_NO', 'CAT_OWNER_CODE', 'EVENT_LINK_ID', 'SETUP_SETDOWN_TIME',
             'SC_TRANSLATION_GEMTRANSLATION_', 'DATE_SORT_COLUMN', 'GTD', 'ACT', 'RESORT', 'Column1']

EVENT_TYPE_KEEP = ['BKFB', 'LNCB', 'OTHR', 'BKFT', 'RECM', 'REBE', 'DINB', 'RECH', 'DINR', 'RECE']
BREAKFAST_EVENTS = ['BKFB', 'BKFT']
LUNCH_EVENTS = ['LNCB']
DINNER_EVENTS = ['DINB', 'DINR', 'OTHR', 'RECM', 'REBE', 'RECH', 'RECE']
   
    

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
    st.write('clean_hitlist called)')
    filtered_events = event_filter(df)
    summary_by_day = []
    df.drop(columns=[col for col in drop_list if col in df.columns], inplace=True)

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


    
    






  


       


