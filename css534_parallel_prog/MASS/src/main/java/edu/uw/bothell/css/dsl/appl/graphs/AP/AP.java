package edu.uw.bothell.css.dsl.appl.graphs.AP;

import java.util.List;

import edu.uw.bothell.css.dsl.MASS.Agents;
import edu.uw.bothell.css.dsl.MASS.GraphPlaces;
import edu.uw.bothell.css.dsl.MASS.MASS;
import edu.uw.bothell.css.dsl.MASS.graph.Graph;
import edu.uw.bothell.css.dsl.MASS.graph.transport.VertexModel;
import edu.uw.bothell.css.dsl.MASS.logging.LogLevel;

/**
 * AP.java - Counts and enumerates all articulation point in a given graph
 *
 * @author Dazhi Li <dazhili@uw.edu>, Fred Xu <zxu725@uw.edu>, Letitia Su <suruoxi@uw.edu>, Jeremy Gao <leyug@uw.edu>
 * @version 1.0
 * @since December 7, 2024
 */
public class AP {
    private static int sequentialId = 2;

    /**
     * Counts all the articulation point in a graph by brute force
     *
     * @param args TBD
     */
    public static void main(String[] args) {
        // file path argument varification
        if (args.length != 1) {
            System.err.println("Usage: java -jar TriangleCounting.jar <dsl_graph_file>");
            System.exit(-1);
        }
        String filePath = args[0];

        MASS.setLoggingLevel(LogLevel.DEBUG);
        MASS.init(10000000);

        System.out.println("Begin data space generation");
        
        long begin = System.currentTimeMillis();
        
        GraphPlaces network = new GraphPlaces(1, BfVertex.class.getName());
        try {
            network.loadDSLFile(filePath);
        } catch(Exception e) {
            System.err.println("Error reading in graph file: " + e);
            System.exit(3);
        }
        
        
        long end = System.currentTimeMillis();
        
        System.out.println("Import complete\nImport time: " + (end - begin) / 1000.0 + " s");

        find_articulation_point((GraphPlaces) network);

        System.out.println("Finish MASS");

        MASS.finish();
    }

    public static void find_articulation_point(GraphPlaces network) {
        Graph graph = network;

        List<VertexModel> vertices = graph.getGraph().getVertices();

        int nVertices = vertices.size();

        System.out.println("Number of Vertices is : " + nVertices);

        try {

            network.callAll(BfVertex.init_, (Object) nVertices);

            // Time measurement starts
            System.out.println("Go! Find Articulation Point");
            long startTime = System.currentTimeMillis();

            // Instantiate an agent at each node
            Agents crawlers = new Agents(sequentialId++, BfAgent.class.getName(), null, network, nVertices);

            crawlers.callAll(BfAgent.init_, nVertices);

            // mark every agent's spawn place as the cutted vertex, move to one random neighbor as the start place for dfs
            int[][] dummyArgs = new int[nVertices][1];
            Object[] status = (Object[]) crawlers.callAll(BfAgent.show_location_, (Object[]) dummyArgs);
            for (int i = 0; i < status.length; i++)
                System.out.println((String) status[i]);
            crawlers.callAll(BfAgent.skip_vertex_, null);
            crawlers.manageAll();

            // As long as there is still agent not finishing their dfs progress
            int countFinished = 0;
            while (countFinished != nVertices) {
                // mark a place as visited and doing migration to next point
                crawlers.callAll(BfAgent.mark_move_on_next_, null);
                crawlers.manageAll();
                // For stats
                Object[] finishedList = (Object[]) crawlers.callAll(BfAgent.show_finished_, (Object[]) dummyArgs);
                countFinished = 0;
                for (Object obj : finishedList) {
                    if ((Boolean) obj)
                        countFinished++;
                }
            }

            // Time measurement ends
            long elapsedTime = System.currentTimeMillis() - startTime;
            System.out.println("Elapsed time = " + elapsedTime);


            Object[] routes = (Object[]) crawlers.callAll(BfAgent.get_routes_, (Object[]) dummyArgs);
            for (Object route : routes) {
                System.out.println((String) route);
            }


            // Enumerate all articulation point
            Object[] answers = (Object[]) crawlers.callAll(BfAgent.get_articulation_point_, (Object[]) dummyArgs);
            crawlers.manageAll();
            int articulationPointCount = 0;
            for (Object ans : answers) {
                if (ans != null) {
                    articulationPointCount++;
                }
            }
            System.out.println("The number of articulation point is " + articulationPointCount);


        } catch (Exception e) {
            System.err.println("Error in execution: " + e.getMessage());

            e.printStackTrace(System.err);
        }
    }
}
