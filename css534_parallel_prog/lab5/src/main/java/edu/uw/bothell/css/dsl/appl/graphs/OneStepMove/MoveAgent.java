package edu.uw.bothell.css.dsl.appl.graphs.OneStepMove;

import edu.uw.bothell.css.dsl.MASS.GraphAgent;
import edu.uw.bothell.css.dsl.MASS.MASS;

public class MoveAgent extends GraphAgent{

    // function identifiers
    public static final int init_ = 0;
    public static final int one_step_move_ = 1;
    public static final int show_location_ = 2;
    public Object callMethod(int functionId, Object argument) {
        switch (functionId) {
            case init_:
                return init(argument);
            case one_step_move_:
                return migrateRandom(argument);
            case show_location_:
                return showLocation(argument);
        }
        return null;
    }

    /**
     * Is the default constructor.
     */
    public MoveAgent() {
        super();
    }

    public MoveAgent(Object arg) {
        super(arg);
        MASS.getLogger().debug("agent(" + getAgentId() + ") was born.");
    }

    public Object init(Object arg) {
        return null;
    }

    public Object showLocation(Object arg) {
        return "Now agent(" + getAgentId() + ") is @: place index =" + getPlace().getIndex()[0];
    }
}
