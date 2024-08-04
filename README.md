## Lane-Changing (LC) Compatible Scheduling
This project provides a LC scheduling algorithm based on simulated annealing (SA). The project also estimates the accuracy of the proposed algorithm.

## Problem Statement
Given compatible tables, determine the arrival time of vehicles to optimize the completion time, i.e., the arrival time of the last one.

To obtain more details, please check this [documentation](https://drive.google.com/drive/folders/1GmdtAKjIU5hTDw8ksPZX9af7ymEz5ady).

## utils.py
> Define classes as well as functions about recording

### Classes
- Vehicle: store information about a vehicel, including ID, model type, original lane, earliest arrival time, and scheduled entering time.
- Vehicles: store objects of all vehicles according to their original lanes.
- ScheduleRecord: store information about a scheduling result.

## sa.py
> Run tests to estimate the accuracy of a LC scheduling algorithm.

### Algorithms
- exhaustive search: find the optimal scheduling by brute force.
- (simplified) SA: for each round, evaluate the neighbor of the currently best state and store it if it performs better than the original one.

### main function
There are two arguments, `num_runs` and `record`.
- `num_runs`: determine the number of testing runs.
- `record`: determine whether to record the information about scheduling results.

## run.sh
The following command will execute `sa.py` to perform the experiment of 1000 runs.
```bash
./run.sh 1000
```

Comparing to the previous one, the following command allows you to additionally record all printed information to the file `result.out`.
 ```bash
./run.sh 1000 result.out
```
