from datetime import datetime
from Schedule import Schedule
import re
import math
import copy

#Create a calendar and working schedule
# given the string date, workers and their constraints and holidays
class Calendar(object):

    #initialize calendar with a date in type string
    def __init__(self, strDate, workers, holiday):
        for person in workers:
            person.name = person.name.upper()
        self.strDate = strDate
        self.workers = workers
        self.holiday = holiday

    
    # launch schedule and return according to request
    def launch(self):
        # convert the date
        date = datetime.strptime(self.strDate, '%b %d %Y')
        month = date.month
        year = date.year
        day = date.day

        # get schedule
        return self.printCalendar(day, month, year) 

    
    # print out the calendar
    def printCalendar(self, day, month, year):

        #months[i] = name of month i
        #leave empty so that months[1] = "January"
        months = ["", "January", "February", "March", "April", "May", "June", 
        "July", "August", "September", "October", "November", "December"]
        
        #days[i] = number of days in month i
        days = [0,31,28,31,30,31,30,31,31,30,31,30,31]

        #check for leap year
        if (year % 4 == 0) and (year % 100 != 0) or (year % 400 == 0):
            days[2] = 29

        # calculate the number of shifts and weeks covered
        myDict = self.calculate(len(self.workers), month, year, day, days[month], self.dayCannotWork())

        #print calendar header
        print "        " + months[month] + " " + str(year)
        print " S   M   Tu   W  Th   F   S"

        # get calendar and schedule
        myCalendar = self.generateCalendar(month, day, year, days, myDict)
        myWeekList = Schedule().generateSchedule(myCalendar, self.workers, myDict, 
            self.checkHoliday(month, day), day, self.day(month, day, year), self.dayCannotWork())

        #print them out
        for i in range(0,len(myWeekList)):
            print " " + '  '.join(p for p in myCalendar[i])
            print '   '.join(p for p in myWeekList[i])

        return {'calendar': myCalendar, 'schedule': myWeekList}

    
    # generate the calendar
    def generateCalendar(self, month, day, year, days, myDict):
        #concatenate calendar
        calendar = []
        for i in range(0, myDict['numWeeks']):
            calendar.append([])

        counter = 0
        
        # for the beginning of the month that does not work, append empty string
        for i in range (0, self.day(month, day, year)):
            calendar[counter].append("  ")
        
        # for days that work, append date of day to mark
        for i in range(day, days[month]+1):
            if i < 10:
                calendar[counter].append("0" + str(i))
            else:
                calendar[counter].append(str(i))
            # if it reaches Saturday, increment counter to enter new week
            if (self.day(month, i, year) == 6):
                counter += 1

        # print out the excess day needed to complete a round
        for i in range(0, myDict['excessDay']):
            if i < 9:
                calendar[counter].append("0" + str(i+1))
            else:
                calendar[counter].append(str(i+1))
            # if it reaches Saturday, increment counter to enter new week
            if month != 12:
                if (self.day(month+1, i+1, year) == 6):
                    counter += 1
            else:
                if (self.day(1, i+1, year+1) == 6):
                    counter += 1
        
        # append the not working days of last week with empty string
        while (len(calendar[len(calendar)-1]) < 7):
            calendar[len(calendar)-1].append("  ")

        return calendar


    # check for input holiday
    def checkHoliday(self, month, startDay):

        # remove any repeat days in holiday
        for day in self.holiday:
            if self.holiday.count(day) > 1:
                for number in range(0, self.holiday.count(day)-1):
                    self.holiday.remove(day)
        dayInMonth = []
        dayNextMonth = []
        
        #split the date and month
        for day in self.holiday:
            myDay = day.split("/")
            # append holiday this month and following month in different list
            if int(myDay[1]) == month and int(myDay[0]) >= startDay:
                dayInMonth.append(int(myDay[0]))
            elif int(myDay[1]) == month+1:
                dayNextMonth.append(int(myDay[0]))
        
        return {'dayInMonth': dayInMonth, 'dayNextMonth': dayNextMonth}

    
    # day that nobody can work
    def dayCannotWork(self):

        # remove any repeat constraints of each person
        for person in self.workers:
            for i in person.constraints:
                if person.constraints.count(i) > 1:
                    for number in range(0, person.constraints.count(i)-1):
                        person.constraints.remove(i)
        dayCannotWork = copy.deepcopy(self.workers[0].constraints)
        toRemove = []

        # check if there is a day nobody can work
        for day in dayCannotWork:
            for person in self.workers:
                if day not in person.constraints:
                    toRemove.append(day)
                    break
        for i in toRemove:
            dayCannotWork.remove(i)
        return dayCannotWork
    
    
    # calculate the number of shifts and weeks covered to complete round
    def calculate(self, numWorkers, month, year, startDay, totalDayOfMonth, dayCannotWork):

        workingDays = totalDayOfMonth - startDay + 1
        indexFirstDay = self.day(month, startDay, year)
        totalShift = 0
        # number of shifts in the first week of month
        if (indexFirstDay != 0):   
            totalShift += 6 - indexFirstDay + 1
        else:
            totalShift += 8 #each week has 8 shifts
        
        remainingDays = workingDays - (6 - indexFirstDay + 1)
        # residual is the number of days in the last week of month
        # calculate number of shifts in that remaining week
        residual = remainingDays % 7
        if residual == 1:
            totalShift += 2
        elif residual != 0:
            totalShift += 2 + residual - 1

        # calculate number of shifts in the remaining full weeks
        totalShift += (remainingDays - residual) / 7 * 8

        # if there is a day nobody can work, decrement shift of that day
        for day in dayCannotWork:
            for i in range(startDay, totalDayOfMonth+1):
                if self.day(month, i, year) == 0 and (day == 1 or day == 0):
                    totalShift -= 1
                elif self.day(month, i, year)+1 == day:
                    totalShift -= 1
        
        # if there is a holiday, if it falls on sunday
        # total shift decrement by 2, otherwise, decrement by 1
        for i in self.checkHoliday(month, startDay)['dayInMonth']:
            if self.day(month, i, year) == 0 and 0 in dayCannotWork and 1 in dayCannotWork:
                pass
            elif self.day(month, i, year) == 0 and (0 in dayCannotWork or 1 in dayCannotWork):
                totalShift -= 1
            elif self.day(month, i, year) == 0:
                totalShift -= 2
            elif (self.day(month, i, year)+1) in dayCannotWork:
                pass
            else:
                totalShift -= 1

        return self.getInfo(totalShift, numWorkers, indexFirstDay, workingDays,
            self.checkHoliday(month, startDay)['dayNextMonth'], dayCannotWork, month, year)


    # generate other info
    def getInfo(self, totalShift, numWorkers, indexFirstDay, workingDays, extraHolidays, dayCannotWork, month, year):
        completeRound = 0
        # when a round hasn't completed
        while (totalShift % numWorkers != 0):
            isHoliday = False
            completeRound +=1
            for i in extraHolidays:
                if i == completeRound:
                    isHoliday = True
                    break
            if not isHoliday:
                if month < 12: # if it's december
                    # increment the days and shifts
                    # if an excess day falls on Sunday, increment shift by 2
                    if self.day(month+1, completeRound, year) == 0 and 0 in dayCannotWork and 1 in dayCannotWork:
                        pass
                    elif self.day(month+1, completeRound, year) == 0 and (0 in dayCannotWork or 1 in dayCannotWork):
                        totalShift += 1
                    elif self.day(month+1, completeRound, year) == 0:
                        totalShift += 2
                    elif (self.day(month+1, completeRound, year)+1) in dayCannotWork:
                        pass
                    else:
                        totalShift +=1
                else:
                    # increment the days and shifts
                    # if an excess day falls on Sunday, increment shift by 2
                    if self.day(1, completeRound, year+1) == 0 and 0 in dayCannotWork and 1 in dayCannotWork:
                        pass
                    elif self.day(1, completeRound, year+1) == 0 and (0 in dayCannotWork or 1 in dayCannotWork):
                        totalShift += 1
                    elif self.day(1, completeRound, year+1) == 0:
                        totalShift += 2
                    elif (self.day(1, completeRound, year+1) + 1) in dayCannotWork:
                        pass
                    else:
                        totalShift +=1
                        
        # calculate number of weeks covered and the average shift of each worker
        numWeeks = int(math.ceil(float(workingDays + completeRound + indexFirstDay)/7))
        averageNumShifts = totalShift / numWorkers

        return {'numWeeks': numWeeks, 'numShifts': averageNumShifts, 'excessDay': completeRound}
    
    
    # Given the month (M), day (D), and year (Y), return which day
    # of the week it falls on. 1 for January, 2 for February, and so forth.
    # 0 for Sunday, 1 for Monday, and so forth.
    def day(self, M, D, Y):
        y = Y - (14 - M) / 12
        x = y + y/4 - y/100 + y/400
        m = M + 12 * ((14 - M) / 12) - 2
        d = (D + x +(31*m)/12) % 7
        return d
