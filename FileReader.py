# importing glob for it file handling capabilities
import glob
# import re for its regex capabilities 
import re
# importing scipy as signal for use of its butterworth filter
from scipy import signal
# importing os module 
import os 
# importing math
import math
# importing statistics 
import statistics

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

# This function will calculate the CopX and CopY values.
# This function will take MX, MY and FZ
# Returns Copx first and then Copy
def calcCop(mx, my, fz):
    _copX, _copY = 0, 0
    _copX = -my/fz
    _copY = mx/fz
    return _copX, _copY


def calculateDisplacement(CopA, CopB):
    return CopB - CopA

#def calculateVelocity(CopA, CopB, TimeA, TimeB):
#    return (CopB - CopA)/(TimeB - TimeA)

def calculateVelocity(Displacement, TimeA, TimeB):
    return Displacement/(TimeB - TimeA)

def calculatePathlength(displacementXA, displacementYA):
    return (math.sqrt(pow(displacementXA, 2) + pow(displacementYA, 2)))


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
    
    #print(len(lineOfValues))
    #print(len(timeValues))
    displacementX = []
    displacementY = []
    velocityX = []
    velocityY = []
    pathlength = []
    # Run a for loop with the range through one of the lists it shouldn't matter which one you choose because they should both be the same side.
    for index in range(len(lineOfValues) - 1):
        displacementX.append(calculateDisplacement(lineOfValues[index][6], lineOfValues[index + 1][6]))
        displacementY.append(calculateDisplacement(lineOfValues[index][7], lineOfValues[index + 1][7]))
        velocityX.append(calculateVelocity(displacementX[index], timeValues[index], timeValues[index + 1]))
        velocityY.append(calculateVelocity(displacementY[index], timeValues[index], timeValues[index + 1]))
        pathlength.append(calculatePathlength(displacementX[index], displacementY[index]))
    return displacementX, displacementY, velocityX, velocityY, pathlength

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
    print(file)

#newFileName = []
#for Tfile in txtfiles:
#    newFileName.append(Tfile.replace('.txt', '_CalculatedFile.txt'))
for current_file in txtfiles:
    newFileName = current_file.replace('.txt', '_CalculatedFile.txt')
    # We probably want to start transtioning when 
    # Open each file.
    f = open(current_file, "r")
    #f = open(txtfiles[0], "r")
    #f = open("BeforeDemoTest001Just a test.txt", "r") #Opens each file we are going to work with. 
    # Read from the file line by line.
    f1 = f.readlines()
    mainList = []# We will be doing all of our calculations on this list.
    timeList = [] # We will hold all the times on here.
    timeSubList = [] 
    subList = []
    maxApCopX, maxMLCopY = 0, 0
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
            copx, copy = calcCop(res[3], res[4], res[2])
            maxApCopX = max(maxApCopX, copx)
            maxMLCopY = max(maxMLCopY, copy)
            res.append(copx) # COPX at position [6], -My/Fz
            res.append(copy)  # COPY at position [7], Mx/Fz
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
        

    #Used only for debugging purposes only.
    #print(txtfiles)
    #fw = open("TestParse.txt","w+")
    #print(len(mainList))
    #for i in mainList:
    #    fw.write("========================================================================================================================\n")
    #    for j in i:
    #        fw.write(str(j)+"\n")
    #fw.close()
    #print("Done writing")

    #for x in mainList:
    #    for j in x:
    #        print(j)
    #print(findSizeofData(mainList))
    #print(filterData(mainList))
    #print("Before Filtering:")
    #calculateValues(mainList)
    #print("After Filtering:")
    #filterData(mainList)
    displacementX = []
    displacementY = []
    velocityX = []
    velocityY = []
    pathLength = []
    maxVelocityX, maxVelocityY = 0, 0
    minVelocityX, minVelocityY = 0, 0
    meanVelocityX, meanVelocityY = 0, 0
    filteredList = filterData(mainList)
    index = 0
    for stage in filteredList:
        displacementX, displacementY, velocityX, velocityY, pathLength = calculateValues(stage, timeList[index])
        maxVelocityX = max(velocityX)
        maxVelocityY = max(velocityY)
        meanVelocityX = statistics.mean(velocityX)
        meanVelocityY = statistics.mean(velocityY)
        index = index + 1
        break
    asbDisplacementX = [abs(value) for value in displacementX]
    asbDisplacementY = [abs(value) for value in displacementY]
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
    #txfiles = []
    #for file in glob.glob("*.txt"):
    #    txtfiles.append(file)
    #print(txtfiles)

    #print("Time Length: ", len(timeList))
    #print("DisplacementX: ", len(displacementX))
    #print("absdisplacement :", len(asbDisplacementX))
    #[print(asbDisplacementX[i]) for i in range(len(asbDisplacementX))]
    completeName = os.path.join(path, newFileName)
    file1 = open(completeName, "w")
    file1.write("Time\t CoPx\t Distance(d)\t Abs Distance\t Velocity\n")
    for i in range(len(timeList[0])):
        if i == 0:
            file1.write(str(timeList[0][i]) + '\t' +str(round(filteredList[0][i][6], 4)) + '\n')
        else:
            file1.write(str(timeList[0][i]) + '\t' + str(round(filteredList[0][i][6], 4)) + '\t' +
            str(round(displacementX[i-1], 4)) + '\t' + str(round(asbDisplacementX[i-1], 4)) + '\t' + str(round(velocityX[i-1], 4)) + "\n")

    file1.write("Max Range is: " + str(max(asbDisplacementX)) + "\n")
    file1.write("Mean Range is: " + str(statistics.mean(asbDisplacementX)) + "\n")
    file1.write("Peak Velocity is: " + str(max(velocityX)) + "\n")
    file1.write("Mean Velocity is: " + str(statistics.mean(velocityX)) + "\n")

    file1.write("\nTime\t CoPy\t Distance(d)\t Abs Distance\t Velocity\n")
    for i in range(len(timeList[0])):
        if i == 0:
            file1.write(str(timeList[0][i]) + '\t' + str(round(filteredList[0][i][7], 4)) + '\n')
        else:
            file1.write(str(timeList[0][i]) + '\t' + str(round(filteredList[0][i][7], 4)) + '\t' +
            str(round(displacementY[i-1], 4)) + '\t' + str(abs(round(asbDisplacementY[i-1], 4))) + '\t' + str(round(velocityY[i-1], 4)) +"\n")
    file1.write("Max Range is: " + str(max(displacementY)) + "\n")
    file1.write("Mean Range is: " + str(statistics.mean(displacementY)) + "\n")
    file1.write("Peak Velocity is: " + str(max(velocityY)) + "\n")
    file1.write("Mean Velocity is: " + str(statistics.mean(velocityY)) + "\n")
    file1.close()

'''
JUST AS NOTES FOR NOW:
STEP 1):
break the data up into x,y,z,mx,my,mz,copx,copy DONE
STEP 2):
Filter the data DONE 
STEP 3):
Find Max AP (Copx) and Max ML (Copy) per stage
Max Velocity Copx and Max Velocity Copy 
Displacement of X Velocity of X, Displacement of Y Velocity of Y 
Get the MAX and MEAN for each   
STEP 4):
FIND path length between time 2 and time 1
STEP 5):
output might look like this?
CoPx
Time    CoPx    Distance (d)  Abs Distance    Velocity
t1      -          -            -               -
t2      Copx1   t2 - t1       Abs(d1)         d1/(t2-t1)
.
.
.

Max Range = Max of Abs distance column
Mean Range = Mean of abs distance column

Peak Velocity = Max of Velocity column
Mean Velocity = Mean of Velocity column

*repeat these calculations for CoPY
~Calculate path length
#repeat all calculations for both AP and ML

'''
'''
NOTE on how to create files in another direcotry:
# Creating the directory that we will be putting the new files into. 
# Directory 
directory = "Calculation Files"
filename = "testy.txt"
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

completeName = os.path.join(path, filename)
file1 = open(completeName, "w")
file1.close()
'''