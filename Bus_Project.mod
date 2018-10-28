/*********************************************
 * OPL 12.6.0.0 Model
 * Authors: Johannes Bogensperger, Gerard Cegarra Dueñas
 * Creation Date: 28.10.2018 at 16:52:52
 *********************************************/
 
 int nServices = ...;
 int nBuses = ...;
 int nDrivers = ...;
 
 range S = 1..nServices;
 range B = 1..nBuses;
 range D = 1..nDrivers;

 
 /*********************************************
 ************  INPUT DATA *********************
 *********************************************/
 
  // Services
 int start[s in S] = ...; // minutes after 0:00 (i.e. 510 is 8:30am)
 int duration[s in S] = ...; //minutes
 int kms[s in S] = ...;
 int passengers[s in S] = ...;
 int overlapping[s1 in S][s2 in S];
 
 // Drivers
 int maxWorkingTime[d in D] = ...; //minutes
 int BM = ...; //minutes
 float CBM = ...;  //euros
 float CEM = ...;  //euros
 
 
 //Buses
 int capacity[b in B] = ...;
 int maxBuses = ...;
 float cost_km[b in B] = ...;     // euros
 float cost_min[b in B] = ...; // euros
 
 
 
  /*********************************************
 ************ Decision Variables   *************
 **********************************************/
 dvar boolean used[b in B]; // if a Bus is used or not
 
 dvar boolean ds[d in D][s in S]; // whether driver d is assigned to service s
 dvar boolean bs[b in B][s in S]; // whether bus b is assigned to service s
 
 dvar boolean overtime[d in D]; // if a driver is allowed to work overtime or is still doing base minutes
 

 dvar int WBM[d in D]; // Driver d working base minutes
 dvar int WEM[d in D]; // Driver d working extra minutes
 
 
  
  /*********************************************
 ************ Preprocessing Block  *************
 **********************************************/
 
 execute {
 for (var s1 in S)
 	for (var s2 in S) 
 		if (start[s1] <= (start[s2]+duration[s2])  && (start[s1]+duration[s1]) >= start[s2]  ){ 
 			overlapping[s1][s2] = 1; 
 	}	
}	 
 
 
 
   /*********************************************
 ********  Obj function + constraints  **********
 **********************************************/
 
 
 minimize  ( sum(b in B) sum(s in S) bs[b][s] * ((duration[s] * cost_min[b]) + (kms[s] * cost_km[b]))    )
 		+  ( sum(d in D)  (WBM[d] * CBM + WEM[d] * CEM) );
 
 subject to {
  
  	forall(s in S){
 		 	sum(d in D) ds[d][s] == 1; // Each Line s must have exactly one driver
 		 	sum(b in B) bs[b][s] == 1; // Each Line s must have exactly one Bus.
	 	}
	 	
	forall(s in S)
	  forall(b in B)
	    capacity[b] >= bs[b][s] * passengers[s]; // capacity must be bigger than the passengers of the service
	    
	forall(s1 in S) // Every driver/bus is only allowed to be used in max one service of the overlapping 
	  forall(s2 in S: overlapping[s1][s2] == 1){ // service pairs
	  		forall(b in B) bs[b][s1] + bs[b][s2] <= 1; 
	  		forall(d in D) ds[d][s1] + ds[d][s2] <= 1;
	  }
	  
	forall(d in D){
		WBM[d] + WEM[d] <= 	maxWorkingTime[d]; // Ensure maximum working time for each driver
		WBM[d] + WEM[d] >= sum(s in S) ds[d][s] * duration[s]; // Ensure the driver works enough for all services he operates
		WBM[d] <= BM; // Driver is only receiving CBM until the BM.. therfor WBM is not allowed to be bigger 
	}
	
	forall(d in D){ // Overime allowed or not..
		WBM[d] >= BM * overtime[d];
		WEM[d] <= maxWorkingTime[d] * overtime[d];
	}
	
	
	sum(b in B) used[b] <= maxBuses; // maximum amount of buses used
	
	forall(b in B){ // ensuring that used is set when a bus is used..
		used[b] * nServices >= sum(s in S) bs[b][s];
		sum(s in S) bs[b][s] >= used[b];
	}

	 	
 }
 
 
  /*********************************************
 ********     POST processing block   **********
 **********************************************/
 
  execute {
// TODO 	
}	
 