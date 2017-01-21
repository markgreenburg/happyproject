# import the regex module
import re

happy_days = {'monday': 1, 'tuesday': 2, 'wednesday': 3, 'thursday': 4, 'friday': 5, 'saturday': 6, 'sunday': 7}
happy_day_nums = [1, 2, 3, 4, 5, 6, 7]
# set the string (this would be within your iterative loop, when
# looping over your foursquare string results
str = "served monday-friday | 3:00 - 6:30 p.m. dine-in bar area only. $2.95 minimum beverage " \
      "purchase per guest.	4b25390ef964a520466e24e3	" \
      "2515 S. Loop W. Fwy. (btwn Buffalo Spdwy. & Kirby)"
# use regex to find matches to any of the days of week, and even the three letter abbreviation
# to those days
# (just incase they are represented like that by the enduser)
m = re.findall(r"(everyday|thru|through|-|and|&|monday|tuesday|wednesday|thursday"
               r"|friday|saturday|sunday|mon|tue|wed|thur|fri|sat|sun)", str.lower())[0:3]

if m[0] != 'everyday':
    if m[1] == '-' or m[1] == 'thru' or m[1] == 'through':
        start_day = happy_days.get(m[0])
        end_day = happy_days.get(m[2])
        days = [i for i in happy_day_nums if start_day <= i <= end_day]
        print days
    elif m[1] == 'and' or m[1] == '&':
        days = [happy_days.get(m[0]), happy_days.get(m[2])]
        print days
if m[0] == 'everyday':
    days = happy_day_nums
    print days
