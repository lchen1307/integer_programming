\ Model Master Problem
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  x_0 + x_1 + x_2 + x_3 + x_4 + new_x1 + new_x2 + new_x3
Subject To
 c_1: 8 x_0 + 6 x_1 + 6 x_2 + 5 x_3 + 5 x_4 >= 46
 c_2: x_1 + x_3 + 2 x_4 + 4 new_x2 + 3 new_x3 >= 22
 c_3: x_2 + x_3 + 7 new_x1 + 2 new_x3 >= 43
Bounds
End
