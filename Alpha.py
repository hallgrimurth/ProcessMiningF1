from collections import defaultdict
from datetime import datetime
import xml.etree.ElementTree as ET
from itertools import combinations

class PetriNet:
    def __init__(self):
        self.p = []  # Set of places
        self.t = {}  # Set of transitions (name to ID mapping)
        self.f = []  # Set of directed arcs (edges)
        self.m = {}  # Current marking (tokens in places), mapping place name to count
        self.initial_marking = {}  # Store initial marking to reset later

    def add_place(self, name):
        if name not in self.p:
            self.p.append(name)

    def add_transition(self, name, id):
        if name not in self.t:
            self.t[name] = id

    def add_edge(self, source, target):
        if (source in self.p and target in self.t.values()) or (source in self.t.values() and target in self.p):
            self.f.append((source, target))
        else:
            print(f"Invalid edge: source {source} or target {target} is not valid.")
        return self

    def get_tokens(self, place):
        return self.m.get(place, 0)

    def is_enabled(self, transition):
        for edge in self.f:
            if edge[1] == transition:  # Edge from place to transition
                if self.get_tokens(edge[0]) == 0:
                    return False
        return True

    def fire_transition(self, transition):
        if not self.is_enabled(transition):
            print(f"Transition {transition} is not enabled.")
            return
        # Remove tokens from input places
        for edge in self.f:
            if edge[1] == transition:
                if self.m[edge[0]] > 0:
                    self.m[edge[0]] -= 1
        # Add tokens to output places
        for edge in self.f:
            if edge[0] == transition:
                self.m[edge[1]] = self.m.get(edge[1], 0) + 1

        # consumed = 0
        # produced = 0
        # missing = 0
        # # Check if transition is enabled
        # is_enabled = True
        # for edge in self.f:
        #     if edge[1] == transition:
        #         place = edge[0]
        #         required_tokens = 1  # Assuming weight is 1
        #         available_tokens = self.get_tokens(place)
        #         if available_tokens < required_tokens:
        #             missing += required_tokens - available_tokens
        #             is_enabled = False
        # if not is_enabled:
        #     return consumed, produced, missing
        # # Remove tokens from input places
        # for edge in self.f:
        #     if edge[1] == transition:
        #         required_tokens = 1  # Assuming weight is 1
        #         self.m[edge[0]] -= required_tokens
        #         consumed += required_tokens
        # # Add tokens to output places
        # for edge in self.f:
        #     if edge[0] == transition:
        #         produced_tokens = 1  # Assuming weight is 1
        #         self.m[edge[1]] = self.m.get(edge[1], 0) + produced_tokens
        #         produced += produced_tokens
        
        # return consumed, produced, missing

    def add_marking(self, place, tokens=1):
        """Sets the token count for a place and stores the initial marking."""
        if place in self.p:
            self.m[place] = tokens
            self.initial_marking[place] = tokens

    def reset_marking(self):
        """Reset the token marking to the initial marking."""
        self.m = self.initial_marking.copy()

    def transition_name_to_id(self, name):
        return self.t.get(name)

def alpha(log):
    # Step 1: Extract T_W, T_I, T_O
    T_W = set()
    T_I = set()
    T_O = set()
    W = []
    for case_id, events in log.items():
        events.sort(key=lambda x: x['time:timestamp'])
        trace = [event['concept:name'] for event in events]
        if trace:
            W.append(trace)
            T_W.update(trace)
            T_I.add(trace[0])
            T_O.add(trace[-1])

    # Step 2: Build directly follows relation
    directly_follows_pairs = set()
    for trace in W:
        for i in range(len(trace) - 1):
            directly_follows_pairs.add((trace[i], trace[i + 1]))

    # Step 3: Build footprint matrix
    T_W_list = list(T_W)
    footprint = {}
    for a in T_W_list:
        for b in T_W_list:
            if (a, b) in directly_follows_pairs and (b, a) not in directly_follows_pairs:
                footprint[(a, b)] = '>'
            elif (b, a) in directly_follows_pairs and (a, b) not in directly_follows_pairs:
                footprint[(a, b)] = '<'
            elif (a, b) in directly_follows_pairs and (b, a) in directly_follows_pairs:
                footprint[(a, b)] = '||'
            else:
                footprint[(a, b)] = '#'

    # Step 4: Generate X_W
    def get_non_empty_subsets(s):
        s_list = list(s)
        subsets = []
        for r in range(1, len(s_list)+1):
            subsets.extend(combinations(s_list, r))
        return subsets

    A_subsets = get_non_empty_subsets(T_W)
    B_subsets = get_non_empty_subsets(T_W)
    X_W = set()
    for A in A_subsets:
        for B in B_subsets:
            if not A or not B:
                continue
            condition_satisfied = True
            for a in A:
                for b in B:
                    if footprint.get((a, b)) != '>':
                        condition_satisfied = False
                        break
                if not condition_satisfied:
                    break
            if not condition_satisfied:
                continue
            for i in range(len(A)):
                for j in range(i+1, len(A)):
                    if footprint.get((A[i], A[j])) != '#' or footprint.get((A[j], A[i])) != '#':
                        condition_satisfied = False
                        break
                if not condition_satisfied:
                    break
            if not condition_satisfied:
                continue
            for i in range(len(B)):
                for j in range(i+1, len(B)):
                    if footprint.get((B[i], B[j])) != '#' or footprint.get((B[j], B[i])) != '#':
                        condition_satisfied = False
                        break
                if not condition_satisfied:
                    break
            if condition_satisfied:
                X_W.add((frozenset(A), frozenset(B)))

    # Step 5: Generate Y_W
    Y_W = set(X_W)
    for (A1, B1) in X_W:
        for (A2, B2) in X_W:
            if (A1 != A2 or B1 != B2) and A1.issubset(A2) and B1.issubset(B2):
                Y_W.discard((A1, B1))
                break

    # Step 6: Construct P_W and F_W
    pn = PetriNet()
    for t in T_W:
        pn.add_transition(t, t)
    pn.add_place('i_W')
    pn.add_place('o_W')
    place_counter = 0
    place_map = {}
    for (A, B) in Y_W:
        place_name = f'p_{place_counter}'
        place_counter += 1
        pn.add_place(place_name)
        place_map[(A, B)] = place_name
    for t in T_I:
        pn.add_edge('i_W', t)
    for t in T_O:
        pn.add_edge(t, 'o_W')
    for (A, B) in Y_W:
        place_name = place_map[(A, B)]
        for a in A:
            pn.add_edge(a, place_name)
        for b in B:
            pn.add_edge(place_name, b)
    pn.add_marking('i_W', tokens=1)
    return pn

def read_from_file(filename):
    # Parse the XES file
    tree = ET.parse(filename)
    root = tree.getroot()

    # Define the XES namespace (usually 'xes' but can vary)
    namespace = {'xes': 'http://www.xes-standard.org/'}

    # The log dictionary will map case_id to its list of events
    log = defaultdict(list)

    # Find all trace elements
    traces = root.findall("xes:trace", namespace)

    # Process each trace
    for trace in traces:
        # Get the case_id (concept:name of the trace)
        case_id = trace.find("xes:string[@key='concept:name']", namespace)
        if case_id is not None:
            case_id_value = case_id.attrib['value']
        else:
            case_id_value = "Unknown"  # Default if no concept:name found

        # List to hold the events for this case_id
        events = []

        # Extract each event within the trace
        for event in trace.findall("xes:event", namespace):
            event_dict = {}

            # Iterate over all attributes of the event
            for attribute in event:
                key = attribute.attrib['key']
                value = attribute.attrib['value']

                # Type casting based on the key
                if key == "time:timestamp":
                    # Convert string to a datetime object
                    try:
                        value = datetime.fromisoformat(value.replace("Z", "+00:00"))
                        value = value.replace(tzinfo=None)
                    except ValueError:
                        pass  # If there's an issue, keep the original value

                elif key == "cost" or key == "urgency":
                    # Convert to integer
                    try:
                        value = int(value)
                    except ValueError:
                        pass  # If there's an issue, keep the original value

                # Store the processed value in the event dictionary
                event_dict[key] = value

            # Add this event to the list of events for the current trace (case_id)
            events.append(event_dict)

        # Add events for the current trace (case_id) to the log
        log[case_id_value] = events

    return log

def fitness_token_replay(log, pn):
    total_produced = 0
    total_consumed = 0
    total_missing = 0
    total_remaining = 0

    # Process each case in the log
    for case_id, events in log.items():
        # Reset the marking to the initial state
        pn.reset_marking()

        # Sort the events by timestamp for each case
        events.sort(key=lambda x: x["time:timestamp"])

        produced = 0
        consumed = 0
        missing = 0
        # Iterate through the events to replay the trace
        for event in events:
            task = event["concept:name"]
            cons, prod, miss = pn.fire_transition(task)
            consumed += cons
            produced += prod
            missing += miss
        # After processing the trace, count the remaining tokens (excluding 'o_W')
        remaining_tokens = sum(pn.get_tokens(place) for place in pn.p if place != 'o_W')
        total_remaining += remaining_tokens

        total_produced += produced
        total_consumed += consumed
        total_missing += missing

    # Now compute the fitness
    if (total_consumed + total_produced) == 0:
        return 0
    fitness = 1 - ((total_missing + total_remaining) / (total_consumed + total_produced))
    return fitness

if __name__ == "__main__":

    log = read_from_file("extension-log-4.xes")
    log_noisy = read_from_file("extension-log-noisy-4.xes")

    mined_model = alpha(log)
    print(round(fitness_token_replay(log, mined_model), 5))
    mined_model.add_marking('i_W', tokens=1)
    print(round(fitness_token_replay(log_noisy, mined_model), 5))
