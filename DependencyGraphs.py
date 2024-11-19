from collections import defaultdict
from datetime import datetime

def log_as_dictionary(log):
    # Create a dictionary where the key is the case id and the value is a list of events
    log_dict = defaultdict(list)
    
    # Split the log into lines
    lines = log.strip().split("\n")
    
    # Process each line, but skip empty lines
    for line in lines:
        if not line.strip():  # Skip empty or whitespace-only lines
            continue
        
        task, case_id, user, timestamp = line.split(";")
        event = {
            "task": task,
            "case_id": case_id,
            "user": user,
            "timestamp": datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        }
        log_dict[case_id].append(event)
    
    return log_dict


def dependency_graph_inline(log):
    # Create a dictionary to store the dependency graph
    dependency_graph = defaultdict(lambda: defaultdict(int))
    
    # Process each case in the log
    for case_id, events in log.items():
        # Sort the events by timestamp for each case
        events.sort(key=lambda x: x["timestamp"])
        
        # Iterate through the events to establish relationships
        for i in range(len(events) - 1):
            source_activity = events[i]["task"]
            target_activity = events[i + 1]["task"]
            dependency_graph[source_activity][target_activity] += 1
    
    return dependency_graph

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


def dependency_graph_file(log):
    # Create a dictionary to store the dependency graph
    dependency_graph = defaultdict(lambda: defaultdict(int))
    
    # Process each case in the log
    for case_id, events in log.items():
        # Sort the events by timestamp for each case
        events.sort(key=lambda x: x["time:timestamp"])
        
        # Iterate through the events to establish relationships
        for i in range(len(events) - 1):
            source_activity = events[i]["concept:name"]
            target_activity = events[i + 1]["concept:name"]
            dependency_graph[source_activity][target_activity] += 1
    
    return dependency_graph



if __name__  == "__main__":

    log = read_from_file("extension-log.xes")



    # general statistics: for each case id the number of events contained
    for case_id in sorted(log):
        print((case_id, len(log[case_id])))

    first_key = list(log.keys())[0]
    first_value = log[first_key]

    # # Print the first key and its corresponding value
    print(f"First key: {first_key}")
    print(f"First value: {first_value}")
    case_id = "case_123"
    event_no = 0
    case = log[case_id]
    print((log[case_id][event_no]))

    # details for a specific event of one case
    print((log[case_id][event_no]["concept:name"], log[case_id][event_no]["org:resource"], log[case_id][event_no]["time:timestamp"],  log[case_id][event_no]["cost"]))
