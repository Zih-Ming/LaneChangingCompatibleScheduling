import random
import numpy as np
import copy
import math
from utils import *
import sys

# use record functions to record information about scheduling result if recorded is True
recorded = True

# random sample from 0. to time_range. for earliest arrival time
time_range = 10

def sampleEarliestArrivalTimeAndModel():
    a = sorted(np.random.uniform(0, time_range, ALPHA))
    b = sorted(np.random.uniform(0, time_range, BETA))
    a_models = [random.randint(1, NMODELS) for _ in range(ALPHA)]
    b_models = [random.randint(1, NMODELS) for _ in range(BETA)]
    return a, b, a_models, b_models

def initTestCase():
    # a, b: sorted earliest arrival times
    # a_models, b_models: models
    a, b, a_models, b_models = sampleEarliestArrivalTimeAndModel()

    vehicles_lane_A = np.array([Vehicle(i, 'A', a[i], a_models[i]) for i in range(0, ALPHA)])
    vehicles_lane_B = np.array([Vehicle(j, 'B', b[j], b_models[j]) for j in range(0, BETA)])

    return Vehicles(vehicles_lane_A, vehicles_lane_B)

# generate the order of version A given vehicles and their earliest arrival times
def generateOrderByEarliest(vehicles):
    order = []
    iA, iB, accuB = 0, 0, 0

    while iA < ALPHA and iB < BETA:
        if vehicles.laneA[iA].earliest <= vehicles.laneB[iB].earliest:
            order.append(accuB)
            accuB = 0
            iA += 1
        else:
            accuB += 1
            iB += 1
    order.append(max(accuB, BETA - iB))
    if iA < ALPHA:
        order.extend([0] * (ALPHA - iA))

    return order

# generate the order of version A given vehicles and their schedule times
# note that the function won't check if schedule time is valid
def generateOrderBySchedule(vehicles):
    order = []
    iA, iB, accuB = 0, 0, 0

    while iA < ALPHA and iB < BETA:
        if vehicles.laneA[iA].schedule <= vehicles.laneB[iB].schedule:
            order.append(accuB)
            accuB = 0
            iA += 1
        else:
            accuB += 1
            iB += 1
    order.append(max(accuB, BETA - iB))
    if iA < ALPHA:
        order.extend([0] * (ALPHA - iA))

    return order

# generate all possible permutations
# each permutation is represented by order of version A
def generateAllPerm(n, m, cur_combination = []):
    if n == 1:
        yield cur_combination + [m]
    else:
        cur_combination.append(0)
        for i in range(m+1):
            cur_combination[-1] = i
            yield from generateAllPerm(n-1, m-i, cur_combination)
        cur_combination.pop(-1)

# do exhaustive search and return the schedule record
def exhaustiveSearch(vehicles):
    exhaustive_schedule_record = ScheduleRecord()
    orders = generateAllPerm(ALPHA+1, BETA)
    for order in orders:
        curr_schedule_record = scheduleEnteringTime(vehicles, order)
        if curr_schedule_record < exhaustive_schedule_record:
            exhaustive_schedule_record = curr_schedule_record
    return exhaustive_schedule_record

# do search based on simulated annealing and return the schedule record
def saSearch(vehicles, order):
    sa_schedule_record = scheduleEnteringTime(vehicles, order)

    # TODO: implement SA
    t = 460
    while t > 0:
        new_order = changeOrder(sa_schedule_record.order)
        curr_schedule_record = scheduleEnteringTime(vehicles, new_order)
        if curr_schedule_record < sa_schedule_record:
            sa_schedule_record = curr_schedule_record
            if recorded:    recordCurr(vehicles, new_order)
        t -= 1
    
    return sa_schedule_record

# switch two consecutive vehicles
def switchTwo(order):
    choice = random.randint(0, 2*ALPHA-1)
    i = (choice+1) // 2
    while order[i] == 0:
        choice = random.randint(0, 2*ALPHA-1)
        i = (choice+1) // 2
    
    new_order = copy.deepcopy(order)
    new_order[i] -= 1
    new_order[choice // 2 + 1 - choice % 2] += 1
  
    return new_order

# if the argument is the order of version A, the return value is the corresponding order of version B and vice versa
def transformOrderView(order):
    order_another_view, accu = [], 0
    for i in range(len(order)):
        for j in range(order[i]):
            order_another_view.append(accu)
            accu = 0
        accu += 1
    order_another_view.append(accu-1)
    return order_another_view

# move a vehicle randomly
def moveOne(order):
    # create an order encoded by vehicles on lane B
    orders = [[], []]
    orders[0] = copy.deepcopy(order)
    orders[1] = transformOrderView(order)
    
    choice_lane, choice_i, num = 0, 0, random.randint(0, ALPHA+BETA-1)
    if ALPHA > num:
        choice_lane, choice_i = 0, num
    else:
        choice_lane, choice_i = 1, num-ALPHA
    move_range = orders[choice_lane][choice_i] + orders[choice_lane][choice_i+1]

    # move_range is 0 means that the selected vehicle cannot move, so it's necessary to randomly select a vehicle again
    while move_range == 0:
        num = random.randint(0, ALPHA+BETA-1)
        choice_lane, choice_i = 0, 0
        if ALPHA > num:
            choice_lane, choice_i = 0, num
        else:
            choice_lane, choice_i = 1, num-ALPHA
        move_range = orders[choice_lane][choice_i] + orders[choice_lane][choice_i+1]
    
    # randomly select an interger i such that the vehicle would be moved
    # consider the nearby vehicles on different lanes and the selected vehicle itself. we can see those move_range vehicles as a subarray
    # the new location of the selected vehicle is of index i
    i = random.randint(0, move_range)
    while i == orders[choice_lane][choice_i]:
        i = random.randint(0, move_range)

    if choice_lane == 0:
        # move orders[0] directly
        orders[0][choice_i] = i
        orders[0][choice_i+1] = move_range - i
    else:
        # move orders[1] then transform to order encoded by vehicles on lane A
        orders[1][choice_i] = i
        orders[1][choice_i+1] = move_range - i
        orders[0] = transformOrderView(orders[1])
    
    return orders[0]

# randomly choose a way to modify the order of vehicles
def mixed(order):
    if random.random() <= 0.5:
        return switchTwo(order)
    else:
        return moveOne(order)

# choose a way to change the order of vehicles
def changeOrder(order):
    # return switchTwo(order)
    # return moveOne(order)
    return mixed(order)

# given order, calculate the schedule time of each vehicle
def scheduleEnteringTime(vehicles, order):
    # indices: index of each vehicle based on the given order
    indices = [[] for _ in range(2)]
    accu = 0
    for i in range(ALPHA+1):
        ninsert = order[i]
        for j in range(ninsert):
            indices[1].append(i + accu)
            accu += 1
        if i != ALPHA:
            indices[0].append(i + accu)
    # add an impossible index into each index list to avoid boundary checking
    for i in range(2):
        indices[i].append(ALPHA+BETA+1)
    
    # print(indices)

    iA, iB = 0,0
    vehicle, vehicle_prev, lane, idx = None, None, 0, 0
    for i in range(ALPHA+BETA):
        if indices[0][iA] < indices[1][iB]:
            vehicle, lane, idx = vehicles.laneA[iA], vehicles.laneA, iA
            iA += 1
        else:
            vehicle, lane, idx = vehicles.laneB[iB], vehicles.laneB, iB
            iB += 1

        if i == 0:
            # first vehicle: shedule time is its earliest arrival time
            vehicle.schedule = vehicle.earliest
            vehicle_prev = vehicle
        else:
            # ensure the distances between current vehicle and [the previous one / the previous on the same lane] are both enouth 
            vehicle.schedule = max(vehicle_prev.schedule + getWaitingTime(vehicle_prev, vehicle), vehicle.earliest)
            if idx != 0:
                vehicle_prev_same_lane = lane[idx-1]
                vehicle.schedule = max(vehicle_prev_same_lane.schedule + getWaitingTime(vehicle_prev_same_lane, vehicle), vehicle.schedule)
            vehicle_prev = vehicle
        # print(i, vehicle, vehicle_prev)

    result = ScheduleRecord(vehicle.schedule, calculateAvgSchedule(vehicles), calculateAvgDelay(vehicles), copy.deepcopy(order))
    # print(result)
    return result

# calculate how long veh2 need to wait for veh1
def getWaitingTime(veh1, veh2):
    dt = veh2.earliest - veh1.schedule
    dx = dt * VLIMIT 
    w = 0
    if dx < 0:
        dx = 0
    if veh1.lane == veh2.lane:
        if dx >= DSAFE:
            w = 0
        else:
            w = (DSAFE - dx) / VLIMIT
    else:
        dxs = pickCompatiblePoint(veh1, veh2, dx)
        if dxs == dx:
            w = 0
            return w
        else:
            w = dxs / VLIMIT
            while w < dt:
                print(f'w<dt, dx={dx}, dxs={dxs}')
                dxs = pickCompatiblePoint(veh1, veh2, dxs)
                w = dxs / VLIMIT
                dxs += 1 
    return w

# given compatible table in utils_modified.py, pick a proper compatible point
def pickCompatiblePoint(veh1, veh2, dx):
    while dx < XSCOPE and table[veh1.model][veh2.model][int(dx)] == 'X':
        dx += 1
    return dx

def oneRun():
    vehicles = initTestCase()

    # brute-force
    initial_order = generateOrderByEarliest(vehicles)
    initialRecord = scheduleEnteringTime(vehicles, initial_order)
    if recorded:    recordInitial(vehicles, initial_order)

    # SA
    sa_schedule_record = saSearch(vehicles, initial_order)
    scheduleEnteringTime(vehicles, sa_schedule_record.order)
    if recorded:    recordSA(vehicles, sa_schedule_record)

    # exhaustive search
    exhaustive_schedule_record = exhaustiveSearch(vehicles)
    scheduleEnteringTime(vehicles, exhaustive_schedule_record.order)
    if recorded:    recordExhaustive(vehicles, exhaustive_schedule_record)
    
    order_same = sa_schedule_record.order == exhaustive_schedule_record.order
    schedule_same = sa_schedule_record.last_schedule_time == exhaustive_schedule_record.last_schedule_time
    avg_same = sa_schedule_record.avg_schedule_time == exhaustive_schedule_record.avg_schedule_time
    delay_same = sa_schedule_record.avg_delay_time == exhaustive_schedule_record.avg_delay_time
    
    # whether SA result is the same as exhaustive search
    print(f"Order same: {order_same}, Schedule same: {schedule_same}, Avg same: {avg_same}, Delay same: {delay_same}")
   
    if not order_same or not schedule_same or not avg_same or not delay_same:
        print("ERROR: not all properties are the same!")
    print("=====================================================================")

    return schedule_same

def main(num_runs = 1, record = True):
    # pass True to record if you want to record information about scheduling result
    global recorded
    recorded = record

    cnt = 0
    for i in range(1, num_runs+1):
        print(f"[Running {i} of {num_runs}]")
        if oneRun():
            cnt += 1
    
    print("Execution completed.")
    print(f"Accuracy: {round(cnt / num_runs, 6)}")

if __name__ == '__main__':
    main(int(sys.argv[1]))
