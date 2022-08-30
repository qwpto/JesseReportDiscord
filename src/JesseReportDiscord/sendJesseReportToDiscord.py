from discord_webhook import DiscordWebhook
from jesse.services.file import store_logs
import jesse.helpers as jh
from jesse.modes import backtest_mode
from jesse.config import config
from jesse.services import charts
from jesse.services import report
from jesse.routes import router
from datetime import datetime, timedelta
from jesse.store import store
import jesse.services.metrics as stats
import git

import pandas as pd
import os
from matplotlib import pyplot as plt

import zipfile
from os.path import basename

from packaging import version
from jesse.version import __version__ as jesse_version

# from jesse.strategies import Strategy


def sendJesseReportToDiscord(webhookUrl: str, customFiles={}):
    if(True):#config["app"]["trading_mode"] == 'backtest'):
        if store.completed_trades.count > 0:
            messageContent = ""

            generate_json = generate_tradingview = generate_csv = True
            logs_path = store_logs(generate_json, generate_tradingview, generate_csv)
            if(len(customFiles)>0):
                logs_path.update(customFiles)
            file_name = jh.get_session_id()
            studyname = backtest_mode._get_study_name()
            chartOverview = charts.portfolio_vs_asset_returns(studyname)
            plt.close()

            if(version.parse(jesse_version) < version.parse("0.39.0")):
                start_date = datetime.fromtimestamp(store.app.starting_time / 1000)
                date_list = [start_date + timedelta(days=x) for x in range(len(store.app.daily_balance))]
                fullCandles = backtest_mode.load_candles(date_list[0].strftime('%Y-%m-%d'), date_list[-1].strftime('%Y-%m-%d'))
                quantStats = backtest_mode._generate_quantstats_report(fullCandles)

            messageContent += studyname + "\n"

            # current version info
            repo = git.Repo(search_parent_directories=False)
            messageContent += "Branch: " + repo.head.reference.name + "\n"
            messageContent += "Version: " + repo.head.object.hexsha + "\n"

            messageContent += "\n"

            hp = stats.hyperparameters(router.routes)
            for item in hp:
                # if(type(item[1]) == float):
                #   messageContent += ("{:<1} \t{:.7g}\n".format(item[0], item[1]))            
                # else:
                messageContent += ("{:<1} \t{:<1}\n".format(item[0], item[1]))

            messageContent += "\n"

            for key, value in report.portfolio_metrics().items():
                # if(type(value) == float):
                #    messageContent += ("{:<1} \t{:.7g}\n".format(key, value))
                # else:
                messageContent += ("{:<1} \t{:<1}\n".format(key, value))

            # update csv to readable date:
            df = pd.read_csv(logs_path['csv'])
            df['opened_at'] = df["opened_at"].apply(lambda t: datetime.utcfromtimestamp(t / 1000).strftime('%Y-%m-%d %H:%M:%S'))
            df['closed_at'] = df["closed_at"].apply(lambda t: datetime.utcfromtimestamp(t / 1000).strftime('%Y-%m-%d %H:%M:%S'))
            df.to_csv(logs_path['csv'], index=False)

            while(len(messageContent)>=1999): # the discord message limit is 2000
                index = messageContent.rfind("\n", 0, 1999)
                webhook = DiscordWebhook(url=webhookUrl, content=messageContent[0:index])
                response = webhook.execute() #should check response code
                messageContent = messageContent[index+1:len(messageContent)]

            webhook = DiscordWebhook(url=webhookUrl, content=messageContent)
            attachmentSize = 0
            with open(chartOverview, "rb") as f: webhook.add_file(file=f.read(), filename=file_name + '_overview.png')
            attachmentSize += os.path.getsize(chartOverview)

            if(version.parse(jesse_version) < version.parse("0.39.0")):
                with open(quantStats, "rb") as f: webhook.add_file(file=f.read(), filename=file_name + '_quantstats.html')
                attachmentSize += os.path.getsize(quantStats)
            
            discordSizeLimit = 7999000 #discord file limit 8MB
            for types, path in logs_path.items():
                if(os.path.getsize(path) > discordSizeLimit):
                    #zip the file up
                    with zipfile.ZipFile(path + '.zip', 'w', zipfile.ZIP_DEFLATED) as zipObj2:
                      zipObj2.write(path, basename(path))
                      path = path + '.zip'
                      types = types + '.zip'

                if(os.path.getsize(path) > discordSizeLimit):#still too big after zipping it
                    #file is too big to attach in one piece
                    file_number = 1
                    with open(path, "rb") as f:
                        chunk = f.read(discordSizeLimit)
                        while chunk:
                            with open(path + str(file_number), 'wb') as chunk_file:
                                chunk_file.write(chunk)                            
                            chunk = f.read(discordSizeLimit)
                            if((attachmentSize + os.path.getsize(path + str(file_number))) > discordSizeLimit):
                                response = webhook.execute()
                                webhook = DiscordWebhook(url=webhookUrl, content='')
                                attachmentSize = 0                                
                            with open(path + str(file_number), "rb") as f2: webhook.add_file(file=f2.read(), filename=file_name + '.' + types + str(file_number))
                            attachmentSize += os.path.getsize(path + str(file_number))
                            file_number += 1
                else:
                    if((attachmentSize + os.path.getsize(path)) > discordSizeLimit):
                        response = webhook.execute()
                        webhook = DiscordWebhook(url=webhookUrl, content='')
                        attachmentSize = 0
                        
                    with open(path, "rb") as f: webhook.add_file(file=f.read(), filename=file_name + '.' + types)
                    attachmentSize += os.path.getsize(path)
            if(attachmentSize > 0):
                response = webhook.execute()
            
            
            plt.close()
