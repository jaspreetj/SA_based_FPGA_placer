#Jaspreet Jhoja
#Implementation of Ranging Windows

import random,copy, statistics, timeit, threading, math
from math import *
import numpy as np
import matplotlib.pyplot as plt
import plot as pt
import queue as Queue

#In test case, we will read cm138a.txt file
print("SIMULATED ANNEALING Range Windows BASED PLACER")
files = ['cm138a.txt', 'cm150a.txt', 'cm151a.txt', 'cm162a.txt', 'alu2.txt', 'C880.txt',
         'e64.txt', 'apex1.txt', 'cps.txt', 'paira.txt', 'pairb.txt', 'apex4.txt']
#filename = "cm138a.txt"
for i in range(len(files)):
    print('['+str(i)+']'+' - '+ files[i])

choice = input("choose files to run")
gui_choice = input("Do you want to see the progress in a GUI? y/n")
for i in range(1):
    #for choice in range(len(files)):
    
    filename = files[int(choice)]

    #filename = 'ap.txt'

    print(filename)

    global nets, nodes, grid, netsn, nodesn
    nets = []  #net details
    nodes = {} #store all nodes in a dictionary
    grid = []  #stores grid size
    netsn = 0  #number of nets
    nodesn = 0 #number of nodes
    optimum = {}#optimum results

    grids = {} #facilitate coodinate searching
    old_swap = [None, None]#previously swapped nodes
    new_swap = [None, None] #currently proposed moves to swap


    ## Simulated Annealing variables
    current_cost = 0
    new_cost = 0

    old_temp = 0
    current_temp = 0

    iterations = 0


    #####################  NOTES   ###################
    #to get sinks for a node
    #get nodedata by nodes[number][0]
    #get sinks list by nodes[number][1]


    #function to read file
    def readfile(filename): 
        global grid, netsn, nodesn, nets, nodes
        
        #split lines to read one by one
        lines = open(filename).read().splitlines()

        #extract grid
        grid = [int(lines[0].split(' ')[-1]),int(lines[0].split(' ')[-2])]
        nets = []

        #iterate lines, extract number of nets and individual net nodes 
        for i in range(len(lines)):
            if(i==0):
                netsn = int(lines[i].split(' ')[-3])  #extract number of nets
                nodesn = int(lines[i].split(' ')[0])  #extract number of nodes

                #generate coordinates for nodes which we will use for cost eval
                coordinates = []
                for c in range(grid[0]):
                        for r in range(grid[1]):
                                coordinates.append([c,r*2])   


                #based on number of nodes, create dictionary keys
                for each_node in range(grid[0]*grid[1]):
                           nodes[str(each_node)] = [coordinates[each_node],[]]
                           grids[str(coordinates[each_node])] = str(each_node)
            
            else:
                #separate the net details and put them in a list
                temp = list(filter(None,lines[i].split(' ')[1:]))
                if(len(temp)>0):
                    nets.append(temp)

                    # associate nodes to their connections
                    source =temp[0]
                    sinks = temp[1:]
                    for each_sink in sinks:
                        nodes[source][1].append([each_sink])

        # for nodes with no sinks, set none as their sinks so no arrow emerge from those nodes
        for each_node in nodes:
                sink_list = nodes[str(each_node)][1]
                if(len(sink_list)==0):
                    nodes[str(each_node)][1].append(None)

    #run the read function
    readfile(filename)




    #select moves based on coordinates and range windows
    
    def select_nodes(previous_swaps, grid_dict, R_val):
        new_lot = []
        while True:
            if(len(new_lot)==0):
                #if there is no selection then select any as long it wasnt selected previously
                #this is to avoid being stuck in a loop
                new_node = random.choice([x for x in range(grid[0]*grid[1]) if x not in previous_swaps])
                new_lot.append(str(new_node))

            elif(len(new_lot) == 1):
                #select previously generated element
                first = new_lot[0]

                #get coordinates to compare
                f_coord = nodes[str(first)][0]


                #generating second value within the range window
                
                #generate u and v random values between 0 - 1
                u = random.random()
                v = random.random()
                
                w = R_val * math.sqrt(u)
                t = 2*math.pi * v
                 #factors to calculate  x & y  values
                x = w * math.cos(t)
                y = w*math.sin(t)   

                #get new coordinates
                new_point = [int(x+f_coord[0]), int(y+f_coord[1])]

                #check if its a point on the board and is not a negative value
                if(new_point[0]>=0 and new_point[1]>=0):
                    while True:
                        #if its y value is positive and is a multiple of 2
                        #accept it
                        if(new_point[1]%2 == 0):
                            break
                        #generate a new y vaue between the range of 0 - range+1
                        #example for range of 3, the possible value it can accept are
                        #0 and 2
                        new_y =  int(random.randrange(0,new_point[1]+1,2))
                        if(new_y<new_point[1]):
                            new_point[1] = new_y
                   # print(new_point)
                    #check in the list
                    if(str(new_point) in grid_dict):
                        new_node = grid_dict[str(new_point)] 
                        if(new_node not in previous_swaps):
                                new_lot.append(str(new_node))            
                    #return the point we want to swap not coordinates
        
            elif(len(new_lot)==2):
                return new_lot




    # accept moves
    def make_swap(nodes_dict, grid_dict, swap):
            a = swap[0]
            b = swap[1]
            coor_a = nodes_dict[a][0]
            coor_b = nodes_dict[b][0]
            nodes_dict[a][0] = coor_b
            nodes_dict[b][0] = coor_a

            grid_dict[str(coor_a)] = a
            grid_dict[str(coor_b)] = b
            
            return(nodes_dict, grid_dict)
            

    def calculate_cost(nodes_dict, nets):
        cost = []
        for each_net in nets:
            net_x = []
            net_y = []
            dx = 0
            dy = 0
            for each_node in each_net:
                data = nodes_dict[each_node][0]
                net_x.append(data[0])
                net_y.append(data[1])
            dx = abs(max(net_x) - min(net_x))
            dy = abs(max(net_y) - min(net_y))
            cost.append(dx+dy)
        return(sum(cost))
            


    #start plotting
    if(gui_choice == "y"):        
        queue = Queue.Queue()
        plot_thread = threading.Thread(target=pt.plotter, args=(queue, ))
        plot_thread.start()
    
    
    #timer function
    start_time = timeit.default_timer()


    #setup SA
    #number of iterations
    iterations = int(10*((nodesn)**(3/4))) #based on number of cells to place
    #iterations = int(10*(math.sqrt(grid[0]*2*grid[1])**(4/3)))
    iterations = 100

    #R_limiter values
    R_current = grid[0]+(2*grid[1])
    R_prev = R_current

    #set initial cost    
    initial_cost = calculate_cost(nodes, nets)

    #set initial temperature
    sigma_list = []
    r_vals = []

    current_temp = 200*(initial_cost/(grid[0]*grid[1]))
    print(current_temp, iterations)

    #start with simulated annealing

    optimum = nodes

    while current_temp!=0:

        sigma_list = []
        for i in range(iterations):
            
            current_cost = calculate_cost(nodes, nets)

            #copy nodes data
            temp_nodes = copy.deepcopy(nodes)
            temp_grids = copy.deepcopy(grids)

            #get nodes to swap for temp_nodes
            new_swap = select_nodes(old_swap, temp_grids, R_current)
            old_swap = new_swap

            #modify node data
            temp_nodes, temp_grids = make_swap(temp_nodes, temp_grids, new_swap)

            #get cost for new swap
            new_cost = calculate_cost(temp_nodes, nets)
            dc = new_cost - current_cost

            if(dc<0):
                nodes = temp_nodes
                grids = temp_grids
                sigma_list.append(new_cost)
                
            else:
                r = random.random()
                if(r< e**(-dc/current_temp)):
                    nodes = temp_nodes
                    grids = temp_grids
                    sigma_list.append(new_cost)


            if(calculate_cost(optimum,nets)>calculate_cost(nodes, nets)):
                            optimum = nodes
            
        R_accept = len(sigma_list)/iterations #ration of moves accepted in the previous iteration
        #R_limit
        print(R_current)
        #update range windows
        if(R_accept<0.44):
            R_current = R_current - 1
        elif(R_accept>0.44):
            R_current = R_current + 1

        
        #R_current = R_prev * (1 - 0.44 + R_accept)
            #increase range
    
      
        if(0.96 < R_accept):
            alpha = 0.5
        elif(0.8 < R_accept and R_accept<=0.96):
            alpha = 0.9
        elif(0.15 < R_accept and R_accept<=0.8):
            alpha = 0.95
        elif(R_accept<=0.15):
            alpha = 0.8

        r_vals.append(alpha)
        
        current_temp = alpha* current_temp

        #current_temp = current_temp *e**(-0.7*current_temp/sigma)

        if(current_temp< 0.01):
            current_temp = 0

        #add for plotting
        if(gui_choice == "y"):            
            pt.update_data_sync(current_temp, calculate_cost(nodes, nets))
            queue.put("GO")
        #print(calculate_cost(nodes,nets), current_temp)


    if(calculate_cost(optimum,nets)<calculate_cost(nodes, nets)):
        nodes = optimum

    final_cost = calculate_cost(nodes, nets)
    elapsed = timeit.default_timer() - start_time
    print("0.5", r_vals.count(0.5))
    print('0.9', r_vals.count(0.9))
    print('0.95', r_vals.count(0.95))
    print('0.8', r_vals.count(0.8))
    print("time elapsed : ", elapsed)
    print("final cost :", final_cost)






