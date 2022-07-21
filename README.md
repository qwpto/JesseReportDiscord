# Jesse discord reporting library

Post the results of backtests to a discord channel using a webhook

install with:
	pip install JesseReportDiscord

Add the following to your strategy:

	import JesseReportDiscord
	 
		def terminate(self):
			JesseReportDiscord.sendJesseReportToDiscord('http://mydiscordgeneratedwebhook')
