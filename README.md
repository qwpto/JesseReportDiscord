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

Note that if the attachment files are too large for discord (8MB) they will be zipped into a zip archive. In case they are still too large the archive will be broken up into several uploads with the index _n for each file where n is incrementing. To recombine these for example in wondows download all the parts and then run:
	Downloads> COPY /B cb611e9b-458d-4450-a6c4-bfc19b194559_1.tvreport.html.zip + cb611e9b-458d-4450-a6c4-bfc19b194559_2.tvreport.html.zip test.zip

The library will break the upload up into several posts in case it can't all fit into one.

Users can add any number of additonal reports with a second argument passed as a map for example:
	JesseReportDiscord.sendJesseReportToDiscord('http://mydiscordgeneratedwebhook', {'tvreport.html':'relative/path/to/custom/report.html'})

Don't use the in built indexes which are 'json', 'html', 'tradingview', 'csv' unless you want to overwrite those.