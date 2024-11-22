\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  6 y_0 + 2 x_0_0 + 6 x_1_0 + 11 x_2_0 + 7 y_1 + 2 x_0_1 + 7 x_1_1
   + 13 x_2_1 + 6 y_2 + 12 x_0_2 + 8 x_1_2 + x_2_2
Subject To
 R0: x_0_0 + x_0_1 + x_0_2 = 1
 R1: y_0 - x_0_0 >= 0
 R2: y_1 - x_0_1 >= 0
 R3: y_2 - x_0_2 >= 0
 R4: x_1_0 + x_1_1 + x_1_2 = 1
 R5: y_0 - x_1_0 >= 0
 R6: y_1 - x_1_1 >= 0
 R7: y_2 - x_1_2 >= 0
 R8: x_2_0 + x_2_1 + x_2_2 = 1
 R9: y_0 - x_2_0 >= 0
 R10: y_1 - x_2_1 >= 0
 R11: y_2 - x_2_2 >= 0
Bounds
 x_0_0 <= 1
 x_1_0 <= 1
 x_2_0 <= 1
 x_0_1 <= 1
 x_1_1 <= 1
 x_2_1 <= 1
 x_0_2 <= 1
 x_1_2 <= 1
 x_2_2 <= 1
Binaries
 y_0 y_1 y_2
End
