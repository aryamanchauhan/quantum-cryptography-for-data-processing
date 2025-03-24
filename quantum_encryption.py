import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.visualization import plot_histogram
from qiskit.quantum_info import Statevector
from qiskit_aer import Aer
import matplotlib.pyplot as plt

def encrypt_data(data: str, key: int):
    n = len(data)
    circuit = QuantumCircuit(n)
    encrypted_bits = [(int(data[i]) ^ ((key >> i) & 1)) for i in range(n)]
    for i, bit in enumerate(encrypted_bits):
        if bit == 1:
            circuit.x(i)
    return circuit, encrypted_bits

def create_grover_circuit(target_bits: list):
    n = len(target_bits)
    qc = QuantumCircuit(n)

    # Initialize superposition
    # ADDING THE HADAMARD GATES to all n qubits
    qc.h(range(n))

    # Oracle
    for i, bit in enumerate(target_bits):
        if bit == 0:
            qc.x(i)

    qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)  # Multi-controlled X gate
    qc.h(n - 1)

    for i, bit in enumerate(target_bits):
        if bit == 0:
            qc.x(i)

    # Diffusion Operator
    # REFER CIRCUIT DIAGRAM FOR CLARITY
    qc.h(range(n))
    qc.x(range(n))
    qc.h(n - 1)
    qc.mcx(list(range(n - 1)), n - 1)
    qc.h(n - 1)
    qc.x(range(n))
    qc.h(range(n))

    qc.measure_all()
    return qc

def main():
    data = "1101"
    key = 6
    encrypted_circuit, encrypted_bits = encrypt_data(data, key)
    print("Quantum Encryption Circuit:")
    print(encrypted_circuit)

    print("\nEncrypted Bits:", encrypted_bits)

    # Use encrypted_bits as the target for Grover's algorithm
    grover_circuit = create_grover_circuit(encrypted_bits)
    print("\nGrover's Algorithm Circuit:")
    print(grover_circuit)

    backend = Aer.get_backend("qasm_simulator")

    try:
        new_circuit = transpile(grover_circuit, backend)
        job = backend.run(new_circuit, shots=1024)
        measurement_result = job.result().get_counts()

        plot_histogram(measurement_result)
        plt.title("Grover's Algorithm Measurement")
        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(f"Simulation error: {e}")

if __name__ == "__main__":
    main()
