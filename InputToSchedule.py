import re
import json
from Employee import Employee
from Calendar import *

# PROGRAM GENERATING MONTH SCHEDULE
# INPUT: A DATE OF TYPE STRING (MONTH, DAY, YEAR)
# PERSON AND THEIR CONSTRAINTS. CONSTRAINTS ARE 0 TO 7, 0 FOR SUNDAY MORNING,
# 1 FOR SUNDAY EVENING, 2 -> 7 FOR MONDAY, TUESDAY, ETC.
# CONSTRAINTS IS A LIST OF INTEGERS
# HOLIDAY IS A STRING WITH DATE AND MONTH
# ACTION: 0 FOR GETTING MONTHLY SCHEDULE, 1 FOR GETTING PERSONAL SCHEDULE OF EACH PERSON
# PERSON'S NAME (TYPE STRING) (CASE INSENSITIVE) FOR PERSONAL SCHEDULE OF PARTICULAR PERSON

# convert input to generate schedule
class InputToSchedule(object):

    # initialize data, open file to read
    def __init__(self, inputLink):
        try:
            with open(inputLink) as data_file:
                data = json.load(data_file)
            self.readInput(data)
        except:
            print "Please check input link"
            print self.help()

    # read file
    def readInput(self, data):
        # instance to keep track
        inputString = ""
        employee = []
        holiday = []
        # if a key value match date pattern, keep track of it
        if re.compile("(?i)^(jan|feb|mar|apr|may|jun|jul|aug|\
            sep|oct|nov|dec)\s0?[0-7]\s\d{4}$").match(data['date'].strip()):
            inputString = data['date'].strip()
        else:
            print "Input is invalid, please check date"
            print self.help()
            return

        names = []
        # if any name is repeat, return
        for i in data['employees']:
            for name in names:
                if i['name'].upper() == name.upper():
                    print "Employee name is repeated"
                    print self.help()
                    return
            names.append(i['name'])

            # check if that person's constraints are out of range
            for value in i['constraints']:
                if value not in range(0,8):
                    print "Wrong employee constraints"
                    print self.help()
                    return
            # initialize a worker and append it to list
            employee.append(Employee(i['name'], i['constraints']))

        # if key value matches holiday
        if re.compile("^((\s?([0-2]?[0-9]|3[0-1])\/(0?[1-9]|1\
            [0-2]))?|\s?([0-2]?[0-9]|3[0-1])\/(0?[1-9]|1[0-2])(\s?,\s?([0-2]?[0-9]|3\
            [0-1])\/(0?[1-9]|1[0-2]))*)$").match(data['holiday'].strip()):
            days = data['holiday'].split(",")
            # keep track of holiday
            for day in days:
                holiday.append(day.strip())
        else:
            print "Input is invalid, please check holiday"
            print self.help()
            return

        # if provide enough info, return according to request
        if inputString != "" and len(employee) != 0 and 'action' in data:
            calendar = Calendar(inputString, employee, holiday).launch()
            
            # if asking for schedule of particular person, return schedule
            for person in employee:
                if type(data['action']) == unicode and data['action'].lower() == person.name.lower():
                    return self.personalSchedule(calendar, employee, data['action'].upper())
            # if asking for monthly schedule, return
            if data['action'] == 0:
                return self.getSchedule(calendar)
            # if asking for personal schedule of everyone, return
            elif data['action'] == 1:
                return self.personalSchedule(calendar, employee, 1)
            
            # otherwise, wrong input
            else:
                print "Please check action"
                print self.help()
                return
        else:
            print "Please provide all input"
            print self.help()
            return

    
    # print help if provide wrong input
    def help(self):
        help = "Usage of SCHEDULE GENERATOR\n"
        help += "key 'date':        a date of type string in format 'mmm dd yyyy'\n"
        help += "                   mmm is substring of name of month in English. ex: Jan, Feb, etc. (case insensitive)\n"
        help += "key 'employee':    A list of objects, each created with keys\n"
        help += "                   'name' - name of worker, type string (case insensitive)\n"
        help += "                   Name of each person must be different\n"
        help += "                   'constraints' - a list of days (type int) that worker cannot work\n"
        help += "                   0 for Sunday morning, 1 for Sunday evening, 2 for Monday, 3 for Tuesday, etc.\n"
        help += "key 'holiday':     a string of holidays, each separated by a comma (,)\n"
        help += "                   A holiday is marked with date and month in format dd/mm. ex: 19/6\n"
        help += "key 'action':      Action the user want to make\n"
        help += "                   0 for generating monthly schedule\n"
        help += "                   1 for generating personal schedule of everyone\n"
        help += "                   a string of a person's name for generating that particular person's schedule"
        return help

    
    def checkInput(self, data, inputString, holiday, employee):
        # if a key value match date pattern, keep track of it
        if re.compile("(?i)^(jan|feb|mar|apr|may|jun|jul|aug|\
            sep|oct|nov|dec)\s0?[0-7]\s\d{4}$").match(data['date'].strip()):
            inputString = data['date'].strip()
        else:
            print "Input is invalid, please check date"
            return False

        names = []
        # if any name is repeat, return
        for i in data['employees']:
            for name in names:
                if i['name'].upper() == name.upper():
                    print "Employee name is repeated"
                    return False
            names.append(i['name'])

            # check if that person's constraints are out of range
            for value in i['constraints']:
                if value not in range(0,8):
                    print "Wrong employee constraints"
                    return False
            # initialize a worker and append it to list
            employee.append(Employee(i['name'], i['constraints']))

        # if key value matches holiday
        if re.compile("^((\s?([0-2]?[0-9]|3[0-1])\/(0?[1-9]|1\
            [0-2]))?|\s?([0-2]?[0-9]|3[0-1])\/(0?[1-9]|1[0-2])(\s?,\s?([0-2]?[0-9]|3\
            [0-1])\/(0?[1-9]|1[0-2]))*)$").match(data['holiday'].strip()):
            days = data['holiday'].split(",")
            # keep track of holiday
            for day in days:
                holiday.append(day.strip())
        else:
            print "Input is invalid, please check holiday"
            return

    
    # get monthly schedule
    def getSchedule(self, calendar):
        # get schedule and calendar
        myCalendar = calendar['calendar']
        myWeekList = calendar['schedule']

        # formatting JSON file
        jsObj = {}
        jsObj['schedule'] = []
        day = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        for a in range(0, len(myCalendar)):
            for i in range(0, len(myCalendar[a])):
                if myCalendar[a][i].strip() == "":
                    pass
                else:
                    dayJs = {}
                    dayJs[myCalendar[a][i]] = {}
                    if myWeekList[a][i].strip() == "*":
                        dayJs[myCalendar[a][i]]['name'] = "Holiday"
                    elif myWeekList[a][i].strip() == "!":
                        dayJs[myCalendar[a][i]]['name'] = "Open shift"
                    else:
                        dayJs[myCalendar[a][i]]['name'] = myWeekList[a][i]
                    dayJs[myCalendar[a][i]]['day'] = day[i]
                    jsObj['schedule'].append(dayJs)

        # write file to output
        writeFile = open('Output.json', 'w')
        with writeFile as f:
            json.dump(jsObj, f)
        writeFile.close()
        
        print jsObj
        return jsObj


    # get personal schedule
    def personalSchedule(self, calendar, employee, p):
        # get schedule and calendar
        myCalendar = calendar['calendar']
        myWeekList = calendar['schedule']

        # formatting JSON file
        jsObj = {}
        day = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        for person in employee:
            jsObj[person.name] = []
            for a in range(0, len(myWeekList)):
                for i in range(0, len(myWeekList[a])):
                    if person.name in myWeekList[a][i]:
                        dayJs = {}
                        dayJs['date'] = myCalendar[a][i]
                        if myWeekList[a][i] == person.name:
                            dayJs['day'] = day[i]
                        elif myWeekList[a][i] == person.name + '|' + person.name:
                            dayJs['day'] = "Sunday morning and evening"
                        elif myWeekList[a][i].startswith(person.name):
                            dayJs['day'] = "Sunday morning"
                        else:
                            dayJs['day'] = "Sunday evening"
                        jsObj[person.name].append(dayJs)
        # if asking for schedule of particular person, get schedule
        if p != 1:
            personCheck = {}
            personCheck[p] = jsObj[p]
            jsObj = personCheck
        
        # write schedule out to file
        writeFile = open('Output.json', 'w')
        with writeFile as f:
            json.dump(jsObj, f)
        writeFile.close()
        
        print jsObj
        return jsObj


InputToSchedule("input.json")

