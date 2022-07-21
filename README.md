# A sample Python project

Post the results of backtests to a discord channel using a webhook

Add the following to your strategy:

from jesse-report-discord import sendJesseReportToDiscord
 
	def terminate(self):
		sendJesseReportToDiscord('http://mydiscordgeneratedwebhook')
