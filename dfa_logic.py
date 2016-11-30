TOTAL_STATES = "states"
START_STATE = "start"
ALPHABETS = "alphabet"
TRANSITION_TABLE = "transitions"
ACCEPTED_STATE = "accept"


class DFA:

    def __init__(self, dfa_instructions):
        self.states = dfa_instructions[TOTAL_STATES]
        self.alphabet = dfa_instructions[ALPHABETS]
        self.description = 'A Sample Example'
        self.start_state = dfa_instructions[START_STATE]
        self.accepted_states = dfa_instructions[ACCEPTED_STATE]
        self.transitions = dfa_instructions[TRANSITION_TABLE]

    @property
    def get_dfa(self):
        return self, self.test_strings

    def run_dfa(self, input_str):
        logs = []
        current_state = self.start_state
        print "Description: " + self.description + " On the Input: " + input_str

        if current_state == "":
            logs.append("Invalid DFA: Start state not provided in the DFA." + "\n")
            return logs
        elif len(self.accepted_states) == 0 or (len(self.accepted_states)==1 and self.accepted_states[0]==''):
            logs.append("Invalid DFA: Accept state not provided in the DFA." + "\n")
            return logs
        elif input_str == "":
            logs.append("Invalid DFA: Input string is not provided in the DFA." + "\n")
            return logs

        for state in self.accepted_states:
            if state not in self.states:
                logs.append("Invalid DFA: " + state + " is not a state in the DFA." + "\n")
                return logs
        
        print "run_dfa:self.transitions:", self.transitions
        for character in input_str:
            if current_state in self.transitions and character in self.transitions[current_state].keys():
                new_state = self.transitions[current_state][character]
            else:
                logs.append("--Unable to move from state: " + current_state + " on input: " + character + "\n")
                logs.append("DFA REJECTED for: " + input_str + "\n")
                return logs
            logs.append("--Moving from state: " + current_state + " to State: " + new_state + " on input: " + character + "\n")
            current_state = new_state

        if any(current_state in s for s in self.accepted_states):
            logs.append("DFA ACCEPTED for: " + input_str + "\n")
        else:
            logs.append("DFA REJECTED for: " + input_str + "\n")
        return logs