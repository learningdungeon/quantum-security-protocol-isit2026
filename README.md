

#  Q Defence in Depth - Hybrid Quantum/PQC Authentication (Demo)

**ISIT 2026 QHack — Phase Shifters** | **Presenter:** Noor Ul Ain Faisal

---

## Overview

RAQT is a 3-layer hybrid authentication protocol combining quantum and post-quantum cryptographic primitives. This is a pedagogical demonstration using Qiskit quantum simulations.

### The Three Layers

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **1** | GHZ States (Quantum) | Verify entangled resources |
| **2** | BB84 Protocol (Quantum) | Secure key distribution + eavesdropper detection |
| **3** | Lattice Signatures (PQC) | Transaction signing with quantum-derived keys |

**Cross-layer binding:** SHA-256 hash of quantum key used as input to lattice signature.

---

## Quick Start

### Install Dependencies
```
pip install qiskit qiskit-aer numpy matplotlib
```

### Run the Demo
```
python raqt_demo.py
```

### Command-Line Options
```
python raqt_demo.py --bb84-bits 32    # More bits for BB84
python raqt_demo.py --quiet           # Minimal output
python raqt_demo.py --no-viz          # Skip visualization
python raqt_demo.py --seed 42         # Reproducible results
python raqt_demo.py --output plot.png # Custom output filename
```

---

## Core Mechanics

### Layer 1: GHZ Verification
Creates a 3-qubit entangled state and checks correlation. Valid GHZ states show over 90% all-0 or all-1 outcomes.

### Layer 2: BB84 Quantum Key Distribution
Alice sends qubits in random bases (Z or X). Bob measures in random bases. Matching bases form the shared key. QBER (Quantum Bit Error Rate) detects eavesdroppers. Channel is compromised if QBER exceeds 11%.

### Layer 3: Lattice-Based Signatures
Simplified CRYSTALS-Dilithium-inspired signatures using a 5-dimensional lattice. Production implementations use 1024+ dimensions. Security is based on Short Integer Solution (SIS) and Learning With Errors (LWE) hard problems. Transactions are signed using the quantum-derived key hash.

---

## Attack Simulation

The script detects three distinct attack types:

| Attack | Detection Method |
|--------|-----------------|
| Replay Attack | Protocol-level detection |
| MITM Attack | QBER threshold (above 25%) |
| Traffic Analysis | Pattern monitoring |

---

## Security Index

Scores from 0 to 100 with configurable penalties:
- QBER contribution: -1 per 1% error rate
- Replay attack: -15
- MITM attack: -25
- Traffic analysis: -10

---

## Example Output

```
LAYER 1: GHZ State Verification
  GHZ Correlation: 100.00% — Valid

LAYER 2: BB84 QKD
  No Eve:  QBER = 0.00%  (clean)
  With Eve: QBER = 50.00% (detected!)

LAYER 3: Lattice Signature
  Signature Valid — Cross-layer binding successful

ATTACK SIMULATION
  MITM Attack: DETECTED (QBER above 25%)

SECURITY INDEX: 15/100 — POOR
```

---

## Visualization

Generates `security_visualization.png` containing three panels:
- QBER comparison (No Eve vs. With Eve)
- Security index score with thresholds
- Attack detection status

---

## File Structure

```
raqt-demo/
├── raqt_demo.py              # Main script
├── security_visualization.png # Generated output
└── README.md                 # This file
```

---

## Configuration

Edit the parameters inside `raqt_demo.py`:

```
GHZ_QUBITS = 3                  # GHZ state size
BB84_NUM_BITS = 16              # BB84 transmission length
BB84_QBER_SECURE_THRESHOLD = 0.11  # Security cutoff
LATTICE_DIMENSION = 5           # Lattice security parameter
```

### Testing Different Scenarios

**Clean channel (high score expected):**
```
python raqt_demo.py --seed 42
```

**Eavesdropper present (low score expected):**
```
python raqt_demo.py --seed 123
```

**Batch testing (Linux/Mac):**
```
for i in $(seq 1 10); do
    python raqt_demo.py --seed $i --no-viz
done
```

**Batch testing (Windows PowerShell):**
```
for ($i=1; $i -le 10; $i++) {
    python raqt_demo.py --seed $i --no-viz
}
```

---

## Project Information

- **Team:** Phase Shifters
- **Event:** ISIT 2026 QHack
- **Presenter:** Noor Ul Ain Faisal

### For QHack Judges

- This is a concept demonstration, not production code
- Simplified models are used intentionally for educational clarity
- All limitations are documented in code comments and this README
- The hybrid approach showcases the complementarity of quantum and PQC layers
- Feedback on scaling to real hardware implementations is welcome

### Disclaimer

This is a pedagogical demonstration for educational purposes only.
- Lattice signature components use toy parameters and are NOT cryptographically secure
- Security weights are illustrative, not empirical
- Code has not been audited for production use
- Real-world implementation of CRYSTALS-Dilithium requires NIST-compliant parameters

---

## References

- Bennett & Brassard (1984) — BB84 Protocol
- Greenberger, Horne, Zeilinger (1989) — GHZ States
- NIST PQC Standardization — CRYSTALS-Dilithium
- Qiskit — https://qiskit.org

---

## AI Usage Disclosure

- **Tools Used:** DeepSeek AI, Gemini, ChatGPT
- **AI Assistance:** Code structure suggestions, markdown formatting, visualization code, cross checking
- **Human-Created:** Protocol architecture, quantum circuit design, BB84 implementation, GHZ state logic, attack detection methodology, and all scientific explanations are original work based on MIT 8.04 study, Qiskit Advocate training, and published research
- **Verification:** All code manually tested. Author can explain every quantum concept and line of code

---

## Author

**Noor Ul Ain Faisal**
- IBM Qiskit Advocate (2025)
- Friend of OQI, Open Quantum Institute at CERN (2026)
- Mentor, Qiskit Advocate Mentorship Program (QAMP)
- unitaryHACK 2026 Winner

GitHub: [learningdungeon](https://github.com/learningdungeon)  
LinkedIn: [noorulain-faisal](https://linkedin.com/in/noorulain-faisal)

---

## License

MIT License
 
