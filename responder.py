#!/usr/bin/env python

import smtplib
import poplib
import re
import StringIO
import os
import sys

from bgmsettings import *

dayTemplate = '/Users/shadowbrain/Workspace/dayTemplate.txt'
nightTemplate = '/Users/shadowbrain/Workspace/nightTemplate.txt'

def sendMsg(toAddr, mSubject, mBody, fromAddr=gmailUser):
	""" Connects to gmail, auths, sends the message, and then disconnects 

		TODO: Wrap in email object, add less-ghetto debug. (maybe) add connection-persistance
	"""
	s = smtplib.SMTP("smtp.gmail.com",587)
	r = s.ehlo()[0]
#	print r # 250
	r = s.starttls()[0]
#	print r # 220
	r = s.ehlo()[0]
#	print r # 250
	r = s.login(gmailUser, gmailPass)[0]
#	print r # 235
	# This next bit probably shouldnt be hard-coded...	
	header = 'To:' + toAddr + '\n' + 'From: ' + fromAddr + '\n' + 'Subject:' + mSubject + ' \n'
	msg = header + mBody
	r = s.sendmail(gmailUser, toAddr, msg)
	# r should be {}
	s.close()

def processInbox(user=gmailUser, password=gmailPass, isDay=True):
	""" Log into a gmail account and process each message """
	p = poplib.POP3_SSL('pop.gmail.com', 995)
	p.user(user)
	p.pass_(password)
	for msg in range(len(p.list()[1])):
		dest = ""
		raw = p.retr(msg+1)[1]
		raw = '\n'.join(raw)
		# do some cleaning if its in html
		raw = re.sub('&lt:', '<', raw)
		raw = re.sub('&gt:', '>', raw)
		print raw
		content = re.search('To: mc.+', raw, re.DOTALL)
		if content:
			toLine = re.search('To: mc.+', raw).group(0)
			if re.search('<', toLine):
				dest = toLine.split('<')[1].split('>')[0]
			else:
				dest = toLine.split('To: ')[1]
		matchObject = re.search('ProspectID.+Source', raw, re.DOTALL)
		if matchObject:
			processed = matchObject.group(0)
#			fromLine = re.search('From:.+To', raw).group(0)
            fromLine = re.search('From:.\S+', raw).group(0)
			fromLine=re.sub('=20',' ',fromLine)
#			fromLine=re.sub('\|(To)?','',fromLine)
			print fromLine 
			if re.search('<', fromLine):
				toAddr = fromLine.split('<')[1].split('>')[0]
			else:
				toAddr = fromLine.split()[1]
			print toAddr
			# Do work here
			if isDay:
				message = parseLead(dest, processed, dayTemplate)
			else:
				message = parseLead(dest, processed, nightTemplate)
			sendMsg(toAddr, "Moore Cadillac Chantilly", message)
		else :
			processed = "**** XML NOT FOUND ****"
			processed += raw
#			print processed
		# do real stuff here
		#print processed 
		
	p.quit()

def parseLead(destAddr, crm, templateFile):
	input = open(templateFile)
	template = ""
	for s in input.xreadlines():
		template += s
#		template += "\n"
	fromLine = re.search('FirstName:.+', crm).group(0)
	firstName = fromLine.split('FirstName: ')[1]
	fromLine = re.search('LastName:.+', crm).group(0)
	lastName = fromLine.split('LastName: ')[1]
	customerName = ""
	customerName += firstName 
	customerName += " " 
	customerName += lastName
	template = template.replace("CUSTOMERNAME", customerName)
	salesEmail = destAddr
	template = template.replace("SALESEMAIL", salesMailDict[salesEmail])
	template = template.replace("SALESNAME", salesDict[salesEmail])
	return template

def main(isDaytime=True):
	processInbox(isDay=isDaytime)
	print "DONE"

if __name__ == '__main__':
	if len(sys.argv) == 2:
		if sys.argv[1] == 'day':
			main(True)
		else:
			print "trying night"
			main(False)
	main()

