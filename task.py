###########################################################################################
# Python Script Reads the .lib file and list                                                                  
#                                                                                   
# Description: Scrapes .lib files to collect cell information                       
#                                                                                   
# <CELL_NAME> <DRIVE STRENGTH> <NO. of PINS> <AREA> <DENSITY> <CELL FOOTPRINT>   
# <CELL LEAKAGE POWER> <PIN NAME> <DIRECTION>  <INPUT CAPACITENCE> <OUTPUT CAPACITENCE>                  
# <RELATED PIN> <CELL RISE AVERAGE> <RISE TRANASITION AVERAGE> <CELL FALL AVERAGE>    
# <FALL TRANSITION> <DEFAULT OPERATING CONDITIONS> <PATH of the FILE>
#                                                                                   
# Name - Olarewaju Abraham                                                          
# Date - 06/28/2022                                                                 
#                                                                                    
# Microsoft Corporation                                                                     
############################################################################################


import os
import io
import glob
import gzip
import sys
import re


labels = ["CELL NAME:", 'VT:', "#", "AREA:", "DENSITY:", "CELL FP:", "CELL LP:", "PN:", "DIRECT:", "INCAP:", "OUTCAP:", "RP:", 'CR:', 'RT:', 'CF:', 'FT:', "PATH:" ,'DOC:']
format_string = "{:<34} {:<5} {:<4} {:<10} {:<11} {:<10} {:<11} {:<5} {:<8} {:<12} {:<12} {:<10} {:<10} {:<10} {:<10} {:<9} {:<34} {:<34}"

lib_file = "/home/t-oabraham/Desktop/tcbn03e_bwph169l3p48cpd_base_elvtssgnp_0p675v_125c_cworst_CCworst_T_hm_lvf.lib.gz" #path of the file
path = lib_file

if re.search('.gz', lib_file):                      #if the file is gz type, read byte
    lib_file = gzip.open(lib_file, 'rb')
    with io.TextIOWrapper(lib_file, encoding='utf-8') as file:                
        cell_text = file.readlines()                #place the contents of the file in cell_text
        
else:                                       # else just read the file
    libfile = open(lib_file, 'r')
    with open(lib_file,'r') as file:                #read file
        cell_text = file.readlines()            #place the contents of the file in cell_text

print('\n')
print(format_string.format(*labels))                #print the labels of the columns first 
print('\n', end ="")

f = open("msft_confidental.csv", "w")                      #place the data structure in this file
write_line = ""

cell_T = pin_T = False                              #reset all the variables to for the cell information 
corner = A = True
cell_list, data_struc, cell_block = [],[],[]
pin_name = cell_leakage_power = cell_footprint = density = area = 'N/A'                    
pin_num = real_count = density =  0               
leak  = 1
temp_relatedpin, cell_vt = "",""


direction = incap = outcap = related_pin = cell_rise = rise_transition = cell_fall = fall_transition = "N/A"           #reset all the variables to for the pin information 
c1 = c2 = c3 = c4 = d = x = Ave1 = Ave2 = Ave3 = Ave4 = False
tempList, timing_list,the_list, pin_list =  [],[],[],[]
the_sum = c_count=0


def appendPinItems():                       #add the pin name, direction, incap, and outcap to the pin list
    if pin_name not in pin_list:
            pin_list.append(pin_name)
    if direction not in pin_list:
        pin_list.append(direction)
    if incap not in pin_list:
        pin_list.append(incap)
    if outcap not in pin_list:
        pin_list.append(outcap)

def appendTimingArc():              # add the related pin, cell rise, rise transition, cell_fall, fall_transition, default_operating_conditions, and file path to the timing arc list
    timing_list.append(related_pin)
    timing_list.append(cell_rise)
    timing_list.append(rise_transition)
    timing_list.append(cell_fall)
    timing_list.append(fall_transition)
    timing_list.append(path)
    timing_list.append(doc)
    
    
def createLists():
    the_list = [*cell_list + pin_list + timing_list ]       #combine the list of the cell , pin, and timing items into one list. This list is unique to each timing arc
    cell_block.append(the_list)                              # combine the list above into another list containing all the info of the cell
    
def printCell():
    
        
    if cell in cell_list and cell_footprint not in cell_list:       # if the cell only has the cell name and the area, give it the default list
        cell_vt = cell_list[0]
        cell_vt = cell_vt.split('PD')[1]
        tempList = [cell, cell_vt, 'N/A', area,'N/A','N/A','N/A','N/A','N/A','N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A' , 'N/A', path , doc]
        data_struc.append(tempList)

        print(format_string.format(*tempList))      #print the list to the terminal
   
        for j in tempList:              #write the list/line in the file seperated by a commma
            write_line = str(j)
            f.write(write_line)
            f.write(",")
        f.write('\n')
     
    for i in cell_block:
        
        global temp_relatedpin
    
        
        if cell_footprint not in i:             #insert the remaining items of the cell into the list such as footprint and leakage power
            i.insert(2, cell_footprint)
        if leakage_power not in i:
            i.insert(3,leakage_power)
        i.insert(1, str(pin_num))

        density = float( float(i[2]) /pin_num)      #insert the cell density to the list
        density = round(density, 7)
        i.insert(3, str(density))
        if len(i) != 17:
            i.insert(2, 'N/A')
        
        cell_vt = cell_list[0]                      #insert the voltage threshold to the list
        cell_vt = cell_vt.split('PD')[1]
        i.insert(1, cell_vt)
        
        if temp_relatedpin == i[11] and i[11] != 'N/A':     #print/append only one timing arc for each input pin into the data structure
            continue
        temp_relatedpin = i[11]
        
        print(format_string.format(*i))             #print the cell list
        data_struc.append(i)                           #add the cell list to the data structure that contains all the cell info
        
        for j in i:                                     #write the cell list into the file
            write_line = str(j)
            f.write(write_line)
            f.write(",")
        f.write('\n')
        
for i,line in enumerate(cell_text):   

    if corner == True and 'default_operating_conditions' in line:       # find the  default_operating_conditions
        doc = line.split(': ')
        doc = doc[1].split(' ;')
        doc = doc[0]
        corner = False             
    
    if "cell (" in line :             #find the cell name
        cell_line = line.split('(')
        cell_line = cell_line[1].split(')')
        cell = cell_line[0]
        cell_T = True
        if cell not in cell_list:
            cell_list.append(cell)
              
    
    if "area :" in line and A == True and cell_T == True:                #find the area and density
        area1 = line.split(': ')
        area2 = area1[1].split(';')
        area = str(area2[0])
        A = False
        if area  not in cell_list:
            cell_list.append(area)
    
    if "cell_footprint : " in line and cell_T == True:        #find the cell_footprint
        cf = line.split('"')
        cell_footprint = cf[1]
        if cell_footprint not in cell_list:
            cell_list.append(cell_footprint)

    if "leakage_power () " in line and cell_T == True:     #find the cell_leakage_power
        leak -=1
    if "value : " in line and leak == 0:
        lp = line.split(": ")
        lp = lp[1].split(";")
        leakage_power = float(lp[0])
        leakage_power = round(leakage_power, 9)
        leakage_power = str(leakage_power)

        if leakage_power not in cell_list:
            cell_list.append(leakage_power)
    
    if "pin(" in line and cell_T == True:                       # find the pin_name
        cell_rise = rise_transition = cell_fall = fall_transition = direction = incap = outcap ="N/A"       #reset the pin items when a new pin is found
        d = Ave4 = c4 = Ave3 = c3 = Ave2 = c2 = c1 = Ave1 = False
        pin_list, timing_list = [],[]
        pin_T = True   
        pin_num +=1
        the_sum = c_count = 0
        row =""

        pin1 = line.split('(')
        pin2 = pin1[1].split(')')
        pin_name = pin2[0]
        
    if "direction : " in line and d == False and pin_T == True:       #finds the direction of each pin
        if re.search("input", line) :
            direction = 'INPUT'
        
        elif re.search("output", line):
            direction = 'OUTPUT'
        d = True
        
    if "capacitance : " in line and direction == 'INPUT' and "_" not in line and pin_T == True:     #find the capacitence for input pins
        incap = line.split(': ')
        incap = (incap[1].split(';'))
        incap = str(incap[0])
        appendPinItems()
        appendTimingArc()
        createLists()
        
        timing_list = [] 
        pin_T = False
    
    if "max_capacitance : " in line and direction == 'OUTPUT' and pin_T == True:     #find the capacitence for input pins
        outcap = line.split(': ')
        outcap = (outcap[1].split(';'))
        outcap = str(outcap[0])
        appendPinItems()
    
    if direction == "OUTPUT" and pin_T == True:                     
        if 'timing () {' in line:                   #indicate that a new timing arc is found
            x = True
            timing_list = []                                #reset all the timing arc values when a new one is found
            cell_rise = rise_transition = cell_fall = related_pin = fall_transition = "N/A"
            
        
        if 'related_pin : ' in line and x == True:      #find the timing arc's related pin
            related_pin = line.split('"')
            related_pin = related_pin[1]
            

        
        numbers = ['1','2','3','4','5','6','7','8','9','0', ',','.','-', 'e' ]      # list of valid characters to collect in the lines of the timing arc data
        if c1 == True:                                       # if the line contains the cell rise data
            the_line = str(line)                              #collect the data into the stinf
            for i in the_line:                                  #filter the characters to have only the numbers
                if i in numbers:
                    row = row+i
            c_count+=1
            if c_count == 8:
                row = row.split(",")                           #once all the data is collected in a string, split them into floats, 
                for t in (row):
                    t = float(t)
                    the_sum+= t
                cell_rise  = the_sum /(len(row))                # compute the values averages
                cell_rise = round(cell_rise, 7)
            
                c1 = Ave1 = False                               #reset the data use to compute the average
                c_count = 0
                row =""
                the_sum = 0
        
        if c2 == True:                    # repeat the steps above for the rise transition data
            the_line = str(line)
            for i in the_line:
                if i in numbers:
                    row = row+i
            c_count+=1
            if c_count == 8:
                row = row.split(",")
                for q in (row):
                    q = float(q)
                    the_sum+= q
                rise_transition  = the_sum /(len(row))
                rise_transition = round(rise_transition, 7)
            
                Ave2 = c2 = False
                c_count = 0
                row =""
                the_sum = 0
                
        if c3 == True:                  # repeat the steps above for the fall transition data
            the_line = str(line)
            for i in the_line:
                if i in numbers:
                    row = row+i
            c_count+=1
            if c_count == 8:
                row = row.split(",")
                for q in (row):
                    q = float(q)
                    the_sum+= q
                cell_fall  = the_sum /(len(row))
                cell_fall = round(cell_fall, 7)
            
               
                Ave3 = c3 = False
                c_count = 0
                row =""
                the_sum = 0
                
        if c4 == True:                  # repeat the steps above for the cell fall data
            the_line = str(line)
            for i in the_line:
                if i in numbers:
                    row = row+i
            c_count+=1
            if c_count == 8:
                row = row.split(",")
                for q in (row):
                    q = float(q)
                    the_sum+= q
                fall_transition  = the_sum /(len(row))
                fall_transition = round(fall_transition, 7)
            
                appendTimingArc()
                createLists()
                Ave4 = c4 = False
                c_count = 0
                row =""
                x = False
                the_sum = 0
        
                       
        if 'cell_rise (' in line and 'ocv' not in line and x == True:           #set Ave1 = True to indicate that cell rise data is coming up
            Ave1 = True
        if 'values (' in line and x == True and Ave1 == True:                   # set c1 = True to indicate that cell rise data  is going to be in the next line of the file
            c1 = True
        
        if 'rise_transition (' in line and 'ocv' not in line and x == True:     #set Ave2= True to indicate that rise transition data is coming up
            Ave2 = True
        if 'values (' in line and x == True and Ave2 == True:                   # set c2 = True to indicate that rise transition data  is going to be in the next line of the file
            c2 = True
        
        if 'cell_fall (' in line and 'ocv' not in line and x == True:       #set Ave3 = True to indicate that cell fall data is coming up
            Ave3 = True
        if 'values (' in line and x == True and Ave3 == True:               # set c3 = True to indicate that cell fall data  is going to be in the next line of the file
            c3= True
        
        if 'fall_transition (' in line and 'ocv' not in line and x == True:     #set Ave4 = True to indicate that fall transition data is coming up
            Ave4 = True
        if 'values (' in line and x == True and Ave4 == True:               # set c4 = True to indicate that fall transition data  is going to be in the next line of the file
            c4= True
        
    if "Design : " in line and cell_T == True:         #stop at the end of pin section

        printCell()                                     #prints the cell information at the start of every cell
        real_count +=1
        if real_count == -1 :#29:                   #keeps count of cells in the file, can be set to print up to a certain amount of cells
            break
        
        cell_T = pin_T = False                                      # reset/erase all variables and set the N/A as default values when a new cell is founded
        A = True
        cell_list, cell_block, pin_list,timing_list =  [],[],[],[]
        pin_name = cell_leakage_power = cell_footprint = density = area =  'N/A'                                
        direction = incap = outcap = related_pin = cell_rise = rise_transition = cell_fall = fall_transition = "N/A"
        Ave2 = c2 = Ave1 = c1 = Ave3 = c3 = Ave4 = c4 = False
        temp_relatedpin, row ="",""
        c_count =pin_num =the_sum = 0 
        leak=1
        
print("\n")

file.close()        #close file and end the program
f.close()
sys.exit()
