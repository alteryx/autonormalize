import csv
import random

def generate_example_3():
    csvData = [['A', 'B', 'C', 'D', 'E', 'F', 'G']]

    for x in range(100000):
        b = random.randint(0, 25)
        c = random.randint(0, 3)
        d = random.randint(-10, 20)
        elem = [x, b, c, d, c != 1, b<10, c+d]
        for x in range(7):
            elem[x] = str(elem[x])
        csvData.append(elem)

    with open('example_3', 'w') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(csvData)

    csvFile.close()
