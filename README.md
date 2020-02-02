# Deterministic-Simplified-Backgammon
game-playing agent based on Minimax search and Alpha-Beta pruning

A simple game master program for Simplified Backgammon.

To use this program, run the program under Python 3.x from a command line:
python3 gameMaster.py  

The rules of the game are simplified for this version of Backgammon.
A. WHITE always plays first, so there is no initial rolling and
   requirement that the first player use the initial roll.
   
B. No doubling allowed. "Cube value" is therefore always 1.

C. A player may pass on any turn, in either of two ways:
     -- Pass on the whole turn. 
     -- Pass on moving a second checker.
     
D. If no move is available to a player on its turn, then it MUST pass
   or forfeit the game.  If it can move only one checker, then it
   should do that and pass for the second checker.
   
E. If the dice come out doubles (like a pair of sixes), then unlike
   standard backgammon, where the player can move 4 checkers, we
   don't allow any special bonus.
   
F. Standard backgammon has a rule that if a player can only use one
   of the two dice, the player must use the larger number.  We do not
   follow that rule.  Either number may be used.
   
G. No special rules are in effect, like the Crawford rule, since
   we don't use the doubling cube.
