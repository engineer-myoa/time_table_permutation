# -*- coding: utf-8 -*-
from __future__ import print_function

from collections import namedtuple
import re
import itertools, copy
from configparser import ConfigParser

import pprint # for debug
import sys, codecs

python_ver = (3,)
isPython3 = False
if sys.version_info >= python_ver:
    isPython3 = True

ClassData = namedtuple("ClassType", ["classname", "timetable", "isSep"])

timeTable = [ [ None for xr in range(12)]  for xr in range(7) ] # 3.4 호환
rawTimeTable = [ [ None for xr in range(12)]  for xr in range(7) ] # 3.4 호환

# 클래스화 하기
# classList, fixedList, sepList, sepList2
# timeTable, rawTimeTable 멤버변수로 놓기

def timeTableCast(elem, baseTimeTable, rawTimeTable):
    #pprint.pprint(baseTimeTable)
    stringList = parseSubjectTime(elem.timetable)
    #print(elem)
    prototypeTable = copy.deepcopy(baseTimeTable)
    prototypeRawTable = copy.deepcopy(rawTimeTable)

    try:
        if type(stringList) != type(list()):
            raise TypeError("잘못된 입력정보.")

        for timeElem in stringList:

            if len(timeElem) != 2 and type(timeElem) != type(str()):
                raise ValueError("정상적인 시간정보가 아닙니다.")

            if prototypeTable[int(timeElem[0])][int(timeElem[1])] != None:
                raise AttributeError("시간표가 중복됩니다. 불가능합니다. 원상태로 이전합니다.")

            prototypeTable[int(timeElem[0])][int(timeElem[1])] = elem.classname
            prototypeRawTable[int(timeElem[0])][int(timeElem[1])] = elem

        return prototypeTable, prototypeRawTable

    except Exception as e:
        #print(e)

        return None, None

def parseSubjectTime(string):

    string = string.replace("월","0")
    string = string.replace("화","1")
    string = string.replace("수","2")
    string = string.replace("목","3")
    string = string.replace("금","4")
    string = string.replace("토","5")
    string = string.replace("일","6")

    string = string.replace("Mon","0")
    string = string.replace("Tue","1")
    string = string.replace("Wed","2")
    string = string.replace("Thu","3")
    string = string.replace("Fri","4")
    string = string.replace("Sat","5")
    string = string.replace("Sun","6")
    return re.findall("(?:(\d\d)\s*)+?",string) # spliting
    #return	re.findall("(([A-G]\d)\s*)+?", string)

def initApp():
    classList = []

    config = ConfigParser()
    #config.read("class.conf")
    config.read_file(codecs.open("class.conf", "r", "utf8"))

    for i in config.sections():
        section = config[i]
        subjectName = section.get("subjectName")
        classTime = section.get("classTime")
        isSep = section.getboolean("isSep")
        if isSep == True:
            isSep = int(section.get("sepNo"))
        else:
            isSep = 0
        
        classList.append( ClassData(subjectName, classTime, isSep) )
    return classList



def classParsing(classList): # 수업 분류작업
    fixedList = []
    sepList = {}

    for i in classList:
        if(i.isSep == 0):
            fixedList.append(i)
        else:
            temp = sepList.get(i.classname)
            if temp is None:
                sepList.update({i.classname : []})

                temp = sepList.get(i.classname)
            temp.append(i)

    setFixedElem(fixedList) # 분반이 없는 수업들을 timeTable에 배치

    sepList2 = []
    for k in sepList.keys():
        sepList2.append( sepList.get(k))

    iterated = itertools.product(*sepList2)
    return iterated

    #return fixedList, sepList
def setFixedElem(someList):
    global timeTable, rawTimeTable
    for i in someList:
        timeTable, rawTimeTable = timeTableCast( i, timeTable, rawTimeTable)

def parseFromRawData():
    pass

#  ------------------------------------------------------------
# --AAAAAAAAAA--AAAAAAAAAA------AA-------AAAAAA-----AAAAAAAAAA--
# --AA--------------AA---------AAAA------AA----AA-------AA------
# --AA--------------AA--------AA--AA-----AA------AA-----AA------
# --AAAAAAAAAA------AA-------AA----AA----AAAAAAAA-------AA------
# ----------AA------AA------AAAAAAAAAA---AA----AA-------AA------
# ----------AA------AA-----AA--------AA--AA-----AA------AA------
# --AAAAAAAAAA------AA-----AA--------AA--AA------AA-----AA------
#  ------------------------------------------------------------


#parseFromRawData

iterated = classParsing( initApp() )

finalList = []
for i in iterated:
    protoTimeTable = copy.deepcopy(timeTable)
    protoRawTimeTable = copy.deepcopy(rawTimeTable)

    for j in i: # 조합에서 각각의 시간표.

        protoTimeTable, protoRawTimeTable = timeTableCast( j, protoTimeTable, protoRawTimeTable)
        if protoTimeTable == None:
            break
    if protoTimeTable != None:
        finalList.append(protoTimeTable)

        #pprint.pprint(protoTimeTable)

        #print("====================================================")

for i in finalList:
    for weekIndex, j in enumerate(i): # 각 줄은 요일별 정보. 인덱싱을 다르게 표현하면 각 줄을 달력처럼 표시가능
        if(weekIndex in (5,6)): # 토,일은 스킵 (코드 주석시 포함가능)
            continue
        for timeIndex, k in enumerate(j):
            if(timeIndex in (0, 10,11)):
                continue
            if k == None:
                print("".ljust(16, "#"), end="\t")
                continue
            #print("{:<16}".format(k), end=" ")
            if not isPython3:
                k = k.decode("UTF-8")
            print(k.ljust((16 - len(k) * 2) + len(k), " "), end = "\t")

        print()
    print("=====================================================")
