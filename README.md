# 列生成算法及其代码实现

## 1 下料问题

### 1.1 问题描述

* **问题详细描述：**
  * 有 $m$ 种成品板材，构成一个成品板材集合 $I=\lbrace 1,2,...,m \rbrace$，每一种板材 $i \in I$ 都有各自的规格（长度）$w_i$ 和 市场需求率 $b_i$
  * 原料板材有统一的长度 $W$，并且满足 $W \ge \max_{i \in I} w_i$
  * 问题：在保证每种成品板材 $i \in I$ 的市场需求都满足的情况下，原料板材的最低消耗是多少？
* **问题实例：**
  * 

### 1.2 模型构建

#### 1.2.1 Kantorovich模型

* **决策变量：**
  * $x_{ij}:$ 使用原料板材 $i$ 产出成品板材 $i \in I$ 的数量
  * $y_j = \begin{cases} 
    1, & \text{如果原料板材 } j \in J \text{ 被使用} \\
    0, & \text{otherwise}
    \end{cases}$
* **数学模型：**

aaaaa



#### 1.2.2 Gilmore-Gomory模型



### 1.3 模型求解



### 1.4 列生成算法及其应用



## 2 VRP问题