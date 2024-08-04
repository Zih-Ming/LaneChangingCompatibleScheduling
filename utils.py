import random
import math
from itertools import chain

# scheduling parameter
DSAFE = 20 # d_s (m)
VLIMIT = 25 # (m/s)
ALPHA, BETA = 7, 7
NMODELS = 4 # the number of LC models
XSCOPE = 30

# SA parameters
T0 = 1000
TMIN = 0.1
NSTEP = 40
COOLNUM = 0.98

# compatibility tables at delta_v=0, from delta_x=0 to delta_x=30
# change the table manually to observe the sensitivity
table = [["" for _ in range(NMODELS+1)] for _ in range(NMODELS+1)]
table[1][1] = "OOOOOOOOOOOXXXXXXXOOOOOOOOOOOO"
table[1][2] = "OOOOOOOOOOOOOOOXXXOOOOOOOOOOOO"
table[1][3] = "OOOXXXXXOOOOOOOXXXOOOOOOOOOOOO"
table[1][4] = "XXXXXOOXXOOOOOOXXXXOOOOOOOOXXX"
table[2][1] = "OOOOOOOOXXXXOOOXXXOOOOOOOOOOOO"
table[2][2] = "OOOXXXOOXXXXOOOXXXOOOOOOOOOOOO"
table[2][3] = "OOOXXXXXOOOOOOXXXXOOOOOOOOOXXX"
table[2][4] = "OOOOOOOOOOOOOOOOOXXXXXXXXXXXXX"
table[3][1] = "OOOOOOOXXOOOOOOXXXOOOOOOOOOOOO"
table[3][2] = "OOOXXXXXXXXXXXXOOOOOOOOXXXOXXX"
table[3][3] = "OOOXXXXXXXXXXXXOOOOOOOOXXXOXXX"
table[3][4] = "XXXXXXXXXXXXOOOOOOOOOOOOOOOOOO"
table[4][1] = "XXXXXOOXXOOOOOOXXXXOOOOOOOOXXX"
table[4][2] = "OOOXXXXXXXXXXXXOOOOOOOOOOOOOOO"
table[4][3] = "XXXXXXXXXOOOOXXXXXXXXXXXXXXXOO"
table[4][4] = "OOOOOOOOOOOOOXXXXXXXXXXXXXXXOO" 

class Vehicle:
    def __init__(self, id, lane, earliest, model):
        # model: determine the type of LC model
        # lane: currently consider only two lanes, 'A' and 'B'
        self.id = id
        self.model = model
        self.lane = lane
        self.earliest = earliest
        self.schedule = -1.0
    def __str__(self):
        return f'({self.lane}{self.id} - {round(self.earliest, 2)}, {round(self.schedule, 2)})'
    def __repr__(self):
        return f'({self.lane}{self.id} - {round(self.earliest, 2)}, {round(self.schedule, 2)})'

class Vehicles:
    def __init__(self, vehicles_lane_A, vehicles_lane_B):
        self.laneA = vehicles_lane_A
        self.laneB = vehicles_lane_B

        # generate a list of all vehicles sorted by earliest arrival time
        self._list_of_vehicles = []
        iA, iB = 0, 0

        while iA < ALPHA and iB < BETA:
            if self.laneA[iA].earliest <= self.laneB[iB].earliest:
                self._list_of_vehicles.append(self.laneA[iA])
                iA += 1
            else:
                self._list_of_vehicles.append(self.laneB[iB])
                iB += 1

        self._list_of_vehicles.extend(self.laneA[iA:] if iA < ALPHA else self.laneB[iB:])

    def __iter__(self):
        return iter(self._list_of_vehicles)

class ScheduleRecord:
    def __init__(self, last_schedule_time = math.inf, avg_schedule_time = math.inf, avg_delay_time = math.inf, order = []):
        # order: a list that represents a vehicle order with the view of vehicles on lane A (order of version A, for short)
        self.last_schedule_time = last_schedule_time
        self.avg_schedule_time = avg_schedule_time
        self.avg_delay_time = avg_delay_time
        self.order = order
    def __str__(self):
        return f'(schedule time: {self.last_schedule_time}, average schedule time: {self.avg_schedule_time}, average delay time: {self.avg_delay_time}, order of version A: {self.order})'
    def __repr__(self):
        return f'(schedule time: {self.last_schedule_time}, average schedule time: {self.avg_schedule_time}, average delay time: {self.avg_delay_time}, order of version A: {self.order})'
    def __lt__(self, other):
        return [self.last_schedule_time, self.avg_schedule_time, self.avg_delay_time] < [other.last_schedule_time, other.avg_schedule_time, other.avg_delay_time]

def calculateAvgSchedule(vehicles):
    # calculate the avg schedule entering time of all vehicles
    return sum([vehicle.schedule for vehicle in vehicles]) / (ALPHA + BETA)

def calculateAvgDelay(vehicles):
    # calculate the avg delay of all vehicles 
    return sum([vehicle.schedule - vehicle.earliest for vehicle in vehicles]) / (ALPHA + BETA)


def recordOrder(vehicles, order, print_earliest = False):
    accu = 0
    for i in range(ALPHA+1):
        ninsert = order[i]
        for j in range(ninsert):
            print(f'{vehicles.laneB[accu].lane}{vehicles.laneB[accu].id} - {round(vehicles.laneB[accu].earliest if print_earliest else vehicles.laneB[accu].schedule, 2)}', end=", ")
            accu += 1
        if i != ALPHA:
            print(f'{vehicles.laneA[i].lane}{vehicles.laneA[i].id} - {round(vehicles.laneA[i].earliest if print_earliest else vehicles.laneA[i].schedule, 2)}', end=", ")

def recordInitial(vehicles, order):
    print()
    print("Initial scheduled time:", vehicles.laneA[-1].schedule if order[ALPHA] == 0 else vehicles.laneB[-1].schedule)
    print()
    print("Initial order:")
    recordOrder(vehicles, order)
    print()

def recordCurr(vehicles, order):
    print("Current best order:")
    recordOrder(vehicles, order)
    print("Current best scheduled time:", vehicles.laneA[-1].schedule if order[ALPHA] == 0 else vehicles.laneB[-1].schedule)

def recordScheduleRecord(schedule_record, algorithm_name):
    print(f"{algorithm_name} last scheduled time: ", schedule_record.last_schedule_time) # the last vehicle
    print(f"{algorithm_name} avg scheduled time: ", schedule_record.avg_schedule_time)

def recordSA(vehicles, schedule_record):
    print("----------------------\n")
    print("SA order:")
    recordOrder(vehicles, schedule_record.order)
    print()
    recordScheduleRecord(schedule_record, "SA")
    print("----------------------\n")

def recordExhaustive(vehicles, schedule_record):
    print("Exhaustive order:")
    recordOrder(vehicles, schedule_record.order)
    print()
    recordScheduleRecord(schedule_record, "Exhaustive")
    print("----------------------\n")

