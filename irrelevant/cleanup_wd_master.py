import re

file_old_master = open("wd_master_old.csv", mode='r', encoding='utf-8')

file_new_master = open("../scripts/wd_master.csv", mode='a', encoding='utf-8')

# Gather all properties and their descriptions
old_master = []
for line in file_old_master:
    elements = re.split(r'''((?:[^,"']|"[^"]*"|'[^']*')+)''', line)[1::2]
    elements[3] = elements[3].replace("\n","")

    value = elements[3]
    label = elements[2]
    decider = elements[1].replace("true", "True").replace("false", "False")

    old_master.append((label, value, decider))
# Sort all properties alphabetically
old_master.sort(key=lambda x: x[0])

for element in old_master:
    file_new_master.write("%s,%s,%s\n" % (element[0], element[2], element[1]))