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

from matplotlib import pyplot as plt

# from jesse.strategies import Strategy


def sendJesseReportToDiscord(webhookUrl: str):
    if(config["app"]["trading_mode"] == 'backtest'):
        messageContent = ""

        generate_json = generate_tradingview = generate_csv = True
        logs_path = store_logs(generate_json, generate_tradingview, generate_csv)
        file_name = jh.get_session_id()
        studyname = backtest_mode._get_study_name()
        chartOverview = charts.portfolio_vs_asset_returns(studyname)
        plt.close()

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
            messageContent += ("{:<1} \t{:<1}\n".format(item[0], item[1]))

        messageContent += "\n"

        for key, value in report.portfolio_metrics().items():
            messageContent += ("{:<1} \t{:<1}\n".format(key, value))

        # update csv to readable date:
        df = pd.read_csv(logs_path['csv'])
        df['opened_at'] = df["opened_at"].apply(lambda t: datetime.utcfromtimestamp(t / 1000).strftime('%Y-%m-%d %H:%M:%S'))
        df['closed_at'] = df["closed_at"].apply(lambda t: datetime.utcfromtimestamp(t / 1000).strftime('%Y-%m-%d %H:%M:%S'))
        df.to_csv(logs_path['csv'], index=False)

        webhook = DiscordWebhook(url=webhookUrl, content=messageContent)
        with open(chartOverview, "rb") as f: webhook.add_file(file=f.read(), filename=file_name + '_overview.png')
        with open(quantStats, "rb") as f: webhook.add_file(file=f.read(), filename=file_name + '_quantstats.html')

        for types, path in logs_path.items():
            with open(path, "rb") as f: webhook.add_file(file=f.read(), filename=file_name + '.' + types)

        response = webhook.execute()
