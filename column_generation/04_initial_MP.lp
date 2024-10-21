\ Model MasterProblem
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  10000 slackVar[0] + 10000 slackVar[1] + 10000 slackVar[2]
Subject To
 R0: slackVar[0] >= 11
 R1: slackVar[1] >= 36
 R2: slackVar[2] >= 12
Bounds
End
