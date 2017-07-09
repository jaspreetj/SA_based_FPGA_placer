#Jaspreet Jhoja
#plotting function

import random
import time, math
import queue as Queue
import threading
import numpy as np
import matplotlib.pyplot as plt

#variables to collect x and y data
plot_x = []
plot_y = []
lock = threading.Lock()

#update data with locks
def update_data_sync(x, y):
    lock.acquire()
    plot_x.append(x)
    plot_y.append(y)
    lock.release()
    
#parse data to plotter
def get_data_sync():
    lock.acquire()
    v1 = list(plot_x)
    v2 = list(plot_y)
    lock.release()
    return (v1,v2)

#does the main plotting
def plotter(queue):
    plt.ion()
    fig = plt.figure(1)
    ax = fig.add_subplot(111)
    ax.set_title("Cost vs Temperature")
    ax.autoscale(enable=True, axis='both')
    ax.set_xlabel("Temperature")
    ax.set_ylabel("cost")
    ax.invert_xaxis()
    global line1
    line1, line2 = ax.plot([], [], 'b-', [], [], 'r-')

    while True:
        need_draw = False
        is_bye = False

        while True:
            ## Try to exhaust all pending messages
            try:
                msg = queue.get_nowait()
                if msg is None:
                    #print "thread: FATAL, unexpected")
                    sys.exit(1)
                if msg == 'BYE':
                    #print "thread: got BYE"
                    is_bye = True
                    break
                # Assume default message is just let me draw
                need_draw = True
            except Queue.Empty as e:
                # Not 'GO' or 'BYE'
                break

        ## Flow control
        if is_bye:
            break
        if not need_draw:
            plt.pause(0.33)
            continue;

        ## Draw it
        (v1,v2) = get_data_sync()
        line1.set_ydata(v2)
        line1.set_xdata(v1)

         #Adjust view
        ax.set_xlim(max(line1.get_xdata())+ int((1/4)*max(line1.get_xdata())), -1*math.sqrt(max(line1.get_xdata())))
        ax.set_ylim(-(1/3)*max(line1.get_ydata()), max(line1.get_ydata()) + int((1/4)*max(line1.get_ydata())))
        ax.relim()
        ax.autoscale_view(tight=True, scalex=True, scaley=False)
        fig.canvas.draw()
        plt.pause(0.05)
    plt.show(block=True)
    plt.close('all')
    #print "thread: worker exit"
    return



