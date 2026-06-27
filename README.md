# Quantum Secure Authentication (QSA) Protocol
### Multi-Layer Identity & Privacy Protection for E-Commerce

A 3-layer hybrid quantum-classical security architecture designed to provide simultaneous identity anonymity and tamper-evident transaction authentication. This project was developed as a solo contribution for the **ISIT 2026 QHack** by team **Phase Shifters**.

---

## 🚀 Protocol Architecture

The QSA framework secures the complete lifecycle of an e-commerce authentication transaction across three interconnected layers:

### 🔹 Layer 3: Message Integrity (Post-Quantum Cryptography)
* **Primitive:** CRYSTALS-Dilithium Scheme (Simulated)
* **Function:** Ensures that the classical transaction payload (e.g., user login request, timestamps, and metadata) cannot be altered, forged, or replayed by an adversary.

### 🔹 Layer 2: Channel Security (Quantum Key Distribution)
* **Primitive:** BB84 QKD Protocol
* **Function:** Establishes a tamper-evident communication channel between the user and the verification node. It actively monitors state error rates against a strict threshold (error rate > 25%) to detect intercept-resend attacks (Eve) and abort insecure transactions instantly.

### 🔹 Layer 1: Privacy & Sender Anonymity (Quantum Networks)
* **Primitive:** RAQT (Quantum Anonymous Transmission) Protocol
* **Function:** Leverages multi-node GHZ entangled states and X-basis measurements to perform anonymous bit transmission. This verifies token validity while physically preventing the network or external observers from tracing the specific identity of the sender.

---

## 📊 Project Roadmap & Implementation

### Phase 1: Algorithmic Verification (Current Status)
* **Framework:** `qiskit` & `qiskit-aer`
* **File:** `bb84_raqt.ipynb`
* **Outcome:** Successfully validated the underlying state logic, quantum gate operations, signature binding mechanics, and error-detection thresholds under simulated network environments.

### Phase 2: Physical Network Stress Testing (Next Steps)
* **Framework:** `NetSquid`
* **Objective:** Migrate the 3-layer stack into a discrete-event network simulator to analyze real-world physical constraints.
* **Metrics:** Investigate how hardware-level imperfections—such as fiber photon loss, channel environmental noise, routing delays, and quantum memory decoherence—impact authentication fidelity and error rates.

---

---

## 🏆 Hackathon Context

**Event:** ISIT 2026 Quantum Hackathon  
**Challenge:** Quantum Secure Authentication Protocols with Privacy Protection  
**Team:** Phase Shifters  
**Presenter:** Noor Ul Ain Faisal (Solo Participant)  
**Objective:** Develop advanced authentication protocols using quantum security primitives like QKD, quantum hashes, or post-quantum signatures.

---
---

## 🤖 AI Usage Disclosure

**Tool Used:** DeepSeek AI and Gemini

**AI Assistance:** Used for code structure evaluations, markdown formatting, and presentation slide text. All quantum protocol design, cryptographic architecture decisions, Qiskit implementation logic, and technical validation were directed and verified by the author.

**Human-Created:** The 3-layer QSA protocol architecture, RAQT protocol integration, BB84 implementation, Dilithium simulation logic, and e-commerce application scenario are original work by the author based on personal study of MIT 8.04 OCW Quantum Physics, IBM Quantum Learning platform, Qiskit Advocate training, and published research.

**Verification:** All code was manually tested on Google Colab. The author can explain every quantum concept and every line of code to a reviewer if asked.

## 👤 Author

**Noor Ul Ain Faisal**  
IBM Qiskit Advocate | Friend of OQI, CERN  
GitHub: learningdungeon (https://github.com/learningdungeon)  
LinkedIn: noorulain-faisal (https://linkedin.com/in/noorulain-faisal)

## 📄 License
This project is licensed under the **MIT License** - see the LICENSE file for details. Open-source implementation is encouraged with appropriate attribution to the author.
