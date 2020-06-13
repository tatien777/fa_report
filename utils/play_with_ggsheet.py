from apiclient import discovery
from oauth2client import client
from oauth2client import tools
import httplib2
import json
import pandas as pd 

JSON_DATA = {"access_token": "ya29.a0AfH6SMAr50Gvgqho0ZOgCCcRzD1nelmdX4Dt8M30beKeAQ5onjbRvieBNSM3WlzpJTTbrNtD_ji5XkVU1ynK0aqEx_AfV1A8e567b0gibJLxap_LOZSCQy424BwJVc-kqAUI27tDqmYpOjWs7q8JtRHXF08TdKrMjc0", 
             "client_id": "691772516136-ffblqulaum0ar049n25b3ut5q8tp9avl.apps.googleusercontent.com", 
             "client_secret": "xkzuqRyIQLChIQlpu_naDseY", 
             "refresh_token": "1//0ek219OBxjfW3CgYIARAAGA4SNwF-L9IrRHej1mrI3EN9SlVyNJy9xJNZdKP69xZoYIko9RkBT9EFq28H8S0zsMCjb1EICyr2eHE", 
             "token_expiry": "2017-09-05T15:52:02Z", 
             "token_uri": "https://oauth2.googleapis.com/token", 
             "user_agent": "Google Sheets API Python Quickstart", 
             "revoke_uri": "htt://accounts.google.com/o/oauth2/revoke", 
             "id_token":  None, 
             "id_token_jwt": None, 
             "token_response": {
                 "access_token": "ya29.a0AfH6SMAr50Gvgqho0ZOgCCcRzD1nelmdX4Dt8M30beKeAQ5onjbRvieBNSM3WlzpJTTbrNtD_ji5XkVU1ynK0aqEx_AfV1A8e567b0gibJLxap_LOZSCQy424BwJVc-kqAUI27tDqmYpOjWs7q8JtRHXF08TdKrMjc0", 
                 "expires_in": 3600, 
                 "refresh_token": "1//0ek219OBxjfW3CgYIARAAGA4SNwF-L9IrRHej1mrI3EN9SlVyNJy9xJNZdKP69xZoYIko9RkBT9EFq28H8S0zsMCjb1EICyr2eHE", 
                 "token_type": "Bearer"
             }, 
             "scopes": ["https://www.googleapis.com/auth/spreadsheets"], 
             "token_info_uri": "https://www.googleapis.com/oauth2/v3/tokeninfo", 
             "invalid": False, 
             "_class": "OAuth2Credentials", 
             "_module": "oauth2client.client"
            }

def play_with_gsheet(spreadsheetId=None, _range=None, dataframe=None, method='read'):
    """
    method: {'read', 'write', 'clear', 'append'}
    """
    
    credentials = client.Credentials.new_from_json(json.dumps(JSON_DATA))
    service = discovery.build('sheets', 'v4', credentials=credentials)
    
    if method == 'read':
        result = service.spreadsheets().values().get(spreadsheetId=spreadsheetId, range=_range).execute()
        values = result.get('values', [])
        if len(values) > 1:
            df = pd.DataFrame(values)
            df = df.iloc[1:]
            df.columns = values[0]
        elif len(values) == 1:
            df = pd.DataFrame(columns = values[0])
        else: df = pd.DataFrame()
        return df
    
    if method == 'write':
        values = [dataframe.columns.values.astype(str).tolist()] + dataframe.astype(str).values.tolist()
        data = [
        {
            'range': _range,
            'values': values
        }
        ]
        body = {
            'valueInputOption':'RAW',
            'data':data
        }
        result = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body=body).execute()
    
    if method == 'clear':
        body = {
            'ranges':_range
        }
        result = service.spreadsheets().values().batchClear(spreadsheetId=spreadsheetId, body=body).execute()
        
    if method == 'append' and dataframe is not None:
        body = {
            'values': dataframe.astype(str).values.tolist()
        }
        result = service.spreadsheets().values().append(spreadsheetId=spreadsheetId, range=_range,
                                                        valueInputOption='RAW', insertDataOption='INSERT_ROWS',
                                                        body=body).execute()
