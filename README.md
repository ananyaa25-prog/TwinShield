# TwinShield: Uncertainty-Aware Network Digital Twin for Safe Multi-Flow Network Control

## Overview

**TwinShield** is a research-oriented framework for intelligent and risk-aware network management using a **Network Digital Twin**.

Modern networks are highly dynamic: congestion, changing traffic patterns, resource contention, and failures can cause Service-Level Agreement (SLA) violations. Traditional reactive approaches generally respond after degradation has already occurred and often optimize the affected flow without considering the impact on other flows.

TwinShield addresses this problem by combining:

* **Network Digital Twin simulation**
* **Multi-flow telemetry**
* **Machine learning-based outcome prediction**
* **Uncertainty estimation and calibration**
* **Counterfactual what-if evaluation**
* **Risk-aware action selection**
* **Multi-flow safety constraints**
* **Explainable decisions**

The central objective is:

> **Predict what is likely to happen, quantify how uncertain that prediction is, evaluate possible interventions, and select an action only when it is safe for the network as a whole.**

---

## Research Problem

Given a dynamic network state containing multiple interacting flows, SAFE-Twin aims to answer:

> **Which network action should be taken when a flow is approaching an SLA violation, while ensuring that the intervention does not create unacceptable risk for other flows?**

This requires moving beyond a simple:

```text
Detect → React
```

towards:

```text
Observe → Predict → Quantify Uncertainty → What-If → Check Safety → Act
```

---

## Proposed Architecture

```text
                Real / Simulated Network
                         │
                         ▼
                  Network Telemetry
                         │
                         ▼
              ┌──────────────────────┐
              │   Digital Twin       │
              │  Current Network     │
              │       State          │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Outcome Prediction   │
              │                      │
              │ Delay / Loss / QoS   │
              │ SLA Violation Risk   │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Uncertainty &        │
              │ Calibration          │
              └──────────┬───────────┘
                         │
                         ▼
              Candidate Interventions
                         │
                         ▼
              ┌──────────────────────┐
              │ Counterfactual       │
              │ What-If Evaluation   │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Risk-Aware Decision  │
              │ Engine               │
              │                      │
              │ Multi-flow Safety    │
              │ Constraints          │
              └──────────┬───────────┘
                         │
                    ┌────┴────┐
                    ▼         ▼
                  ACCEPT    REJECT/
                             ABSTAIN
                    │
                    ▼
              Execute Action
                    │
                    ▼
             Network State Update
                    │
                    └──────────► Digital Twin
```

---

## Key Idea

A network intervention should not be considered successful merely because it improves the target flow.

For every candidate action, SAFE-Twin evaluates:

1. **Target-flow improvement**
2. **Impact on other flows**
3. **Probability of SLA violations**
4. **Uncertainty in predicted outcomes**
5. **Network-level safety constraints**

An action may therefore be:

* **Accepted** — predicted to satisfy safety constraints
* **Rejected** — predicted to violate one or more constraints
* **Abstained** — uncertainty is too high to make a reliable decision

This makes the system **risk-aware rather than purely performance-driven**.

---

## Methodology

### 1. Network Digital Twin

A virtual representation of the network is maintained using network simulation and telemetry.

The Digital Twin captures information such as:

* Network topology
* Link utilization
* Queue occupancy
* Flow characteristics
* Delay
* Packet loss
* Throughput
* Resource utilization
* SLA requirements

Dynamic scenarios are generated to represent realistic network conditions including congestion, resource pressure, and changing traffic demands.

---

### 2. Outcome Prediction

Machine learning models learn the relationship between the current network state and future network outcomes.

The prediction component can estimate:

* Future delay
* Future packet loss
* QoS degradation
* SLA violation probability
* Time-to-SLA violation

Multiple prediction approaches are evaluated against simple baselines to determine whether the proposed modeling approach provides meaningful improvements.

---

### 3. Uncertainty Estimation

A prediction without confidence information can be dangerous in a control system.

SAFE-Twin therefore incorporates uncertainty estimation to distinguish between:

```text
High-confidence prediction
        vs.
Highly uncertain prediction
```

Prediction intervals, probabilistic risk estimates, and calibration techniques are used to determine whether the model's confidence is reliable.

---

### 4. Counterfactual What-If Evaluation

Before executing an intervention, SAFE-Twin evaluates possible alternatives inside the Digital Twin.

For example:

```text
Current State
     │
     ├── Continue
     │
     ├── Reroute Flow
     │
     └── Other Candidate Action
              │
              ▼
        Simulated Outcomes
              │
              ▼
       Safety Evaluation
```

This allows the system to estimate the consequences of an action before applying it to the actual network.

---

### 5. Risk-Aware Decision Making

Candidate actions are evaluated using predicted outcomes and their uncertainty.

A simplified safety requirement is:

$$
P(\text{SLA violation}_f \mid a) \leq \epsilon_f
$$

for every relevant flow \(f\).

Therefore, an action that improves one flow but creates excessive risk for another can be rejected.

---

## Experimental Evaluation

SAFE-Twin is evaluated against progressively stronger baselines.

### Baselines

* Reactive threshold-based control
* Predict-and-act without safety constraints
* Point-estimate constrained decision making
* Uncertainty-aware SAFE-Twin

### Evaluation Metrics

#### Prediction

* MAE
* RMSE
* Prediction interval coverage
* Calibration error
* SLA-risk prediction performance

#### Network Performance

* SLA violation rate
* Average delay
* Packet loss
* Throughput
* Recovery time

#### Safety

* Constraint violation rate
* Collateral damage to unaffected flows
* Unsafe action rate
* Abstention rate

#### Decision Quality

* Successful interventions
* Target-flow improvement
* Network-wide improvement
* Risk-adjusted utility

---

## Research Questions

The project investigates the following questions:

### RQ1 — Prediction

Can a Digital Twin combined with machine learning accurately predict future network outcomes before an SLA violation occurs?

### RQ2 — Uncertainty

Does incorporating calibrated uncertainty improve the reliability of network-control decisions?

### RQ3 — Safety

Can risk-aware multi-flow constraints reduce collateral degradation caused by network interventions?

### RQ4 — Decision Making

Does SAFE-Twin achieve a better balance between performance improvement and network-wide safety than reactive and unconstrained approaches?

---

## Technology Stack

| Component          | Technology                        |
| ------------------ | --------------------------------- |
| Network Simulation | ns-3 / Mininet                    |
| Programming        | Python                            |
| Machine Learning   | Scikit-learn / PyTorch            |
| Data Processing    | Pandas / NumPy                    |
| Graph Modeling     | PyTorch Geometric *(if required)* |
| Experimentation    | Python-based experiment pipeline  |
| Version Control    | Git / GitHub                      |

---

## Repository Structure

```text
SAFE-Twin/
│
├── simulation/          # Network simulation and telemetry
├── prediction/          # ML prediction and uncertainty
├── actions/             # Candidate interventions
├── twin_evaluator/      # Counterfactual what-if evaluation
├── safety/              # Risk-aware decision engine
├── explainability/      # Decision explanations
├── experiments/         # Baselines and experiments
├── configs/             # Experiment configurations
├── data/                # Dataset organization
├── tests/               # Unit and integration tests
├── notebooks/           # Analysis and visualization
└── docs/                # Research documentation
```

---

## Expected Contribution

SAFE-Twin aims to contribute a unified framework for **prediction-driven and safety-aware network control**.

The key contribution is the integration of:

```text
Network Digital Twin
        +
ML Outcome Prediction
        +
Uncertainty Estimation
        +
Counterfactual Evaluation
        +
Multi-Flow Safety Constraints
        =
Risk-Aware Network Control
```

Rather than optimizing network performance in isolation, the framework explicitly considers **uncertainty, intervention consequences, and collateral effects across multiple flows**.

---

## Reproducibility

All experiments are designed to be reproducible through:

* Configurable network scenarios
* Automated dataset generation
* Fixed train/validation/test splits
* Reproducible experiment configurations
* Baseline implementations
* Recorded evaluation metrics
* Version-controlled source code

---

## Project Status

🚧 **Research Prototype — Under Development**

Current development focuses on building the Digital Twin, generating dynamic multi-flow network scenarios, developing predictive models, and integrating uncertainty-aware safety-constrained decision making.

---

## Team

**Tanya Rastogi**
Prediction, uncertainty estimation, and risk modeling

**Ananya Ambastha**
Network simulation, dynamic state evolution, action execution, evaluation, and integration

Both contributors collaborate on research design, experimentation, analysis, and documentation.

---

## Disclaimer

SAFE-Twin is a research prototype intended for experimentation and evaluation of intelligent network-management techniques. It is not intended to directly control production network infrastructure.
