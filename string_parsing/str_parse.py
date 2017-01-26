# import the regex module
import re
import datetime

happy_days = {'monday': 1, 'tuesday': 2, 'wednesday': 3, 'thursday': 4, 'friday': 5, 'saturday': 6, 'sunday': 7}
happy_day_nums = [1, 2, 3, 4, 5, 6, 7]
times = []
# set the string (this would be within the iterative loop, when
# looping over the foursquare string results
str = "served monday-sunday | 10:00 a.m.  - 6:30 p.m. dine-in bar area only. $2.95 minimum beverage " \
      "purchase per guest.	4b25390ef964a520466e24e3	" \
      "2515 S. Loop W. Fwy. (btwn Buffalo Spdwy. & Kirby)"
# use regex to find matches to any of the days of week, and even the three letter abbreviation
# to those days
# (just incase they are represented like that by the enduser)
m = re.findall(r"(everyday|every day|thru|through|-|and|&|monday|tuesday|wednesday|thursday"
               r"|friday|saturday|sunday|mon|tue|wed|thur|fri|sat|sun)", str.lower())[0:3]

t = re.findall(r'\d{1,2}(?:(?:am|pm)|(?::\d{1,2})(?:am|A.M.|a.m.|pm|p.m.|P.M.| am| A.M.| a.m.| pm| p.m.| P.M.)?)', str)
times.append(t[0])
times.append(t[1])

if len(times[0]) < 3:
    times[0] += ':00'
if len(times[1]) < 3:
    times[1] += ':00'
print times
if m[0] != 'everyday' or m[0] != 'every day':
    if m[1] == '-' or m[1] == 'thru' or m[1] == 'through':
        start_day = happy_days.get(m[0])
        end_day = happy_days.get(m[2])
        days = [i for i in happy_day_nums if start_day <= i <= end_day]
    elif m[1] == 'and' or m[1] == '&':
        days = [happy_days.get(m[0]), happy_days.get(m[2])]
        print days
if m[0] == 'everyday' or m[0] == 'every day':
    days = happy_day_nums
print days

currenttime = datetime.datetime.now().time().strftime("%H:%M")
for time in times:
    if(re.findall('p.m.|pm', t[0])):
        time = time.replace("p", 'P')
        time = time.replace('.', '')
        time = time.replace('m', 'M')
        # time = ("""%s%s""" % (time, " PM"))
        time = datetime.datetime.strptime(time, '%I:%M %p')
        time = time.strftime("%H:%M %p")
        time = time[:-3]
    else:
        time = time.replace("a", "A")
        time = time.replace('.', '')
        time = time.replace('m', 'M')
        # time = ("""%s%s""" % (time, " AM"))
        time = datetime.datetime.strptime(time, '%I:%M %p')
        time = time.strftime("%H:%M %p")
        time = time[:-3]
    print time

# l = times[1]
# if "10:00" <= currenttime <= "13:00":
#     if l >= "10:00" and l >= "12:00":
#         l = ("""%s%s""" % (l, " AM"))
#     else:
#         l = ("""%s%s""" % (l, " PM"))
# else:
#     l = ("""%s%s""" % (l, " PM"))
#     l = datetime.datetime.strptime(l, '%I:%M %p')
#     l = l.strftime("%H:%M %p")
#     l = l[:-3]
# print l
