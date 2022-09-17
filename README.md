# Jesse discord reporting library

Post the results of backtests to a discord channel using a webhook.

![example](https://github.com/qwpto/JesseReportDiscord/blob/release/example1.png?raw=true)

The library is published on pypi here: https://pypi.org/project/JesseReportDiscord/

So that to install you can run from a command line in your operating system:
```
pip install JesseReportDiscord
```
Update:
```
pip install JesseReportDiscord --upgrade
```

Once it's installed you just add the following lines to your Jesse strategy:
```python
import JesseReportDiscord

	def terminate(self):
		JesseReportDiscord.sendJesseReportToDiscord('https://discordapp.com/api/webhooks/your/generated/webhook')
```
Where https://discordapp.com/api/webhooks/your/generated/webhook is the url of the webhook you generate in the discord server's channel settings.


It publishes everything that you get after enabling all the options for your backtest (except debug logs) and a little more:
- strategy name, 
- routes, 
- hyperparameters, 
- git branch,
- git commit SHA,
- json report,
- csv report (dates updated to human readable),
- legacy chart, 
- quantstats report,
- tradingview pine editor script
- summary metrics

Note that if the attachment files are too large for discord (8MB) they will be zipped into a zip archive. In case they are still too large the archive will be broken up into several uploads with the index _n for each file where n is incrementing. To recombine these for example in wondows download all the parts and then run:
```
Downloads> COPY /B cb611e9b-458d-4450-a6c4-bfc19b194559_1.tvreport.html.zip + cb611e9b-458d-4450-a6c4-bfc19b194559_2.tvreport.html.zip test.zip
```

The library will break the upload up into several consecutive posts in case it can't all fit into one.

Users can add any number of additonal reports with a second argument passed as a map for example:
```python
JesseReportDiscord.sendJesseReportToDiscord('http://mydiscordgeneratedwebhook', {'tvreport.html':'relative/path/to/custom/report.html'})
```
Don't use the in built indexes which are 'json', 'html', 'tradingview', 'csv' unless you want to overwrite those.

Generation of data is controlled via the map config eg:
```python
myConfig = {'generate_json':True, generate_tradingview:False, generate_csv:False, generate_chart_overview:False, generate_quantstats_report:False, generate_version:False, generate_hyper_parameters:False, generate_portfolio_metrics:False, generate_study_name:False}
JesseReportDiscord.sendJesseReportToDiscord('http://mydiscordgeneratedwebhook',config=myConfig)
```
or for this example more briefly:
```python
myConfig = {'generate_json':True, 'generate_none':True}
JesseReportDiscord.sendJesseReportToDiscord('http://mydiscordgeneratedwebhook',config=myConfig)
```

Custom text can be posted with customMessage, so to only send a custom message to the channel:
```python
JesseReportDiscord.sendJesseReportToDiscord('http://mydiscordgeneratedwebhook', customMessage='hello', generation_config={'none':True} )
```


CHANGELOG
1.0.11, remove quantstats report for versions 0.39 and above due to new candle management changes in jesse 0.39.+
1.1.0, support live trading
1.2.0, added config to control which info is posted, and customMessage.
1.2.1, added timeouts to discord posts, and catching any exceptions to prevent disruptions to trading. Noted to be caused by discord rate limits.