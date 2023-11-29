import pandas as pd
from firebase_admin import credentials, db
import firebase_admin

def GetDataFromFirebase(JSON_DB_File:str="database-of-hwd-durations-firebase-adminsdk-d3yd8-a4a0833a8f.json",
                        ProjectID:str = "database-of-hwd-durations",
                        databaseURL:str = "database-of-hwd-durations.firebaseapp.com"):
    cred = credentials.Certificate(JSON_DB_File)
    Config = {
    "apiKey": "AIzaSyCHD9raTlgFp-OT64UP3wV-oIU-pXLAd54",
    "authDomain": databaseURL,
    "databaseURL": "https://database-of-hwd-durations-default-rtdb.firebaseio.com",
    "projectId": ProjectID,
    "storageBucket": "database-of-hwd-durations.appspot.com",
    "messagingSenderId": "359816228479",
    "appId": "1:359816228479:web:7606ca596bbb4678c2594a",
    "measurementId": "G-ZYKYSKCF8X"
    }

    firebase_admin.initialize_app(cred, Config)
    ref = db.reference("/")
    data = ref.get()
    df = pd.DataFrame(data)
    df = df.rename_axis('Time').reset_index()
    df.sort_values(by='Time', inplace=True)
    df = df.drop(columns=['LED_VAL'])
    return df

database = GetDataFromFirebase()#.fillna("No Detection happended this Time")
