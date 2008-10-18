#!/usr/bin/env python2.5

import re, random, os.path
from collections import *
from copy import *
from string import *
from threading import *


from utils import *
from slot import *
from dialogueAct import *
from rule import *
from baseTD import *

class Trainer(BaseTD):
    def __init__(self, fos, fosa, trgCond,tmpData):
        BaseTD.__init__(self, fos = fos, fosa = fosa, trgCond = trgCond)
        self.tmpData = tmpData
        
        return

    def findBestRule(self):
        print '=================== FIND BEST START ====================='
        self.rules = defaultdict(int)
        self.trg2d = defaultdict(list)
        # get all applicable rules
        for i in xrange(len(self.das)):
            rs, ts = getRules(self.das[i], self.trgCond)
            
            for r in rs:
                self.rules[r] += 1
            
            for t in ts:
                # collect indexes of DAs for which the trigger satisfies the 
                # conditions. As a result I do not have to
                # call the validate function on these DAs
                self.trg2d[t].append(i)
            
        for r in self.rules:
            r.occurence = self.rules[r]
            
        print '========================================================='
        print 'Number of applicable rules: %d' % len(self.rules)

        self.rls = self.rules.keys() 
        for r in self.rls:
            if r.occurence < 2:
                del self.rules[r]
        print '                 pruned to: %d' % len(self.rules)

        self.rls = self.rules.keys() 
        # I might delete self.rules it seem that I do not need it any more
        self.rls.sort(cmp=lambda x,y: cmp(x.occurence, y.occurence), reverse=True)

        # apply each rule and measure the score
        R = 0
        maxNetScore = 0
        N = len(self.das)
        for rule in self.rls:
            if rule.occurence < maxNetScore:
                # the best possible benefit of the rule is lower than the
                # benefit of some already tested rule. And because the rules 
                # are sorted w.r.t occurence, I can not find a better rule.
                break
                
            R += 1

            # compute netScore for the curent rule
            netScore = 0 
            for i in self.trg2d[rule.trigger]:
                netScore += rule.transformation.measureDiff(self.das[i])
            
            if netScore > maxNetScore:
                maxNetScore = netScore
            
            rule.setPerformance(netScore)
            
##            print '%s netScore Occ:%d NetScore:%d Cplx:%d' % (rule, rule.occurence, netScore, rule.complexity())
        
        print '    Number of tested rules: %d ' % R
        print '========================================================='
        
        # sort the rules according their performance and complexity
        self.rls.sort(cmp=lambda x,y: x.cmpPlx(y))
            
        if len(self.rls) == 0:
            print 'No applicable rules.'
            return None
        else:
            print 'Best: %s Occ:%d NetScore:%d Cplx:%d' % (self.rls[0], self.rls[0].occurence, self.rls[0].netScore, self.rls[0].complexity())
            for i in range(1, min([len(self.rls), 10])):
                print ' Opt: %s Occ:%d NetScore:%d Cplx:%d' % (self.rls[i], self.rls[i].occurence, self.rls[i].netScore, self.rls[i].complexity())
        
        print '==================== FIND BEST END ======================'
        return self.selectBestRules(self.rls[:10])

    def applyBestRule(self, bestRule):
        for da in self.das:
            bestRule.apply(da)
    
    def selectBestRules(self, bestRules):
        br = []
        br.append(bestRules[0])

        # I have to encourage increase perferomance in recall because
        # this learning is very defensive = 
        # it slowly increases the recall
        for i in range(1, len(bestRules)):
            if bestRules[i].transformation.addSlot == None:
                continue
            elif bestRules[i].netScore < 2:
                continue
            elif bestRules[i].transformation.addSlot == bestRules[i-1].transformation.addSlot:
                # remove duplicates
                continue
                
            br.append(bestRules[i])

##        for r in br:
##            priaccnt '<<<Slct: %s Cplx:%d' % (r, r.complexity())
        
        br.reverse()
        sr = []
        # filter out the same (duplict) opperations
        for i in range(0, len(br)):
            ok = True
            for j in range(i+1, len(br)):
                if br[i].transformation.addSlot == br[j].transformation.addSlot:
                    # remove duplicates
                    ok = False
                    break
                
            if ok:
                sr.append(br[i])
        
        sr.reverse()
        
        for r in sr:
            print 'Slct: %s Occ:%d NetScore:%d Cplx:%d' % (r, r.occurence, r.netScore, r.complexity())
                
        return sr
    
    def train(self):
        self.bestRules = []
        self.iRule = 0
        
        self.rulesPruningHiThreshold = 0
        self.rulesPruningLowThreshold = 0
        
        bestRules = self.findBestRule()
        
        while bestRules[0].netScore >= 2:
            # store the selected rules
            for r in bestRules:
                self.bestRules.append(r)
                
            # apply the best rule on the training set
            for r in bestRules:
                self.applyBestRule(r)
            
            self.writeRules(os.path.join(self.tmpData,'rules.txt'))
            self.writePickle(os.path.join(self.tmpData,'rules.pickle'))
            self.writeDict(os.path.join(self.tmpData,'rules.pckl-dict'))

            self.iRule += 1
            bestRules = self.findBestRule()
            
            if bestRules == None:
                break
