\ Model MasterProblem
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  10000 slackVar[0] + 10000 slackVar[1] + 10000 slackVar[2]
Subject To
 R0: slackVar[0] >= 9
 R1: slackVar[1] >= 16
 R2: slackVar[2] >= 47
Bounds
End
