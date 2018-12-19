/*********************************************
 * OPL 12.6.0.0 Model
 * Author: Johannes
 * Creation Date: 01.10.2018 at 11:07:23
 *********************************************/
main {
	var src = new IloOplModelSource("Bus_Project.mod");
	var def = new IloOplModelDefinition(src);
	var cplex = new IloCplex();
	var model = new IloOplModel(def,cplex);
	var data = new IloOplDataSource("InstanceGenerator/instances/example_6.dat");
	//var data = new IloOplDataSource("examen.dat");
	model.addDataSource(data);
	model.generate();
	cplex.epgap=0.01;
	cplex.TiLim=7200;
	
	if (cplex.solve()) {
		writeln("Solution value: " + cplex.getObjValue() );
		
	}
	else {
		writeln("Not solution found");
	}
	
	model.end();
	data.end();
	def.end();
	cplex.end();
	src.end();
};