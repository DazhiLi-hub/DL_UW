import java.util.ArrayList;
import java.util.Arrays;
import java.util.Iterator;
import java.util.List;

import org.apache.spark.SparkConf;
import org.apache.spark.api.java.JavaRDD;
import org.apache.spark.api.java.JavaPairRDD;
import org.apache.spark.api.java.JavaSparkContext;

import org.apache.spark.api.java.function.PairFunction;
import org.apache.spark.api.java.function.PairFlatMapFunction;
import org.apache.spark.api.java.function.Function2;
import org.apache.spark.api.java.function.Function;

import scala.Tuple2;

public class ShortestPath {

    public static boolean is_still_active(JavaPairRDD<String, Data> network) {
        return network.filter(d -> d._2().is_active()).count() > 0 ;
    }
 
    public static void main(String[] args) {
        // start Sparks and read a given input file
        String inputFile = args[0];
        String srcVtx = args[1];
        String dstVtx = args[2];
        SparkConf conf = new SparkConf( ).setAppName( "BFS-based Shortest Path Search" );
        JavaSparkContext jsc = new JavaSparkContext( conf );
        JavaRDD<String> lines = jsc.textFile( inputFile );
        // now start a timer
        long startTime = System.currentTimeMillis();

        // initializing the whole grogram: loading data
        JavaPairRDD<String, Data> network =  lines.mapToPair(
            new PairFunction<String, String, Data>() {
                @Override 
                public Tuple2<String, Data> call(String line) { 
                    // splitOne: ["0", "3,4;1,3"] -> ["source vertext", "neighbors info"]
                    String[] splitOne = line.split("=");
                    String vtx = splitOne[0];
                    List<Tuple2<String, Integer>> neighbors = null;
                    if (splitOne[1] != null && splitOne[1].length() != 0) {
                        neighbors = new ArrayList<Tuple2<String, Integer>>();
                        // singleEdge: "3,4" -> "nextVertex, nextVertexEdgeLength"
                        for (String singleEdge : splitOne[1].split(";")) {
                            // splitTwo: ["3", "4"] -> ["nextVertex", "nextVertexEdgeLength"]
                            String[] splitTwo = singleEdge.split(",");
                            neighbors.add(new Tuple2<>(splitTwo[0], Integer.valueOf(splitTwo[1])));
                        }
                    }
                    // specialize the source index to initiate the program
                    Data singleNetwork = null;
                    if (srcVtx.equals(vtx)) {
                        singleNetwork = new Data(neighbors, 0, 0, "ACTIVE");
                    } else {
                        singleNetwork = new Data(neighbors, Integer.MAX_VALUE, Integer.MAX_VALUE, "INACTIVE");
                    }
                    return new Tuple2<>(vtx, singleNetwork);
                }
            }
        );

        while (is_still_active(network)) {
            JavaPairRDD<String, Data> propagatedNetwork = network.flatMapToPair(
            // If a vertex is “ACTIVE”, create Tuple2( neighbor, new Data( … ) ) for
            // each neighbor where Data should include a new distance to this neighbor.
            // Add each Tuple2 to a list. Don’t forget this vertex itself back to the
            // list. Return all the list items.
            new PairFlatMapFunction<Tuple2<String, Data>, String, Data>() {
                @Override
                public Iterator<Tuple2<String, Data>> call(Tuple2<String, Data> vertex) {
                    List<Tuple2<String, Data>> results = new ArrayList<>();
                    // Doing propagation
                    if (vertex._2().is_active()) {
                        for (Tuple2<String,Integer> neighbor : vertex._2.getNeighbors()) {
                            results.add(new Tuple2<>(neighbor._1(), new Data(null, vertex._2().getPrev() + neighbor._2(), Integer.MAX_VALUE, "INACTIVE")));
                        }
                        vertex._2().setStatus("INACTIVE");
                        results.add(vertex);
                    } else {
                        results.add(vertex);
                    }
                    return results.iterator();
                }
            }
            );
            network = propagatedNetwork.reduceByKey(
            // For each key, (i.e., each vertex), find the shortest distance and
            // update this vertex’ Data attribute.
            new Function2<Data, Data, Data>() {
                @Override
                public Data call(Data k1, Data k2) {
                    Integer newDistance = 0;
                    Integer newPrev = 0;
                    List<Tuple2<String,Integer>> newNeighbors = null;
                    // calculating new distance
                    if (k1.getDistance() < k2.getDistance()) {
                        newDistance = k1.getDistance();
                    } else {
                        newDistance = k2.getDistance();
                    }
                    // remain existed prev
                    if (k1.getPrev() != Integer.MAX_VALUE) {
                        newPrev = k1.getPrev();
                    } else {
                        newPrev = k2.getPrev();
                    }
                    // remain existed neighbors
                    if (k1.getNeighbors().isEmpty()) {
                        newNeighbors = k2.getNeighbors();
                    } else {
                        newNeighbors = k1.getNeighbors();
                    }
                    return new Data(newNeighbors, newDistance, newPrev, "INACTIVE");
                }
            }
            );
           
            network = network.mapValues(
            // If a vertex’ new distance is shorter than prev, activate this vertex
            // status and replace prev with the new distance.
            new Function<Data, Data>() {
                @Override
                public Data call(Data value) {
                    if (value.getDistance() < value.getPrev()) {
                        value.setPrev(value.getDistance());
                        value.setStatus("ACTIVE");
                    }
                    value.setDistance(Integer.MAX_VALUE);
                    return value;
                }
            }
            );
        }
        // ending time
        long endTime = System.currentTimeMillis();
        // Print out results
        System.out.println("Time Elapsed = " + (endTime - startTime));
        List<Tuple2<String, Data>> finalNetwork = network.collect();
        for (Tuple2<String, Data> tuple: finalNetwork) {
            if (tuple._1().equals(dstVtx)) {
                System.out.println("from " + srcVtx + " to " + dstVtx + " takes distance = " + tuple._2().getPrev());
            }
        }
    }
 
}
