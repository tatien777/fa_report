import requests 
import os 
import pandas as pd 
import numpy as np
import streamlit as st 


# from fa_report.untils import play_with_ggsheet,import_file
import utils.import_file as import_file
# import utils.play_with_gsheet 
# import utils.import_file

## Read data
def read_df(csv,index=False):
    df = pd.read_csv(csv, index)
    return df
def main():
    st.write("``` Phần này import file có sameday hộ e nhé: ```")
    m4_user_trans = import_file.import_file('m4_user')
    if m4_user_trans is None:
        print('None')
    else:
        # st.dataframe(m4_user_trans.id.c())
        m4 = m4_user_trans.copy()
        ## BONUS
        bonus = m4[(m4['policy_code'] == 'BONUSPREPAID') |(m4['note'].str.contains('Bonus for')) |(m4['note'].str.contains('bonus for'))] 
        bonus['policy_full'] = 'BONUSPREPAID'
        bonus['TK'] = '64181'
        no_bonus = m4[~m4.id.isin(bonus.id)]
        ## Momo 
        momo = no_bonus[(no_bonus['note'].str.contains("MoMo Topup transid")) | (no_bonus['note'].str.contains('MoMo QR Topup transid'))]
        momo['policy_full'] = 'THU MOMO' 
        momo['TK'] = '13882'
        no_momo = no_bonus[~no_bonus.id.isin(momo.id)]
        no_momo['note'] = no_momo['note'].fillna('None')
        ## vnp 
        vnp = no_momo[no_momo['note'].str.contains('VNPAY QR Topup transid')] 
        vnp['policy_full'] = 'THU VNPAY'
        vnp['TK'] = '13882'
        no_vnp = no_momo[~no_momo.id.isin(vnp.id)]
        ## REFERRAL
        referral = no_vnp[no_vnp['type'] == 'REFERRAL']
        referral['policy_full'] = 'REFERRAL' 
        referral['TK'] = '64181' 
        no_refer = no_vnp[~no_vnp.id.isin(referral.id)]
        ## TX-KH
        TX_KH = no_refer[(no_refer['policy_code'] == 'OTHERS')&((no_refer['note'].str.contains('Chuyển tiền từ tài khoản tài xế'))| (no_refer['note'].str.contains('tiền từ tài khoản tài xế')) | (no_refer['note'].str.contains('tiền từ tài khoản')))] 
        TX_KH['policy_full'] = 'TX_KH'
        TX_KH['TK'] = '33882'
        no_txkh = no_refer[~no_refer.id.isin(TX_KH.id)]
        ## PREPAID
        prepaid = no_txkh[(no_txkh['note'].str.contains('PREPAID')) | (no_txkh['policy_code'] == 'PREPAID')]
        prepaid['policy_full'] = 'PREPAID'
        prepaid['TK'] = '112'
        no_prepaid = no_txkh[~no_txkh.id.isin(prepaid.id)]
        ## ClearCN
        clearcn = no_prepaid[(no_prepaid['note'].str.contains('NAPTKC'))|(no_prepaid['note'].str.contains('công nợ'))|(no_prepaid['note'].str.contains('Clear CN'))|(no_prepaid['note'].str.contains('CN'))|(no_prepaid['policy_code'] == 'NAPTKC') ]
        clearcn['policy_full'] = 'CLEARCN'
        clearcn['TK'] = '112'
        no_CN = no_prepaid[~no_prepaid.id.isin(clearcn.id)]
        print(no_CN)
        ## Đổi TK
        doiTK = no_CN[(no_CN['note'].str.contains('DOITK'))|(no_CN['policy_code'] == 'DOITK')]
        doiTK['policy_full'] = 'DOITK'
        doiTK['TK'] = 'NO'
        no_doiTK = no_CN[~no_CN.id.isin(doiTK.id)]
        ## Đền bù
        denbu = no_doiTK[(no_doiTK['policy_code'] == 'OTHERS') & (no_doiTK['type'] == 'REWARD') & (no_doiTK['note'].str.contains('Đền bù'))|(no_doiTK['note'].str.contains('Den bu'))| (no_doiTK['note'].str.contains('den bu'))|(no_doiTK['note'].str.contains('đền bù'))] 
        denbu['policy_full'] = 'DENBU'
        denbu['TK'] = '64186'
        no_denbu = no_doiTK[~no_doiTK.id.isin(denbu.id)]
        print(no_denbu)
        ### ALL ### 
        frames = [bonus,momo,vnp,referral,TX_KH,prepaid,clearcn,doiTK,denbu]
        result = pd.concat(frames)
        st.markdown(' ** ALL data ** ')
        st.dataframe(result.count()) 
        result1=bonus.append(momo).append(vnp).append(referral).append(TX_KH).append(prepaid).append(clearcn).append(doiTK).append(denbu)
        result['policy_code'] = result['policy_code'].fillna('None')
        result['order_id'] = result['order_id'].fillna('None')
        result_final = result.groupby(['policy_full','TK','city_id']).agg({'amount':'sum', 'time':'count'}).reset_index()
        result_final['amount'] = result_final['amount'].apply(lambda x: round(x))
        result_final_2 = result.groupby('policy_full').agg({'amount':'sum'}).reset_index(drop = False )
        result_final_2['amount'] = result_final_2['amount'].apply(lambda x: round(x))
        st.dataframe(result_final)
        st.dataframe(result_final_2)

main()  
