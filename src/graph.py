#!/usr/bin/env python2.5

import sys, struct, commands, getopt, sys, os.path
from pylab import *

from decoder import *

split = 50
binDir = '../../bin'
resultsDir=''

try:
    opts, args = getopt.gnu_getopt(sys.argv[1:], "hp", 
        ["resultsDir=",
         'dataDir='])
         
except getopt.GetoptError, exc:
    print("ERROR: " + exc.msg)
    usage()
    sys.exit(2)

for o, a in opts:
    if o == "-h":
        usage()
        sys.exit()
    elif o == "--resultsDir":
        resultsDir = a
    elif o == "--dataDir":
        dataDir = a

def decode(data, inPickle, nRules = 0):
    outSem = 'graph.sem'
    
    dcd = Decoder.readDecoderPickle(inPickle)
    print dcd.trgCond

    dcd.loadData(data)
    dcd.decode(nRules)
    dcd.writeOutput(outSem)

    o = commands.getoutput('%s/cuedSemScore.pl -d %s %s' % (binDir, outSem, data))
    o = o.split()
    
    return len(dcd.bestRules), o[0], o[3]

    
def decodeSet(data):
    data = os.path.join(dataDir, data)
    inPickle = os.path.join(resultsDir, 'rules.pckl-decoder')
    
    i = 16
    iMax = 30

    nRules = []
    acc = []
    fm = []
    
    print data
    while i<iMax:
        iMax, a, f = decode(data, inPickle, i)
        acc.append(float(a))
        fm.append(float(f))
        nRules.append(i)
        print i, iMax, a, f
        
        if i+1 == iMax:
            break
            
        i += int(iMax/split)
        
        if i > iMax:
            i = iMax-1
            
    return acc, fm, nRules
    

def findMax(data):
    max = 0
    iMax = 0
    
    for i in range(len(data)):
        if data[i]> max:
            iMax = i
            max = data[i]
    
    return iMax
    
settingsFN = os.path.join(resultsDir,'settings')

f = file(settingsFN, 'r')
settings = ''
for s in f.readlines():
    if s.startswith('TBEDP_TRN_DATA_FILE'):
        settings += s+'\n'
    if s.startswith('TBEDP_TRG_COND'):
        settings += s.replace('{', '').replace('}','').replace("':", '=').replace("'",'')+'\n'
f.close()

outGraph = os.path.join(resultsDir,'rules.performance.clean.eps')
trainCleanAcc, trainCleanF, nRules1 = decodeSet('towninfo-train.sem')
devCleanAcc, devCleanF, nRules2 = decodeSet('towninfo-dev.sem')
testCleanAcc, testCleanF, nRules3 = decodeSet('towninfo-test.sem')

fig = figure(figsize=(11.7, 8.3))

title('Clean test data')

xlabel('nRules - number of used rules')
ylabel('Acc [%], F[%]')

plot(nRules1, trainCleanAcc, "g-.")
plot(nRules1, trainCleanF,  "g-")

plot(nRules2, devCleanAcc, "b-.")
plot(nRules2, devCleanF,  "b-")

plot(nRules3, testCleanAcc, "r-.")
plot(nRules3, testCleanF,  "r-")

legend(("train data - Accurracy",
        "train data - Item F-masure", 
        "  dev data - clean - Accurracy",
        "  dev data - clean - Item F-masure",         
        " test data - clean - Accurracy",
        " test data - clean - Item F-masure"),         
        loc = "lower right")

grid(True)

i = findMax(devCleanF)
plot([nRules2[i]], [devCleanF[i]], 'bs-')

annotate('Best performance on the dev set.', (nRules2[i], devCleanF[i]), 
        (int(nRules2[-1]/2), devCleanF[i]-7), 
        arrowprops=dict(facecolor='black', shrink=0.05, width=1),
        fontsize=14)

xlim(xmin=nRules2[0]-2)

text(int(nRules2[-1]/2), devCleanF[i]-9, 'Dev data: nRules=%d Acc=%.2f F=%.2f' % (nRules2[i], devCleanAcc[i], devCleanF[i]), fontsize=14)
text(int(nRules2[-1]/2), devCleanF[i]-11, 'Test data: nRules=%d Acc=%.2f F=%.2f' % (nRules2[i], testCleanAcc[i], testCleanF[i]), fontsize=14)
text(nRules2[0], devCleanF[i]-17, settings)

savefig(outGraph)
print commands.getoutput("epstopdf %s" % (outGraph))
print commands.getoutput("rm -f %s" % (outGraph))


outGraph = os.path.join(resultsDir,'rules.performance.asr.eps')
trainCleanAcc, trainCleanF, nRules1 = decodeSet('towninfo-train.asr')
devCleanAcc, devCleanF, nRules2 = decodeSet('towninfo-dev.asr')
testCleanAcc, testCleanF, nRules3 = decodeSet('towninfo-test.asr')

fig = figure(figsize=(11.7, 8.3))
title('ASR test data')
xlabel('nRules - number of used rules')
ylabel('Acc [%], F[%]')

plot(nRules1, trainCleanAcc, "g-.")
plot(nRules1, trainCleanF,  "g-")

plot(nRules2, devCleanAcc, "b-.")
plot(nRules2, devCleanF,  "b-")

plot(nRules3, testCleanAcc, "r-.")
plot(nRules3, testCleanF,  "r-")

legend(("train data - Accurracy",
        "train data - Item F-masure", 
        "  dev data - ASR - Accurracy",
        "  dev data - ASR - Item F-masure",         
        " test data - ASR - Accurracy",
        " test data - ASR - Item F-masure"),         
        loc = "lower right")

grid(True)

i = findMax(devCleanF)
plot([nRules2[i]], [devCleanF[i]], 'bs-')

annotate('Best performance on the dev set.', (nRules2[i], devCleanF[i]), 
        (int(nRules2[-1]/2), devCleanF[i]-7), 
        arrowprops=dict(facecolor='black', shrink=0.05, width=1),
        fontsize=14)

xlim(xmin=nRules2[0]-2)

text(int(nRules2[-1]/2), devCleanF[i]-9, 'Dev data: nRules=%d Acc=%.2f F=%.2f' % (nRules2[i], devCleanAcc[i], devCleanF[i]), fontsize=14)
text(int(nRules2[-1]/2), devCleanF[i]-11, 'Test data: nRules=%d Acc=%.2f F=%.2f' % (nRules2[i], testCleanAcc[i], testCleanF[i]), fontsize=14)
text(nRules2[0], devCleanF[i]-17, settings)


savefig(outGraph)
print commands.getoutput("epstopdf %s" % (outGraph))
print commands.getoutput("rm -f %s" % (outGraph))