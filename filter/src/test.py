import csv

data = """5,Gladiator,2000,Action,8.5
6,The Departed,2006,Crime,8.5
7,The Prestige,2006,Mystery,8.5
8,Memento,2000,Mystery,8.4
9,The Social Network,2010,Drama,7.8
10,Whiplash,2014,Drama,8.5
11,La La Land,2016,Drama,8.0
12,Moonlight,2016,Drama,7.4
13,Parasite,2019,Drama,8.5"""

# Split the data into lines
lines = data.splitlines()

# Parse CSV
parsed_data = list(csv.reader(lines))

# Print each row
for row in parsed_data:
    print(row)


# for line in lines:
#     fields = line.split(",")
#     print(fields)