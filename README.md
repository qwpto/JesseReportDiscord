# Jesse discord reporting library

Post the results of backtests to a discord channel using a webhook

install with:
	pip install JesseReportDiscord

Add the following to your strategy:

	import JesseReportDiscord
	 
		def terminate(self):
			JesseReportDiscord.sendJesseReportToDiscord('http://mydiscordgeneratedwebhook')


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