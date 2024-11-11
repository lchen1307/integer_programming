\ Model DW Master Problem
\ LP format - for model browsing. Use MPS format to capture full model detail.
Maximize
  800 y3 + 280 y4 + 240 y7
Subject To
 rmp_con_central: 60 y3 + 28 y4 + 20 y7 <= 80
 rmp_con_convex_combine_mu: y1 + y3 = 1
 rmp_con_convex_combine_lam: y2 + y4 + y7 = 1
Bounds
 y1 <= 1
 y2 <= 1
 y3 <= 1
 y4 <= 1
End
