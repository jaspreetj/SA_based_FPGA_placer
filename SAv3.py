#Author: Jaspreet Jhoja
#contact:Jaspreetj@ece.ubc.ca

import random,copy, statistics, timeit, threading, math
from math import *
import numpy as np
import matplotlib.pyplot as plt
import plot as pt
import queue as Queue


print("SIMULATED ANNEALING BASED PLACER")
files = ['cm138a.txt', 'cm150a.txt', 'cm151a.txt', 'cm162a.txt', 'alu2.txt', 'C880.txt',
         'e64.txt', 'apex1.txt', 'cps.txt', 'paira.txt', 'pairb.txt', 'apex4.txt']


for i in range(len(files)):
    print('['+str(i)+']'+' - '+ files[i])

choice = input("choose files to run")

gui_choice = input("Do you want to see the progress in a GUI? y/n")

#if you want to use custom iterations and temperature, define here
user_iterations = 0
user_temp = 0

#want to run a mix of temperature handlers
hybrid = 0


#or choice in range(len(files)):
for i in range(1):
    
    filename = files[int(choice)]

    print(filename)

    global nets, nodes, grid, netsn, nodesn, plot_x, plot_y
    nets = []  #net details
    nodes = {} #store all nodes in a dictionary
    grid = []  #stores grid size
    netsn = 0  #number of nets
    nodesn = 0 #number of nodes
    optimum = {}#optimum results

    plot_x = []
    plot_y = []

    old_swap = [None, None]#previously swapped nodes
    new_swap = [None, None] #currently proposed moves to swap


    ## Simulated Annealing variables
    current_cost = 0 #initial or current cost
    new_cost = 0  #new proposed cost

    old_temp = 0  #previous temperature
    current_temp = 0 #current or initial temperature
    iterations = 0 #iterations


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


    # select two nodes which have  not been repeated in the previous swap
    def select_nodes(nodes_dict, previous_swaps):
        new_lot = []
        while True:
            if(len(new_lot)==2):
                #check if i am swapping two unoccupied slots
                a = new_lot[0]
                b = new_lot[1]
                coor_a = nodes_dict[a][0][0]
                coor_b = nodes_dict[b][0][0]
                if(coor_a == None and coor_b == None):
                    print(new_lot)
                    new_lot = []
                else:
                    return new_lot
            new_node = random.choice([x for x in range(grid[0]*grid[1]) if x not in previous_swaps])
            new_lot.append(str(new_node))


    # accept moves
    def make_swap(nodes_dict,swap):
            a = swap[0]
            b = swap[1]
            coor_a = nodes_dict[a][0]
            coor_b = nodes_dict[b][0]
            nodes_dict[a][0] = coor_b
            nodes_dict[b][0] = coor_a
            return(nodes_dict)
            
    #function to calculate cost
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
            #calculate half-perimeter
            dx = abs(max(net_x) - min(net_x))
            dy = abs(max(net_y) - min(net_y))
            cost.append(dx+dy)
        return(sum(cost))
            

    #timer function
    start_time = timeit.default_timer()


    #setup SA
    if(user_iterations == 0):
        iterations = int(10*((nodesn)**(4/3)))
    else:
        iterations = user_iterations
        
    initial_cost = calculate_cost(nodes, nets)

    sigma = 0 #std dev of cost of accepted solutions
    sigma_list = [] #list to store solutions
    r_val = []
    
    #set initial temperature
    if(user_temp == 0):
        for i in range(50):
            sigma_node = copy.deepcopy(nodes)
            sigma_swap = select_nodes(sigma_node, old_swap)
            old_swap = sigma_swap
            sigma_node = make_swap(sigma_node, sigma_swap)
            temp_cost = calculate_cost(sigma_node, nets)
            if(temp_cost<initial_cost):
                sigma_list.append(temp_cost)

        #calculate the standard deviation of accepted sigma values
        sigma = statistics.stdev(sigma_list)
        current_temp = 20*sigma

    print(initial_cost, current_temp, iterations)
    old_swap=[None, None]
    #start with simulated annealing

    #start plotting
    if(gui_choice == "y"):        
        queue = Queue.Queue()
        plot_thread = threading.Thread(target=pt.plotter, args=(queue, ))
        plot_thread.start()

    #check if cost is being repeated
    isrepeating = 0

    #record optimum node ever came across
    optimum = nodes

    while current_temp!=0:
      
        sigma_list = []
        for i in range(iterations):
            current_cost = calculate_cost(nodes, nets)

            #copy nodes data
            temp_nodes = copy.deepcopy(nodes)

            #get nodes to swap for temp_nodes
            new_swap = select_nodes(temp_nodes, old_swap)
            old_swap = new_swap

            #modify node data
            temp_nodes = make_swap(temp_nodes, new_swap)

            #get cost for new swap
            new_cost = calculate_cost(temp_nodes, nets)
            dc = new_cost - current_cost

            #if good
            if(dc<0):
                nodes = temp_nodes
                sigma_list.append(new_cost)
                        #update best

            #if bad
            else:
                r = random.random()
                if(r< math.e**(-dc/current_temp)):
                    nodes = temp_nodes
                    sigma_list.append(new_cost)


            if(calculate_cost(optimum,nets)<calculate_cost(nodes, nets)):
                            optimum = nodes

        #current_temp = 0.98 *current_temp
        #acceptance ratio of moves accepted to total tried 
        R_accept = len(sigma_list)/iterations

        previous_temp = copy.deepcopy(current_temp)

        if(0.96 < R_accept):
            alpha = 0.5
        elif(0.8 < R_accept and R_accept<=0.96):
            alpha = 0.9
        elif(0.05 < R_accept and R_accept<=0.8):
            if(iterations==500):
                alpha = 0.98
            else:
                alpha = 0.95
        elif(R_accept<=0.05):
            alpha = 0.8
            
        r_val.append(alpha)
        
        try:
            if(hybrid == 1):
                    
                #check if temperature is stuck
                if(isrepeating ==5):
                    current_temp = alpha*current_temp
                    isrepeating = 0

                elif(isrepeating >=10):
                    current_temp = 0
                    
                else:
                    sigma = statistics.stdev(sigma_list)
                    current_temp = current_temp *math.e**(-0.7*(current_temp/sigma))
                    isrepeating = 0
            else:
                    current_temp = alpha*current_temp
                    isrepeating = 0

        except Exception as e:
            None



        #COMMENT THIS LINE IF DONT WANT ANY UPDATES
        print(alpha,calculate_cost(nodes, nets), current_temp )

        if(str(previous_temp)[:7] == str(current_temp)[:7]):
            isrepeating = isrepeating + 1
            
        #print(isrepeating)
        if(current_temp<5e-6):
            current_temp = 0


        #add for plotting
        if(gui_choice == "y"):            
            pt.update_data_sync(current_temp, calculate_cost(nodes, nets))
            queue.put("GO")
       # print(calculate_cost(nodes,nets), current_temp)

   
    final_cost = calculate_cost(nodes, nets)
    elapsed = timeit.default_timer() - start_time
    print("time elapsed : ", elapsed)
    print("final cost :", final_cost)

    
    if(gui_choice == 'y'):
        queue.put('BYE')

