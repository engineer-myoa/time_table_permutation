# -*- coding: utf-8 -*-
from __future__ import print_function

from collections import namedtuple
import re
import itertools, copy
from configparser import ConfigParser

import pprint # for debug
import sys, codecs

ClassData = namedtuple("ClassType", ["classname", "timetable", "isSep"])

class TimeTabler:

    def __init__(self):
        python_ver = (3,)
        self.isPython3 = False
        if sys.version_info >= python_ver:
            self.isPython3 = True

        self.timeTable = [ [ None for xr in range(12)]  for xr in range(7) ] # 3.4 호환
        self.rawTimeTable = [ [ None for xr in range(12)]  for xr in range(7) ] # 3.4 호환

        self.classList = []

        self.fixedList = []
        self.sepList = {}
        self.sepList2 = []

        self.finalList = []

    def clear(self):
        self.timeTable = [ [ None for xr in range(12)]  for xr in range(7) ] # 3.4 호환
        self.rawTimeTable = [ [ None for xr in range(12)]  for xr in range(7) ] # 3.4 호환

        self.classList = []

        self.fixedList = []
        self.sepList = {}
        self.sepList2 = []
        
        self.finalList = []

    def parseSubjectTime(self, string):

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

    def timeTableCast(self, elem, baseTimeTable, rawTimeTable):
        #pprint.pprint(baseTimeTable)
        stringList = self.parseSubjectTime(elem.timetable)
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

        except Exception as e: # 비정상적 시간정보일시, 시간표 중복시
            #print(e) 
            return None, None

    
    def loadConfig(self, filename="E:\\dev\\DEV_100SERVER\\time_tabler\\class.conf"):
        config = ConfigParser()
        config.read_file(codecs.open(filename, "r", "utf8"))

        for i in config.sections():
            section = config[i]
            subjectName = section.get("subjectName")
            classTime = section.get("classTime")
            isSep = section.getboolean("isSep")
            if isSep == True:
                isSep = int(section.get("sepNo"))
            else:
                isSep = 0
            
            self.classList.append( ClassData(subjectName, classTime, isSep) )
        #return self.classList

    def classParsing(self): # 수업 분류작업

        if self.classList == None or len(self.classList) <=0:
            raise IndexError("loadConfig 함수를 통해 시간표 raw값을 불러오세요")

        for i in self.classList:
            if(i.isSep == 0):
                self.fixedList.append(i)
            else:
                temp = self.sepList.get(i.classname)
                if temp is None:
                    self.sepList.update({i.classname : []})

                    temp = self.sepList.get(i.classname)
                temp.append(i)

        self.setFixedElem() # 분반이 없는 수업들을 timeTable에 배치

        for k in self.sepList.keys():
            self.sepList2.append( self.sepList.get(k))



        iterated = itertools.product(*self.sepList2)
        #return iterated

        for i in iterated:
            protoTimeTable = copy.deepcopy(self.timeTable)
            protoRawTimeTable = copy.deepcopy(self.rawTimeTable)

            for j in i: # 조합에서 각각의 시간표.

                protoTimeTable, protoRawTimeTable = self.timeTableCast( j, protoTimeTable, protoRawTimeTable)
                if protoTimeTable == None:
                    break
            if protoTimeTable != None:
                self.finalList.append(protoTimeTable)

        #return fixedList, sepList


    def setFixedElem(self): # 경우에 따라 데이터가 없을 수도 있음
        #global timeTable, rawTimeTable
        for i in self.fixedList:
            self.timeTable, self.rawTimeTable = self.timeTableCast( i, self.timeTable, self.rawTimeTable)

    def pprint(self):
        for i in self.finalList:
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
                    if not self.isPython3:
                        k = k.decode("UTF-8")
                    print(k.ljust((16 - len(k) * 2) + len(k), " "), end = "\t")

                print()
            print("=====================================================")
    
    def exportCsv(self, filepath):
        try:
            pass
        except Exception as e:
            print(e)
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

tt = TimeTabler()
tt.loadConfig()
tt.classParsing()
tt.pprint()