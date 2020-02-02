#!/usr/bin/python3
''' DSBGagent.py
 January 20, 2020.
This file is the implement of DSBG agent and using the Alpha-Beta pruning
'''
from backgState import *

class DSBGagent:
    def __init__(self):
        self.PRUNE=True
        self.MAXPLY = 4
        self.W = 0
        self.R = 1
        self.states_created=0
        self.cutoffs  = 0
        self.evalFunc=self.staticEval

    def game_over(self,state, who):
      if who==self.W: return len(state.white_off)==15
      else: return len(state.red_off)==15

    def remove_from_bar(self,new_state, who):
      #removes a white from start of bar list,
      # or a red from the end of the bar list.
      if who==self.W:
        del new_state.bar[0]
      else:
        new_state.bar.pop()

    def hit(self,new_state, dest_pt_list, dest_pt):
      opponent = 1-new_state.whose_move
      if len(dest_pt_list)==1 and dest_pt_list[0]==opponent:
        if opponent==self.W:
          new_state.bar.insert(self.W, 0) # Whites at front of bar
        else:
          new_state.bar.append(self.R) # Reds at end of bar
        new_state.pointLists[dest_pt-1]=[]
      return new_state

    def handle_move_from_bar(self,state, who, die):
      # We assume there is a piece of this color available on the bar.
      if who==self.W: target_point=die
      else: target_point=25-die
      pointList = state.pointLists[target_point-1]
      if pointList!=[] and pointList[0]!=who and len(pointList)>1:
         return False
      new_state = bgstate(state)
      new_state.whose_move = who
      new_state = self.hit(new_state, pointList, target_point)
      self.remove_from_bar(new_state, who)
      new_state.pointLists[target_point-1].append(who)
      return new_state

    def any_on_bar(self,state, who):
      return who in state.bar

    def bearing_off_allowed(self,state, who):
      # True provided no checkers of this color on the bar or in
      # first three quadrants.
      if self.any_on_bar(state, who): return False
      if who==self.W: point_range=range(0,18)
      else: point_range=range(6,24)
      pl = state.pointLists
      for i in point_range:
        if pl[i]==[]: continue
        if pl[i][0]==who: return False
      return True

    def bear_off(self, state, src_pt, dest_pt, who):
      # Return False if 'who' is not allowed to bear off this way.
      # Otherwise, create the new state showing the result of bearing
      # this one checker off, and return the new state.

      # First of all, is bearing off allowed, regardless of the dice roll?
      if not self.bearing_off_allowed(state, who): return False
      # Direct bear-off, if possible:
      pl = state.pointLists[src_pt-1]
      if pl==[] or pl[0]!=who:
        return False
      # So there is a checker to possibly bear off.
      # If it does not go exactly off, then there must be
      # no pieces of the same color behind it, and dest
      # can only be one further away.
      good = False
      if who==self.W:
        if dest_pt==25:
           good = True
        elif dest_pt==26:
           for point in range(18,src_pt-1):
             if self.W in state.pointLists[point]: return False
           good = True
      elif who==self.R:
        if dest_pt==0:
           good = True
        elif dest_pt== -1:
           for point in range(src_pt, 6):
             if self.R in state.pointLists[point]: return False
           good = True
      if not good: return False
      born_off_state = bgstate(state)
      born_off_state.pointLists[src_pt-1].pop()
      if who==self.W: born_off_state.white_off.append(self.W)
      else:  born_off_state.red_off.append(self.R)
      return born_off_state

    def handle_move_from_point(self, state, who, die, pt):
        if who == self.W:
            dest_pt = pt + die
        else:
            dest_pt = pt - die
        if dest_pt > 24 or dest_pt < 1:
            return self.bear_off(state, pt, dest_pt, who)

        dest_pt_list = state.pointLists[dest_pt - 1]
        if len(dest_pt_list) > 1 and dest_pt_list[0] != who:
            return False
        # So this checker's move is legal. Update the state.
        new_state = bgstate(state)
        new_state.whose_move=who
        # Remove checker from its starting point.
        new_state.pointLists[pt - 1].pop()
        # If the destination point contains a single opponent, it's hit.
        new_state = self.hit(new_state, dest_pt_list, dest_pt)
        # Now move the checker into the destination point.
        new_state.pointLists[dest_pt - 1].append(who)
        return new_state

    def possible_moves(self, state, player, die1, die2):
        first_moves={}
        final_moves={}
        count=0
        for check in state.bar:
            if check == player:
                count +=1

        if count > 1:
            # if there are two or more checkers on the bar, player can only move checkers from the bar
            fist_state = self.handle_move_from_bar(state, player, die1)
            if(fist_state):
                next_state = self.handle_move_from_bar(fist_state, player, die2)
                if(next_state):
                    move="0,0"
                    final_moves[move] = next_state
                else:
                    move="0,p"
                    final_moves[move] = fist_state
            else:
                next_state = self.handle_move_from_bar(state, player, die2)
                if(next_state):
                    move="0,p,R"
                    final_moves[move] = next_state

        else:
            #first move
            if player in state.bar:
                #only one checher on the bar
                next_state = self.handle_move_from_bar(state, player, die1)
                if(next_state):
                    move=(0,)
                    first_moves[move]=next_state
                next_state = self.handle_move_from_bar(state, player, die2)
                if(next_state):
                    move=(0,0)
                    first_moves[move]=next_state
            else:
                #no checker on the bar
                for i in range(len(state.pointLists)):
                    list = state.pointLists[i]
                    if len(list) > 0 and list[0] == player:
                        #possible move with first die
                        next_state = self.handle_move_from_point(state, player, die1, i+1)
                        if (next_state):
                            if self.game_over(next_state, player):
                                move=str(i+1)+",p"
                                final_moves[move] = next_state
                                return final_moves
                            move = (i+1,)
                            first_moves[move] = next_state
                        next_state = self.handle_move_from_point(state, player, die2, i + 1)
                        # possible move with second die
                        if (next_state):
                            if self.game_over(next_state, player):
                                move=str(i+1)+",p,R"
                                final_moves[move] = next_state
                                return final_moves
                            move = (0, i+1)
                            first_moves[move] = next_state

            #second move
            for fmove in first_moves.keys():
                cur_state=first_moves[fmove]
                for i in range(len(cur_state.pointLists)):
                    list = cur_state.pointLists[i]
                    if len(list) > 0 and list[0] == player:
                        if len(fmove) >1 :
                            # move with the first die
                            next_state =self. handle_move_from_point(cur_state, player, die1, i+1)
                            cur_move = "p"
                            if (next_state):
                                cur_move=str(i+1)
                                dupli = cur_move + "," + str(fmove[1])
                                # avoid duplication, 1,12 and 12,1,R are same
                                if dupli in final_moves:
                                    continue
                                final_move = str(fmove[1]) + "," + cur_move + ",R"
                                final_moves[final_move] = next_state
                            else:
                                final_move = str(fmove[1]) + "," + cur_move + ",R"
                                final_moves[final_move] = cur_state
                        else:
                            # move with the second die
                            next_state = self.handle_move_from_point(cur_state, player, die2, i + 1)
                            cur_move="p"
                            if (next_state):
                                cur_move=str(i+1)
                                dupli = cur_move+","+str(fmove[0])+",R"
                                # avoid duplication, 1,12 and 12,1,R are same
                                if dupli in final_moves:
                                    continue
                                final_move=str(fmove[0])+","+cur_move
                                final_moves[final_move] = next_state
                            else:
                                final_move=str(fmove[0])+","+cur_move
                                final_moves[final_move] = cur_state

        return final_moves

    def MinMaxGameTree(self, state, player, die1, die2, depth):

        moves = self.possible_moves(state, player, die1, die2)
        return_moves={}

        #if checker cannot move, then pass
        if len(moves) < 1 :
            moves["p"]=state

        for move in moves.keys():

            if self.game_over(moves[move],player):
                return_moves={}
                return_moves[move] = self.evalFunc(moves[move])
                return return_moves

            if depth <= 0:
                self.states_created +=1
                return_moves[move] = self.evalFunc(moves[move])
                continue

            moves[move].whose_move = 1-player
            next_states= self.MinMaxGameTree(moves[move], 1-player, die1, die2, depth - 1)

            alpha=-float("inf")
            beta=float("inf")
            result_score=None
            for next_move in next_states.keys():
                score=next_states[next_move]
                #max
                if player == self.W and score > alpha:
                    alpha = score
                    result_score = score
                #min
                elif player == self.R and score < beta:
                    beta = score
                    result_score = score
            return_moves[move]=result_score

        return return_moves

    def AlphaBetaGameTree(self, state, player, die1, die2, depth, alpha, beta):
        if self.game_over(state, player) or depth < 0:
            self.states_created += 1
            score = self.evalFunc(state)
            return (score, None)

        moves = self.possible_moves(state, player, die1, die2)

        #if checker cannot move, then pass
        if len(moves) < 1 :
            moves["p"]=state

        # ordering of successors best-first
        order={}
        for move in moves.keys():
            order[move]=self.evalFunc(moves[move])

        if player == self.W:
            #descending order
            order = sorted(order.items(), key=lambda item:item[1], reverse=True)
        else:
            #ascending order
            order = sorted(order.items(), key=lambda item: item[1])

        return_move=None
        for moveOrder in order:
            move = moveOrder[0]
            score, _ = self.AlphaBetaGameTree(moves[move], 1-player, die1, die2, depth - 1, alpha, beta)
            # alpha beta pruning
            # max
            if player == self.W:
                if score > alpha:
                    alpha = score
                    return_move = move
                if alpha >= beta:
                    self.cutoffs += 1
                    break
            # min
            else:
                if score < beta:
                    beta = score
                    return_move = move
                if alpha >= beta:
                    self.cutoffs += 1
                    break

        if player == self.W:
            return (alpha, return_move)
        else:
            return (beta, return_move)

    def staticEval(self, current_state):
            wPenalty = 0
            rPenalty = 0
            for i in range(len(current_state.pointLists)):
                list = current_state.pointLists[i]
                if len(list) > 0:
                    if list[0] == self.W:
                        if i == 18 or i == 19:
                            wPenalty += len(list)
                            continue
                        wPenalty += len(list) * (24 - i) * (24 - i)
                    else:
                        if i == 5 or i == 4:
                            rPenalty += len(list)
                            continue
                        rPenalty += len(list) * (i + 1) *(i + 1)
            for checker in current_state.bar:
                if checker == self.W:
                    wPenalty += 625
                else:
                    rPenalty += 625
            return rPenalty - wPenalty

    def statesAndCutoffsCounts(self):
        print(self.states_created, self.cutoffs)

    def useSpecialStaticEval(self, func):
        self.evalFunc=func

    def useAlphaBetaPruning(self,prune):
        self.states_created=0
        self.cutoff=0
        self.PRUNE = prune

    def setMaxPly(self,maxply):
        self.MAXPLY = maxply

    def move(self, state, die1, die2):
        if self.PRUNE is not True:
            moves = self.MinMaxGameTree(state, state.whose_move, die1, die2, self.MAXPLY)
            move_to_return = None
            alpha=-float("inf")
            beta=float("inf")

            #if player can't move, then pass
            if len(moves) <1:
                return "p"

            for next_move in moves.keys():
                score=moves[next_move]
                if state.whose_move == self.W and score > alpha:
                    alpha = score
                    move_to_return=next_move
                #min
                elif state.whose_move == self.R and score < beta:
                    beta = score
                    move_to_return = next_move
        else:
            alpha=-float("inf")
            beta=float("inf")
            score,move_to_return = self.AlphaBetaGameTree(state, state.whose_move, die1, die2, self.MAXPLY, alpha, beta)

        return move_to_return