import argparse
from datetime import datetime, timedelta
import os
from itertools import combinations

parser = argparse.ArgumentParser(description="OpenX Task 2 Help",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-c", "--calendars", nargs=1, type=str, required=True, help="path from root to calendar .txt files")
parser.add_argument("-d", "--duration-in-minutes",  nargs=1, type=int, required=True, help="how many minutes people should be available")
parser.add_argument("-m", "--minumum-people", "--minimum-people",  nargs=1, type=int, required=True, help="minimum number of people that must be available")
args = parser.parse_args()

if args.minumum_people[0]:
    min_people = args.minumum_people[0]
else:
    min_people = args.minimum_people[0]

currdatetime = datetime(2022,7,1,9,0,0)

path = os.getcwd() + args.calendars[0]
path = os.path.normpath(path)

class Person:
    def __init__(self, name, dateS, dateE, availability):
        self.name = name
        self.dateS = dateS
        self.dateE = dateE
        self.availability = availability

people=[]

for filename in os.listdir(path):
    name = os.path.splitext(filename)[0]
    busy = []
    with open(os.path.join(path, filename), 'r') as f:
        for line in f:
            busy.append(line.strip('\n'))
    dateS=[]
    dateE=[]
    #format busy dates for every person
    for dates in busy:
        if (" - ") in dates:
            dates = dates.split(" - ")
            date1 = datetime.strptime(str(dates[0]), '%Y-%m-%d %H:%M:%S')
            date2 = datetime.strptime(str(dates[1]), '%Y-%m-%d %H:%M:%S')
            if date2<date1:
                sdate = date2
                edate = date1
            else:
                sdate = date1
                edate = date2
        else:
            sdate = datetime.strptime(str(dates), '%Y-%m-%d')
            sdate = sdate.replace(hour=00,minute=00,second=00)
            edate = datetime.strptime(str(dates), '%Y-%m-%d')
            edate = edate.replace(hour=23,minute=59,second=59)
        dateS.append(sdate) #append date-starts
        dateE.append(edate) #append date-ends
    availability = [] #this remains empty for now as it'll be calculated later
    p = Person(name, dateS, dateE, availability)
    people.append(p)

#Find maximum date that we will be generating dates up to
nearest_max = datetime(1,1,1)
for person in people:
    for date in person.dateE:
        if date>nearest_max:
            nearest_max = date + timedelta(seconds=1)

#Function that generates datetime objects to fill person.availability as possible dates from date_from to date_to (date_range)
def generate_datetimes(date_from, date_to, person):
    amount = (date_to-date_from).total_seconds()
    amount = int((amount/60)/5)+1
    #create new datetime objects increasing by 5 minutes
    dates = [date_from + timedelta(minutes=5*x) for x in range(0, amount)]
    for date in dates:
        person.availability.append(date)

for person in people:
    min_before = 0
    min_before = currdatetime
    #this loop checks every start date of a person
    for i, dateStart in enumerate(person.dateS): 
        max_before = dateStart - timedelta(minutes = args.duration_in_minutes[0]) #maximum available date considering date in that loop and task duration
        if i == 0:
            if max_before>min_before: #if first date is later than current date, then generate availability datetimes
                generate_datetimes(min_before,max_before,person)
        else:
            if max_before>person.dateE[i-1]: #if current maximum available date is later than last busy ending date then generate datetimes and overwrite minimum (start) date
                min_before = person.dateE[i-1] + timedelta(seconds=1)
                generate_datetimes(min_before,max_before,person)

    min_after = person.dateE[len(person.dateE)-1] + timedelta(seconds=1)
    generate_datetimes(min_after,nearest_max,person)

#Make a list of indexes (cause number of people may vary)
list_indexes = []
for i in range(0, len(people)):
    list_indexes.append(i)

#Make a list to store dates from every possible combination output
computed_dates = []

#Get the combinations as list
combinations_2 = list(combinations(list_indexes, min_people))
print(combinations_2)

#Iterate through list
for comb in combinations_2:
    comp = []   #for every combination create a list to store the lists in that combination
    for item in comb:   #iterate through indexes of person combinations
        comp.append(set(people[item].availability))
    output = set.intersection(*comp)
    computed_dates.append(min(output)) #append the nearest date from available dates

nearest_date = min(computed_dates)
index_of = combinations_2[computed_dates.index(nearest_date)]

print(nearest_date,"For workers:",index_of)