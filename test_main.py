

import streamlit as st
import main as m1
import SessionState
import test_auth_2
import pandas as pd
import streamlit as st
# import plotly.express as px
import os

from enum import Enum
from io import BytesIO, StringIO
from typing import Union
import base64
import test_auth_2

STYLE = """
<style>
img {
    max-width: 100%;
}
</style>
"""

FILE_TYPES = ["csv", "py", "png", "jpg"]
class FileType(Enum):
    """Used to distinguish between file types"""

    IMAGE = "Image"
    CSV = "csv"
    PYTHON = "Python"


def get_file_type(file: Union[BytesIO, StringIO]) -> FileType:
    """The file uploader widget does not provide information on the type of file uploaded so we have
    to guess using rules or ML

    I've implemented rules for now :-)

    Arguments:
        file {Union[BytesIO, StringIO]} -- The file uploaded

    Returns:
        FileType -- A best guess of the file type
    """

    if isinstance(file, BytesIO):
        return FileType.IMAGE
    content = file.getvalue()
    if (
        content.startswith('"""')
        or "import" in content
        or "from " in content
        or "def " in content
        or "class " in content
        or "print(" in content
    ):
        return FileType.PYTHON

    return FileType.CSV


def import_file(name):
    st.write("run file name: " + str(name))
    file = st.file_uploader("Upload file", type=FILE_TYPES,key=name)
    show_file = st.empty()
    if not file:
        show_file.info("Please upload a file of type: " + ", ".join(FILE_TYPES))
        return

    file_type = get_file_type(file)
    if file_type == FileType.IMAGE:
        show_file.image(file)
    elif file_type == FileType.PYTHON:
        st.code(file.getvalue())
    else:
        data = pd.read_csv(file)
        st.dataframe(data.head(5))
        st.markdown('*** số lượng dòng của file *** ')
        st.dataframe(data.count())
    file.close()
    return data

def main_auto():
    st.title(' Automation app for FA report - Tien Ta')
    st.markdown('You can import file & then generate the Revenue & Cost in automation ')
    st.write("Here import file csv: (please convert .xlsx -> .csv) ")
    st.write("``` Phần này import file có sameday hộ e nhé: ```")

    df_sameday = import_file('sameday')
    if df_sameday is None: st.write("Waiting import data")
    elif df_sameday.empty : st.write("No data")
    else:
        def clean_sameday(df):
            df1_fillna = df.fillna(value=0)
            df1 = df1_fillna[['postpaid','service_id','order_date','payment_method','stoppoint','gsv','aha_revenue', 'gsv_user_app','partner_discount','request_fee_no']]
            # df1['OrderYearMonth'] = df1['order_date'].map(lambda date: 100*date.year + date.month)
            cols = ['gsv_user_app', 'partner_discount', 'request_fee_no']   #convert dtypes from object to numeric
            df1[cols] = df1[cols].apply(pd.to_numeric,errors='coerce', axis=1) # 
            list = ['SGN-SAMEDAY','HAN-SAMEDAY']
            df_sameday = df1[df1['service_id'].isin(list)]
            df_sameday['aha_revenue1'] = (df_sameday['gsv_user_app'] * 0.2) / 1.1
            df_supplier = df1[~df1['service_id'].isin(list)]
            df_concat = pd.concat([df_sameday, df_supplier], ignore_index=True, sort=False)
            df_concat_SD = df_concat.rename(columns={"gsv_user_app":"GSV1", "partner_discount":"discount"})
            df_concat_SD['HĐBH'] = (df_concat_SD['GSV1'] - df_concat_SD['aha_revenue1']*1.1)
            df_concat_SD = df_concat_SD.drop(columns='stoppoint', axis=0)
            df_concat_SD['service_type'] = "SAMEDAY"
            df_concat_SD['stoppoint']=df_sameday['stoppoint']
            df_concat_SD['aha_vat1']=df_concat_SD['aha_revenue1']*0.1
            df_concat_SD['GSV (Exclude VAT)'] = df_concat_SD['GSV1'] - df_concat_SD['aha_vat1']
            return df_concat_SD
        df_concat_SD = clean_sameday(df_sameday)
        st.markdown('sau khi cleanData : ')
        st.dataframe(df_concat_SD.head(5)) 
        st.dataframe(df_concat_SD.groupby('service_type')['service_type'].count()) 
        
    st.write("Here import file csv: (please convert .xlsx -> .csv) ")
    st.write("``` Phần này import file không có sameday hộ e nhé: ```")    
    df_noSD = import_file('no_sameday')
    if df_noSD is None: st.write("Waiting import data")
    elif df_noSD.empty : st.write("No data")
    else:
        def clean_no_sameday(df):
            df2 = df.copy()
            # df_Aha = df2.convert_objects(convert_numeric=True)
            df_Aha = df2.fillna(value=0)
            def gsv(row):
                two_prices_services = ['HAN-FOOD', 'HAN-LAZADA','SGN-FOOD','SGN-LAZADA','SGN-SENDO-TMDT']
                if row["service_id"] in two_prices_services:
                    return row['gsv_user_app']
                return row['gsv']

            df_Aha['GSV1'] = df_Aha.apply(gsv, axis=1)

            def gsv(row):
                two_prices_services = ['HAN-FOOD', 'HAN-LAZADA','SGN-FOOD','SGN-LAZADA','SGN-SENDO-TMDT']
                if row["service_id"] in two_prices_services:
                    return row['partner_discount']
                return row['discount']
            df_Aha['discount1'] = df_Aha.apply(gsv, axis=1)
            df_Aha['check_com'] = (df_Aha['PIT_driver']+df_Aha['aha_commission'])/(df_Aha['gsv']-df_Aha['request_fee_no'])
            df_Aha['commission_rate'] = (df_Aha['aha_commission'])/(df_Aha['gsv']-df_Aha['request_fee_no'])
            df_Aha['aha_revenue1'] = (df_Aha['GSV1']*df_Aha['commission_rate'])/1.1
            df_Aha['aha_vat1'] = (df_Aha['GSV1']*df_Aha['commission_rate'])/1.1*0.1
            df_Aha['HĐBH'] = (df_Aha['GSV1'] - (df_Aha['aha_revenue1']+df_Aha['aha_vat1']))
            df_Aha['gross_up_driver_income1'] = (df_Aha['gsv']-df_Aha['request_fee_no'])*(1 - df_Aha['commission_rate'])
            df_Aha['diff_two_price'] = df_Aha['HĐBH'] - df_Aha['gross_up_driver_income1'] - df_Aha['request_fee_no']
            df_Aha['GSV (Exclude VAT)'] = df_Aha['GSV1'] - df_Aha['aha_vat1']        
            return df_Aha  
        df_Aha = clean_no_sameday(df_noSD)
        st.markdown('sau khi cleanData : ')
        st.dataframe(df_Aha.head(5)) 
        st.dataframe(df_Aha.groupby('service_type')['service_type'].count()) 

    st.header('Run button below to get full-report')  
    # @st.cache(persist=True) 
    
    def merge_pivot(res_samday,res_no_sameday):
        df_MIS = pd.concat([res_no_sameday, res_samday], ignore_index=True, sort=False)
        pivot_MIS1 = df_MIS.pivot_table(index=['service_type','postpaid'], values=['GSV1','discount','request_fee_no','GSV (Exclude VAT)','HĐBH'],aggfunc='sum',margins=True)
        MIS1 = pivot_MIS1.reset_index()
        MIS1_fn = MIS1[['service_type','postpaid','GSV1','discount','request_fee_no','GSV (Exclude VAT)','HĐBH']]
        MIS1_fn[['GSV1','discount','request_fee_no','GSV (Exclude VAT)','HĐBH']].astype(float)
        return MIS1_fn
    session_state = SessionState.get(name="", button_sent=False)
    session_state.button = st.button('Click to run report',key="run")
    if session_state.button == True:
        pd.options.display.float_format = '{:,}'.format
        result = merge_pivot(df_concat_SD, df_Aha)
        st.dataframe(result) 
        # st.button('Click to export result.csv',key="export")
        csv = result.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
        href = f'<a href="data:file/csv;base64,{b64}">Download CSV File</a> (right-click and save as &lt;some_name&gt;.csv)'
        st.markdown(href, unsafe_allow_html=True)


import streamlit as st
import collections
import functools

class StopExecution(Exception):
    """Special Exception which does not display any output to the Streamlit app."""
    pass
import test_auth
def main():
    valid = test_auth.confirm_button_example()
    if valid: main_auto()
main()