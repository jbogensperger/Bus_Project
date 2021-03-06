# Bus Project
This is an course Project of UPC Barcelona course Algorithmic and Mathematical Models. It contains an ILP optimization and its equivalent in custom python script using meta-heuristics.

# How to solve instances from linux terminal

Assuming `/opt/ibm/ILOG/CPLEX_Studio126/` as the installation directory of CPLEX Studio.

### Define the LD_LIBRARY_PATH environment variable

Add this line to ~/.bashrc to automatically run it when a terminal session is initiated:

```bash
export LD_LIBRARY_PATH='/opt/ibm/ILOG/CPLEX_Studio126/opl/bin/x86-64_linux'
```

### Add oplrun to PATH environment variable

Add this line to ~/.bashrc to automatically run it when a terminal session is initiated:

```bash
export PATH=$PATH:'/opt/ibm/ILOG/CPLEX_Studio126/opl/bin/x86-64_linux/'
```

### Run OPL Solver

From the project root, run oplrun. It gets the model and the data file as parameters:

```bash
oplrun OPL/Bus_Project.mod InstanceGenerator/instances/example_0.dat
```
