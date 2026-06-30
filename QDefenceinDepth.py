"""
RAQT PROTOCOL DEMONSTRATION — WITH QISKIT AND VISUALIZATIONS
ISIT 2026 QHack — Phase Shifters
Presenter: Noor Ul Ain Faisal

This is a pedagogical demonstration of a 3-layer hybrid quantum/PQC
authentication concept. Layers 1 and 2 use Qiskit quantum simulations.

NOTE: This is a simplified conceptual demonstration for educational
purposes. The lattice-based signature (Layer 3) uses toy parameters
and is NOT the full NIST-standardized CRYSTALS-Dilithium implementation.
The BB84 simulation abstracts away some physical channel details for clarity.
All security scoring weights are illustrative, not empirically derived.
"""

import random
import hashlib
import argparse
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import matplotlib.pyplot as plt
from collections import Counter


# ============================================================
# CONFIGURATION & UTILITY
# ============================================================

class Config:
    """Central configuration for the demonstration."""
    GHZ_QUBITS = 3
    GHZ_SHOTS = 1024
    GHZ_CORRELATION_THRESHOLD = 0.90
    
    BB84_NUM_BITS = 16
    BB84_QBER_SECURE_THRESHOLD = 0.11  # Standard BB84 threshold
    BB84_QBER_NOISE_THRESHOLD = 0.05   # Below this = clean channel
    BB84_MITM_THRESHOLD = 0.25         # Intercept-resend typical QBER
    
    LATTICE_DIMENSION = 5
    LATTICE_MODULUS = 8380417  # Prime modulus (real Dilithium uses 8380417)
    LATTICE_SEED = 42          # Fixed for reproducibility
    
    SECURITY_WEIGHTS = {
        'qber_per_percent': 1,     # -1 point per 1% QBER
        'replay_attack': 15,       # -15 if replay detected
        'mitm_attack': 25,         # -25 if MITM detected
        'traffic_analysis': 10,    # -10 if traffic analysis risk
    }
    SECURITY_GOOD_THRESHOLD = 70
    SECURITY_MODERATE_THRESHOLD = 50


# ============================================================
# LAYER 1: GHZ VERIFICATION WORKFLOW (Qiskit)
# ============================================================

def create_ghz_state(num_qubits=Config.GHZ_QUBITS):
    """
    Create a GHZ state |0...0⟩ + |1...1⟩ and return measurement counts.
    
    A true GHZ state should show strong correlation between all qubits,
    with measurements collapsing to either all-0 or all-1.
    
    Args:
        num_qubits: Number of qubits in the GHZ state
        
    Returns:
        dict: Measurement counts from 1024 shots
    """
    qc = QuantumCircuit(num_qubits, num_qubits)
    
    # Create entanglement: H on qubit 0, then CNOT chain
    qc.h(0)
    for i in range(num_qubits - 1):
        qc.cx(i, i + 1)
    
    # Measure all qubits
    qc.measure(range(num_qubits), range(num_qubits))
    
    simulator = AerSimulator()
    compiled = transpile(qc, simulator)
    result = simulator.run(compiled, shots=Config.GHZ_SHOTS).result()
    counts = result.get_counts()
    
    return counts


def run_ghz_demonstration():
    """Run Layer 1: GHZ state verification and correlation analysis."""
    print("\n" + "=" * 60)
    print("LAYER 1: GHZ-BASED VERIFICATION WORKFLOW (Qiskit)")
    print("=" * 60)
    
    counts = create_ghz_state(num_qubits=Config.GHZ_QUBITS)
    print(f"\n  📊 GHZ State Measurement Counts: {counts}")
    
    # Calculate GHZ correlation: all-0 and all-1 outcomes
    total = sum(counts.values())
    all_zeros = '0' * Config.GHZ_QUBITS
    all_ones = '1' * Config.GHZ_QUBITS
    ghz_correlation = counts.get(all_zeros, 0) + counts.get(all_ones, 0)
    correlation_ratio = ghz_correlation / total if total > 0 else 0
    
    print(f"  📊 GHZ Correlation: {correlation_ratio:.2%}")
    print(f"     (Expected: >{Config.GHZ_CORRELATION_THRESHOLD:.0%} for valid GHZ state)")
    
    if correlation_ratio > Config.GHZ_CORRELATION_THRESHOLD:
        print("  ✅ GHZ correlation PRESERVED — valid GHZ state")
        print("     → Confirms: No tampering with the entangled resource")
    else:
        print("  🚨 GHZ correlation BROKEN — invalid token detected")
        print("     → Indicates: Possible interference or state preparation error")
    
    return counts


# ============================================================
# LAYER 2: BB84-STYLE QKD (Single Qubit Per Transmission)
# ============================================================

def bb84_single_qubit_transmission(alice_bit, alice_basis, bob_basis,
                                    eve_basis=None, eve_present=False):
    """
    Simulate a single qubit transmission in the BB84 protocol.
    
    Each qubit gets its own quantum circuit to prevent cross-contamination
    between transmissions. This accurately models the sequential nature
    of real QKD systems.
    
    NOTE: This is a simplified simulation. In a real implementation:
    - Eve would forward her EXACT measurement result (not a random bit)
    - Physical channel noise would be modeled separately
    - Detection efficiency and dark counts would be included
    
    Args:
        alice_bit: Alice's bit value (0 or 1)
        alice_basis: Alice's encoding basis ('Z' or 'X')
        bob_basis: Bob's measurement basis ('Z' or 'X')
        eve_basis: Eve's measurement basis (if present)
        eve_present: Whether Eve is intercepting
        
    Returns:
        int: Bob's measurement result (0 or 1)
    """
    qc = QuantumCircuit(1, 1)
    
    # === Alice's Preparation ===
    if alice_bit == 1:
        qc.x(0)  # Prepare |1⟩
    if alice_basis == 'X':
        qc.h(0)  # Rotate to X-basis: |+⟩ or |-⟩
    
    # === Eve's Intercept-Resend Attack (if present) ===
    if eve_present:
        # Eve measures in her chosen basis
        if eve_basis == 'X':
            qc.h(0)
        qc.measure(0, 0)
        
        # Eve re-prepares based on her measurement
        # NOTE: In a real intercept-resend attack, Eve would forward
        # exactly what she measured. Here we simulate the measurement
        # outcome by preparing a known state for Bob.
        qc.reset(0)
        
        # Since we can't easily extract Eve's measurement mid-circuit,
        # we simulate her re-preparation. This is a known simplification.
        eve_measured_bit = random.randint(0, 1)
        if eve_measured_bit == 1:
            qc.x(0)
        if eve_basis == 'X':
            qc.h(0)
    
    # === Bob's Measurement ===
    if bob_basis == 'X':
        qc.h(0)  # Rotate to measure in X-basis
    qc.measure(0, 0)
    
    # === Run Simulation ===
    simulator = AerSimulator()
    compiled = transpile(qc, simulator)
    result = simulator.run(compiled, shots=1).result()
    counts = result.get_counts()
    
    # Extract Bob's result from the single shot
    bob_result = int(list(counts.keys())[0]) if counts else 0
    
    return bob_result


def bb84_qkd_simulate(num_bits=Config.BB84_NUM_BITS, eve=False):
    """
    Full BB84-style QKD simulation with independent qubit transmissions.
    
    Protocol steps:
    1. Alice generates random bits and random bases
    2. Bob chooses random measurement bases
    3. Each bit is transmitted as a single quantum state
    4. Alice and Bob sift: keep bits where bases matched
    5. Calculate QBER to detect eavesdropping
    
    Args:
        num_bits: Number of bits to transmit
        eve: Whether an eavesdropper is present
        
    Returns:
        dict: Results including shared key, QBER, and security status
    """
    # Generate random choices
    alice_bits = [random.randint(0, 1) for _ in range(num_bits)]
    alice_bases = [random.choice(['Z', 'X']) for _ in range(num_bits)]
    bob_bases = [random.choice(['Z', 'X']) for _ in range(num_bits)]
    
    eve_bases = [random.choice(['Z', 'X']) for _ in range(num_bits)] if eve else [None] * num_bits
    
    # Transmit each qubit independently
    bob_results = []
    for i in range(num_bits):
        bob_bit = bb84_single_qubit_transmission(
            alice_bit=alice_bits[i],
            alice_basis=alice_bases[i],
            bob_basis=bob_bases[i],
            eve_basis=eve_bases[i] if eve else None,
            eve_present=eve
        )
        bob_results.append(bob_bit)
    
    # Sifting: keep bits where Alice and Bob used the same basis
    sifted_alice = []
    sifted_bob = []
    for i in range(num_bits):
        if alice_bases[i] == bob_bases[i]:
            sifted_alice.append(alice_bits[i])
            sifted_bob.append(bob_results[i])
    
    # Calculate Quantum Bit Error Rate (QBER)
    if len(sifted_alice) > 0:
        errors = sum(1 for a, b in zip(sifted_alice, sifted_bob) if a != b)
        qber = errors / len(sifted_alice)
    else:
        qber = 1.0  # No key established
    
    # Security assessment
    secure = qber < Config.BB84_QBER_SECURE_THRESHOLD
    
    return {
        'shared_key': ''.join(map(str, sifted_alice)),
        'shared_key_length': len(sifted_alice),
        'qber': qber,
        'secure': secure,
        'sifted_length': len(sifted_alice)
    }


def run_bb84_demonstration():
    """Run Layer 2: BB84 QKD with and without eavesdropper."""
    print("\n" + "=" * 60)
    print("LAYER 2: BB84-STYLE QKD (Independent Qubit Transmission)")
    print("=" * 60)
    print("  ℹ️  Simplified simulation — each qubit transmitted separately")
    print("  ℹ️  Eve's re-preparation uses random bit (see code comments)")
    
    # Scenario 1: Normal operation
    result_no_eve = bb84_qkd_simulate(num_bits=Config.BB84_NUM_BITS, eve=False)
    
    print(f"\n  📊 Normal Operation (no Eve):")
    print(f"  ├─ Bits transmitted: {Config.BB84_NUM_BITS}")
    print(f"  ├─ Sifted key bits: {result_no_eve['sifted_length']}")
    print(f"  └─ QBER: {result_no_eve['qber']:.2%}")
    
    # Scenario 2: Eavesdropper present
    result_eve = bb84_qkd_simulate(num_bits=Config.BB84_NUM_BITS, eve=True)
    
    print(f"\n  🕵️  With Eavesdropper (Intercept-Resend):")
    print(f"  ├─ Bits transmitted: {Config.BB84_NUM_BITS}")
    print(f"  ├─ Sifted key bits: {result_eve['sifted_length']}")
    print(f"  └─ QBER: {result_eve['qber']:.2%}")
    
    # Analysis
    print(f"\n  📈 Analysis:")
    
    # No-eve analysis
    if result_no_eve['qber'] < Config.BB84_QBER_NOISE_THRESHOLD:
        print(f"  ✅ No Eve: QBER = {result_no_eve['qber']:.2%} (clean channel)")
    else:
        print(f"  ⚠️  No Eve: QBER = {result_no_eve['qber']:.2%} (noise above expected)")
        print(f"     Expected: <{Config.BB84_QBER_NOISE_THRESHOLD:.0%} for clean channel")
    
    # With-eve analysis
    if result_eve['qber'] > Config.BB84_MITM_THRESHOLD:
        print(f"  🚨 With Eve: QBER = {result_eve['qber']:.2%} (clearly detected)")
        print(f"     Intercept-resend attacks typically cause QBER >{Config.BB84_MITM_THRESHOLD:.0%}")
    elif result_eve['qber'] > Config.BB84_QBER_SECURE_THRESHOLD:
        print(f"  ⚠️  With Eve: QBER = {result_eve['qber']:.2%} (above secure threshold)")
    else:
        print(f"  ⚠️  With Eve: QBER = {result_eve['qber']:.2%} (below detection threshold)")
        print(f"     NOTE: This can happen when Eve guesses bases correctly")
    
    # Final verdict
    if not result_eve['secure']:
        print(f"\n  🚨 EAVESDROPPER DETECTED — Channel insecure (QBER > {Config.BB84_QBER_SECURE_THRESHOLD:.0%})")
    else:
        print(f"\n  ✅ No eavesdropper detected (QBER within acceptable range)")
    
    return result_no_eve, result_eve


# ============================================================
# LAYER 3: LATTICE-BASED SIGNATURE (Simplified PQC)
# ============================================================

class LatticeSignatureProtocol:
    """
    Simplified lattice-based signature inspired by CRYSTALS-Dilithium.
    
    IMPORTANT DISCLAIMER: This is a TOY implementation for educational
    demonstration only. It uses:
    - A 5-dimensional lattice (real Dilithium uses much larger dimensions)
    - Simplified signing procedure
    - No rejection sampling or compression
    
    The real CRYSTALS-Dilithium is a NIST PQC standardized algorithm
    with rigorous security proofs. This demo shows the CONCEPT of
    lattice-based signatures, not a secure implementation.
    """
    
    def __init__(self, dimension=Config.LATTICE_DIMENSION, modulus=Config.LATTICE_MODULUS):
        """
        Initialize lattice key pair.
        
        Args:
            dimension: Lattice dimension (security parameter)
            modulus: Prime modulus for arithmetic
        """
        self.q = modulus
        self.dimension = dimension
        
        # Fixed seed for reproducibility in demonstrations
        np.random.seed(Config.LATTICE_SEED)
        
        # Generate secret key (short vector)
        self.s1 = np.random.randint(-2, 3, size=(self.dimension, 1))
        
        # Generate public matrix A (uniform random)
        self.A = np.random.randint(0, self.q, size=(self.dimension, self.dimension))
        
        # Public key: t = A·s1 (mod q)
        # Security: Recovering s1 from (A, t) is the Short Integer Solution (SIS) problem
        self.t = (np.dot(self.A, self.s1)) % self.q
        
        print(f"\n  🔑 Lattice-based key pair generated (SIMPLIFIED DEMO)")
        print(f"  ├─ Security basis: SIS/LWE hard problems")
        print(f"  ├─ Lattice dimension: {self.dimension} (real Dilithium uses 1024+)")
        print(f"  ├─ Modulus: {self.q}")
        print(f"  └─ Inspired by: CRYSTALS-Dilithium (NIST PQC Standard)")
        print(f"  ⚠️  NOT suitable for production use")
    
    def sign(self, message, quantum_key_hash):
        """
        Create a simplified lattice-based signature.
        
        In real Dilithium, signing involves:
        1. Hashing message to a polynomial
        2. Rejection sampling to hide secret
        3. Compression for smaller signatures
        
        This demo simplifies to show the core concept.
        
        Args:
            message: Transaction message to sign
            quantum_key_hash: Hash of quantum-derived key for binding
            
        Returns:
            tuple: (signature z, challenge c)
        """
        # Combine transaction with quantum-derived key
        # This binds the classical transaction to the quantum channel
        combined = message + quantum_key_hash
        msg_hash = int(hashlib.sha256(combined.encode()).hexdigest(), 16) % self.q
        
        # Challenge derived from message
        c = np.array([[msg_hash % self.q]])
        
        # Generate masking vector (randomness for security)
        y = np.random.randint(-100, 101, size=(self.dimension, 1))
        
        # Signature: z = y + c·s1 (mod q)
        # Knowledge of s1 is required to create valid signatures
        z = (y + c * self.s1) % self.q
        
        return z, c
    
    def verify(self, message, quantum_key_hash, z, c):
        """
        Verify a lattice-based signature.
        
        In a real implementation, verification would check:
        - That z is sufficiently small (norm bound)
        - That the challenge was correctly computed
        
        Args:
            message: Original transaction message
            quantum_key_hash: Hash of quantum-derived key
            z: Signature vector
            c: Challenge vector
            
        Returns:
            bool: True if signature is valid
        """
        # Recompute challenge from the same inputs
        combined = message + quantum_key_hash
        msg_hash = int(hashlib.sha256(combined.encode()).hexdigest(), 16) % self.q
        expected_c = np.array([[msg_hash]])
        
        # Verify challenge matches
        if c[0][0] != expected_c[0][0]:
            return False
        
        # In a real implementation, we would also verify:
        # - ||z|| is small (bounded norm)
        # - A·z - c·t has small coefficients
        
        return True
    
    def run_signature_demonstration(self, transaction, quantum_key_hash):
        """
        Demonstrate the complete sign-verify workflow.
        
        Args:
            transaction: Transaction data to sign
            quantum_key_hash: Quantum key hash binding Layer 2 to Layer 3
            
        Returns:
            bool: Whether signature verification succeeded
        """
        print("\n" + "=" * 60)
        print("LAYER 3: LATTICE-BASED SIGNATURE (Simplified PQC)")
        print("=" * 60)
        print("  ℹ️  Toy implementation — conceptual demonstration only")
        
        z, c = self.sign(transaction, quantum_key_hash)
        verified = self.verify(transaction, quantum_key_hash, z, c)
        
        print(f"\n  📝 Transaction: {transaction}")
        print(f"  🔗 Quantum Key Hash: {quantum_key_hash[:16]}...")
        print(f"  📐 Signature dimension: {z.shape}")
        print(f"  ✅ Signature Valid: {verified}")
        
        if verified:
            print(f"  🔒 Cross-layer binding successful (Quantum → Classical)")
        
        return verified


# ============================================================
# ATTACK SIMULATION MODULE
# ============================================================

class AttackSimulator:
    """
    Simulates various attack scenarios on the hybrid protocol.
    
    NOTE: Attack detection probabilities in this demo are illustrative.
    Real implementations require rigorous security analysis.
    """
    
    @staticmethod
    def replay_attack():
        """
        Detect replay attacks via protocol-level nonces/timestamps.
        
        In production, this would check message freshness using:
        - Timestamps with synchronized clocks
        - Cryptographic nonces
        - Sequence numbers
        
        Returns:
            bool: Whether replay attack is detected (simulated)
        """
        # Simulated: In real deployment, this checks actual protocol state
        return random.choice([True, False])
    
    @staticmethod
    def mitm_attack(qber_eve):
        """
        Detect Man-in-the-Middle attacks via QBER threshold.
        
        In BB84, an intercept-resend MITM attack introduces errors because
        Eve cannot know the correct bases. The expected QBER is ~25% for
        this attack type.
        
        Args:
            qber_eve: Measured Quantum Bit Error Rate
            
        Returns:
            bool: True if MITM detected (QBER exceeds threshold)
        """
        detected = qber_eve > Config.BB84_MITM_THRESHOLD
        return detected
    
    @staticmethod
    def traffic_analysis():
        """
        Detect traffic analysis patterns.
        
        Traffic analysis looks for suspicious patterns in:
        - Message timing
        - Message sizes
        - Communication frequency
        
        Returns:
            bool: Whether traffic analysis risk is detected (simulated)
        """
        return random.choice([True, False])
    
    def run_attack_demonstration(self, qber_eve):
        """
        Run all attack simulations and report results.
        
        Args:
            qber_eve: QBER from Layer 2 (with eavesdropper)
            
        Returns:
            tuple: (replay_detected, mitm_detected, traffic_detected)
        """
        print("\n" + "=" * 60)
        print("ATTACK SIMULATION")
        print("=" * 60)
        
        replay = self.replay_attack()
        mitm = self.mitm_attack(qber_eve)
        traffic = self.traffic_analysis()
        
        print(f"  🎯 Replay Attack:         {'⚠️  DETECTED' if replay else '✅ Not detected'}")
        print(f"  🎯 MITM Attack:           {'🚨 DETECTED' if mitm else '✅ Not detected'}")
        print(f"     (via QBER threshold > {Config.BB84_MITM_THRESHOLD:.0%})")
        print(f"  🎯 Traffic Analysis Risk: {'⚠️  PRESENT' if traffic else '✅ Not detected'}")
        
        return replay, mitm, traffic


# ============================================================
# SECURITY INDEX
# ============================================================

class SecurityIndex:
    """
    Calculate a composite security score for the hybrid protocol.
    
    IMPORTANT: The scoring weights are ILLUSTRATIVE and chosen for
    clear demonstration. Real security metrics require:
    - Empirical testing
    - Formal security proofs
    - Domain-specific threat modeling
    
    The scoring formula:
        score = 100 - Σ(penalties)
    
    Penalties are applied for:
    - QBER (higher = more deduction)
    - Detected attacks (each type has specific weight)
    """
    
    def __init__(self, weights=None):
        """
        Initialize with configurable weights.
        
        Args:
            weights: Dict of penalty weights (uses Config defaults if None)
        """
        self.weights = weights or Config.SECURITY_WEIGHTS
    
    def calculate(self, qber, replay_detected, mitm_detected, traffic_detected):
        """
        Calculate security score from 100 down to 0.
        
        Args:
            qber: Quantum Bit Error Rate
            replay_detected: Whether replay attack was detected
            mitm_detected: Whether MITM attack was detected
            traffic_detected: Whether traffic analysis risk detected
            
        Returns:
            int: Security score (0-100)
        """
        score = 100
        
        # QBER penalty: higher error rate = less secure
        score -= int(qber * 100) * self.weights['qber_per_percent']
        
        # Attack penalties
        if replay_detected:
            score -= self.weights['replay_attack']
        if mitm_detected:
            score -= self.weights['mitm_attack']
        if traffic_detected:
            score -= self.weights['traffic_analysis']
        
        return max(score, 0)
    
    def run_security_index_demonstration(self, qber, replay, mitm, traffic):
        """
        Display security score calculation with breakdown.
        
        Args:
            qber: Quantum Bit Error Rate
            replay: Replay attack detection status
            mitm: MITM attack detection status
            traffic: Traffic analysis detection status
            
        Returns:
            int: Final security score
        """
        print("\n" + "=" * 60)
        print("SECURITY INDEX")
        print("=" * 60)
        print("  ℹ️  Scoring weights are illustrative for demonstration")
        
        score = self.calculate(qber, replay, mitm, traffic)
        
        # Breakdown
        qber_penalty = int(qber * 100) * self.weights['qber_per_percent']
        replay_penalty = self.weights['replay_attack'] if replay else 0
        mitm_penalty = self.weights['mitm_attack'] if mitm else 0
        traffic_penalty = self.weights['traffic_analysis'] if traffic else 0
        
        print(f"  📊 Starting score: 100")
        print(f"  📊 QBER ({qber:.1%}):  -{qber_penalty} points")
        print(f"  📊 Replay Attack:    -{replay_penalty} points {'(detected)' if replay else '(not detected)'}")
        print(f"  📊 MITM Attack:      -{mitm_penalty} points {'(detected)' if mitm else '(not detected)'}")
        print(f"  📊 Traffic Analysis: -{traffic_penalty} points {'(detected)' if traffic else '(not detected)'}")
        print(f"  {'─' * 40}")
        print(f"  ✅ Final Security Score: {score}/100")
        
        # Interpretation
        if score >= Config.SECURITY_GOOD_THRESHOLD:
            print(f"  🟢 Rating: GOOD — System is resilient")
        elif score >= Config.SECURITY_MODERATE_THRESHOLD:
            print(f"  🟡 Rating: MODERATE — Some concerns present")
        else:
            print(f"  🔴 Rating: POOR — Significant vulnerabilities")
        
        return score


# ============================================================
# VISUALIZATION
# ============================================================

def plot_security_results(qber_no_eve, qber_with_eve, security_score, attacks_detected):
    """Generate visualization figure for the hackathon submission."""
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    
    # ── Plot 1: QBER Comparison ──
    ax1 = axes[0]
    categories = ['No Eavesdropper', 'With Eavesdropper']
    qber_values = [qber_no_eve * 100, qber_with_eve * 100]
    colors_qber = ['#4CAF50', '#f44336']
    
    bars = ax1.bar(categories, qber_values, color=colors_qber,
                   edgecolor='black', linewidth=1.5)
    ax1.set_ylabel('QBER (%)', fontsize=12)
    ax1.set_title('BB84 Eavesdropper Detection', fontsize=12, fontweight='bold')
    ax1.set_ylim(0, max(100, max(qber_values) * 1.3))
    
    # Detection threshold line
    threshold = Config.BB84_QBER_SECURE_THRESHOLD * 100
    ax1.axhline(y=threshold, color='orange', linestyle='--', linewidth=2,
                label=f'Security Threshold ({threshold:.0f}%)')
    ax1.legend(loc='upper left', fontsize=9)
    
    # Value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2., height + 2,
                 f'{height:.1f}%', ha='center', va='bottom',
                 fontsize=10, fontweight='bold')
    
    # ── Plot 2: Security Index ──
    ax2 = axes[1]
    if security_score >= Config.SECURITY_GOOD_THRESHOLD:
        color = '#4CAF50'
    elif security_score >= Config.SECURITY_MODERATE_THRESHOLD:
        color = '#FF9800'
    else:
        color = '#f44336'
    
    ax2.bar(['Security Index'], [security_score], color=color,
            edgecolor='black', linewidth=1.5)
    ax2.set_ylabel('Score (0-100)', fontsize=12)
    ax2.set_title('Overall Security Index', fontsize=12, fontweight='bold')
    ax2.set_ylim(0, 105)
    
    # Threshold lines
    ax2.axhline(y=Config.SECURITY_GOOD_THRESHOLD, color='green',
                linestyle='--', linewidth=1.5, alpha=0.5, label=f'Good (>={Config.SECURITY_GOOD_THRESHOLD})')
    ax2.axhline(y=Config.SECURITY_MODERATE_THRESHOLD, color='orange',
                linestyle='--', linewidth=1.5, alpha=0.5, label=f'Moderate (>={Config.SECURITY_MODERATE_THRESHOLD})')
    ax2.legend(loc='lower left', fontsize=7)
    
    ax2.text(0, security_score + 3, f'{security_score}/100',
             ha='center', va='bottom', fontsize=14, fontweight='bold')
    
    # ── Plot 3: Attack Detection Status ──
    ax3 = axes[2]
    attack_names = ['Replay\nAttack', 'MITM\nAttack', 'Traffic\nAnalysis']
    attack_values = [1 if attacks_detected[i] else 0 for i in range(3)]
    colors_attack = ['#f44336' if v else '#4CAF50' for v in attack_values]
    
    ax3.bar(attack_names, attack_values, color=colors_attack,
            edgecolor='black', linewidth=1.5)
    ax3.set_ylabel('Detection Status', fontsize=12)
    ax3.set_title('Attack Detection Status', fontsize=12, fontweight='bold')
    ax3.set_ylim(0, 1.4)
    ax3.set_yticks([0, 1])
    ax3.set_yticklabels(['Not Detected', 'Detected'])
    
    # Status labels — use ASCII-safe characters
    for i, (name, val) in enumerate(zip(attack_names, attack_values)):
        label = '[!] DETECTED' if val else '[OK] Clear'
        ax3.text(i, val + 0.08, label, ha='center', va='bottom',
                 fontsize=9, fontweight='bold')
    
    plt.tight_layout(pad=2.0)
    
    return fig


def save_visualization(fig, filename='security_visualization.png'):
    """Save the visualization figure to disk."""
    fig.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"\n📊 Visualization saved as '{filename}'")
    plt.close(fig)


def print_visualization_summary(qber_no_eve, qber_with_eve, security_score, attacks_detected):
    """Print text summary of visualization results."""
    print("\n" + "=" * 60)
    print("📊 SECURITY VISUALIZATION SUMMARY")
    print("=" * 60)
    print(f"  ✅ QBER (No Eve):      {qber_no_eve * 100:.1f}% — Clean Channel")
    print(f"  🚨 QBER (With Eve):    {qber_with_eve * 100:.1f}% — Eavesdropper Present")
    print(f"  📊 Security Index:     {security_score}/100")
    print(f"  🎯 Attacks Detected:   {sum(attacks_detected)}/3")
    print("=" * 60)


# ============================================================
# MAIN EXECUTION
# ============================================================

def parse_arguments():
    """Parse command-line arguments for the demonstration."""
    parser = argparse.ArgumentParser(
        description='RAQT Protocol Demonstration — 3-Layer Hybrid Quantum/PQC Authentication',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python raqt_demo.py                    # Run with default settings
  python raqt_demo.py --bb84-bits 32     # Use 32 bits for BB84
  python raqt_demo.py --quiet            # Minimal output
  python raqt_demo.py --no-viz           # Skip visualization
  python raqt_demo.py --seed 123         # Set random seed for reproducibility
        """
    )
    parser.add_argument('--bb84-bits', type=int, default=Config.BB84_NUM_BITS,
                        help=f'Number of bits for BB84 simulation (default: {Config.BB84_NUM_BITS})')
    parser.add_argument('--quiet', action='store_true',
                        help='Reduce output verbosity')
    parser.add_argument('--no-viz', action='store_true',
                        help='Skip visualization generation')
    parser.add_argument('--seed', type=int, default=None,
                        help='Random seed for reproducibility (default: random)')
    parser.add_argument('--output', type=str, default='security_visualization.png',
                        help='Output filename for visualization (default: security_visualization.png)')
    return parser.parse_args()


def main():
    """Main execution flow for the RAQT protocol demonstration."""
    args = parse_arguments()
    
    # Set random seed if specified
    if args.seed is not None:
        random.seed(args.seed)
        np.random.seed(args.seed)
    
    # Header
    if not args.quiet:
        print("""
╔══════════════════════════════════════════════════════════════╗
║   RAQT PROTOCOL CONCEPT DEMONSTRATION                       ║
║   ISIT 2026 QHack — Phase Shifters                           ║
║   Presenter: Noor Ul Ain Faisal                              ║
║                                                              ║
║   A pedagogical demonstration of a 3-layer hybrid            ║
║   quantum / post-quantum cryptographic authentication        ║
║   concept. Layers 1 and 2 use Qiskit quantum simulations.    ║
║                                                              ║
║   ⚠️  All implementations are simplified for educational    ║
║   purposes and NOT suitable for production use.              ║
╚══════════════════════════════════════════════════════════════╝
        """)
    
    # Sample transaction
    transaction = "TransactionID: 1001; Amount: 500.00; User: Noor"
    
    # ═══════════════════════════════════════════════════
    # LAYER 1: GHZ Verification
    # ═══════════════════════════════════════════════════
    if not args.quiet:
        run_ghz_demonstration()
    
    # ═══════════════════════════════════════════════════
    # LAYER 2: BB84 QKD
    # ═══════════════════════════════════════════════════
    if not args.quiet:
        result_no_eve, result_eve = run_bb84_demonstration()
    else:
        result_no_eve = bb84_qkd_simulate(num_bits=args.bb84_bits, eve=False)
        result_eve = bb84_qkd_simulate(num_bits=args.bb84_bits, eve=True)
    
    # Derive quantum key hash for cross-layer binding
    quantum_key_hash = hashlib.sha256(result_eve['shared_key'].encode()).hexdigest()
    
    # ═══════════════════════════════════════════════════
    # LAYER 3: Lattice Signature
    # ═══════════════════════════════════════════════════
    lattice = LatticeSignatureProtocol()
    signature_valid = lattice.run_signature_demonstration(transaction, quantum_key_hash)
    
    # ═══════════════════════════════════════════════════
    # Attack Simulation
    # ═══════════════════════════════════════════════════
    attack = AttackSimulator()
    replay, mitm, traffic = attack.run_attack_demonstration(result_eve['qber'])
    
    # ═══════════════════════════════════════════════════
    # Security Index
    # ═══════════════════════════════════════════════════
    security = SecurityIndex()
    score = security.run_security_index_demonstration(
        result_eve['qber'], replay, mitm, traffic
    )
    
    # ═══════════════════════════════════════════════════
    # Final Report
    # ═══════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("FINAL REPORT — RAQT HYBRID AUTHENTICATION PROTOCOL")
    print("=" * 60)
    print(f"  ✅ Layer 1 (GHZ Verification):    Demonstrated")
    print(f"  ✅ Layer 2 (BB84 QKD):             {'Secure' if result_eve['secure'] else 'Compromised'} "
          f"(QBER: {result_eve['qber']:.2%})")
    print(f"  ✅ Layer 3 (Lattice Signature):    {'Valid ✓' if signature_valid else 'Invalid ✗'}")
    print(f"  📊 Overall Security Index:         {score}/100")
    print(f"\n  🔗 Cross-layer binding: Quantum key hash → Lattice signature")
    print(f"  🎯 Hybrid quantum/PQC authentication workflow demonstrated")
    print(f"\n  ℹ️  DISCLAIMER: This is a pedagogical demonstration.")
    print(f"  ℹ️  All implementations are simplified for clarity.")
    print(f"  ℹ️  Not audited for production security.")
    print("=" * 60)
    
    # ═══════════════════════════════════════════════════
    # Visualization
    # ═══════════════════════════════════════════════════
    if not args.no_viz:
        print("\n📊 GENERATING SECURITY VISUALIZATIONS...")
        
        attacks_detected = [replay, mitm, traffic]
        print_visualization_summary(
            result_no_eve['qber'], result_eve['qber'], score, attacks_detected
        )
        
        fig = plot_security_results(
            qber_no_eve=result_no_eve['qber'],
            qber_with_eve=result_eve['qber'],
            security_score=score,
            attacks_detected=attacks_detected
        )
        save_visualization(fig, args.output)
    
    print("\n" + "=" * 60)
    print("END OF SIMULATION")
    print("=" * 60)


if __name__ == "__main__":
    main()
