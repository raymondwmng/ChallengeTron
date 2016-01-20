#!/usr/bin/python

import sys,re,os
# import numpy as np

class ZoneList:
  def __init__(self,list_=None):
    self.list_ = list_
    self.next = None

  def cleanList(self):
    if self.list_ == None:
      return
    else:
      current = self
    while True:
      current.list_ = sorted(set(current.list_))
      if current.next == None:
        return
      else:
        current = current.next

 
  def addList(self,zones):
    [zone1,zone2] = [zones[0],zones[1]]
    if self.list_ == None:
      self.list_ = zones
    else:
      current = self
      is_grouped = False
      while True:
        try:
          # add zone2 to zone1
          current.list_.index(zone1)
          current.list_.append(zone2)
          is_grouped = True
          break
        except ValueError:
          try:
            # add zone1 to zone2
            current.list_.index(zone2)
            current.list_.append(zone1)
            is_grouped = True
            break
          except ValueError:
            if current.next == None:
              break
            else:
              current = current.next
      if is_grouped == False:
        current.next = ZoneList(zones)

    ## DEBUG ADDLIST
    # print '====== CHECK addlist results ======'
    # current = self
    # while True:
    #   print current.list_
    #   print current.next
    #   if current.next == None:
    #     break
    #   else:
    #     current = current.next


class Zones:

  def __init__(self,blocks):
    self.root = None
    self.barrier = blocks 
    self.zones = dict()
    for i in range(0,225):
      self.zones[i] = i

  def findzoneidx(self,key_):
    return self.zones[key_]


  def ij2index(self,i,j):
    return i*15+j

  def index2ij(self,index):
    return (int(index)/15,int(index)%15)

  def mergezones(self,zonelist):
    # build mergedict
    mergedict = dict()
    if zonelist.list_ == None:
      return
    else:
      current = zonelist
      while True:
        for i in range(1,len(current.list_)):
          mergedict[current.list_[i]] = current.list_[0]
        if current.next == None:
          break
        else:
          current = current.next


    # redirect zone
    for ctr1 in range(0,225):
      try:
        self.zones[ctr1] = mergedict[self.zones[ctr1]]
      except KeyError:
        pass

  def drawzones(self,incl_i=None,incl_j=None):
    for ctr1 in range(0,225):
      (i1,j1) = self.index2ij(ctr1)
      if incl_i != None and incl_j != None:
        if self.barrier[i1][j1] == 1 and (not(i1 == incl_i and j1==incl_j)):
          # zoneidx1 = self.findzoneidx(ctr1)
          # BUG: self.zones[zoneidx1] = -1
          self.zones[ctr1] = -1
      else:
        if self.barrier[i1][j1] == 1:
          # zoneidx1 = self.findzoneidx(ctr1)
          # BUG: self.zones[zoneidx1] = -1
          self.zones[ctr1] = -1

    tomerge = list()
    for ctr1 in range(0,225):
      (i1,j1) = self.index2ij(ctr1)
      equivalent = list()
      for ctr2 in range(0,ctr1):
        zoneidx1 = self.zones[ctr1]
        zoneidx2 = self.zones[ctr2]
        if zoneidx1 == -1 or zoneidx2 == -1:
          continue
        elif zoneidx1 == zoneidx2:
          continue
        else:
          (i2,j2) = self.index2ij(ctr2)
          if (abs(i1-i2) == 1 and j1==j2) or (abs(j1-j2) == 1 and i1==i2):
            # BUG: # self.zones[zoneidx1] = self.zones[zoneidx2]
            self.zones[ctr1] = self.zones[ctr2]
            equivalent.append(self.zones[ctr2])
      if len(equivalent) > 1:
        equivalent.sort()
        tomerge.append(equivalent)

    # merge dictionary
    zonelist = ZoneList()
    for ctr_i in range(0,len(tomerge)):
      zonelist.addList(tomerge[ctr_i])
    zonelist.cleanList()
    self.mergezones(zonelist)   


 
# -------------------------------------------

class Node:
  def __init__(self,s_i,s_j,o_i,o_j,vor):
    self.s_i = s_i
    self.s_j = s_j
    self.o_i = o_i
    self.o_j = o_j
    self.vor = vor
    self.links = None
  
  def genneighbour(self,vor,sdirection,odirection):
    i_moves = [ -1, 0 , 1 , 0]
    j_moves = [  0, -1, 0 , 1]
    dir_str = ['UP','LEFT','DOWN','RIGHT']
    new_s_i = self.s_i + i_moves[sdirection]
    new_s_j = self.s_j + j_moves[sdirection]
    new_o_i = self.o_i + i_moves[odirection]
    new_o_j = self.o_j + j_moves[odirection]
    new_tempblock = [[0 for j in range(0,15)] for i in range(0,15)]
    new_tempblock[self.s_i][self.s_j] = 1
    new_tempblock[self.o_i][self.o_j] = 1
    return Node(new_s_i,new_s_j,new_o_i,new_o_j,vor)
  
  def stepadvance(self,perm_block):
    if self.links == None:
      self.links = list()
      for sdirection in range(0,4):
        for odirection in range(0,4):
          (voronoi_sum_,s_dead,o_dead,o_block) = gen_voronoi_sum(self.s_i,self.s_j,self.o_i,self.o_j,perm_block,sdirection,odirection)
          if s_dead == True or o_dead == True:
            self.links.append([]) 
          else:
            newnode = self.genneighbour(voronoi_sum_,sdirection,odirection)
            self.links.append(newnode)
      return
    else:
      for link in self.links:
        if link != []:
          link.stepadvance(perm_block)

  def totalvor(self):
    if self.links == None:
      return self.vor
    else:
      vor = 0
      for link in self.links:
        if link != []:
          if vor == 0:
            vor = link.totalvor()
          else:
            vor = max(vor,link.totalvor())
      return self.vor + vor
         
 

class Tree:
  def __init__(self,node):
    self.root = node
  
  




def board2block(board):
  block = [[] for i in xrange(0,15)]
  for i in xrange(0,15):
    block[i] = [[] for j in xrange(0,15)]
    for j in xrange(0,15):
      if board[i][j] != '-':
        block[i][j] = 1   # infeasible
      else:
        block[i][j] = 0
  return block




def gen_voronoi(i,j,o_i,o_j):
  v = [[] for i in xrange(0,15)]
  for vi in xrange(0,15):
    v[vi] = [[] for j in xrange(0,15)]
    for vj in xrange(0,15):
      if abs(vi-i)+abs(vj-j) > abs(vi-o_i)+abs(vj-o_j):
        v[vi][vj] = 1
      elif abs(vi-i)+abs(vj-j) < abs(vi-o_i)+abs(vj-o_j):
        v[vi][vj] = -1
      else:
        v[vi][vj] = 0
  return v


          


def gen_voronoi_wblocks(i,j,o_i,o_j,block):
  zone = Zones(block)
  zone.drawzones()

  # DRAWZONE DEBUG
  # for xxi in range(0,15):
  #   for xxj in range(0,15):
  #    sys.stdout.write(' '+str(zone.zones[xxi*15+xxj]))
  #   sys.stdout.write('\n') 
  # print zone.zones 
  # print i,j,zone.zones[zone.ij2index(i,j)]

  ctr_s = zone.ij2index(i,j)
  ctr_o = zone.ij2index(o_i,o_j)
  zoneidx_s = zone.findzoneidx(ctr_s)
  zoneidx_o = zone.findzoneidx(ctr_o)

  v = [[] for i_ctr in xrange(0,15)]
  for vi in xrange(0,15):
    v[vi] = [[] for j_ctr in xrange(0,15)]
    for vj in xrange(0,15):
      if block[vi][vj] == 1:
        v[vi][vj] = 0
        continue
      
      ctr = zone.ij2index(vi,vj)
      zoneidx_v = zone.findzoneidx(ctr)

      v[vi][vj] = 0
      if (zoneidx_v == zoneidx_s):
        if (zoneidx_v == zoneidx_o):
          if abs(vi-i)+abs(vj-j) < abs(vi-o_i)+abs(vj-o_j):
            v[vi][vj] = v[vi][vj] + 1
          elif abs(vi-i)+abs(vj-j) > abs(vi-o_i)+abs(vj-o_j):
            v[vi][vj] = v[vi][vj] - 1
        else:  # o inaccessible
          if abs(vi-i)+abs(vj-j) < abs(vi-o_i)+abs(vj-o_j):
            v[vi][vj] = v[vi][vj] + 0
          elif abs(vi-i)+abs(vj-j) > abs(vi-o_i)+abs(vj-o_j):
            v[vi][vj] = v[vi][vj] - 0
      elif (zoneidx_v != zoneidx_s):
        v[vi][vj] = v[vi][vj] - 1    

  
      ### OLD METHOD
      # if abs(vi-i)+abs(vj-j) > abs(vi-o_i)+abs(vj-o_j):
      #   v[vi][vj] = 1
      # elif abs(vi-i)+abs(vj-j) < abs(vi-o_i)+abs(vj-o_j):
      #   v[vi][vj] = -1
      # else:
      #   v[vi][vj] = 0
  # VORONOI BLOCK DEBUG
  # print 'v:'+str(zoneidx_v)+',s:'+str(zoneidx_s)+',o:'+str(zoneidx_o)
  # print i,j,o_i,o_j
  # for xxi in range(0,15):
  #   print v[xxi]
  # print '--------'
  return v

def checkijrange(i):
  if i > 0 and i < 14:
    return True
  else:
    return False

def gen_voronoi_sum(s_i,s_j,o_i,o_j,block,self_move,o_move): 
  i_moves = [ -1, 0 , 1 , 0]
  j_moves = [  0, -1, 0 , 1]
  dir_str = ['UP','LEFT','DOWN','RIGHT']
 
  s_dead = False
  o_dead = False  
  o_block = False 

  # gen voronoi_scores for 4*4 movement possibilities 
  self_new_i = s_i + i_moves[self_move]
  self_new_j = s_j + j_moves[self_move]
  o_new_i = o_i + i_moves[o_move]
  o_new_j = o_j + j_moves[o_move]


  # impossible direction for self and opponent and prune
  if checkijrange(self_new_i) == False or \
    checkijrange(self_new_j) == False:
      voronoi_change = -999999
      s_dead = True
  elif block[self_new_i][self_new_j] == 1:
    voronoi_change = -999999
    s_dead = True
  if checkijrange(o_new_i) == False or \
    checkijrange(o_new_j) == False:
      voronoi_change = 1
      o_dead = True
  elif block[o_new_i][o_new_j] == 1:
    voronoi_change = 1
    o_block = True
    # o_dead = True
 
  
  this_voronoi = gen_voronoi_wblocks(self_new_i,self_new_j,o_new_i,o_new_j,block)
  
  # if s_dead == True or o_dead == True:
  if s_dead == True:
    return (voronoi_change,s_dead,o_dead,o_block)
  else:
    return (sum([sum(this_voronoi[i]) for i in range(0,len(this_voronoi))]),s_dead,o_dead,o_block) 

  # nextDirection = voronoi_sum_o.index(max(voronoi_sum_o))
  # return dir_str[nextDirection]
  


S=3
def nextMove(player,s_i,s_j,o_i,o_j,board):
  block = board2block(board)

  node = Node(s_i,s_j,o_i,o_j,0)
  # generate trees predicting S steps  
  for k in range(0,S-1):
    node.stepadvance(block)

  score = [-999999 for i in range(0,4)]
  is_forbidden = [True,True,True,True]
  # integrate the voronoi scores
  for next_node_index in range(0,16):
    direction_index = int(next_node_index)/4
    if node.links[next_node_index] != []:
      if is_forbidden[direction_index] == True:
        is_forbidden[direction_index] = False
        score[direction_index] = 0       
      score[direction_index] = score[direction_index] + node.links[next_node_index].totalvor()
      # print '----DIRECTION:'+str(direction_index)+' INDEX:'+str(next_node_index)+'----'
      # print node.links[next_node_index].s_i
      # print node.links[next_node_index].s_j
      # print node.links[next_node_index].o_i
      # print node.links[next_node_index].o_j
      # print node.links[next_node_index].totalvor()
           
  
  # i_moves = [ -1, 0 , 1 , 0]
  # j_moves = [  0, -1, 0 , 1]
  dir_str = ['UP','LEFT','DOWN','RIGHT']
  # return dir_str[score.index(max(score))]

    
  ######
  # DEBUG
  #
  # print score[0]
  # print score[1]
  # print score[2]
  # print score[3] 
  # print [node.s_i,node.s_j,node.o_i,node.o_j,node.vor] 
  # print node.links
  # for i in node.links:
  #    if i != []:
  #      print '-------'+str(i.s_i)+' '+str(i.s_j)+'-------'
  #      # print [i.s_i,i.s_j,i.o_i,i.o_j,i.vor]
  #      for j in i.links:
  #        if j != []:
  #         print [j.s_i,j.s_j,j.o_i,j.o_j,j.vor]
  #      # print [i.s_i,i.s_j,i.o_i,i.o_j,i.vor] 
  
  return dir_str[score.index(max(score))]
 
 
            
  
   
##########
## MAIN ##
##########
player = raw_input()
pos = raw_input().split()
if player == 'r':
  [x,y,o_x,o_y] = [int(i) for i in pos]
elif player == 'g':
  [o_x,o_y,x,y] = [int(i) for i in pos]

board = []
for i in xrange(0,15):
  board.append(raw_input())


move = nextMove(player,x,y,o_x,o_y,board)
print move
