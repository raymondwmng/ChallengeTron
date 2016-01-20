#!/usr/bin/python


class Node:
  def __init__(self,s_i,s_j,o_i,o_j,vor,oldtempblock=None,newtempblock=None):
    self.s_i = s_i
    self.s_j = s_j
    self.o_i = o_i
    self.o_j = o_j
    self.vor = vor
    if newtempblock==None and oldtempblock==None:
      self.tempblock = [[0 for j in range(0,15)] for i in range(0,15)]
    else:
      self.tempblock = oldtempblock + newtempblock
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
    return Node(new_s_i,new_s_j,new_o_i,new_o_j,vor,self.tempblock,new_tempblock)
  
  def stepadvance(self,perm_block):
    if self.links == None:
      self.links = list()
      for sdirection in range(0,4):
        for odirection in range(0,4):
          (voronoi_sum_,s_dead,o_dead,o_block) = gen_voronoi_sum(self.s_i,self.s_j,self.o_i,self.o_j,perm_block,self.tempblock,sdirection,odirection)
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
  v = [[] for i_ctr in xrange(0,15)]
  for vi in xrange(0,15):
    v[vi] = [[] for j_ctr in xrange(0,15)]
    for vj in xrange(0,15):
      if abs(vi-i)+abs(vj-j) < abs(vi-o_i)+abs(vj-o_j):
        v[vi][vj] = 1
      elif abs(vi-i)+abs(vj-j) > abs(vi-o_i)+abs(vj-o_j):
        v[vi][vj] = -1
      else:
        v[vi][vj] = 0
  return v



def checkijrange(i):
  if i > 0 and i < 14:
    return True
  else:
    return False

def gen_voronoi_sum(s_i,s_j,o_i,o_j,block,tempblock,self_move,o_move): 
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
  elif block[self_new_i][self_new_j] == 1 or tempblock[self_new_i][self_new_j] == 1:
    voronoi_change = -999999
    s_dead = True
  if checkijrange(o_new_i) == False or \
    checkijrange(o_new_j) == False:
      voronoi_change = 1
      o_dead = True
  elif block[o_new_i][o_new_j] == 1 or tempblock[o_new_i][o_new_j] == 1:
    voronoi_change = 1
    o_block = True
    o_dead = True
 
  
  this_voronoi = gen_voronoi(self_new_i,self_new_j,o_new_i,o_new_j)
  
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
           
  dir_str = ['UP','LEFT','DOWN','RIGHT']

    
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
