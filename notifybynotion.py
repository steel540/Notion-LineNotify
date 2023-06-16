# -*- coding: utf-8 -*-
"""
Created on Fri May 12 21:54:38 2023

@author: User
"""

import requests
import pandas as pd
from notion_client import Client
import time
from datetime import datetime

# notion information
database_id  = "c23041161c8f45dba3dc362db47eab3d" # notion table page
notion_token = "your_Notion_token" # notion connection token
Line_token   = "your_Line_token"




def lineNotifyMessage(Line_token, msg):

    headers = {
        "Authorization": "Bearer " + Line_token, 
        "Content-Type" : "application/x-www-form-urlencoded"
    }

    payload = {'message': msg }
    r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
    return r.status_code


def getnotiontable(database_id, notion_token):
    # 設定 Notion API Token 和 Database ID
    notion = Client(auth=notion_token)
    
    
                   
    # 取得資料庫中的所有資料
    results = notion.databases.query(database_id).get("results")
    
    # 將 Notion 資料轉換成 Pandas DataFrame
    data = []
    for item in results:
        try:
            text = item["properties"]["Name"]["title"][0]["text"]["content"]
        except:
            text = None    
        try:
            date = item["properties"]["Date"]["date"]["start"]
        except:
            date = None    
        try:
            Message = item["properties"]["Message"]["rich_text"][0]["text"]["content"]
        except:
            Message = None
        try:
            Line_group = item["properties"]["Line group"]["multi_select"][0]["name"]
        except:
            Line_group = None
        try:
            Tigger = item["properties"]["Tigger"]["select"]["name"]
        except:
            Tigger = None        
        data.append([text, date, text, Message, Line_group, Tigger])
    
    df = pd.DataFrame(data, columns=["Name", "Date", "video file", "Message", "Line group", "Tigger"])
    
    return df



if __name__ == "__main__":


    # 讀取DataFrame資料
    df = getnotiontable(database_id, notion_token)
    print(df)
    # 設定監控頻率
    monitor_interval = 60  # 每一分鐘檢查一次
    
    while True:
        # 取得目前時間，並轉換為與行程時間相同的格式
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        # 搜尋是否有任何行程需要啟動
        for index, row in df.iterrows():
            scheduled_time = datetime.strptime(row['Date'][:19], '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d %H:%M')
            print('scheduled_time :', scheduled_time)
            print('current_time :', current_time)
            if scheduled_time == current_time:
                print('時間符合')
                if row['Tigger'] == 'Yes':
                    print('啟動推播')
                    lineNotifyMessage(Line_token, row['Message'])
                    
        # 休息一段時間再進行下一次監控
        print('sleep')
        time.sleep(monitor_interval)
        # update notion table information
        df = getnotiontable(database_id, notion_token)
        print(df)
        
