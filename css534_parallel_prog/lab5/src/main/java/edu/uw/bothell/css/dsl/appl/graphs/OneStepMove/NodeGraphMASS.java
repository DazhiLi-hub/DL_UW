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

package edu.uw.bothell.css.dsl.appl.graphs.OneStepMove;

import edu.uw.bothell.css.dsl.MASS.MASSBase;
import edu.uw.bothell.css.dsl.MASS.MASS;
import edu.uw.bothell.css.dsl.MASS.VertexPlace;

import java.util.Arrays;
import java.util.stream.Collectors;

public class NodeGraphMASS extends VertexPlace {
    // function identifiers
    public static final int init_ = 0;
    public static final int display_ = 1;

    public Object callMethod(int functionId, Object argument) {
        switch (functionId) {
            case init_:
                return init(argument);
            case display_:
                return display();
        }
        return null;
    }

    private Object display() {
        try {
            String neighborString = Arrays.stream(getNeighbors())
                    .map(String::valueOf)
                    .collect(Collectors.joining(", "));

            MASSBase.getLogger().debug(getIndex().toString() + ": " + neighborString);

        } catch (Exception e) {
            MASSBase.getLogger().error("Exception displaying vertex", e);
        }
        return null;
    }

    /**
     * Is the default constructor.
     */
    public NodeGraphMASS() {
        super();
    }

    public NodeGraphMASS(Object arg) {
        super(arg);
    }

    public Object init(Object arg) {
        return null;
    }
}
