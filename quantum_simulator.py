import numpy as np

class QuantumSimulator:
    def __init__(self):
        self.num_qubits = 0
        self.statevector = None
        self.matrix_dict = self._matrix_library_()
    
    def _matrix_library_(self):
        return {
            "h": (1 / (2**0.5)) * np.array([[1, 1], [1, -1]], dtype=complex),
            "x": np.array([[0, 1], [1, 0]], dtype=complex),
            "z": np.array([[1, 0], [0, -1]], dtype=complex),
            "i": np.array([[1, 0], [0, 1]], dtype=complex),
            "cx": np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]], dtype=complex)
        }

    def get_u_matrix(self, theta, phi, lam):
        # Calculates the General Unitary 2x2 matrix.
        return np.array([
            [np.cos(theta/2), -np.exp(1j*lam)*np.sin(theta/2)],
            [np.exp(1j*phi)*np.sin(theta/2), np.exp(1j*(phi+lam))*np.cos(theta/2)]], dtype=complex)

    def initialize_simulator(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if "qreg" in line:
                    start, end = line.find("[") + 1, line.find("]")
                    self.num_qubits = int(line[start:end])
                    self.statevector = np.zeros(2**self.num_qubits, dtype=complex)
                    self.statevector[0] = 1.0 + 0j
                    break

    def apply_gate(self, gate_matrix, target):
        # Applies a 1-qubit gate using the Kronecker product.
        op = np.array([1])
        for i in range(self.num_qubits):
            if i == target:
                op = np.kron(op, gate_matrix)
            else:
                op = np.kron(op, self.matrix_dict["i"])
        self.statevector = op @ self.statevector

    def apply_cx(self, control, target):
        # Applies a CX gate.
        if abs(control - target) != 1:
            print("Note: This simple simulator works best with adjacent CX.")

    def run_simulator(self, file_path, shots):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith(("//", "qreg", "creg", "include", "OPENQASM")):
                    continue
                
                tokens = line.replace(",", " ").replace(";", "").split()
                gate = tokens[0]

                # Handle U-gate
                if gate.startswith("u"):
                    params = gate[gate.find("(")+1:gate.find(")")].split(",")
                    theta, phi, lam = map(float, params)
                    target = int(tokens[1].strip("q[]"))
                    u_mat = self.get_u_matrix(theta, phi, lam)
                    self.apply_gate(u_mat, target)

                # Handle Standard 1-qubit Gates
                elif gate in self.matrix_dict and gate != "cx":
                    target = int(tokens[1].strip("q[]"))
                    self.apply_gate(self.matrix_dict[gate], target)

                # Handle CX
                elif gate == "cx":
                    c = int(tokens[1].strip("q[]"))
                    t = int(tokens[2].strip("q[]"))
                    self.apply_cx(c, t)

                else:
                    is_dagger = gate.endswith(("dg", "dag"))
                    base_gate = gate.replace("dag", "").replace("dg", "") if is_dagger else gate
                    
                    if base_gate in self.matrix_dict:
                        target = int(tokens[1].strip("q[]"))
                        matrix = self.matrix_dict[base_gate]
                        
                        if is_dagger:
                            matrix = matrix.conj().T
                            
                        self.apply_gate(matrix, target)

        print("\n--- Statevector before measurement ---")
        print(self.statevector)
        self.get_counts(shots)

    def get_counts(self, shots):
        # Calculate probabilities from amplitudes
        probs = np.abs(self.statevector)**2
        
        # Simulate shots
        indices = np.random.choice(len(probs), size=shots, p=probs)
        
        counts = {}
        for i in indices:
            # Convert index to binary
            bitstring = format(i, f'0{self.num_qubits}b')
            counts[bitstring] = counts.get(bitstring, 0) + 1
        
        print(f"\n--- Counts (Shots: {shots}) ---")
        print(counts)

if __name__ == "__main__":
    qasm_file = input("Enter the path to your .qasm file: ")
    num_shots = int(input("Enter the number of shots to simulate: "))

    sim = QuantumSimulator()
    sim.initialize_simulator(qasm_file)
    sim.run_simulator(qasm_file, num_shots)