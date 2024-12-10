\ Model DW Master Problem
\ LP format - for model browsing. Use MPS format to capture full model detail.
Maximize
  s_1
Subject To
 rmp_con_central: - s_1 <= 80
 rmp_con_convex_combine_mu: = 0
 rmp_con_convex_combine_lam: = 0
Bounds
 s_1 <= 1000
End
