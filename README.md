# AETHER-QKD
# AETHER-QKD

**Adaptive Quantum Key Distribution: A Quantum Immune System**  
*By Aryan Kumar*

---

## Table of Contents

1. [Introduction](#introduction)  
2. [Motivation](#motivation)  
3. [Architecture](#architecture)  
4. [Installation](#installation)  
5. [Usage](#usage)  
6. [Simulation & Results](#simulation--results)  
7. [Mathematical Foundations](#mathematical-foundations)  
8. [Limitations & Scope](#limitations--scope)  
9. [Contributing](#contributing)  
10. [License](#license)  
11. [Acknowledgements](#acknowledgements)  

---

## Introduction

**AETHER-QKD** is a Python-based simulator of an **adaptive quantum key distribution (QKD) system**, inspired by the principles of biological immune systems.  
It aims to explore **resilient and efficient secure communication** in both ideal and hostile environments.

This project is designed for educational and research purposes, to provide a **reproducible framework** for adaptive QKD simulations, and to introduce the broader community to the concept of a “quantum immune system.”

AETHER-QKD is a Python-based simulator of an adaptive quantum key distribution (QKD) system, inspired by the principles of biological immune systems. For an extended article and full explanation of the architecture, see the [AETHER project page](https://www.alwaysask.co.uk/portfolio-2-2/project-one-ephnc-tk2l7).

---

## Motivation

Traditional QKD protocols such as **BB84** or **Decoy-State MDI** rely on static defenses and can be vulnerable to:

- Hardware side-channel attacks (e.g., detector blinding)  
- Source imperfections (e.g., multi-photon pulses)  
- Source-side leakage (information leaking before encoding)  
- Fixed protocols that cannot adapt to new threats  

**AETHER-QKD** addresses these challenges by implementing a **controller-driven, adaptive architecture** capable of switching between:

- **TEAL-E Racer:** High-efficiency engine for clean, low-noise channels  
- **TEAL Fortress:** Resilient protocol for hostile, high-noise channels  

The system is fully simulated, demonstrating improved resilience and throughput while remaining **open, transparent, and reproducible**.

---

## Architecture

The AETHER system is composed of three main components:

1. **AETHER Strategic Controller**  
   - Acts as the “brain” of the system  
   - Runs diagnostic rounds to detect noise and source-side leakage  
   - Chooses which protocol (TEAL-E or TEAL Fortress) to deploy  

2. **TEAL-E Racer**  
   - Entanglement-based, high-efficiency protocol  
   - Ideal for clean channels  
   - Maximizes raw key generation rate while maintaining MDI-level security  

3. **TEAL Fortress**  
   - Block-based, resilient protocol  
   - Employs **Adaptive Braid (v4) Locking Unitaries** to nullify leakage  
   - Engages “Lock” mode when threats are detected  

All components are implemented in Python and designed to **interoperate seamlessly**.

---

## Installation

**Requirements:**

- Python 3.10+  
- NumPy  
- Matplotlib (for plotting results)  

**Install dependencies via pip:**

```bash
pip install numpy matplotlib
```


## Running Baseline Tests

The AETHER-QKD simulator comes with a set of baseline tests to verify performance and compare protocols. To run these tests:

1. Make sure you have Python 3.10+ installed, along with the required dependencies (see [Installation](#installation) above).
2. Navigate to the project root directory.
3. Run the main simulation script:

```bash
python main.py
```
