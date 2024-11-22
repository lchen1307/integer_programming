\ Model Piece-wise Linear Function Example
\ LP format - for model browsing. Use MPS format to capture full model detail.
Maximize
  y
Subject To
 x_eq: x - 20 beta_1 - 30 beta_2 - 40 beta_3 = 0
 y_eq: y - 40 beta_1 - 55 beta_2 - 67 beta_3 = 0
 beta_eq: beta_0 + beta_1 + beta_2 + beta_3 = 1
 z_eq: z_1 + z_2 + z_3 = 1
 Logic_0: beta_0 - z_1 <= 0
 Logic_3: beta_3 - z_3 <= 0
 Logic_1: beta_1 - z_1 - z_2 <= 0
 Logic_2: beta_2 - z_2 - z_3 <= 0
 R8: x = 35
Bounds
 beta_0 <= 1
 beta_1 <= 1
 beta_2 <= 1
 beta_3 <= 1
Binaries
 z_1 z_2 z_3
End
