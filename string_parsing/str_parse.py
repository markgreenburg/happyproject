# # import the regex module
# import re
# import datetime
#
# happy_days = {'monday': 1, 'tuesday': 2, 'wednesday': 3, 'thursday': 4, 'friday': 5, 'saturday': 6, 'sunday': 7}
# happy_day_nums = [1, 2, 3, 4, 5, 6, 7]
# times = []
# # set the string (this would be within the iterative loop, when
# # looping over the foursquare string results
# str = "8:00am - 7:30pm ; monday - friday (in bar & patio area only)"
# # use regex to find matches to any of the days of week, and even the three letter abbreviation
# # to those days
# # (just incase they are represented like that by the enduser)
# m = re.findall(r"(everyday|every day|thru|through|-|and|&|monday|tuesday|wednesday|thursday"
#                r"|friday|saturday|sunday|mon|tue|wed|thur|fri|sat|sun)", str.lower())[0:3]
#
# t = re.findall(r'\d{1,2}(?:(?:am|pm)|(?::\d{1,2})(?:am|A.M.|a.m.|pm|p.m.|P.M.| am| A.M.| a.m.| pm| p.m.| P.M.)?)', str)
# times.append(re.findall('\d+:\d\d|\d+', t[0]))
# times.append(re.findall('\d+:\d\d|\d+', t[1]))
# if len(times[0][0]) < 3:
#     times[0][0] += ':00'
# if len(times[1][0]) < 3:
#     times[1][0] += ':00'
#
# if m[0] != 'everyday' or m[0] != 'every day':
#     if m[1] == '-' or m[1] == 'thru' or m[1] == 'through':
#         start_day = happy_days.get(m[0])
#         end_day = happy_days.get(m[2])
#         days = [i for i in happy_day_nums if start_day <= i <= end_day]
#         print days
#     elif m[1] == 'and' or m[1] == '&':
#         days = [happy_days.get(m[0]), happy_days.get(m[2])]
#         print days
# if m[0] == 'everyday' or m[0] == 'every day':
#     days = happy_day_nums
#     print days
#
# currenttime = datetime.datetime.now().time().strftime("%H:%M")
# print currenttime
# m = times[0][0]
#     if "10:00" <= currenttime <= "13:00":
#     if m >= "07:00" and m >= "12:00":
#         m = ("""%s%s""" % (m, " AM"))
#     else:
#         m = ("""%s%s""" % (m, " PM"))
# else:
#     m = ("""%s%s""" % (m, " PM"))
#     m = datetime.datetime.strptime(m, '%I:%M %p')
#     m = m.strftime("%H:%M %p")
#     m = m[:-3]
# print m
#
# l = times[1][0]
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
