import streamlit as st 
from Home import face_rec
from auth import authenticator
import pandas as pd
#st.set_page_config(page_title='Reporting',layout='wide')
st.subheader('Reporting')

if 'authentication_status' not in st.session_state:
    st.session_state['authentication_status'] = False
if st.session_state['authentication_status']:
    authenticator.logout('Logout', 'sidebar', key='unique_key')

    # Retrive logs data and show in Report.py
    # extract data from redis list
    name = 'Attendance:logs'
    def load_logs(name,end=-1):
        logs_list = face_rec.r.lrange(name,start=0,end=end) # extract all data from the redis database
        return logs_list

    # tabs to show the info
    tab1, tab2, tab3 = st.tabs(['Registered Data','Logs','Attendance Report'])

    with tab1:
        if st.button('Refresh Data'):
            # Retrive the data from Redis Database
            with st.spinner('Retriving Data from Redis DB ...'):
                redis_face_db = face_rec.retrive_data(name='academy:register')
                st.dataframe(redis_face_db[['Name','Role']])

    with tab2:
        if st.button('Refresh Logs'):
            Logs_file = load_logs(name=name)
            convert_byte_to_string_1 = lambda x: x.decode('utf-8')
            logs_list_string1 = list(map(convert_byte_to_string_1,Logs_file))
            split_string = lambda x: x.split('@')
            logs_nested_list1 = list(map(split_string, logs_list_string1))
            st.write(logs_nested_list1)
    
    with tab3:
        st.subheader('Attendance Report')

        #load logs into attribute logs_list
        logs_list = load_logs(name=name)
        
        #step-1 Convert the logs that in list of bytes into list of string
        convert_byte_to_string = lambda x: x.decode('utf-8')
        logs_list_string = list(map(convert_byte_to_string,logs_list))
        
        # step -2: split string by @ and create nested list
        split_string = lambda x: x.split('@')
        logs_nested_list = list(map(split_string, logs_list_string))
        #convert nested list info into dataframe
        
        logs_df = pd.DataFrame(logs_nested_list,columns = ['Name','Role','Timestamp'])
        
        # step 3 : Time based Analysis or Report
        
        logs_df['Timestamp'] = pd.to_datetime(logs_df['Timestamp'])
        logs_df['Date']= logs_df['Timestamp'].dt.date
        
        #step 3.1 : cal , Intime and OutTime
        #In Time : At which person is first detected in that day (min TimeStamp of the date)
        #Out time: At which person is last detected in that day(Max Timestamp of the date)
        
        report_df = logs_df.groupby(by=['Date','Name','Role']).agg(
            In_time = pd.NamedAgg('Timestamp','min'), # in time
            Out_time = pd.NamedAgg('Timestamp','max'),# out time
        
            ).reset_index()
        
        report_df['In_time'] = pd.to_datetime(report_df['In_time'])
        report_df['Out_time'] = pd.to_datetime(report_df['Out_time'])

        report_df['Duration'] = report_df['Out_time'] - report_df['In_time']
        
        #Step 4: MArking Person is Present or Absent
        all_dates = report_df['Date'].unique()
        name_role = report_df[['Name','Role']].drop_duplicates().values.tolist()
        
        date_name_rol_zip = []
        for dt in all_dates:
            for name, role in name_role:
                date_name_rol_zip.append([dt,name,role])
                
        date_name_rol_zip_df = pd.DataFrame(date_name_rol_zip, columns = ['Date','Name','Role'])
        
        # left join with report_df
        
        date_name_rol_zip_df = pd.merge(date_name_rol_zip_df,report_df, how = 'left',on=['Date','Name','Role'])
    
        
        #Duration
        #Hours
        date_name_rol_zip_df['Duration_seconds']=date_name_rol_zip_df['Duration'].dt.seconds
        date_name_rol_zip_df['Duration_hours']=date_name_rol_zip_df['Duration_seconds'] / (60*60)
        
        def status_maker(x):
            if pd.Series(x).isnull().all():
                return 'Absent'
            elif x >= 0 and x < 1:
                return 'Absent (Less than 1 hours)'
            elif x > 1 and x < 4:
                return 'Half Day(less than 4 hours)'
            elif x >= 4 and x < 6:
                return 'Present'
            elif x >= 6:
                return 'Present'
            
        date_name_rol_zip_df['Status'] = date_name_rol_zip_df['Duration_hours'] .apply(status_maker)
        
        st.dataframe(date_name_rol_zip_df)
        
else:
    name, authentication_status, username = authenticator.login('main')

