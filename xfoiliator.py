# -*- coding: utf-8 -*-
"""
Created on Sun Dec  6 10:53:26 2020

@author: rhino
"""


import subprocess as sp
import os
import numpy


xfoilpath = r'C:\Users\rhino\Desktop\Fluids Project\XFOIL6.99\xfoil.exe'

#Initial requirements
M = 5000
Temp = 15
roeSea = 1025

viscSea = .00122
pAtm = 101325
pV = 2000
depth = 1.5
cmax = .65
b = 4
Tmax = 20*10**3
g = 9.81
e = .9
W = M*g


pinf = depth*g*roeSea+pAtm


#list to change over iterations can be changed accordingly
allAirfoils = ['0009','0012','2414','2415','6409','0008','0010','0015','0018','0021','0024','1408','1412','2408','2410','2411','2412','2415','2418','2421','2424','4412','4415','4421','4424','6412']
allRe = [9*10**6]
allC = numpy.linspace(.59,.65,num=100)

def buildAirfoils():
    final = []
    for j in [1]:
        for z in numpy.linspace(0,8,num=9,dtype=(int)):
            for i in numpy.linspace(10,40,num =31,dtype=int):
                final.append(str(j)+str(z)+str(i))
    return final
        
allAirfoils = buildAirfoils()


#uses xfoil to get data as 'Naca#_Re#.log'
def dataOut(naca,re): #(string number)
    
    #communicates directly with xfoil
    def Cmd(cmd):
        ps.stdin.write((cmd+'\n').encode('utf-8'))
    #builds the file name 
    def nameBuilder():
        return 'Naca'+naca+'_Re'+str(re)+'.log'
        
    #deletes the filename if it already exists   
    try:
        os.remove(nameBuilder())
    except :
        pass
    
    # run xfoil
    ps = sp.Popen(xfoilpath ,stdin=sp.PIPE,stderr=sp.PIPE,stdout=sp.PIPE)
    ps.stderr.close()
    
    # command part    
    Cmd('naca '+naca) #starts by choosing airfoil
    Cmd('OPER')
    Cmd('VISC')
    Cmd(str(re))
    Cmd('CINC')
    Cmd('PACC')
    Cmd(nameBuilder())  # output file
    Cmd(' ')          # no dump file
    Cmd('aseq -2 2 .1')
    Cmd(' ')     # escape OPER
    Cmd(' ')
    Cmd('quit')  # exit
    ps.stdout.close()
    ps.stdin.close()
    ps.wait()
    
    print('DONE '+nameBuilder())
    
def vel2Knots(v):
    return float(v*1.94384)

def vel2d(cl,c): #WORKS
    AR = b/c
    n = e*AR/(e*AR+2)
    CL=n*cl
    
    vel = (W*2/(CL*c*b*roeSea))**.5
    return vel

def checkCaviation(v,cpMin):
    sigma = getSigma(v)
    return sigma >= -cpMin


def getSigma(v):
    sigma = (pinf-pV)/(.5*roeSea*v**2)
    return sigma

def checkStucture(naca,c):
    tbar = int(naca[-2:])/100
    return 90*W*b/(32*tbar**2*c**3) <= 500*10**6/2.5

def getDrag(cd,cl,c,v):
    AR = b/c
    n = e*AR/(e*AR+2)
    CL=n*cl
    CD = cd+CL**2/(3.1415*e*AR)
    
    return CD*1/2*roeSea*v**2*c*b

def checkDrag(cd,cl,c,v):
    D = getDrag(cd, cl, c, v)
    return D<=20*10**3


def searchFile(naca,re,c):
    
    bestVel = 0
    best = 0
    
    filename = 'Naca'+naca+'_Re'+str(re)+'.log'
    f = open(filename, 'r')
    
    flines = f.readlines()
    
    
    for i in range(12,len(flines)):
        numbers = flines[i].split()
        cl = float(numbers[1])
        
        if cl>0:
            
            #alphaList.append(float(numbers[0]))
            #clList.append(float(numbers[1]))
            #cdList.append(float(numbers[2]))
            #cpMinList.append(float(numbers[5]))
            cd = float(numbers[2])
            cpMin = float(numbers[5])
            alpha = numbers[0]
            
            v = vel2d(cl,c)
            
            #print(checkStucture(naca, c),checkCaviation(v, cpMin),checkDrag(cd, cl, c, v),c)
            if checkStucture(naca, c) and checkCaviation(v, cpMin) and checkDrag(cd, cl, c, v) and vel2Knots(v)>45:
                print(filename,c,vel2Knots(v))       
                
    
    f.close()
    return(bestVel,best)

def buildData(airfoilList,reList):
    for i in airfoilList:
        for j in reList:
            dataOut(i, j)
    print('DONE building')
    
    
def testData(airfoilList,reList,cList):
    for i in airfoilList:
        for j in reList:
            for z in cList:
                searchFile(i,j,z)
            
    print('DONE testing')

