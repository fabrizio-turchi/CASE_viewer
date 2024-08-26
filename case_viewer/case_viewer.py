import json
import codecs
import sys
from collections import deque
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
#import logging

class TableModel(QtCore.QAbstractTableModel):
	def __init__(self, data):
		super(TableModel, self).__init__()
		self._data = data

	def data(self, index, role):
		if role == Qt.DisplayRole:
			# See below for the nested-list data structure.
			# .row() indexes into the outer list,
			# .column() indexes into the sub-list
			return self._data[index.row()][index.column()]

	def rowCount(self, index):
		# The length of the outer list.
		return len(self._data)

	def columnCount(self, index):
		# The following takes the first sub-list, and returns
		# the length (only works if all rows are an equal length)
		return len(self._data[0])

class view(QWidget):
	def __init__(self, treeData, tableData):
		super(view, self).__init__()
		self.tree = QTreeView(self)

		self.table = QTableView(self)
		#self.table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
		#self.table.setWordWrap(True)        
		self.tableData = tableData
		self.treeData = treeData


		self.model = TableModel(tableData)
		self.table.setModel(self.model)

		self.table.headers = []


		grid = QGridLayout()
		grid.setSpacing(15)

		grid.addWidget(self.tree, 1, 0, 8, 10)
		grid.addWidget(self.table, 1, 3, 8, 8)

		self.setLayout(grid)

		self.model = QStandardItemModel()
		self.model.setHorizontalHeaderLabels(['Cyber item'])
		#self.tree.header().setDefaultSectionSize(180)
		self.tree.setModel(self.model)
		self.importData(self.treeData)
		self.tree.clicked.connect(self.itemSelectionChanged)
		self.tree.collapseAll()

	# Function to save populate treeview with a dictionary
	def importData(self, data, root=None):
		self.model.setRowCount(0)
		if root is None:
			root = self.model.invisibleRootItem()
		seen = {}   # List of  QStandardItem
		values = deque(data)
		while values:
			value = values.popleft()
			if value['unique_id'] == ':00000000':
				parent = root
			else:
				pid = value['parent_id']
				if pid not in seen:
					values.append(value)
					continue
				parent = seen[pid]
			unique_id = value['unique_id']
			parent.appendRow([
				QStandardItem(value['short_name']),
			])
			seen[unique_id] = parent.child(parent.rowCount() - 1)

	# Function to transverse treeview and derive tree_list
	def transverse_tree(self):
		tree_list = []
		for i in range(self.model.rowCount()):
			item = self.model.item(i)
			level = 0
			self.GetItem(item, level, tree_list)
		return tree_list

	def GetItem(self, item, level, tree_list):
		if item != None:
			if item.hasChildren():
				level = level + 1
				short_name = ' '
				height = ' '
				weight = ' '
				id = 0
				for i in range(item.rowCount()):
					id = id + 1
					for j in reversed([0, 1, 2]):
						childitem = item.child(i, j)
						if childitem != None:
							if j == 0:
								short_name = childitem.data(0)
							else:
								short_name = short_name
							if j == 1:
								height = childitem.data(0)
							else:
								height = height
							if j == 2:
								weight = childitem.data(0)
							else:
								weight = weight

							if j == 0:
								dic = {}
								dic['level'] = level
								dic['id'] = id
								dic['short_name'] = short_name
								tree_list.append(dic)
							self.GetItem(childitem, level, tree_list)
				return tree_list



	def buildTableData(self, idObject):
		self.headers = []
		tData = self.buildDataChatMessages(idObject)
		if len(tData) == 0:
			tData = self.buildDataPhoneCalls(idObject)
		if len(tData) == 0:
			tData = self.buildDataCalendars(idObject)
		if len(tData) == 0:
			tData = self.buildDataBluetooths(idObject)
		if len(tData) == 0:
			tData = self.buildDataSms(idObject)
		if len(tData) == 0:
			tData = self.buildDataContacts(idObject)
		if len(tData) == 0:
			tData = self.buildDataCellSites(idObject)
		if len(tData) == 0:
			tData = self.buildDataWirelessNet(idObject)
		if len(tData) == 0:
			tData = self.buildDataSearchedItems(idObject)
		if len(tData) == 0:
			tData = self.buildDataSocialMediaActivities(idObject)
		if len(tData) == 0:
			tData = self.buildDataEvents(idObject)
		if len(tData) == 0:
			tData = self.buildDataCookies(idObject)
		if len(tData) == 0:
			tData = self.buildDataEmailMessages(idObject)
		if len(tData) == 0:
			tData = self.buildDataFiles(idObject)
		if len(tData) == 0:
			tData = self.buildDataWebBookmarks(idObject)
		if len(tData) == 0:
			tData = self.buildDataWebHistories(idObject)
		if len(tData) == 0:
			tData = self.buildDataLocationDevice(idObject)

		return tData


	def buildDataChatMessages(self, idObject):

		tData = []
		threadFound = False
		threadSlot = []

		for t in chatThreads:
			if t["@id"] == idObject:
				threadFound = True
				threadSlot = t["thread:messages"]
				break

		if not threadFound:
			print('Thread not found')
			return tData
		#print(f"threadSlot=\n{threadSlot}")
		self.headers = ["From", "To", "Date", "Text", "Type", "Attachments"]
		for idMsg in threadSlot:
			for m in chatMessages:
				if idMsg == m["@id"]:
					msgFrom = m["uco-observable:from"]
					msgTo = m["uco-observable:to"]
					msgDate = m["uco-observable:sentTime"]
					msgText = m["uco-observable:messageText"]
					msgType = m["uco-observable:messageType"]
					msgAttachments = m["uco-observable:attachedFiles"]


					tData.append([msgFrom, msgTo, msgDate, msgText, msgType, msgAttachments])

		return tData

	def buildDataContacts(self, idObject):
		tData = []

		if idObject == ':Accounts':
			self.headers = ["Identifier", "Phone", "Application", "Name"]

			for a in accounts:
				accountIdentifier = a["uco-observable:accountIdentifier"]
				accountPhone = a["uco-observable:phoneAccount"]
				accountName = a["uco-observable:displayName"]
				applicationName = a["uco-observable:application"]
				tData.append([accountIdentifier, accountPhone, applicationName, accountName])

		return tData

	def buildDataBluetooths(self, idObject):
		tData = []

		if idObject != ':Bluetooths':
			print('Bluetooth not found')
			return tData
		else:
			self.headers = ["Address"]
			for bt in bluetooths:
				btAddress = bt["uco-observable:addressValue"]
				#btName = bt["uco-core:name"]
				tData.append([btAddress])

		return tData

	def buildDataCalendars(self, idObject):
		tData = []

		if idObject != ':Calendars':
			print('Calendar not found')
			return tData
		else:
			self.headers = ["Subject", "Repeat", "Start time", "End time", "Status"]
			for c in calendars:
				calendarSubject = c["uco-observable:subject"]
				calendarRepeatInterval = c["uco-observable:repeatInterval"]
				calendarStartDate = c["uco-observable:startTime"]
				calendarEndDate = c["uco-observable:endTime"]
				calendarStatus = c["uco-observable:eventStatus"]
				tData.append([calendarSubject, calendarRepeatInterval, calendarStartDate, calendarEndDate, calendarStatus])

		return tData

	def buildDataPhoneCalls(self, idObject):

		tData = []

		if idObject != ':Calls':
			print('Thread not found')
			return tData
		else:
			self.headers = ["From", "To", "Application", "Date", "Duration"]
			print("phoneCall LEN: " + str(len(phoneCalls)))
			for c in phoneCalls:
				callDate = c["uco-observable:startTime"]
				callDuration = c["uco-observable:duration"]
				#callType = c["uco-observable:callType"]
				#callOutcome = c["uco-observable:proposed:outcome"]
				callApplication = c["uco-core:name"]
				callFrom = c["uco-observable:from"]
				callTo = c["uco-observable:to"]
				tData.append([callFrom, callTo, callApplication, callDate, callDuration])

			return tData


	def buildDataCellSites(self, idObject):
		tData = []

		if idObject == ':CellSites':
			self.headers = ["MCC", "MNC", "LAC", "CID"]
			for c in cell_sites:
				cellMCC = c["uco-observable:cellSiteCountryCode"]
				cellMNC = c["uco-observable:cellSiteNetworkCode"]
				cellLAC = c["uco-observable:cellSiteLocationAreaCode"]
				cellCID = c["uco-observable:cellSiteIdentifier"]
				#cellLocation = c["uco-observable:location"]
				#tData.append([cellMCC, cellMNC, cellLAC, cellCID, cellLocation])
				tData.append([cellMCC, cellMNC, cellLAC, cellCID])

		return tData

	def buildDataWirelessNet(self, idObject):
		tData = []

		if idObject == ':WirelessNet':
			#self.headers = ["SSID", "BSID", "MAC address", "Accuracy", "Time connection", "Location"]
			self.headers = ["SSID", "BSID"]
			for w in wireless_net:
				wirelessSsid = w["uco-observable:ssid"]
				wirelessBsid = w["uco-observable:baseStation"]
				#wirelessMac = w["uco-observable:macAddress"]
				#wirelessAccuracy = w["uco-observable:accuracy"]
				#wirelessTime = w["not-in-ontology:timeConnection"]
				#wirelessLocation = w["uco-observable:location"]

				tData.append([wirelessSsid, wirelessBsid])

		return tData

	def buildDataSearchedItems(self, idObject):
		tData = []

		if idObject == ':SearchedItems':
			self.headers = ["Source", "Launched time", "Value"]
			for s in searched_items:
				searchedSource = s["drafting:searchSource"]
				searchedTime = s["drafting:searchLaunchedTime"]
				searchedValue = s["drafting:searchValue"]

				tData.append([searchedSource, searchedTime, searchedValue])

		return tData

	def buildDataSocialMediaActivities(self, idObject):
		tData = []

		if idObject == ':SocialMediaActivities':
			self.headers = ["Body", "Title", "Date", "App", "Author Identifier", "Name", "Type", "Account identifier"]
			for s in social_media_activities:
				socialBody = s["uco-observable:body"]
				socialTitle = s["uco-observable:pageTitle"]
				socialDate = s["uco-observable:observableCreatedTime"]
				socialApp = s["uco-observable:application"]
				socialAuthorId = s["drafting:authorIdentifier"]
				socialAccountId = s["uco-observable:accountIdentifier"]
				socialName = s["drafting:authorName"]
				socialType = s["drafting:activityType"]

				tData.append([socialBody, socialTitle, socialDate, socialApp, socialAuthorId, 
							  socialName, socialType, socialAccountId])

		return tData

	def buildDataEvents(self, idObject):
		tData = []

		if idObject == ':Events':
			self.headers = ["Date Time", "Type", "Text"]
			for e in events:
				eCreated = e["uco-observable:observableCreatedTime"]
				eType = e["uco-observable:eventType"]
				eText = e["uco-observable:eventText"]

				tData.append([eCreated, eType, eText])

		return tData

	def buildDataCookies(self, idObject):
		tData = []

		if idObject == ':Cookies':
			self.headers = ["Name", "Path", "Created time", "Expiration time"]
			for c in cookies:
				cookieName = c["uco-observable:cookieName"]
				cookiePath = c["uco-observable:cookiePath"]
				cookieCreatedTime = c["uco-observable:observableCreatedTime"]
				cookieExpirationTime = c["uco-observable:expirationTime"]

				tData.append([cookieName, cookiePath, cookieCreatedTime, cookieExpirationTime])

		return tData



	def buildDataEmailMessages(self, idObject):
		#print('in buildDataEmailMessages')
		tData = []

		if idObject == ':EmailMessages':
			self.headers = ["From", "To", "Date", "Subject", "Body", "Status"]
			for e in emailMessages:
				emailSubject = e["uco-observable:subject"]
				emailBody = e["uco-observable:body"]
				emailDate = e["uco-observable:sentTime"]
				emailStatus = e["uco-observable:allocationStatus"]
				emailFrom = e["uco-observable:from"]
				emailTo = e["uco-observable:to"]

				tData.append([emailFrom, emailTo, emailDate, emailSubject, emailBody, emailStatus])

		return tData

	def buildDataFiles(self, idObject):

		tData = []

		print(f"in buildDataFiles, idObject={idObject}")
		if idObject == ':Images':
			self.headers = ["Type", "Name", "Path", "Size"]
			for f in filesImage:
				fileType = f["uco-core:tag"]
				fileName = f["uco-observable:fileName"]
				filePath = f["uco-observable:filePath"]
				fileSize = f["uco-observable:fileSize"]

				tData.append([fileType, fileName, filePath, fileSize])

		if idObject == ':Texts':
			self.headers = ["Type", "Name", "Path", "Size"]
			for f in filesText:
				fileType = f["uco-core:tag"]
				fileName = f["uco-observable:fileName"]
				filePath = f["uco-observable:filePath"]
				fileSize = f["uco-observable:fileSize"]

				tData.append([fileType, fileName, filePath, fileSize])

		if idObject == ':PDFs':
			self.headers = ["Type", "Name", "Path", "Size"]
			for f in filesPDF:
				fileType = f["uco-core:tag"]
				fileName = f["uco-observable:fileName"]
				filePath = f["uco-observable:filePath"]
				fileSize = f["uco-observable:fileSize"]

				tData.append([fileType, fileName, filePath, fileSize])

		if idObject == ':Words':
			self.headers = ["Type", "Name", "Path", "Size"]
			for f in filesWord:
				fileType = f["uco-core:tag"]
				fileName = f["uco-observable:fileName"]
				filePath = f["uco-observable:filePath"]
				fileSize = f["uco-observable:fileSize"]

				tData.append([fileType, fileName, filePath, fileSize])

		if idObject == ':RTFs':
			self.headers = ["Type", "Name", "Path", "Size"]
			for f in filesRTF:
				fileType = f["uco-core:tag"]
				fileName = f["uco-observable:fileName"]
				filePath = f["uco-observable:filePath"]
				fileSize = f["uco-observable:fileSize"]

				tData.append([fileType, fileName, filePath, fileSize])

		if idObject == ':Audios':
			self.headers = ["Type", "Name", "Path", "Size"]
			for f in filesAudio:
				fileType = f["uco-core:tag"]
				fileName = f["uco-observable:fileName"]
				filePath = f["uco-observable:filePath"]
				fileSize = f["uco-observable:fileSize"]

				tData.append([fileType, fileName, filePath, fileSize])

		if idObject == ':Videos':
			self.headers = ["Type", "Name", "Path", "Size"]
			for f in filesVideo:
				fileType = f["uco-core:tag"]
				fileName = f["uco-observable:fileName"]
				filePath = f["uco-observable:filePath"]
				fileSize = f["uco-observable:fileSize"]

				tData.append([fileType, fileName, filePath, fileSize])

		if idObject == ':Archives':
			self.headers = ["Type", "Name", "Path", "Size"]
			for f in filesArchive:
				fileType = f["uco-core:tag"]
				fileName = f["uco-observable:fileName"]
				filePath = f["uco-observable:filePath"]
				fileSize = f["uco-observable:fileSize"]

				tData.append([fileType, fileName, filePath, fileSize])

		if idObject == ':Databases':
			self.headers = ["Type", "Name", "Path", "Size"]
			for f in filesDatabase:
				fileType = f["uco-core:tag"]
				fileName = f["uco-observable:fileName"]
				filePath = f["uco-observable:filePath"]
				fileSize = f["uco-observable:fileSize"]

				tData.append([fileType, fileName, filePath, fileSize])

		if idObject == ':Applications':
			self.headers = ["Type", "Name", "Path", "Size"]
			for f in filesApplication:
				fileType = f["uco-core:tag"]
				fileName = f["uco-observable:fileName"]
				filePath = f["uco-observable:filePath"]
				fileSize = f["uco-observable:fileSize"]

				tData.append([fileType, fileName, filePath, fileSize])

		if idObject == ':Uncategorized':
			self.headers = ["Type", "Name", "Path", "Size"]
			for f in filesUncategorized:
				fileType = f["uco-core:tag"]
				fileName = f["uco-observable:fileName"]
				filePath = f["uco-observable:filePath"]
				fileSize = f["uco-observable:fileSize"]

				tData.append([fileType, fileName, filePath, fileSize])

		return tData


	def buildDataSms(self, idObject):
		#print('in buildDataSms')
		tData = []

		if idObject == ':Sms':
			self.headers = ["From", "To", "Date", "Text", "Status"]
			for m in smsMessages:
				smsText = m["uco-observable:messageText"]
				#smsApp = m["uco-observable:application"]
				smsSentTime = m["uco-observable:sentTime"]
				smsStatus = m["uco-observable:allocationStatus"]
				smsFrom = m["uco-observable:from"]
				smsTo = m["uco-observable:to"]

				tData.append([smsFrom, smsTo, smsSentTime, smsText, smsStatus])

		return tData

	def buildDataWebBookmarks(self, idObject):
		tData = []

		if idObject == ':WebBookmarks':
			self.headers = ["Url", "App", "Path", "Crteated date"]
			for w in webBookmark:
				webUrl = w["uco-observable:urlTargeted"]
				webApp = w["uco-observable:application"]
				webPath = w["uco-observable:bookmarkPath"]
				webDate = w["uco-observable:observableCreatedTime"]
				tData.append([webUrl, webApp, webPath, webDate])

		return tData

	def buildDataWebHistories(self, idObject):
		tData = []
		#wbeUrl = ''
		webApp = ''

		if idObject == ':WebHistories':
			self.headers = ["Url", "Title", "Last visited", "App"]
			for w in webURLHistory:
				webUrl = w["uco-observable:url"]
				webTitle = w["uco-observable:title"]
				webLastVisited = w["uco-observable:lastVisited"]
				webApp = w["uco-observable:browserInformation"]

				tData.append([webUrl, webTitle, webLastVisited, webApp])

		return tData

	def buildDataLocationDevice(self, idObject):
		tData = []


		if idObject == ':LocationDevice':
			self.headers = ["Start date", "Latitude", "Longitude"]
			for l in relationMappedBy:
				lDate = l["uco-observable:mappedByStartDate"]
				lLat = l["uco-observable:mappedByLatitude"]
				lLong = l["uco-observable:mappedByLongitude"]

				tData.append([lDate, lLat, lLong])

		return tData



	def itemSelectionChanged(self, index):
		text = index.data(Qt.DisplayRole)
		threadId = ''

		for i, dic in enumerate(treeData):
			if dic['short_name'] == text:
				#print('text: ' + text + ', selected thread id: ' + str(treeData[i]['unique_id']))
				threadId = treeData[i]['unique_id']
				break

		if threadId == '':
			print('Thread id not found')
		else:
			print(f'Thread id={threadId}')
			self.tableData = self.buildTableData(threadId)
			self.tableData.insert(0, self.headers)

		self.model = TableModel(self.tableData)

		self.table.setModel(self.model)

		#self.table.resizeRowsToContents();

		#self.table.resizeColumnsToContents()


def get_attribute(data, property, default_value):
	return data.get(property) or default_value

def processAttachments():
	for item in chatMessages:
		for attachment in relationAttachmentsTo:
			if item["@id"] == attachment["uco-observable:attachmentTarget"]:
				fileAttached = ''
				for f in filesImage:
					if f["@id"] == attachment["uco-observable:attachmentSource"]:
						fileAttached += f["uco-observable:fileName"] + ';'
						break
				for f in filesVideo:
					if f["@id"] == attachment["uco-observable:attachmentSource"]:
						fileAttached += f["uco-observable:fileName"] + ';'
						break
				for f in filesAudio:
					if f["@id"] == attachment["uco-observable:attachmentSource"]:
						fileAttached += f["uco-observable:fileName"] + ';'
						break
				item["uco-observable:attachedFiles"] = fileAttached

def processRelationAttachments(jsonObj):
	id_attachment_source = jsonObj["uco-core:source"]["@id"]
	id_attachment_target = jsonObj["uco-core:target"]["@id"]

	try:
		relationAttachmentsTo.append(
			{
				"uco-observable:attachmentSource":id_attachment_source,
				"uco-observable:attachmentTarget":id_attachment_target
			})
	except Exception as e:
		print("ERROR: in appending dictionary to chatMessages")
		print (e)

def processRelationConnectedTo(jsonObj):
	id_connected_source = jsonObj["uco-core:source"]["@id"]
	id_connected_target = jsonObj["uco-core:target"]["@id"]

	startTime = ""
	if jsonObj.get("uco-observable:startTime", None):
		startTime = jsonObj["uco-observable:startTime"]["@value"]
	endTime = ""
	if jsonObj.get("uco-observable:endTime", None):
		endTime = jsonObj["uco-observable:endTime"]["@value"]

	try:
		relationConnectedTo.append(
			{
				"uco-core:source":id_connected_source,
				"uco-core:target":id_connected_target,
				"uco-observable:starTime": startTime,
				"uco-observable:endTime": endTime
			})
	except Exception as e:
		print("ERROR: in appending dictionary to chatMessages")
		print (e)

def processRelationMappedBy(jsonObj):
	id_mapped_by_target = jsonObj["uco-core:target"]["@id"]
	latitude_mapped_by = ''
	longitude_mapped_by = ''
	#category = ''

	for c in geo_coordinates:
		if c["@id"] == id_mapped_by_target:
			latitude_mapped_by = c["uco-location:latitude"]
			longitude_mapped_by = c["uco-location:longitude"]
			break

	start_date = jsonObj.get("uco-observable:startTime", None)
	if start_date:
		start_date = jsonObj["uco-observable:startTime"]["@value"]

	try:
		relationMappedBy.append(
			{
				"uco-observable:mappedByLatitude":latitude_mapped_by,
				"uco-observable:mappedByLongitude":longitude_mapped_by,
				"uco-observable:mappedByStartDate":start_date
				#"not-in-ontology:locationType":category

			})
	except Exception as e:
		print("ERROR: in appending dictionary to Relation Mapped_By")
		print (e)

def processMessage(uuid_object=None, facet=None):
	msg_text = facet.get("uco-observable:messageText", None)
	msg_app_id = facet.get("uco-observable:application", None)
	msg_app = "X"
	if msg_app_id:
		msg_app_id = facet["uco-observable:application"]["@id"]
		for a in applications:
			if a["@id"] == msg_app_id:
				msg_app = a["uco-core:name"]
				break

	msg_sent_time = facet.get("uco-observable:sentTime", None)

	if msg_sent_time:
		msg_sent_time = facet["uco-observable:sentTime"]["@value"]

	msg_from = facet.get("uco-observable:from", None)

	if not msg_from:
		msg_from_id = facet["uco-observable:from"]["@id"]
	else:
		msg_from_id = "X"

	msg_to = facet.get("uco-observable:to", None)

	msg_to_id = []
	if not msg_to:
		for item in facet["uco-observable:to"]:
			msg_to_id.append(item["@id"])

	msg_type = facet.get("uco-observable:messageType", None)
	msg_from = ''
	for a in accounts:
		if a["@id"] == msg_from_id:
			msg_from = a["uco-observable:phoneAccount"] + " " + \
				a["uco-observable:accountIdentifier"] + " / " + a["uco-observable:displayName"]
			break

	msg_to = ''
	for item in msg_to_id:
		for a in accounts:
			if a["@id"] == item:
				msg_to += a["uco-observable:phoneAccount"] + " " + \
					a["uco-observable:accountIdentifier"] + " / " + a["uco-observable:displayName"]
				break
	try:
		if facet["uco-observable:messageType"] == "SMS/Native Message":
			smsMessages.append(
				{
					"@id":uuid_object,
					"uco-observable:messageText":msg_text,
					"uco-observable:messageTypte":msg_type,
					"uco-observable:application":'Native',
					"uco-observable:sentTime": msg_sent_time,
					"uco-observable:from":msg_from,
					"uco-observable:to":msg_to,
					"uco-observable:messageType":'SMS/Native Message'
				})
		else:
			chatMessages.append(
				{
					"@id":uuid_object,
					"uco-observable:messageText":msg_text,
					"uco-observable:application":msg_app,
					"uco-observable:sentTime": msg_sent_time,
					"uco-observable:from":msg_from,
					"uco-observable:to":msg_to,
					"uco-observable:attachedFiles": "",
					"uco-observable:messageType":'CHAT Message'
				}
			)
	except Exception as e:
		print("ERROR: in appending dictionary to either ChatMessages or SMSmessages")
		print (e)

def processThread(uuid_object=None, facet=None):
	#threadName = facet.get("uco-observable:displayName", "-")
	thread_participants = list()
	for p in facet["uco-observable:participant"]:
		thread_participants.append(p["@id"])

	thread_len = facet["uco-observable:messageThread"]["co:size"]["@value"]
	thread_messages = list()
	for m in facet["uco-observable:messageThread"]["co:element"]:
		thread_messages.append(m["@id"])

	try:
		chatThreads.append(
			{
				"@id":uuid_object,
				"thread:length": thread_len,
				"thread:messages":thread_messages,
				"thread:participants": thread_participants
			})
	except Exception as e:
		print("ERROR: in appending dictionary to chatThreads, @id=" + threadId)
		print (e)

def processAccount(uuid_object=None, facet=None, kind=None):	
	accountFound = False
	accountPhoneNumber = ""
	accountIdentifier = ""
	accountApplication = ""
	accountName = ""

	if kind == "AccountFacet":
		accountIdentifier = facet.get("uco-observable:accountIdentifier", "-")
		for a in accounts:
			if a["@id"] == uuid_object:
				a["uco-observable:accountIdentifier"] = accountIdentifier
				accountFound = True
				break
	elif kind == "ApplicationAccountFacet":
		idApp = facet["uco-observable:application"]["@id"]
		for app in applications:
			if app["@id"] == idApp:
				accountApplication = app["uco-core:name"]
		for a in accounts:
			if a["@id"] == uuid_object:
				a["uco-observable:application"] = accountApplication
				accountFound = True
				break
	elif kind == "PhoneAccountFacet":
		accountPhoneNumber = facet.get("uco-observable:phoneNumber", "-")
		accountName = facet.get("uco-observable:accountIdentifier", "-")
		for a in accounts:
			if a["@id"] == uuid_object:
				a["uco-observable:phoneAccount"] = accountPhoneNumber
				a["uco-observable:displayName"] = accountName
				accountFound = True
				break
	elif kind == "DigitalAccountFacet":
		accountName = facet.get("uco-observable:displayName", "-")
		for a in accounts:
			if a["@id"] == uuid_object:
				a["uco-observable:displayName"] = accountName
				accountFound = True
				break

	if not accountFound:
		try:
			accounts.append(
				{
					"@id":uuid_object,
					"uco-observable:accountIdentifier": accountIdentifier,
					"uco-observable:phoneAccount":accountPhoneNumber,
					"uco-observable:application":accountApplication,
					  "uco-observable:displayName": accountName
				}
			)


		except Exception as e:
			print("ERROR: in appending dictionary to accounts")
			print (e)

def processEmailAddress(uuid_object=None, facet=None):
	accountEmail = facet.get("uco-observable:addressValue", "-")
	try:
		emailAddresses.append(
			{
				"@id":uuid_object,
				"uco-observable:addressValue": accountEmail
			})

	except Exception as e:
		print("ERROR: in appending dictionary to emailAddresses")
		print (e)


def processEmailAccount(uuid_object=None, facet=None):
	accountEmailId = facet["uco-observable:emailAddress"]["@id"]

	addressEmail = "-"
	for e in emailAddresses:
		if e["@id"] == accountEmailId:
			addressEmail = e["uco-observable:addressValue"]
	try:
		emailAccounts.append(
			{
				"@id":uuid_object,
				"uco-observable:addressValue": addressEmail
			})

	except Exception as e:
		print("ERROR: in appending dictionary to emailAddresses")
		print (e)

def processBluetooth(uuid_object=None, facet=None):
	bt_address = facet.get("uco-observable:addressValue", "-")
	#btName = facet.get("uco-core:name", "-")

	try:
		bluetooths.append(
			{
				"@id":uuid_object,
				"uco-observable:addressValue": bt_address,
				#"uco-core:name": btName
			})

	except Exception as e:
		print("ERROR: in appending dictionary to Bluetooth Connecitons")
		print (e)

def processCellSite(uuid_object=None, facet=None):
	cellMcc = facet.get("uco-observable:cellSiteCountryCode", "-")
	cellCid = facet.get("uco-observable:cellSiteIdentifier", "-")
	cellLac = facet.get("uco-observable:cellSiteLocationAreaCode", "-")
	cellMnc = facet.get("uco-observable:cellSiteNetworkCode", "-")
	try:
		cell_sites.append(
			{
				"@id":uuid_object,
				"uco-observable:cellSiteCountryCode": cellMcc,
				"uco-observable:cellSiteIdentifier": cellCid,
				"uco-observable:cellSiteNetworkCode": cellMnc,
				"uco-observable:cellSiteLocationAreaCode": cellLac,
			})

	except Exception as e:
		print("ERROR: in appending dictionary to Cell Site")
		print (e)

def processEvents(jsonObj, facet):
	eventId = jsonObj["@id"]
	eventCreated = get_attribute(facet, "uco-observable:observableCreatedTime", None)
	if eventCreated:
		eventCreated = facet["uco-observable:observableCreatedTime"]["@value"]

	eventType = get_attribute(facet, "uco-observable:eventType", "-")
	eventText = get_attribute(facet, "uco-observable:eventText", "-")

	try:
		events.append(
			{
				"@id":eventId,
				"uco-observable:observableCreatedTime": eventCreated,
				"uco-observable:eventType": eventType,
				"uco-observable:eventText": eventText
			})

	except Exception as e:
		print("ERROR: in appending dictionary to Event Record")
		print (e)

def processSearchedItems(jsonObj, facet):
	searchId = jsonObj["@id"]
	searchApp = get_attribute(facet, "uco-observable:application", "-")

	if searchApp != '-':
		searchAppId = facet["uco-observable:application"]["@id"]
		for a in applications:
			if a["@id"] == searchAppId:
				searchApp = a["uco-core:name"]
				break

	searchLaunchTime = get_attribute(facet, "drafting:searchLaunchedTime", EMPTY_DATA)
	if searchLaunchTime != EMPTY_DATA:
		searchLaunchTime = facet["drafting:searchLaunchedTime"]["@value"]
	searchValue = get_attribute(facet, "drafting:searchValue", "-")

	try:
		searched_items.append(
			{
				"@id":searchId,
				"drafting:searchSource": searchApp,
				"drafting:searchLaunchedTime": searchLaunchTime,
				"drafting:searchValue": searchValue
			})

	except Exception as e:
		print("ERROR: in appending dictionary to SearchedItems")
		print (e)

def processSocialMediaActivities(jsonObj, facet):
	socialId = jsonObj["@id"]
	socialBody = get_attribute(facet, "uco-observable:body", "-")
	socialTitle = get_attribute(facet, "uco-observable:pageTitle", "-")

	socialDate = get_attribute(facet, "uco-observable:observableCreatedTime", EMPTY_DATA)
	if socialDate != EMPTY_DATA:
		socialDate = facet["uco-observable:observableCreatedTime"]["@value"]

	socialAppId = facet["uco-observable:application"]["@id"]
	socialApp = ''

	for a in applications:
		if a["@id"] == socialAppId:
			socialApp = a["uco-core:name"]
			break

	socialAuthorId = get_attribute(facet, "drafting:authorIdentifier", "-")
	socialAccountId = get_attribute(facet, "uco-observable:accountIdentifier", "-")
	socialName = get_attribute(facet, "drafting:authorName", "-")
	socialType = get_attribute(facet, "drafting:activityType", "-")

	try:
		social_media_activities.append(
			{
				"@id":socialId,
				"uco-observable:body":socialBody,
				"uco-observable:pageTitle":socialTitle,
				"uco-observable:observableCreatedTime": socialDate,
				"uco-observable:application": socialApp,
			"drafting:authorIdentifier": socialAuthorId,
		"uco-observable:accountIdentifier": socialAccountId,
		"drafting:authorName": socialName,
		"drafting:activityType": socialType
			})

	except Exception as e:
		print("ERROR: in appending dictionary to Social Media Activity")
		print (e)

def processWirelessNetwork(jsonObj, facet):
	wId = jsonObj["@id"]
	wSsid = get_attribute(facet, "uco-observable:ssid", '')
	wBssid = get_attribute(facet, "uco-observable:baseStation", '')
	#wMac = get_attribute(facet, "not-in-ontology:macAddress", '')
	#wAccuracy = get_attribute(facet, "uco-observable:accuracy", '')
	#wTime = get_attribute(facet, "not-in-ontology:timeConnection", EMPTY_DATA)

	try:
		wireless_net.append(
			{
				"@id":wId,
				"uco-observable:ssid": wSsid,
				"uco-observable:baseStation": wBssid,
			})

	except Exception as e:
		print("ERROR: in appending dictionary to Wireless Network")
		print (e)

def processCookie(uuid_object=None, facet=None):
	cookieName = get_attribute(facet, "uco-observable:cookieName", None)
	cookiePath = get_attribute(facet, "uco-observable:cookiePath", None)
	cookieCreatedTime = get_attribute(facet, "uco-observable:observableCreatedTime", None)
	if cookieCreatedTime:
		cookieCreatedTime = facet["uco-observable:observableCreatedTime"]["@value"]

	cookieLastAccessedTime = get_attribute(facet, "uco-observable:accessedTime", None)
	if cookieLastAccessedTime:
		cookieLastAccessedTime = facet["uco-observable:accessedTime"]["@value"]

	cookieExpirationTime = get_attribute(facet, "uco-observable:expirationTime", None)
	if cookieExpirationTime:
		cookieExpirationTime = facet["uco-observable:expirationTime"]["@value"]

	try:
		cookies.append(
			{
				"@id":uuid_object,
				"uco-observable:cookieName": cookieName,
				"uco-observable:cookiePath": cookiePath,
				"uco-observable:observableCreatedTime": cookieCreatedTime,
				"uco-observable:accessedTime": cookieLastAccessedTime,
				"uco-observable:expirationTime": cookieExpirationTime
			})

	except Exception as e:
		print("ERROR: in appending dictionary to cookies")
		print (e)

def processCoordinate(uuid_object=None, facet=None):
	coordinateLat = get_attribute(facet, "uco-location:latitude", None)
	if coordinateLat:
		coordinateLat = facet["uco-location:latitude"]["@value"]

	coordinateLong = get_attribute(facet, "uco-location:longitude", None)
	if coordinateLong:
		coordinateLong = facet["uco-location:longitude"]["@value"]

	coordinateAlt = get_attribute(facet, "uco-location:altitude", None)
	if coordinateAlt:
		coordinateAlt = facet["uco-location:altitude"]["@value"]

	try:
		geo_coordinates.append(
			{
				"@id":uuid_object,
				"uco-location:latitude": coordinateLat,
				"uco-location:longitude": coordinateLong,
				"uco-location:altitude": coordinateAlt
			})

	except Exception as e:
		print("ERROR: in appending dictionary to geo coordinate")
		print (e)

def processApplication(uuid_object=None, facet=None):
	applicationName = get_attribute(facet, "uco-core:name", "-")

	try:
		applications.append(
			{
				"@id":uuid_object,
				"uco-core:name": applicationName
			})

	except Exception as e:
		print("ERROR: in appending dictionary to applications")
		print (e)

def processCall(uuid_object=None, facet=None):
	callId = jsonObj["@id"]
	callFromId = facet["uco-observable:from"].get("@id", None)
	if callFromId:
		callFrom = "-"
		for a in accounts:
			if a["@id"] == callFromId:
				callFrom = a["uco-observable:phoneAccount"] + " / " + \
					a["uco-observable:accountIdentifier"]

				break
	callToId = get_attribute(facet["uco-observable:to"], "@id", None)
	if callToId:
		callTo = "-"
		for a in accounts:
			if a["@id"] == callToId:
				callTo = a["uco-observable:phoneAccount"] + " / " + \
					a["uco-observable:accountIdentifier"]
				break

	callApplication = "-"
	callApplicationId = facet["uco-observable:application"].get("@id", None)
	if callApplicationId:
		for a in applications:
			if a["@id"] == callApplicationId:
				callApplication = a["uco-core:name"]

	callStartTime = facet.get("uco-observable:startTime", None)
	if callStartTime:
		callStartTime = facet["uco-observable:startTime"]["@value"]

	callDuration = get_attribute(facet, "uco-observable:duration", "-")
	if callDuration != "-":
		callDuration = facet["uco-observable:duration"]["@value"]
	callStatus = get_attribute(facet, "uco-observable:allocationStatus", "-")
	try:
		phoneCalls.append(
			{
				"@id":callId,
				"uco-observable:from":callFrom,
				"uco-observable:to":callTo,
				"uco-core:name":callApplication,
				"uco-observable:startTime":callStartTime,
			  "uco-observable:duration":callDuration,
			})
	except Exception as e:
		print("ERROR: in appending dictionary to Call")
		print (e)

def processCalendar(uuid_object=None, facet=None):
	calendarSubject = facet.get("uco-observable:subject", "-")
	calendarRepeatInterval = facet.get("uco-observable:recurrence", "-")
	calendarStatus = facet.get("uco-observable:eventStatus", "-")
	calendarStartTime = facet.get("uco-observable:startTime", None)
	if calendarStartTime:
		calendarStartTime = facet["uco-observable:startTime"]["@value"]

	calendarEndTime = facet.get("uco-observable:endTime", None)
	if calendarEndTime:
		calendarEndTime = facet["uco-observable:endTime"]["@value"]

	try:
		calendars.append(
			{
				"@id":uuid_object,
				"uco-observable:subject":calendarSubject,
				"uco-observable:startTime":calendarStartTime,
			  "uco-observable:endTime":calendarEndTime,
			  "drafting:repeatInterval":calendarRepeatInterval,
			  "uco-observable:eventStatus":calendarStatus
			})
	except Exception as e:
		print("ERROR: in appending dictionary to Calendar")
		print (e)

def processEmailMessage(jsonObj, facet):
	emailId = jsonObj["@id"]
	emailSentTime = get_attribute(facet, "uco-observable:sentTime", EMPTY_DATA)
	if emailSentTime != EMPTY_DATA:
		emailSentTime = facet["uco-observable:sentTime"]["@value"]

	emailFromId = facet["uco-observable:from"]["@id"]
	emailFrom = ""
	emailTo = ""

	for e in emailAccounts:
		if e["@id"] == emailFromId:
			emailFrom = e["uco-observable:addressValue"]

	if len(facet["uco-observable:to"]) > 0:
		emailToId = facet["uco-observable:to"][0]["@id"]
		for e in emailAccounts:
			if e["@id"] == emailToId:
				emailTo = e["uco-observable:addressValue"]

	emailCc = get_attribute(facet, "uco-observable:cc", "-")
	emailBcc = get_attribute(facet, "uco-observable:bcc", "-")
	emailBody = get_attribute(facet, "uco-observable:body", "-")
	if emailBody != "-":
		emailBody = emailBody[0:100] + "..."

	emailSubject = get_attribute(facet, "uco-observable:subject", "-")
	emailStatus = get_attribute(facet, "uco-observable:allocationStatus", "-")

	try:
		emailMessages.append(
			{
				"@id":emailId,
				"uco-observable:from":emailFrom,
				"uco-observable:to":emailTo,
				"uco-observable:cc":emailCc,
				"uco-observable:bcc":emailBcc,
			"uco-observable:sentTime":emailSentTime,
			"uco-observable:body":emailBody,
			"uco-observable:subject":emailSubject,
			"uco-observable:allocationStatus":emailStatus,
			})

	except Exception as e:
		print("ERROR: in appending dictionary to emailMessage")
		print (e)

def processFile(jsonObj, facet):    
	fileId = jsonObj["@id"]
	fileTag = get_attribute(facet, "uco-observable:mimeType", "-")

	#if fileTag != "-":
		#fileTag = facet["uco-core:tag"][0]

	fileName = get_attribute(facet, "uco-observable:fileName", "-")
	filePath = get_attribute(facet, "uco-observable:filePath", "-")

	fileSize = get_attribute(facet, "uco-observable:sizeInBytes", "0")

	if fileSize != "0":
		fileSize = facet["uco-observable:sizeInBytes"]["@value"]  

	tagProcessed = False;

	try:
		fileTagNorm = fileTag.lower()
		if fileTagNorm in ('image', 'pictures', 'live photos'):
			filesImage.append(
				{
					"@id":fileId,
					"uco-core:tag": fileTag,
					"uco-observable:fileName":fileName,
					"uco-observable:filePath":filePath,
					"uco-observable:fileSize":fileSize
				})
			tagProcessed = True

		if fileTagNorm == 'audio':
			filesAudio.append(
				{
					"@id":fileId,
					"uco-core:tag": fileTag,
					"uco-observable:fileName":fileName,
					"uco-observable:filePath":filePath,
					"uco-observable:fileSize":fileSize
				})
			tagProcessed = True

		if fileTagNorm.find('text') > -1:
			filesText.append(
				{
					"@id":fileId,
					"uco-core:tag": fileTag,
					"uco-observable:fileName":fileName,
					"uco-observable:filePath":filePath,
					"uco-observable:fileSize":fileSize
				})
			tagProcessed = True

		if fileTagNorm.find('pdf') > -1:
			filesPDF.append(
				{
					"@id":fileId,
					"uco-core:tag": fileTag,
					"uco-observable:fileName":fileName,
					"uco-observable:filePath":filePath,
					"uco-observable:fileSize":fileSize
				})
			tagProcessed = True

		if fileTagNorm.find('rtf') > -1:
			filesRTF.append(
				{
					"@id":fileId,
					"uco-core:tag": fileTag,
					"uco-observable:fileName":fileName,
					"uco-observable:filePath":filePath,
					"uco-observable:fileSize":fileSize
				})
			tagProcessed = True

		if fileTagNorm.find('word') > -1:
			filesWord.append(
				{
					"@id":fileId,
					"uco-core:tag": fileTag,
					"uco-observable:fileName":fileName,
					"uco-observable:filePath":filePath,
					"uco-observable:fileSize":fileSize
				})
			tagProcessed = True

		if fileTagNorm.find('video') > -1:
			filesVideo.append(
				{
					"@id":fileId,
					"uco-core:tag": fileTag,
					"uco-observable:fileName":fileName,
					"uco-observable:filePath":filePath,
					"uco-observable:fileSize":fileSize
				})
			tagProcessed = True

		if fileTagNorm == 'archives':
			filesArchive.append(
				{
					"@id":fileId,
					"uco-core:tag": fileTag,
					"uco-observable:fileName":fileName,
					"uco-observable:filePath":filePath,
					"uco-observable:fileSize":fileSize
				})
			tagProcessed = True

		if fileTagNorm.find('database') > -1:
			filesDatabase.append(
				{
					"@id":fileId,
					"uco-core:tag": fileTag,
					"uco-observable:fileName":fileName,
					"uco-observable:filePath":filePath,
					"uco-observable:fileSize":fileSize
				})
			tagProcessed = True

		if fileTagNorm == 'application':
			filesApplication.append(
				{
					"@id":fileId,
					"uco-core:tag": fileTag,
					"uco-observable:fileName":fileName,
					"uco-observable:filePath":filePath,
					"uco-observable:fileSize":fileSize
				})
			tagProcessed = True

		if not tagProcessed:
			filesUncategorized.append(
				{
					"@id":fileId,
					"uco-core:tag": fileTag,
					"uco-observable:fileName":fileName,
					"uco-observable:filePath":filePath,
					"uco-observable:fileSize":fileSize
				})
	except Exception as e:
		print("ERROR: in appending dictionary to file")
		print (e)


def processURL(jsonObj, facet):
	webId = jsonObj["@id"]  
	webUrl = facet["uco-observable:fullValue"]

	try:
		webURLs.append(
			{
				"@id":webId,
				"uco-observable:url":webUrl
			})

	except Exception as e:
		print("ERROR: in appending dictionary to webURL")
		print (e)


def processWebBookmark(jsonObj, facet):
	webId = jsonObj["@id"] 
	webCreatedTime = ''
	webApp = ""
	webUrl = ""
	webPath = ""

	browserlId = facet["uco-observable:application"]["@id"]
	for a in applications:
		if a["@id"] == browserlId:
			webApp = a["uco-core:name"]

	webCreatedTime = get_attribute(facet, "uco-observable:observableCreatedTime", None)
	if webCreatedTime:
		webCreatedTime = facet["uco-observable:observableCreatedTime"]["@value"]

	webUrl = get_attribute(facet, "uco-observable:urlTargeted", None)
	if webUrl:
		webUrl = facet["uco-observable:urlTargeted"]["@value"]

	webPath = get_attribute(facet, "uco-observable:bookmarkPath", "-")	

	try:
		webBookmark.append(
			{
				"@id":webId,
				"uco-observable:application":webApp,
				"uco-observable:urlTargeted": webUrl,
				"uco-observable:bookmarkPath":webPath,
				"uco-observable:observableCreatedTime":webCreatedTime
			})

	except Exception as e:
		print("ERROR: in appending dictionary to Web Bookmark")
		print (e)

def processURLHistory(jsonObj, facet):
	webId = jsonObj["@id"] 
	webLastVisited = ''
	webTitle = ""
	webStatus = ""
	webUrl = ""
	webApp = ""

	browserlId = get_attribute(facet, "uco-observable:browserInformation", None)
	if browserlId:
		browserlId = facet["uco-observable:browserInformation"]["@id"]
		for a in applications:
			if a["@id"] == browserlId:
				webApp = a["uco-core:name"]
	else:
		webApp = "-"

	firstVisit = get_attribute(facet["uco-observable:urlHistoryEntry"][0], "uco-observable:firstVisit", None)
	if firstVisit:
		firstVisit = facet["uco-observable:urlHistoryEntry"][0]["uco-observable:firstVisit"]["@value"]

	lastVisit = get_attribute(facet["uco-observable:urlHistoryEntry"][0], "uco-observable:lastVisit", None)
	if lastVisit:
		lastVisit = facet["uco-observable:urlHistoryEntry"][0]["uco-observable:lastVisit"]["@value"]	

	webUrlId = get_attribute(facet["uco-observable:urlHistoryEntry"][0], "uco-observable:url", None)
	if webUrlId:
		webUrlId = facet["uco-observable:urlHistoryEntry"][0]["uco-observable:url"]["@id"]

	webTitle = get_attribute(facet["uco-observable:urlHistoryEntry"][0], "uco-observable:pageTitle", "-")	
	webStatus = get_attribute(facet["uco-observable:urlHistoryEntry"][0], "uco-observable:allocationStatus", "-")

	if webUrlId: 
		for w in webURLs:
			if w["@id"] == webUrlId:
				webUrl = w["uco-observable:url"]

	try:
		webURLHistory.append(
			{
				"@id":webId,
				"uco-observable:browserInformation":webApp,
				"uco-observable:url": webUrl,
				"uco-observable:title":webTitle,
				"uco-observable:lastVisited":webLastVisited,
			"uco-observable:allocationStatus":webStatus
			})

	except Exception as e:
		print("ERROR: in appending dictionary to URLHistory")
		print (e)

def number_with_dots(n):
	if isinstance(n, int) or isinstance(n, str):
		n = str(n)
		num_dots = n[-3:]
		n = n[:-3]
		while n:
			num_dots = n[-3:] + "." + num_dots
			n = n[:-3]

		return(num_dots)
	else:
		return('Parameter must be either integer or string')

if __name__ == '__main__':
#--- Gobal variables
#
	C_GREEN = '\033[32m'
	C_RED = '\033[31m'
	C_BLACK = '\033[0m'
	C_CYAN = '\033[36m'
	EMPTY_DATA = "1900-01-01T00:00:00"

	chatThreads = []
	chatMessages = []
	chatMessageAttachments = []
	cookies = []
	geo_coordinates = []
	cell_sites = []
	bluetooths = []
	searched_items = []
	social_media_activities = []
	events = []
	wireless_net = []
	relationAttachmentsTo = []
	relationMappedBy = []
	relationConnectedTo = []
	smsMessages = []
	accounts = []
	emailAddresses = []
	emailAccounts = []
	applications = []
	phoneCalls = []
	calendars = []
	emailMessages = []
	filesUncategorized = []
	filesImage = []
	filesAudio = []
	filesText = []
	filesPDF = []  
	filesWord = []
	filesRTF = []
	filesVideo = []
	filesArchive = []
	filesDatabase = []
	filesApplication = []
	webURLs = []
	webURLHistory = []
	webBookmark = []

#--- Read input file in CASE-JSON format
#    
	try:
		f = codecs.open(sys.argv[1], 'r', encoding='utf-8')
	except Exception as e:
		print(C_RED + '\n' + "ERROR in trying to open the file " + sys.argv[1])
		print (e)
		sys.exit('Open file failed.')

	try:
		print(C_CYAN + "Load JSON structure, it might take some time, please wait ...\n")
		json_obj = json.load(f)
		app = QApplication([])
		msgBox = QMessageBox()
		reply = msgBox.question(None, "CASE syntax check result", 
								"Syntax check went well! Do you want to continue?", 
								QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

		if reply == QMessageBox.No:
			sys.exit('Terminate by user.')

#--- Loop over all Observables of the array "uco-core:object"
#         
		if 'uco-core:object' in json_obj.keys():
			json_data = json_obj['uco-core:object']
		elif '@graph' in json_obj.keys():
			json_data = json_obj['@graph']
		else:
			sys.exit(C_RED + "\n Neither key uco-core:object nor @graph have been found. \
				\n" + C_BLACK)

		nObjects = 0

		for jsonObj in json_data:
			nObjects +=1
			uuid_object = jsonObj['@id']
			print(f"{C_GREEN} Observable n. {str(nObjects)} - uuid={uuid_object}", end='\r')
			dataFacets = jsonObj.get("uco-core:hasFacet", None)
			if not dataFacets:
				observableType = jsonObj.get("@type", None)
				# Only the ObservableRelationship  is considered.
				# Others (i.e. uco-identity:Identity, case-investigation:InvestigativeAction,
				# uco-tool:Tool, uco-identity:Organization, uco-role:Role, 
				# case-investigation:ProvenanceRecord, case-investigation:InvestigativeAction)
				# are ignored.
				if observableType == "uco-observable:ObservableRelationship":
					if jsonObj["uco-core:kindOfRelationship"] == "Attached_To":
						processRelationAttachments(jsonObj)
					elif jsonObj["uco-core:kindOfRelationship"] == "Mapped_By":
						processRelationMappedBy(jsonObj)
					elif jsonObj["uco-core:kindOfRelationship"] == "Connected_To":
						processRelationConnectedTo(jsonObj)
			else:
				for facet in dataFacets:
					objectType = facet.get("@type", None)
					if objectType:
						print(f"objectType={objectType}")
						if objectType == "uco-observable:MessageFacet":
							processMessage(uuid_object=uuid_object, facet=facet)
						elif objectType == "uco-observable:SMSMessageFacet":
							processMessage(uuid_object=uuid_object, facet=facet)
						elif objectType == "uco-observable:BluetoothAddressFacet":
							processBluetooth(uuid_object=uuid_object, facet=facet)
						elif objectType == "uco-observable:CellSiteFacet":
							processCellSite(uuid_object=uuid_object, facet=facet)
						elif objectType == "uco-observable:BrowserCookieFacet":
							processCookie(uuid_object=uuid_object, facet=facet)
						elif objectType == "uco-location:LatLongCoordinatesFacet":
							processCoordinate(uuid_object=uuid_object, facet=facet)
						elif objectType == "uco-observable:MessageThreadFacet":
							processThread(uuid_object=uuid_object, facet=facet)
						elif objectType == "uco-observable:AccountFacet":
							processAccount(uuid_object=uuid_object, facet=facet, kind="AccountFacet")
						elif objectType == "uco-observable:ApplicationAccountFacet":
							processAccount(uuid_object=uuid_object, facet=facet, kind="ApplicationAccountFacet")
						elif objectType == "uco-observable:DigitalAccountFacet" :
							processAccount(uuid_object=uuid_object, facet=facet, kind="DigitalAccountFacet")
						elif objectType == "uco-observable:PhoneAccountFacet":
							processAccount(uuid_object=uuid_object, facet=facet, kind="PhoneAccountFacet")
						elif objectType == "uco-observable:EmailAccountFacet":
							processEmailAccount(uuid_object=uuid_object, facet=facet)
						elif objectType == "uco-observable:ApplicationFacet":
							processApplication(uuid_object=uuid_object, facet=facet)
						elif objectType == "uco-observable:EmailAddressFacet":
							processEmailAddress(uuid_object=uuid_object, facet=facet)
						elif objectType == "uco-observable:CalendarEntryFacet":
							processCalendar(uuid_object=uuid_object, facet=facet)
						elif objectType == "uco-observable:CallFacet":
							processCall(uuid_object=uuid_object, facet=facet)
						elif objectType == "uco-observable:EmailMessageFacet":
							processEmailMessage(jsonObj, facet)
						elif objectType == "uco-observable:FileFacet":
							processFile(jsonObj, facet)
						elif objectType == "uco-observable:URLFacet":
							processURL(jsonObj, facet)
						elif objectType == "uco-observable:URLHistoryFacet":
							processURLHistory(jsonObj, facet)
						elif objectType == "uco-observable:BrowserBookmarkFacet":
							processWebBookmark(jsonObj, facet)
						elif objectType == "uco-observable:WirelessNetworkConnectionFacet":
							processWirelessNetwork(jsonObj, facet)
						elif objectType == "drafting:SearchedItemFacet":
							processSearchedItems(jsonObj, facet)
						elif objectType == "drafting:SocialMediaActivityFacet":
							processSocialMediaActivities(jsonObj, facet)
						elif objectType == "uco-observable:EventRecordFacet":
							processEvents(jsonObj, facet)
		processAttachments()
	except Exception as e:
		print(C_CYAN + "ERROR: in Loading the JSON structure! \n\n" + C_BLACK + "\n\n")
		print (e)
		sys.exit('Load JSON file failed. \n')

	f.close()
	print(C_CYAN + "\n\nEnd Observables processing!" + C_BLACK + "\n\n")

	tableData = [[]]
	treeData = []
	i = 1
	totMessages = 0

	for a in accounts:
		if a["@id"] == "kb:27a87a37-4ff1-45b4-9813-9f6b2e1f491d":
			print(f"accountIdentifier= {a['uco-observable:accountIdentifier']}")
			print(f"phoneAccount= {a['uco-observable:phoneAccount']}")
			print(f"application= {a['uco-observable:application']}")
			print(f"displayName= {a['uco-observable:displayName']}")

	treeData.insert(0, {'unique_id': ':00000000', 'parent_id': '0', 'short_name': 'Cyber items' })

	totAccounts = len(accounts)
	if totAccounts > 0:
		accountText = 'Accounts ' + '(' + number_with_dots(totAccounts) + ')'
		treeData.append({'unique_id': ':Accounts', 'parent_id': ':00000000', 'short_name': accountText })

	totCalendars = len(calendars)
	if totCalendars > 0:
		calendarText = 'Calendars ' + '(' + number_with_dots(totCalendars) + ')'
		treeData.append({'unique_id': ':Calendars', 'parent_id': ':00000000', 'short_name': calendarText })

	totCalls = len(phoneCalls)
	if totCalls > 0:
		callText = 'Calls ' + '(' + number_with_dots(totCalls) + ')'
		treeData.append({'unique_id': ':Calls', 'parent_id': ':00000000', 'short_name': callText })

	totCellSites = len(cell_sites)
	if totCellSites > 0:
		cellSiteText = 'CellSite ' + '(' + number_with_dots(totCellSites) + ')'
		treeData.append({'unique_id': ':CellSites', 'parent_id': ':00000000', 'short_name': cellSiteText })

	for t in chatThreads:
		id = t['@id']
		text = 'N. ' + str(i) + ' (' + number_with_dots(t["thread:length"]) + ')'
		totMessages += int(t["thread:length"])
		treeData.append({'unique_id': id, 'parent_id': ':ChatMessages', 'short_name': text})
		i = i + 1

	totChats = len(chatThreads)
	if totChats > 0:
		chatText = 'Chats ' + '(' + number_with_dots(totChats) + '/' + number_with_dots(totMessages) + ')'
		treeData.append({'unique_id': ':ChatMessages', 'parent_id': ':00000000', 'short_name': chatText})

	totCookies = len(cookies)
	if totCookies > 0:
		cookieText = 'Cookies ' + '(' + number_with_dots(totCookies) + ')'
		treeData.append({'unique_id': ':Cookies', 'parent_id': ':00000000', 'short_name': cookieText })

	totBluetooths = len(bluetooths)
	if totBluetooths > 0:
		btText = 'Device connection (Bluetooth) ' + '(' + number_with_dots(totBluetooths) + ')'
		treeData.append({'unique_id': ':Bluetooths', 'parent_id': ':00000000', 'short_name': btText })


	totEmails = len(emailMessages)
	if totEmails > 0:
		emailText = 'Emails ' + '(' + number_with_dots(totEmails) + ')'
		treeData.append({'unique_id': ':EmailMessages', 'parent_id': ':00000000', 'short_name': emailText })

	totEvents = len(events)
	if totEvents > 0:
		eventText = 'Events ' + '(' + number_with_dots(totEvents) + ')'
		treeData.append({'unique_id': ':Events', 'parent_id': ':00000000', 'short_name': eventText })

	totFiles = (len(filesUncategorized) + len(filesImage) + len(filesArchive) + 
				len(filesVideo) + len(filesAudio) + + len(filesText) + len(filesDatabase) + 
				len(filesApplication) + len(filesPDF) + len(filesWord) + len(filesRTF))
	fileText = 'Files ' + '(' + number_with_dots(totFiles) + ')'
	treeData.append({'unique_id': ':Files', 'parent_id': ':00000000', 'short_name': fileText })

	totImages = len(filesImage)
	if totImages > 0:
		imageText = 'Images ' + '(' + number_with_dots(totImages) + ')'
		treeData.append({'unique_id': ':Images', 'parent_id': ':Files', 'short_name': imageText })

	totAudios = len(filesAudio)
	if totAudios > 0:
		audioText = 'Audios ' + '(' + number_with_dots(totAudios) + ')'
		treeData.append({'unique_id': ':Audios', 'parent_id': ':Files', 'short_name': audioText })

	totTexts = len(filesText)
	if totTexts > 0:
		textText = 'Texts ' + '(' + number_with_dots(totTexts) + ')'
		treeData.append({'unique_id': ':Texts', 'parent_id': ':Files', 'short_name': textText })

	totPDF = len(filesPDF)
	if totPDF > 0:
		pdfText = 'PDFs ' + '(' + number_with_dots(totPDF) + ')'
		treeData.append({'unique_id': ':PDFs', 'parent_id': ':Files', 'short_name': pdfText })

	totWord = len(filesWord)
	if totWord > 0:
		wordText = 'Words ' + '(' + number_with_dots(totWord) + ')'
		treeData.append({'unique_id': ':Words', 'parent_id': ':Files', 'short_name': wordText }) 

	totWord = len(filesRTF)
	if totWord > 0:
		rtfText = 'RTFs ' + '(' + number_with_dots(totWord) + ')'
		treeData.append({'unique_id': ':RTFs', 'parent_id': ':Files', 'short_name': rtfText })  

	totVideos = len(filesVideo)
	if totVideos > 0:
		videoText = 'Videos ' + '(' + number_with_dots(totVideos) + ')'
		treeData.append({'unique_id': ':Videos', 'parent_id': ':Files', 'short_name': videoText })

	totArchives = len(filesArchive)
	if totArchives > 0:
		archiveText = 'Archives ' + '(' + number_with_dots(totArchives) + ')'
		treeData.append({'unique_id': ':Archives', 'parent_id': ':Files', 'short_name': archiveText })

	totDatabases = len(filesDatabase)
	if totDatabases > 0:
		databaseText = 'Databases ' + '(' + number_with_dots(totDatabases) + ')'
		treeData.append({'unique_id': ':Databases', 'parent_id': ':Files', 'short_name': databaseText })

	totApplications = len(filesApplication)
	if totApplications > 0:
		applicationText = 'Applications ' + '(' + number_with_dots(totApplications) + ')'
		treeData.append({'unique_id': ':Applications', 'parent_id': ':Files', 'short_name': applicationText })

	totUncategorized = len(filesUncategorized)
	if totUncategorized > 0:
		uncategorizedText = 'Uncategorized ' + '(' + number_with_dots(totUncategorized) + ')'
		treeData.append({'unique_id': ':Uncategorized', 'parent_id': ':Files', 'short_name': uncategorizedText })

	totLocationDevice = len(relationMappedBy)
	if totLocationDevice > 0:
		locationText = 'Location device ' + '(' + number_with_dots(totLocationDevice) + ')'
		treeData.append({'unique_id': ':LocationDevice', 'parent_id': ':00000000', 'short_name': locationText })

	totSearchedItems = len(searched_items)
	if totSearchedItems > 0:
		searchedItemsText = 'Searched items ' + '(' + number_with_dots(totSearchedItems) + ')'
		treeData.append({'unique_id': ':SearchedItems', 'parent_id': ':00000000', 'short_name': searchedItemsText })

	totSocialMediaActivities = len(social_media_activities)
	if totSocialMediaActivities > 0:
		socialMediaActivitiesText = 'Social media activities ' + '(' + number_with_dots(totSocialMediaActivities) + ')'
		treeData.append({'unique_id': ':SocialMediaActivities', 'parent_id': ':00000000', 'short_name': socialMediaActivitiesText })

	totSMSs = len(smsMessages)
	if totSMSs > 0:
		smsText = 'SMSs ' + '(' + number_with_dots(totSMSs) + ')'
		treeData.append({'unique_id': ':Sms', 'parent_id': ':00000000', 'short_name': smsText })

	totWebBookmarks = len(webBookmark)
	if totWebBookmarks > 0:
		webBookmarkText = 'Web Bookmarks ' + '(' + number_with_dots(totWebBookmarks) + ')'
		treeData.append({'unique_id': ':WebBookmarks', 'parent_id': ':00000000', 'short_name': webBookmarkText })

	totWebs = len(webURLHistory)
	if totWebs > 0:
		webText = 'Web Histories ' + '(' + number_with_dots(totWebs) + ')'
		treeData.append({'unique_id': ':WebHistories', 'parent_id': ':00000000', 'short_name': webText })

	totWirelessNet = len(wireless_net)
	if totWirelessNet > 0:
		wirelessNetText = 'Wireless Net ' + '(' + number_with_dots(totWirelessNet) + ')'
		treeData.append({'unique_id': ':WirelessNet', 'parent_id': ':00000000', 'short_name': wirelessNetText })

#--- Set the UI layout
	view = view(treeData, tableData)
	view.setGeometry(50, 50, 1400, 800)
	view.setWindowTitle('Cyber items view - ' + sys.argv[1] + ' (n. Observables: ' + number_with_dots(nObjects) + ')')
	view.show()
	sys.exit(app.exec_())