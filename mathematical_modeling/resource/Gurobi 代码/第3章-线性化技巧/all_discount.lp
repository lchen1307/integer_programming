\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
 
Subject To
 R0: - pi_1 - pi_2 - pi_3 + x = 0
 R1: - 2 pi_1 - 1.5 pi_2 - 1.2 pi_3 + y = 0
 R2: pi_1 - 20 u_1 <= 0
 R3: - pi_2 + 20 u_2 <= 0
 R4: pi_2 - 30 u_2 <= 0
 R5: - pi_3 + 30 u_3 <= 0
 R6: pi_3 - 40 u_3 <= 0
 R7: u_1 + u_2 + u_3 = 1
 R8: x = 35
Bounds
 pi_1 <= 1000
 pi_2 <= 1000
 pi_3 <= 1000
 x <= 1000
 y <= 1000
Binaries
 u_1 u_2 u_3
End
