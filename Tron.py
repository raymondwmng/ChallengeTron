#!/usr/bin/python

# import sys,re,os

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

# PART1: generate a voronoi diagram
# (See report for pseudocode) 
def gen_voronoi(i,j,o_i,o_j):
  v = [[] for i_ctr in xrange(0,15)]
  for vi in xrange(0,15):
    v[vi] = [[] for j_ctr in xrange(0,15)]
    for vj in xrange(0,15):
      if abs(vi-i)+abs(vj-j) > abs(vi-o_i)+abs(vj-o_j):
        v[vi][vj] = 1    # point closer to self: +1
      elif abs(vi-i)+abs(vj-j) < abs(vi-o_i)+abs(vj-o_j):
        v[vi][vj] = -1   # point closer to opponent: -1
      else:
        v[vi][vj] = 0
  return v

# check if the location is out of bound
def checkijrange(i):
  if i > 0 and i < 14:
    return True
  else:
    return False
  

def nextMove(player,s_i,s_j,o_i,o_j,board):
  block = board2block(board)
 
  i_moves = [ -1, 0 , 1 , 0]
  j_moves = [  0, -1, 0 , 1]
  dir_str = ['UP','LEFT','DOWN','RIGHT']

  # PART2: reward calculation and decision making: 
  # gen voronoi_scores for 4*4 movement possibilities 
  # for each of the 4 self_move directions, 
  # summing the 4 voronoi diagrams from 4 opponent_move directions 
  # See report for pseudocode
  voronoi_sum_o = [0 for i in range(0,4)]
  for self_move in range(0,4):
    self_new_i = s_i + i_moves[self_move]
    self_new_j = s_j + j_moves[self_move]
    if checkijrange(self_new_i) == False or \
      checkijrange(self_new_j) == False:
        voronoi_sum_o[self_move] = -999    # impossible self_move
    elif block[self_new_i][self_new_j] == 1:
        voronoi_sum_o[self_move] = -999    # impossible self_move
    else:
      this_voronoi = [[] for j in range(0,4)]
      for o_move in range(0,4):
        o_new_i = o_i + i_moves[o_move]
        o_new_j = o_j + j_moves[o_move]
        if checkijrange(o_new_i) == False or \
          checkijrange(o_new_j) == False:
          this_voronoi[o_move] = 0
        elif block[o_new_i][o_new_j] == 1:
          this_voronoi[o_move] = 0
        else:        
          voronoi = gen_voronoi(self_new_i,self_new_j,o_new_i,o_new_j)
          this_voronoi[o_move] = 0
          for i in range(0,len(voronoi)):
            this_voronoi[o_move] = this_voronoi[o_move]+sum(voronoi[i])
          # this_voronoi[o_move] = np.sum(voronoi)
        voronoi_sum_o[self_move] = voronoi_sum_o[self_move] + this_voronoi[o_move] 

  nextDirection = voronoi_sum_o.index(max(voronoi_sum_o))

  return dir_str[nextDirection]
   


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
