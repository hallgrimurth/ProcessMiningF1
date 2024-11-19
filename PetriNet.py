class PetriNet:
    def __init__(self):
        self.p = []  # Set of places
        self.t = {}  # Set of transitions (name to ID mapping)
        self.f = []  # Set of directed arcs (edges)
        self.m = []  # Current marking (tokens in places)

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
        return self.m.count(place)

    def is_enabled(self, transition):
        enabled = True
        for edge in self.f:
            if edge[1] == transition and self.get_tokens(edge[0]) == 0:
                enabled = False
        return enabled

    def add_marking(self, place):
        if place in self.p:
            self.m.append(place)

    def fire_transition(self, transition):
        if not self.is_enabled(transition):
            print(f"Transition {transition} is not enabled.")
            return
        for edge in self.f:
            if edge[1] == transition:
                self.m.remove(edge[0])
        for edge in self.f:
            if edge[0] == transition:
                self.m.append(edge[1])

    def transition_name_to_id(self, name):
        return self.t.get(name)


if __name__ == "__main__":
    p = PetriNet()

    p.add_place(1)  # add place with id 1
    p.add_place(2)
    p.add_place(3)
    p.add_place(4)
    p.add_transition("A", -1)  # add transition "A" with id -1
    p.add_transition("B", -2)
    p.add_transition("C", -3)
    p.add_transition("D", -4)

    p.add_edge(1, -1)
    p.add_edge(-1, 2)
    p.add_edge(2, -2).add_edge(-2, 3)
    p.add_edge(2, -3).add_edge(-3, 3)
    p.add_edge(3, -4)
    p.add_edge(-4, 4)

    print(p.is_enabled(-1), p.is_enabled(-2), p.is_enabled(-3), p.is_enabled(-4))

    p.add_marking(1)  # add one token to place id 1
    print(p.is_enabled(-1), p.is_enabled(-2), p.is_enabled(-3), p.is_enabled(-4))

    p.fire_transition(-1)  # fire transition A
    print(p.is_enabled(-1), p.is_enabled(-2), p.is_enabled(-3), p.is_enabled(-4))

    p.fire_transition(-3)  # fire transition C
    print(p.is_enabled(-1), p.is_enabled(-2), p.is_enabled(-3), p.is_enabled(-4))

    p.fire_transition(-4)  # fire transition D
    print(p.is_enabled(-1), p.is_enabled(-2), p.is_enabled(-3), p.is_enabled(-4))

    p.add_marking(2)  # add one token to place id 2
    print(p.is_enabled(-1), p.is_enabled(-2), p.is_enabled(-3), p.is_enabled(-4))

    p.fire_transition(-2)  # fire transition B
    print(p.is_enabled(-1), p.is_enabled(-2), p.is_enabled(-3), p.is_enabled(-4))

    p.fire_transition(-4)  # fire transition D
    print(p.is_enabled(-1), p.is_enabled(-2), p.is_enabled(-3), p.is_enabled(-4))

    # by the end of the execution there should be 2 tokens on the final place
    print(p.get_tokens(4))