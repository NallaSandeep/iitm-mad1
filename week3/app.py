from jinja2 import Template
import sys
import pyhtml as h
import matplotlib.pyplot as plt
import csv

def main():
    fr = open('data.csv', 'r')
    csvreader = csv.reader(fr)
    header = next(csvreader)
    rows = []
    for row in csvreader:
        rows.append(row)
    if(len(sys.argv)>1):
        if(sys.argv[1]=='-s'):
            TEMPLATE=studentTemplate(header,rows)
        elif(sys.argv[1]=='-c'):
            TEMPLATE = courseTemplate(rows)
    else:
        TEMPLATE = wrongTemplate()
    template = TEMPLATE.render()
    fw=open('output.html','w')
    fw.write(template)
    fw.close()
    fr.close()

def studentTemplate(header,rows):
    # print('student')
    stId = sys.argv[2]
    value = 0
    for row in rows:
        if row[0] == stId:
            value += int(row[2])
    if(value==0):
        TEMPLATE = wrongTemplate()
    else:
        TEMPLATE = h.html(
            h.head(
                h.title('Student Data')
            ),
            h.body(
                h.h1('Student Details'),
                h.table(border='1')(
                    h.tr(
                        h.td(cell) for cell in header
                    ),
                    (h.tr(
                        h.td(cell) for cell in row
                    ) for row in rows if row[0] == stId
                    ),
                    h.tr(
                        h.td(colspan='2')('Total Marks'),
                        h.td(value)
                    )
                )
            )
        )
    return TEMPLATE

def courseTemplate(rows):
    # print('course')
    cId = sys.argv[2]
    # print(cId)
    value = 0
    max = 0
    data = {}
    for row in rows:
        # print(row[1],cId,row[1] == cId)
        if int(row[1]) == int(cId):
            i = int(row[2])
            # values += [i]
            # print(i not in data.keys())
            # print(i in data.keys())
            if (i not in data.keys()):
                data[i] = 1
            else:
                data[i] += 1
            # print(i)
            value += i
            if (i > max):
                max = i
    avg = value / len(rows)
    if (value == 0):
        TEMPLATE = wrongTemplate()
    else:
        # data = {'C': 20, 'C++': 15, 'Java': 30,'Python': 35}
        courses = list(data.keys())
        values = list(data.values())
        fig = plt.figure(figsize=(10, 5))
        # creating the bar plot
        plt.bar(courses, values)
        plt.xlabel("Marks")
        plt.ylabel("Frequency")
        # plt.title("Students enrolled in different courses")
        # plt.show()
        fig.savefig('my_plot.png')
        # Show plot
        # plt.show()
        TEMPLATE = h.html(
            h.head(
                h.title('Course Data')
            ),
            h.body(
                h.h1('Course Details'),
                h.table(border='1')(
                    h.tr(
                        h.td('Average Marks'),
                        h.td('Maximum Marks')
                    ),
                    h.tr(
                        h.td(avg),
                        h.td(max)
                    )
                ),
                h.img(src='my_plot.png')
            )
        )
    return TEMPLATE

def wrongTemplate():
    return h.html(
            h.head(
                h.title('Something Went Wrong')
            ),
            h.body(
                h.h1('Wrong Inputs'),
                h.p('Something went wrong')
            )
        )

if __name__=='__main__':
    main()
