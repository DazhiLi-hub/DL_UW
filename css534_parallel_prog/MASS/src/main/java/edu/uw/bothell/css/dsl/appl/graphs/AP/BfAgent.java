/*

 	MASS Java Software License
	© 2012-2021 University of Washington

	Permission is hereby granted, free of charge, to any person obtaining a copy
	of this software and associated documentation files (the "Software"), to deal
	in the Software without restriction, including without limitation the rights
	to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
	copies of the Software, and to permit persons to whom the Software is
	furnished to do so, subject to the following conditions:

	The above copyright notice and this permission notice shall be included in
	all copies or substantial portions of the Software.

	The following acknowledgment shall be used where appropriate in publications, presentations, etc.:      

	© 2012-2021 University of Washington. MASS was developed by Computing and Software Systems at University of 
	Washington Bothell.

	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
	IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
	FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
	AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
	LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
	OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
	THE SOFTWARE.

*/

package edu.uw.bothell.css.dsl.appl.graphs.AP;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.stream.Collectors;

import edu.uw.bothell.css.dsl.MASS.GraphAgent;
import edu.uw.bothell.css.dsl.MASS.MASS;

public class BfAgent extends GraphAgent {
    // private data members
    private int skipVertexId;
    private HashSet<Integer> routes;
    private ArrayList<Integer> parents;
    private boolean isFinished;
    private int nVertices;

    // function identifiers
    public static final int init_ = 0;
    public static final int show_location_ = 1;
    public static final int skip_vertex_ = 2;
    public static final int mark_move_on_next_ = 3;
    public static final int show_finished_ = 4;
    public static final int get_articulation_point_ = 5;
    public static final int get_routes_ = 6;

    public BfAgent() {
        super();
    }

    public BfAgent(Object arg) {
        super(arg);

        MASS.getLogger().debug("agent(" + getAgentId() + ") was born.");
    }

    public Object callMethod(int functionId, Object argument) {
        switch (functionId) {
            case init_:
                return init(argument);
            case show_location_:
                return showLocation();
            case skip_vertex_:
                return skipVertex(argument);
            case mark_move_on_next_:
                return markMoveOnNext();
            case show_finished_:
                return showFinished();
            case get_articulation_point_:
                return getArticulationPoint();
            case get_routes_:
                return getRoutes();
        }
        return null;
    }

    /**
     * @param arg an integer array that includes only the first place to go.
     * @return nothing
     */
    public Object init(Object arg) {
        int nVertices = (int) arg;
        this.nVertices = nVertices;
        routes = new HashSet<>();
        parents = new ArrayList<>();
        isFinished = false;
        return null;
    }

    public Object showLocation() {
        return getAgentId() + "," + getPlace().getIndex()[0];
    }

    public Object skipVertex(Object arg) {
        skipVertexId = getPlace().getIndex()[0];
        migrateRandom(arg);
        return null;
    }

    public Object markMoveOnNext() {
        if (isFinished)
            return null;
        int nextPlaceId = -1;
        BfVertex myVertex = (BfVertex) getPlace();
        int currntPlaceId = myVertex.getIndex()[0];

        // mark this place to routes as visited
        routes.add(currntPlaceId);

        // visit next node if not marked as skipped and not visited
        Object[] neighbors = myVertex.getNeighbors();
        for (Object neighbor : neighbors) {
            int neighborId = (int) neighbor;
            if (neighborId != skipVertexId && !routes.contains(neighbor)) {
                nextPlaceId = neighborId;
                parents.add(currntPlaceId);
                migrate(nextPlaceId);
                return null;
            }
        }
        // get the most recent parent to backward
        if (parents.size() > 0) {
            nextPlaceId = parents.get(parents.size()-1);
            parents.remove(parents.size() - 1);
            migrate(nextPlaceId);
            return null;
        }

        // backward when no elsewhere to go && no parent for backward, set agent finished
        isFinished = true;
        return null;
    }

    public Object showFinished() {
        return isFinished;
    }

    public Object getArticulationPoint() {
        // minus 1 for skipping one node at first
        if (routes.size() < nVertices - 1) {
            return skipVertexId;
        }
        return null;
    }

    // Only for debugging
    public Object getRoutes() {
         String routeString = routes.stream()
                                   .map(String::valueOf)  // Convert each integer to string
                                   .collect(Collectors.joining()); // Concatenate without separator
        return "AgentId=" +getAgentId() + ", routes=" + routeString;
    }
}
