package edu.uw.bothell.css.dsl.appl.graphs.OneStepMove;

import java.util.List;

import edu.uw.bothell.css.dsl.MASS.Agents;
import edu.uw.bothell.css.dsl.MASS.GraphPlaces;
import edu.uw.bothell.css.dsl.MASS.MASS;
import edu.uw.bothell.css.dsl.MASS.graph.Graph;
import edu.uw.bothell.css.dsl.MASS.graph.transport.VertexModel;
import edu.uw.bothell.css.dsl.MASS.logging.LogLevel;

public class OneStepMove {

    /**
     * Spawn agent at every vertex and move one step forward 
     *
     * @param args Input data path
     */
    public static void main(String[] args) {

        // Read and validate input parameters
        if (args.length != 1) {
            System.err.println("Usage: java -jar OneSetpMove.jar <dsl_graph_file>");
            System.exit(-1);
        }
        
        String filePath = args[0];

        MASS.setLoggingLevel(LogLevel.DEBUG);
        MASS.init(10000000);

        // loading data from dsl file
        System.out.println("Begin data space generation");
        
        long begin = System.currentTimeMillis();
        
        GraphPlaces network = new GraphPlaces(1, NodeGraphMASS.class.getName());
        try {
            network.loadDSLFile(filePath);
        } catch(Exception e) {
            System.err.println("Error reading in graph file: " + e);
            System.exit(3);
        }
        
        
        long end = System.currentTimeMillis();
        
        System.out.println("Import complete\nImport time: " + (end - begin) / 1000.0 + " s");
        
        // doing one step movement
        run_one_step_move((GraphPlaces) network);

        System.out.println("Finish MASS");

        MASS.finish();
    }

    public static void run_one_step_move(GraphPlaces network) {
        Graph graph = network;

        List<VertexModel> vertices = graph.getGraph().getVertices();

        int nVertices = vertices.size();

        System.out.println("Number of Vertices is : " + nVertices);

        try {

            network.callAll(NodeGraphMASS.init_);

            // Time measurement starts
            System.out.println("Go! One movement");
            long startTime = System.currentTimeMillis();

            // Instantiate an agent at each node
            Agents crawlers = new Agents(2, MoveAgent.class.getName(), null, network, nVertices);

            crawlers.callAll(MoveAgent.init_, null);
    
            int nAgents = crawlers.nAgents();
            System.out.println("*** Starting Agents = " + nAgents + " ************");
            // printing status before migration
            int[][] dummyArgs = new int[nAgents][1];
            Object[] status = (Object[]) crawlers.callAll(MoveAgent.show_location_, (Object[]) dummyArgs);
            for (int i = 0; i < status.length; i++)
                System.out.println((String) status[i]);

            // Begin first migration
            System.out.println("*** Begin first migration ***");
            crawlers.callAll(MoveAgent.one_step_move_, null);
            crawlers.manageAll();
            System.out.println("*** Movement finished ***");

            // For stats
            nAgents = crawlers.nAgents();
            System.out.println("*** Remain Agents = " + nAgents + " ************");

            // Time measurement ends
            long elapsedTime = System.currentTimeMillis() - startTime;
            System.out.println("Elapsed time = " + elapsedTime);

            // Checking new status after one migration
            status = (Object[]) crawlers.callAll(MoveAgent.show_location_, (Object[]) dummyArgs);
            for (int i = 0; i < status.length; i++)
                System.out.println((String) status[i]);

            network.callAll(NodeGraphMASS.display_);

        } catch (Exception e) {
            System.err.println("Error in execution: " + e.getMessage());

            e.printStackTrace(System.err);
        }
    }
}
