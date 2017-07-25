# SA based FPGA placer

### Objective

### Design Rules

### Requirements
In order to run the program, the user is required to have the following modules installed:
* Python 3.x
* Matplotlib
* Numpy

The basic pseudocode for the placement tool is given below:
```
1: select circuit
2: set initial placement
3: set initial temperature and iterations
4: While not exit condition do
5:    For k iterations do
6:        select cells to swap
7.            Calculate new cost
8.            Calculate deltaC = New cost - Old cost
9.        if(deltaC <0)
10.           Accept the solution
11.       Else:
12.           R = rand(0,1)
13.           if(R< e−deltaC/T )then
14.               Accept the solution
16.           Else
17.               Reject solution
18.       End if
19.   End for
20.   Update T
21.   Update net criticality
22.End while
```


