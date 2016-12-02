import copy

# create a schedule
class Schedule(object):

	# generate working schedule for workers
	def generateSchedule(self, calendar, workers, myDict, holiday, day, startDayIndex, dayCannotWork):
		# make the schedule look pretty
		weekList = copy.deepcopy(calendar)
		tracking = 0
		# check for holiday of following month
		for a in holiday['dayNextMonth']:
			for week in weekList:
				for i in range(0, len(week)):
					# if the date is repeated twice in schedule
					if a >= day:
						if week[i].isdigit() and a == int(week[i]):
							#count the time it appears and mark the second time
							# as holiday
							tracking += 1
							if tracking == 2:
								if i == 0:
									week[i] = "  *"
								else:
									week[i] = "*"
								tracking = 0
					# otherwise, find it and mark as holiday
					else:
						if week[i].isdigit() and a == int(week[i]):
							if i == 0:
								week[i] = "  *"
							else:
								week[i] = "*"
		# iterate through the week, indent to make it look pretty
		for week in weekList:
			for i in range(0, len(week)):
				if week[i] == "  ":
					if week[i] == weekList[0][0]:
						week[i] = "   "
					else:
						week[i] = " "
				else:
					# check for holiday in month and mark it
					for a in holiday['dayInMonth']:
						if week[i].isdigit() and a == int(week[i]):
							if i == 0:
								week[i] = "  *"
							else:
								week[i] = "*"
							holiday['dayInMonth'].remove(a)
							break
			# check for day nobody can work and mark it
			for i in range(0, len(week)):
				if week[i].isdigit():
					if i == 0 and 0 in dayCannotWork and 1 in dayCannotWork:
						week[i] = "! !"
					elif i == 0 and 0 in dayCannotWork:
						week[i] = "!|"
					elif i == 0 and 1 in dayCannotWork:
						week[i] = "!"
					elif i+1 in dayCannotWork:
						week[i] = "!"

		# schedule the weekends first
		self.weekendSchedule(weekList, workers) 
		# then the week days  
		self.weekSchedule(weekList, workers, myDict, startDayIndex)
		# rearrange shift to make sure everyone works the same number of shifts
		self.arrangeShift(weekList, workers, myDict['numShifts'])

		return weekList


	# schedule the weekend 
	def weekendSchedule(self, weekList, workers):
		# for each day of each week, if it's a working day
		for week in weekList:
			for i in range (0,len(week)):
				# if it's saturday
				if (i == 6) and (week[i].isdigit()):
					# for each person, check if they can work that day
					for person in workers:
						canWork = True
						for exception in person.constraints:
							if exception == 7:
								canWork = False
						# if they can work, assign that shift to them and move them to the end of list
						if canWork:
							week[i] = person.name
							person.counter += 1
							workers.insert(len(workers)-1, workers.pop(workers.index(person)))
							break
				
				# if it's sunday
				elif (i == 0) and (week[i].isdigit() or week[i] == "!|" or week[i] == "!"):
					if week[i].isdigit() or week[i] == "!":
						# continue searching until that morning shift is filled
						# for each person, check if they can work that day
						for person in workers:
							canWork = True
							for exception in person.constraints:
								if exception == 0:
									canWork = False
							# if they can work, assign that shift to them and move them to the end of list
							if canWork:
								if week[i].isdigit():
									week[i] = person.name + "|"
								else:
									week[i] = person.name + "|" + week[i]
								person.counter += 1
								workers.insert(len(workers)-1, workers.pop(workers.index(person)))
								break
					
					# continue searching until that evening shift is filled
					if week[i].endswith("|"):
						# for each person, check if they can work that day
						for person in workers:
							canWork = True
							for exception in person.constraints:
								if exception == 1:
									canWork = False
							# if they can work, assign that shift to them and move them to the end of list
							if canWork:
								week[i] += person.name
								person.counter += 1
								workers.insert(len(workers)-1, workers.pop(workers.index(person)))
								break

	#schedule week days
	def weekSchedule(self, weekList, workers, myDict, startDayIndex):
		for week in weekList:
			for person in workers:
				if person.name in week[0] or person.name in week[6]:
					workers.insert(len(workers)-1, workers.pop(workers.index(person)))
			for i in range (0,len(week)):
				canWorkThisDay = []
				work1DayApart = []
				work2DayApart = []
				# for each day of week, if it's a working day
				if (week[i].isdigit()):
					isFilled = False
					# for each person, if their constraints meet that day, they cannot work
					for person in workers:
						canWork = True
						for exception in person.constraints:
							if exception == i+1:
								canWork = False
						# if they can work, check if they have worked recently
						# if they did, check other people
						if canWork:
							canWorkThisDay.append(person)
							if (self.workedRecently(i, week, weekList, person) == 1):
								work1DayApart.append(person)
							elif (self.workedRecently(i, week, weekList, person) == 2):
								work2DayApart.append(person)
							else:
								# otherwise, assign shift to them and move them the end of list
								week[i] = person.name
								person.counter += 1
								workers.insert(len(workers)-1, workers.pop(workers.index(person)))
								isFilled = True
								break
					# if no one can fill the shift, change shift with another person
					# when some can't work the shift and some have already worked recently
					if not isFilled:
						# switch shift with people who can work but worked recently
						if not self.switchShift(i, week, weekList, canWorkThisDay, workers, startDayIndex):
							self.secondBestOption(work1DayApart, work2DayApart, week, i, workers)


	# check if they have worked recently
	# return 1 if they worked 1 day apart, 2 if 2 days apart or 0 if they haven't worked recently
	def workedRecently(self, i, week, weekList, person):
		# if it's Monday, check if it's in the first week or otherwise
		if (i==1):
			if week == weekList[0]:
				if (person.name in week[i-1]) or (person.name in week[i+1]):
					return 1
				elif (person.name in week[i+2]):
					return 2
			else:
				if (person.name in weekList[weekList.index(week)-1][6]) or (person.name in week[i+2]): 
					return 2
				elif (person.name in week[i-1]) or (person.name in week[i+1]):
					return 1
		# if it's Friday, check if it's in the last week or otherwise
		elif (i==5):
			if week == weekList[len(weekList)-1]:
				if (person.name in week[i-1]) or (person.name in week[i+1]):
					return 1
				elif (person.name in week[i-2]):
					return 2
			else:
				if (person.name in week[i-1]) or (person.name in week[i+1]):
					return 1
				elif (person.name in week[i-2]) or (person.name in weekList[weekList.index(week)+1][0]):
					return 2
		# otherwise, check normally
		else:
			if (person.name in week[i-1]) or (person.name in week[i+1]):
				return 1 
			elif (person.name in week[i-2]) or (person.name in week[i+2]):
				return 2
		return 0

	
	# switch shift with 2 previous closest shift
	def switchShift(self, i, week, weekList, canWorkThisDay, workers, startDayIndex):
		# return if it falls on first day of week or month
		if (weekList.index(week) == 0 and i == startDayIndex) or i == 1:
			return False
		# check switching for first previous closest day
		if self.checkShiftSwitch(i, week, weekList, canWorkThisDay, workers, 1):
			return True
		if (weekList.index(week) == 0 and i == startDayIndex + 1) or i == 2:
			return False
		# check switching for second previous closest day
		return self.checkShiftSwitch(i, week, weekList, canWorkThisDay, workers, 2)


	# see if can switch shift
	def checkShiftSwitch(self, i, week, weekList, canWorkThisDay, workers, indexShift):
		objectChange = 0
		# check if person doing previous day can do the day switching
		for a in canWorkThisDay:
			if week[i-indexShift] == a.name:
				objectChange = a
		# if can, see if anyone can take his old shift
		if objectChange != 0:
			week[i-indexShift] = "0"
			for person in workers:
				canWork = True
				for exception in person.constraints:
					if exception == i:
						canWork = False
				# if they can switch, switch their shifts and update counter
				if (canWork and self.workedRecently(i-indexShift, week, weekList, person) == 0 and
					self.workedRecently(i, week, weekList, objectChange) == 0):
					week[i-indexShift] = person.name
					person.counter += 1
					week[i] = objectChange.name
					workers.insert(len(workers)-1, workers.pop(workers.index(person)))
					return True
			# otherwise, resume state
			week[i-indexShift] = objectChange.name
			return False


	# secondbest option if no one can fill in the shifts
	def secondBestOption(self, work1DayApart, work2DayApart, week, i, workers):
		# if there are people working 2 days apart, give them the shift
		if len(work2DayApart) != 0:
			week[i] = work2DayApart[0].name
			work2DayApart[0].counter += 1
			workers.insert(len(workers)-1, workers.pop(workers.index(work2DayApart[0])))
		# otherwise if there are people working 1 day apart, give them the shift
		elif len(work1DayApart) != 0:
			week[i] = work1DayApart[0].name
			work1DayApart[0].counter += 1
			workers.insert(len(workers)-1, workers.pop(workers.index(work1DayApart[0])))


	# rearrange shift to make sure everyone works the same number of shifts
	def arrangeShift(self, weekList, workers, averageNumShifts):
		sameNumberShift = True
		# for each worker, if they work less than they suppose to
		# move them to start of list and stop to check first
		for person in workers:
			if person.counter < averageNumShifts:
				workers.insert(0, workers.pop(workers.index(person)))
				sameNumberShift = False
				break
		# see if arrange shift 2 days apart
		if not self.equalizeShift(averageNumShifts, sameNumberShift, weekList, workers, 0):
			# see if arrange shift 1 day apart
			if not self.equalizeShift(averageNumShifts, sameNumberShift, weekList, workers, 2):
				self.equalizeShift(averageNumShifts, sameNumberShift, weekList, workers, 1)

	
	# arrange shift so people do same amount of shifts
	def equalizeShift(self, averageNumShifts, sameNumberShift, weekList, workers, myRange):
		if not sameNumberShift:
			# check the remaining workers
			for a in range(1, len(workers)-1):
				for week in weekList:
					# if there are 8 workers, try to make each of time work once a week
					if len(workers) >= 8 and (workers[0].name in week or workers[0].name in week[0]):
						pass
					else:
						for i in range(1, len(week)-1):         
							# to ensure weekends are equally divide, check the week days only
							# check the shift of remaining workers
							if workers[a].name in week[i]:
								canWork = True
								# check exception of the worker working less
								for exception in workers[0].constraints:
									if exception == i+1:
										canWork = False
								# if he can work that shift, check if he has worked recently
								if canWork:
									# if he can, assign him to the shift,
									# change the workers' counter accordingly
									# move the first worker to last, call recursion to continue checking
									if self.workedRecently(i, week, weekList, workers[0]) == myRange:
										week[i] = week[i].replace(workers[a].name, workers[0].name)
										workers[0].counter += 1
										workers[a].counter -= 1
										workers.insert(len(workers)-1, workers.pop(0))
										self.arrangeShift(weekList, workers, averageNumShifts)
										return True
			return False

