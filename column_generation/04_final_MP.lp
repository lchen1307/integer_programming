\ Model MasterProblem
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  10000 slackVar[0] + 10000 slackVar[1] + 10000 slackVar[2] + new_x1
   + new_x2 + new_x3 + new_x4
Subject To
 R0: slackVar[0] + 7 new_x1 + new_x2 + new_x4 >= 9
 R1: slackVar[1] + 4 new_x2 + new_x4 >= 16
 R2: slackVar[2] + 3 new_x3 + 2 new_x4 >= 47
Bounds
End
