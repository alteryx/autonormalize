import csv
import random

# csvData = [['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']]

# for x in range(5000):
#     b = random.randint(0, 50)
#     c = random.randint(0, 5)
#     d = random.randint(-20, 20)
#     elem = [x, b, c, d, 2*x, x+b, b+c, x+b+c, b*c*x*2, b*c, b > 20]
#     for x in range(11):
#         elem[x] = str(elem[x])
#     csvData.append(elem)

# with open('example_1', 'w') as csvFile:
#     writer = csv.writer(csvFile)
#     writer.writerows(csvData)

# csvFile.close()

# csvData = [['A', 'B', 'C', 'D', 'E', 'F', 'G']]

# for x in range(5000):
#     b = random.randint(0, 25)
#     c = random.randint(0, 3)
#     d = random.randint(-10, 20)
#     elem = [x, b, c, d, c != 1, b+c, b+c+d]
#     for x in range(7):
#         elem[x] = str(elem[x])
#     csvData.append(elem)

# with open('example_2', 'w') as csvFile:
#     writer = csv.writer(csvFile)
#     writer.writerows(csvData)

# csvFile.close()

# csvData = [['A', 'B', 'C', 'D', 'E', 'F', 'G']]

# for x in range(100000):
#     b = random.randint(0, 25)
#     c = random.randint(0, 3)
#     d = random.randint(-10, 20)
#     elem = [x, b, c, d, c != 1, b<10, c+d]
#     for x in range(7):
#         elem[x] = str(elem[x])
#     csvData.append(elem)

# with open('example_3', 'w') as csvFile:
#     writer = csv.writer(csvFile)
#     writer.writerows(csvData)

# csvFile.close()


# csvData = [['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']]

# for x in range(400000):
#     b = random.randint(0, 25)
#     c = random.randint(0, 3)
#     d = random.randint(-10, 20)
#     elem = [x, b, c, d, c != 1, b<10, c+d, b < 20, c != 1 and b < 20, d+b+c, b*d, b*c*d]
#     for x in range(7):
#         elem[x] = str(elem[x])
#     csvData.append(elem)

# with open('example_4', 'w') as csvFile:
#     writer = csv.writer(csvFile)
#     writer.writerows(csvData)

# csvFile.close()

# csvData = [['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N']]

# for x in range(400000):
#     b = random.randint(0, 25)
#     c = random.randint(0, 3)
#     d = random.randint(-10, 20)
#     elem = [x, b, c, d, c != 1, b<10, c+d, b < 20, c != 1 and b < 20, d+b+c, b*d, b*c*d, b*c, c%2 == 0]
#     for x in range(14):
#         elem[x] = str(elem[x])
#     csvData.append(elem)

# with open('example_5', 'w') as csvFile:
#     writer = csv.writer(csvFile)
#     writer.writerows(csvData)

# csvFile.close()


# csvData = [['A', 'B', 'C', 'D', 'E', 'F', 'G']]

# for x in range(400000):
#     a = random.randint(0, 25)
#     b = random.randint(0, 3)
#     c = random.randint(-10, 20)
#     d = a + b <= 5
#     e = (a + c)%8
#     f = random.randint(0, 200)
#     g = f <= 80
#     elem = [a, b, c, d, e, f, g]
#     for x in range(7):
#         elem[x] = str(elem[x])
#     csvData.append(elem)

# with open('example_norm', 'w') as csvFile:
#     writer = csv.writer(csvFile)
#     writer.writerows(csvData)

# csvFile.close()


csvData = [['A', 'B', 'C', 'D', 'E', 'F']]

for x in range(400000):
    a = random.randint(0, 25)
    b = random.randint(0, 3)
    c = random.randint(-10, 20)
    d = a <= 15 and b >= 2
    e = a + b
    f = a+b+c >= 15
    elem = [a, b, c, d, e, f]
    for x in range(6):
        elem[x] = str(elem[x])
    csvData.append(elem)

with open('example_make_index', 'w') as csvFile:
    writer = csv.writer(csvFile)
    writer.writerows(csvData)

csvFile.close()
