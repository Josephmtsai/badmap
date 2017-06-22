import os 
from apiclient import discovery
from dbHandler import dbHandler
from crawler import googleMapLocation
from Common import Common
import datetime
def syncExcelToDB(apiKey,excelsheetid): 
	sheetList = [u'日',u'一',u'二',u'三',u'四',u'五',u'六']
	service = discovery.build('sheets', 'v4', developerKey=apiKey,discoveryServiceUrl='https://sheets.googleapis.com/$discovery/rest?version=v4')
	result = service.spreadsheets().values().batchGet(spreadsheetId=excelsheetid,ranges=sheetList).execute()
	responseSheet = result.get('valueRanges', [])	
	weekDay = Common.getTodayWeekDay()
	existlocationDict =googleMapLocation.getExistLocationToDict()
	newLocationDict = {}
	badmintonInfoList = []
	coordinate = None
	address = None
	for index,sheet in enumerate( responseSheet):
		rows =sheet.get('values',[])
		for rowIndex,row in  enumerate( rows):  
			if rowIndex == 1 or rowIndex ==0:
				continue
			badmintonInfo = {}
			try:
				if len(row) > 8:
					badmintonInfo['location'] = row[1]
					print(existlocationDict)
					if existlocationDict is not None and badmintonInfo['location'].encode('UTF-8') not in existlocationDict:
						coordinate,address,status =  googleMapLocation.getLocationInfo(row[3],apiKey) 
					if coordinate is not None:
						badmintonInfo['address'] = address
						badmintonInfo['lats'] = coordinate['lat']
						badmintonInfo['lngs'] = coordinate['lng']
						if status is not None:
							newLocationDict = googleMapLocation.locationToDict(newLocationDict,existlocationDict,badmintonInfo['location'],address,coordinate)
					badmintonInfo['payInfo'] = Common.convertToInt(row[6])
					badmintonInfo['contactName'] = row[7]
					badmintonInfo['contactPhone'] = row[8]
					badmintonInfo['startTime'] = Common.convertToDateTime(row[0].split("~")[0],index -weekDay)	
					badmintonInfo['endTime'] = Common.convertToDateTime(row[0].split("~")[1],index -weekDay)
					badmintonInfo['weekDay'] = sheetList[index]
					badmintonInfo['weekDayInt'] = index
					badmintonInfo['source'] = "excel"
					badmintonInfo['line'] = row[9] if len(row) > 9 else ""
					badmintonInfo['sourceData'] = ",".join(row ) 
					#break
			finally:					
				badmintonInfoList.append(badmintonInfo)
	locationList = googleMapLocation.dictToLocationInfoList(newLocationDict)
	if len(locationList) >0:
		dbHandler.insertLocationInfoList(locationList)
	dbHandler.insertStatus({'locationInsert':len(locationList) ,'Time' : datetime.datetime.utcnow() + datetime.timedelta(hours=+8)  })
	return dbHandler.insertbadmintonInfoList(badmintonInfoList)
