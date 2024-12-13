file_new_master = open("../scripts/db_master.csv", mode='r', encoding='utf-8')
file_old_master = open("../scripts/old_master_db.csv", mode='r', encoding='utf-8')

file_corrected_master = open("../scripts/corrected_master_db.csv", mode='a', encoding='utf-8')

# Gather all properties and their descriptions
new_master = []
for line in file_new_master:
    elements = line.split(",")
    elements[len(elements)-1] = elements[len(elements)-1].replace("\n","")

    if len(elements) > 1:
        label = elements[1]
        value = ""
        i = 2
        while i < len(elements):
            value += elements[i]
            i += 1
        value.replace(",", "")
    
        new_master.append((label, value))
# Sort all properties alphabetically
new_master.sort(key=lambda x: x[0])

# Gather all properties and their descriptions
old_master = []
for line in file_old_master:
    elements = line.split(",")
    elements[len(elements)-1] = elements[len(elements)-1].replace("\n","")

    value = elements[6].replace(" Example:  value:", "")
    label = elements[2]
    decider = elements[5]

    old_master.append((label, value, decider))
# Sort all properties alphabetically
old_master.sort(key=lambda x: x[0])

# both lists are compared and a new line is created in the corrected_master, if a match is found
# i is for new_master, j is for old_master
new_master_length = len(new_master)
old_master_length = len(old_master)
i = j = 0
while i < new_master_length and j < old_master_length:
    if new_master[i][0] < old_master[j][0]:
        i += 1
    elif old_master[j][0] < new_master[i][0]:
        j += 1
    else:
        file_corrected_master.write(new_master[i][0] + "," + old_master[j][2] + "," + new_master[i][1] + "\n")
        i +=1
        j +=1
