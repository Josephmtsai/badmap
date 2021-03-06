import os
from apiclient import discovery
from dbHandler import dbHandler
from crawler import googleMapLocation
from Common import Common
import datetime
import re


def syncExcelToDB(apiKey, excelsheetid):
    sheetList = [u'日', u'一', u'二', u'三', u'四', u'五', u'六']
    service = discovery.build('sheets', 'v4', developerKey=apiKey,
                              discoveryServiceUrl='https://sheets.googleapis.com/$discovery/rest?version=v4')
    result = service.spreadsheets().values().batchGet(spreadsheetId=excelsheetid, ranges=sheetList,
                                                      valueRenderOption='FORMULA', dateTimeRenderOption='FORMATTED_STRING').execute()
    responseSheet = result.get('valueRanges', [])
    weekDay = Common.getTodayWeekDay()
    newLocationDict = {}
    existlocationDict = googleMapLocation.getExistLocationToDict()
    badmintonInfoList = []
    coordinate = None
    address = None
    for index, sheet in enumerate(responseSheet):
        rows = sheet.get('values', [])
        for rowIndex, row in enumerate(rows):
            if rowIndex == 1 or rowIndex == 0:
                continue
            badmintonInfo = {}
            try:
                if len(row) > 8:
                    if "HYPERLINK" in row[1]:
                        badmintonInfo['location'] = re.search(
                            r'=HYPERLINK\("(.*)","(.*)"\)', row[1]).group(2)
                    else:
                        badmintonInfo['location'] = row[1]

                    badmintonInfo['level'] = row[5]

                    if existlocationDict is not None and badmintonInfo['location'].encode('UTF-8') not in existlocationDict:
                        coordinate, address, status = googleMapLocation.getLocationInfo(
                            row[3], apiKey)
                        if coordinate is not None:
                            badmintonInfo['address'] = address
                            badmintonInfo['position'] = {
                                'lat': coordinate['lat'], 'lng': coordinate['lng']}
                            if status is not None:
                                newLocationDict = googleMapLocation.locationToDict(
                                    newLocationDict, existlocationDict, badmintonInfo['location'], address, coordinate)
                    elif existlocationDict is not None and badmintonInfo['location'].encode('UTF-8') in existlocationDict:
                        badmintonInfo['position'] = existlocationDict[badmintonInfo['location'].encode(
                            'UTF-8')]['position']
                    badmintonInfo['payInfo'] = Common.convertToInt(row[6])

                    if row[7] != "" and "HYPERLINK" in row[7]:
                        badmintonInfo['contactName'] = re.search(
                            r'=HYPERLINK\("(.*)","(.*)"\)', row[7]).group(2)
                    else:
                        badmintonInfo['contactName'] = row[7]

                    if row[8] != "" and "HYPERLINK" in row[8]:
                        badmintonInfo['contactPhone'] = re.search(
                            r'=HYPERLINK\("(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/(.*)","(.*)"\)', row[8]).group(5)
                    else:
                        badmintonInfo['contactPhone'] = row[8]

                    if re.match('([0-9]*):([0-9]*):([0-9]*)', row[0]) is None:
                        badmintonInfo['startTime'] = Common.convertToSTRDateTime(
                            row[0].split("~")[0], index)
                        badmintonInfo['startHour'] = int(
                            Common.getInputTimeArray(row[0].split("~")[0])[0])
                        badmintonInfo['endTime'] = Common.convertToSTRDateTime(
                            row[0].split("~")[1], index)
                    else:
                        badmintonInfo['startTime'] = Common.convertToSTRDateTime(
                            re.match('(.*):(.*)', row[0]).group(1), index)
                        badmintonInfo['startHour'] = int(Common.getInputTimeArray(
                            re.match('(.*):(.*)', row[0]).group(1))[0])
                        badmintonInfo['endTime'] = Common.convertToSTRDateTime(
                            re.match('(.*):(.*)', row[0]).group(2), index)
                    badmintonInfo['weekDay'] = sheetList[index]
                    badmintonInfo['weekDayInt'] = index
                    badmintonInfo['source'] = "excel"

                    if len(row) > 9 and "HYPERLINK" in row[1] and re.match(r'=HYPERLINK\("(.*)","(.*)"\)', row[9]) is not None:
                        badmintonInfo['line'] = re.search(
                            r'=HYPERLINK\("(.*)","(.*)"\)', row[9]).group(1)
                    else:
                        badmintonInfo['line'] = ""
                    badmintonInfo['sourceData'] = row
                    # break
            finally:
                badmintonInfoList.append(badmintonInfo)
    locationList = googleMapLocation.dictToLocationInfoList(newLocationDict)
    if len(locationList) > 0:
        dbHandler.insertLocationInfoList(locationList)
    dbHandler.insertStatus({'locationInsert': len(
        locationList), 'Time': datetime.datetime.utcnow() + datetime.timedelta(hours=+8)})
    return dbHandler.insertbadmintonInfoList(badmintonInfoList)


def getSheetNames(apiKey, excelsheetid):
    service = discovery.build('sheets', 'v4', developerKey=apiKey,
                              discoveryServiceUrl='https://sheets.googleapis.com/$discovery/rest?version=v4')
    sheet_metadata = service.spreadsheets().get(
        spreadsheetId=excelsheetid).execute()
    sheets = sheet_metadata.get('sheets', '')
    titleList = []
    for sheet in sheets:
        title = sheet['properties']['title']
        titleList.append(title)
    print(titleList)
    return titleList
