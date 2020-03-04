# importing glob for it file handling capabilities
import glob
# import re for its regex capabilities 
import re
# importing scipy as signal for use of its butterworth filter
from scipy import signal
# importing os module 
import os 

#fs = 1000  # Sampling frequency
#fc = 30  # Cut-off frequency of the filter
#w = fc / (fs / 2) # Normalize the frequency
#b, a = signal.butter(5, w, 'low')
#output = signal.filtfilt(b, a, signalc)

def findSizeofData(mainList):
    size = 0
    for x in mainList:
        for j in x:
            size += len(j)
    return size

#This function is the main function that will apply the butterworth filter to the dataset that we will be using.
#This fucntion will take the main 3D list as its input and will output a new list of the same size as its output.
#NOTE That the new list will be a filtered at 8hz, lowpass, and at first order.
def filterData(mainList):
    #fs = findSizeofData(mainList)  # Sampling frequency
    #fc = 8  # Cut-off frequency of the filter
    #w = fc / (fs / 2) # Normalize the frequency
    newMainList = []
    b, a = signal.butter(1, .008, 'low') #Apply a low pass, first order butterworth filter at 8hz to the 3-D dataset. 
    for x in mainList:
        sublist = []
        for j in x:
            if x != None:
                subList.append(list(signal.filtfilt(b, a, j, padlen=7)))
                #print(list(signal.filtfilt(b, a, j, padlen=5)))
        newMainList.append(list(subList))
        sublist.clear()
    return newMainList

# This function will calculate the Cop values for one block of values.
# This function takes a List[][] but will only get passed List[i] i.e List[0] and will work only with List[0][j] or whatever List[i] is passed in
# This fucntion will return two seperate Lists one of them being Copx and the other being Copy.
# Returns Copx first and then Copy
def calcCop(values):
    _copX = [] # Calculated like: -My/Fz
    _copY = [] # Calculated like: Mx/Fz
    for i in values:
        # print(-i[6])
        # print(i[4])
        _copX.append(-i[4]/i[2])
        _copY.append(i[3]/i[2])
        #print("Copx: " + str(-i[4]/i[2]))
        #print("Copy: " + str(i[3]/i[2]))
    return _copX, _copY


def calculateDisplacement(CopXA, CopXB):
    return abs(CopXB - CopXA)


# This is the main function that will calcualate all the extra values will need for each block of values.
def calculateValues(lineOfValues, timeValues):
    # Step #1 find COPx and COPy.
    # NOTE: the lineOfValues[i] looks like this: 
    # [0] = TimeStamp on its own list
    # [0] = Fx
    # [1] = Fy
    # [2] = Fz
    # [3] = Mx
    # [4] = My
    # [5] = Mz
    # [6] = CopX
    # [7] = CopY
    copX = [] #Calculated like: -My/Fz
    copY = [] #Calculated like: Mx/Fz
    copX, copY = calcCop(lineOfValues[0])
    
    print("Copx Max(Max AP): ", max(copX))
    print("Copx Min: ", min(copX))
    print("Copy Max(Max ML): ", max(copY))
    print("Copy Min: ", min(copY))
    print("Printing the displacement:")
    #for x in range(len(copX)-1):
    #    print(calculateDisplacement(copX[x], copX[x+1]))
    return 

# Creating the directory that we will be putting the new files into. 
# Directory 
directory = "Calculation Files"
# Parent Directory path 
parent_dir = os.getcwd()
# Path 
path = os.path.join(parent_dir, directory)

# Create the directory 
# 'Calculation Files' in 
# '/home / User / Documents' 
#print(os.path.isdir(path))
if os.path.isdir(path) == False:
    os.mkdir(path) 
    print("Directory '% s' created" % directory) 

#print(os.listdir(os.getcwd()))

# Create a list of all the text files in the the folder.
txtfiles = []
for file in glob.glob("*.txt"):
    txtfiles.append(file)

#print(txtfiles)
for Tfile in txtfiles:
    Tfile = Tfile.replace('.txt', 'CalculatedFile.txt')
    print(Tfile)
# We probably want to start transtioning when 
# Open each file.
f = open("BeforeDemoTest001Just a test.txt", "r") #Opens each file we are going to work with. 
# Read from the file line by line.
f1 = f.readlines()
mainList = []# We will be doing all of our calculations on this list.
timeList = [] # We will hold all the times on here.
timeSubList = [] 
subList = []
# Go throught each of the lines and using the Regex below to parse each string. 
for line in f1:
    res = re.findall(r"[-+]?\d*\.\d+|\d+", line)
    # Convert each number in from our regular expression from a string back into a float.
    for index in range(len(res)):
        # Convert the regex from string back into a float number so we can work with it.
        res[index] = float(res[index])
    # Currently we only want lines that have 1.0 in the title.
    if len(res) != 0 and res[0] == 1.0:
        # Append res to our subList.
        res.pop(0)
        timestamp = res.pop(0)
        timeSubList.append(timestamp)
        # Calculate COPX and COPY before hand and place it in the subList.
        res.append(-(res[4])/(res[2])) # COPX at position [6]
        res.append((res[3])/(res[2]))  # COPY at position [7]
        subList.append(res)
    # When we are finally see a 2.0 when can put everything we just put into subList to our mainList.
    elif len(res) != 0 and res[0] == 2.0:
        if len(subList) != 0:
            # Putting a copy of it in mainList so when we clear it we don't delete the list.
            mainList.append(list(subList))
            timeList.append(list(timeSubList))
            timeSubList.clear()
            subList.clear()
f.close()
        

#print(txtfiles)
fw = open("TestParse.txt","w+")
#print(len(mainList))
for i in mainList:
    fw.write("========================================================================================================================\n")
    for j in i:
        fw.write(str(j)+"\n")
fw.close()
#print("Done writing")

#for x in mainList:
#    for j in x:
#        print(j)
#print(findSizeofData(mainList))
#print(filterData(mainList))
#print("Before Filtering:")
#calculateValues(mainList)
#print("After Filtering:")
filterData(mainList)
#calculateValues(filterData(mainList), timeList)

'''
newlist = filterData(mainList)
for x in newlist:
    for j in x:
        print(j)
    print("========================================================================================================================\n")
'''
'''
for x in timeList:
    for j in x:
        print(j)
    print("========================================================================================================================\n")
'''
txtfiles = []
for file in glob.glob("*.txt"):
    txtfiles.append(file)
#print(txtfiles)


'''
JUST AS NOTES FOR NOW:
STEP 1):
break the data up into x,y,z,mx,my,mz,copx,copy
STEP 2):
Filter the data DONE 
STEP 3):
Find Max AP (Copx) and Max ML (Copy) per stage
Max Velocity Copx and Max Velocity Copy 
Displacement of X Velocity of X, Displacement of Y Velocity of Y 
Get the MAX and MEAN for each   
STEP 4):
FIND path length between time 2 and time 1
'''
