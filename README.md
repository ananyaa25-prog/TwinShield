# TWINSHIELD: Uncertainty-Aware Digital Twin for Safe Network Control

## Overview

**TWINSHIELD** is a research-oriented framework for **predictive, uncertainty-aware, and safety-conscious network management** using a Network Digital Twin.

Modern networks operate under continuously changing traffic conditions. Congestion, resource contention, workload interactions, and failures can cause Service-Level Agreement (SLA) violations. Traditional reactive approaches generally respond after degradation has occurred and may improve one flow while unintentionally harming other flows.

TWINSHIELD addresses this challenge by combining:

* **Network Digital Twin simulation**
* **Multi-flow network telemetry**
* **Machine learning-based outcome prediction**
* **Uncertainty estimation and calibration**
* **Counterfactual what-if evaluation**
* **Risk-aware action selection**
* **Multi-flow safety constraints**
* **Explainable network decisions**

The central idea is:

> **Predict future network behavior, quantify uncertainty, evaluate possible interventions before execution, and select an action only when its predicted impact remains safe for the network as a whole.**

---

## Research Problem

Given a dynamic network state containing multiple interacting flows, TWINSHIELD aims to answer:

> **How can a network anticipate an upcoming SLA violation and choose an intervention that improves the target flow without introducing unacceptable risk to other flows?**

Instead of relying on a purely reactive approach:

```text
Detect → React
```

TWINSHIELD follows:

```text
Observe
   ↓
Predict
   ↓
Quantify Uncertainty
   ↓
Evaluate What-If Outcomes
   ↓
Check Multi-Flow Safety
   ↓
Act / Reject / Abstain
   ↓
Observe Updated State
```

---

# System Architecture

```text
                    Network Environment
                           │
                           ▼
                  Network Telemetry
                           │
                           ▼
              ┌────────────────────────┐
              │    Network Digital     │
              │         Twin           │
              │                        │
              │ Current Network State  │
              └───────────┬────────────┘
                          │
                          ▼
              ┌────────────────────────┐
              │   ML Outcome Predictor │
              │                        │
              │ Delay / Loss / QoS     │
              │ SLA Violation Risk     │
              └───────────┬────────────┘
                          │
                          ▼
              ┌────────────────────────┐
              │ Uncertainty Estimation │
              │    & Calibration       │
              └───────────┬────────────┘
                          │
                          ▼
                 Candidate Actions
                          │
                          ▼
              ┌────────────────────────┐
              │ Counterfactual         │
              │ What-If Evaluation     │
              └───────────┬────────────┘
                          │
                          ▼
              ┌────────────────────────┐
              │ TWINSHIELD Safety       │
              │ Decision Engine        │
              │                        │
              │ Multi-Flow Constraints │
              └───────────┬────────────┘
                          │
                    ┌─────┴─────┐
                    ▼           ▼
                 ACCEPT     REJECT / ABSTAIN
                    │
                    ▼
              Execute Action
                    │
                    ▼
              Network State Update
                    │
                    └──────────────► Digital Twin
```

---

# Core Concept

TWINSHIELD does **not** judge an intervention solely by whether it improves the flow currently experiencing degradation.

For every candidate action, the framework considers:

1. **Target-flow improvement**
2. **Impact on other flows**
3. **Probability of SLA violations**
4. **Uncertainty in predicted outcomes**
5. **Network-level constraints**

Consequently, an action can result in one of three decisions:

| Decision    | Meaning                                                                     |
| ----------- | --------------------------------------------------------------------------- |
| **Accept**  | The action is predicted to satisfy the required safety constraints          |
| **Reject**  | The action is predicted to violate one or more safety constraints           |
| **Abstain** | Prediction uncertainty is too high to make a sufficiently reliable decision |

The **abstention mechanism** is particularly important because uncertainty should not simply be ignored when an automated system is making network-control decisions.

---

# TWINSHIELD Workflow

## 1. Observe

The Digital Twin receives the current network state through simulated or collected telemetry.

Relevant state information includes:

* Network topology
* Link utilization
* Queue occupancy
* Flow rates
* Delay
* Packet loss
* Throughput
* Resource utilization
* Flow priority
* SLA requirements

---

## 2. Predict

Machine learning models estimate future network outcomes from the current state.

The prediction component can estimate:

* Future delay
* Future packet loss
* QoS degradation
* SLA violation probability
* Time-to-SLA violation

Multiple predictive models and baselines are evaluated to determine the effectiveness of the proposed approach.

---

## 3. Quantify Uncertainty

A point prediction alone does not indicate how trustworthy that prediction is.

TWINSHIELD therefore incorporates uncertainty estimation to distinguish between:

```text
Reliable prediction
        vs.
Uncertain prediction
```

Prediction intervals and probabilistic risk estimates are evaluated using appropriate calibration techniques.

The objective is not simply to make predictions, but to determine **when those predictions are reliable enough to support an intervention**.

---

## 4. Generate Candidate Actions

When degradation is predicted, possible interventions are generated.

The initial action space focuses on feasible network interventions such as:

* Alternative-path rerouting
* Traffic redistribution
* Resource adjustment

The framework can be extended with additional control actions as the research progresses.

---

## 5. Perform Counterfactual What-If Evaluation

Before executing an action, TWINSHIELD evaluates its potential consequences inside the Digital Twin.

For example:

```text
Current Network State
        │
        ├── Continue
        │
        ├── Reroute Flow
        │
        └── Other Candidate Action
                 │
                 ▼
          Simulated Future
                 │
                 ▼
          Safety Evaluation
```

This allows the system to investigate:

> **“What is likely to happen if this action is applied?”**

before committing the action to the network.

---

# Multi-Flow Safety

A key principle of TWINSHIELD is that **local improvement should not come at the cost of unacceptable global degradation**.

For a flow \(f\) and candidate action \(a\), a simplified safety constraint can be expressed as:

$$
P(\text{SLA violation}_f \mid a) \leq \epsilon_f
$$

where:

* \(P(\text{SLA violation}_f \mid a)\) is the predicted probability of violating the SLA,
* \(\epsilon_f\) is the maximum acceptable risk for flow \(f\).

Therefore, an intervention that improves the target flow but significantly increases the risk of another flow can be rejected.

---

# Risk-Aware Decision Making

TWINSHIELD combines predicted outcomes, uncertainty, and safety constraints to select an intervention.

Conceptually:

```text
Candidate Actions
       │
       ▼
Predicted Outcomes
       │
       ▼
Uncertainty Estimates
       │
       ▼
Multi-Flow Risk Analysis
       │
       ▼
Safety Constraints
       │
       ├───────────────┐
       ▼               ▼
    ACCEPT        REJECT / ABSTAIN
       │
       ▼
 Execute Action
```

This transforms the problem from:

> **“Which action gives the highest immediate performance?”**

into:

> **“Which action provides useful improvement while remaining within acceptable network-wide risk?”**

---

# Explainable Decisions

TWINSHIELD is designed to provide an explanation alongside the final decision.

For example:

```text
Decision: REJECT

Reason:
Rerouting Flow F3 improves its predicted SLA risk,
but increases Flow F7's risk beyond its permitted threshold.

Binding constraint:
F7 latency SLA

Target-flow risk:
87% → 19%

Affected-flow risk:
12% → 68%

Result:
Action rejected due to collateral risk.
```

This makes the decision process more interpretable and allows researchers to identify **which constraint caused an intervention to be rejected**.

---

# Experimental Evaluation

TWINSHIELD is evaluated against progressively stronger baselines.

## Baselines

1. **Reactive threshold-based control**
2. **Predict-and-act without safety constraints**
3. **Point-estimate constrained decision making**
4. **Uncertainty-aware TWINSHIELD**

---

## Evaluation Metrics

### Prediction Performance

* MAE
* RMSE
* Prediction interval coverage
* Calibration error
* SLA-risk prediction performance

### Network Performance

* SLA violation rate
* Average delay
* Packet loss
* Throughput
* Recovery time

### Safety

* Constraint violation rate
* Unsafe action rate
* Collateral degradation
* Abstention rate

### Decision Quality

* Successful interventions
* Target-flow improvement
* Network-wide improvement
* Risk-adjusted utility

---

# Research Questions

### RQ1 — Predictive Capability

Can a Network Digital Twin combined with machine learning accurately predict future network outcomes before SLA degradation occurs?

### RQ2 — Uncertainty

Does calibrated uncertainty improve the reliability of automated network-control decisions?

### RQ3 — Safety

Can multi-flow risk constraints reduce collateral degradation caused by network interventions?

### RQ4 — Decision Quality

Does TWINSHIELD provide a better balance between network performance and safety compared with reactive and unconstrained approaches?

---

# Technology Stack

| Component          | Technology                        |
| ------------------ | --------------------------------- |
| Network Simulation | ns-3 / Mininet                    |
| Programming        | Python                            |
| Machine Learning   | Scikit-learn / PyTorch            |
| Data Processing    | Pandas / NumPy                    |
| Graph Modeling     | PyTorch Geometric *(if required)* |
| Experimentation    | Python                            |
| Version Control    | Git / GitHub                      |

---

# Repository Structure

```text
TWINSHIELD/
│
├── simulation/          # Network simulation and telemetry
│
├── prediction/          # ML prediction and uncertainty
│
├── actions/             # Candidate network interventions
│
├── twin_evaluator/      # Counterfactual what-if evaluation
│
├── safety/              # Risk-aware decision engine
│
├── explainability/      # Decision explanations
│
├── experiments/         # Baselines and experiments
│
├── configs/             # Experiment configurations
│
├── data/                # Dataset organization
│
├── tests/               # Unit and integration tests
│
├── notebooks/           # Analysis and visualization
│
└── docs/                # Research documentation
```

---

# Research Contribution

TWINSHIELD aims to provide an integrated framework for **prediction-driven and safety-aware network control**.

The core research pipeline is:

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
        ↓
TWINSHIELD
        ↓
Risk-Aware Network Control
```

The framework therefore moves beyond conventional reactive network management by considering **future behavior, uncertainty, intervention consequences, and cross-flow safety simultaneously**.

---

# Reproducibility

The project is designed around reproducible experimentation through:

* Configurable network scenarios
* Automated dataset generation
* Fixed train/validation/test splits
* Reproducible experiment configurations
* Baseline implementations
* Recorded evaluation metrics
* Version-controlled source code

---

# Project Status

🚧 **Research Prototype — Under Development**

Current development focuses on:

* Dynamic multi-flow network simulation
* Digital Twin state representation
* Dataset generation
* ML-based outcome prediction
* Uncertainty estimation
* Counterfactual action evaluation
* Risk-aware multi-flow decision making
* Experimental evaluation

---

# Team

### Tanya Rastogi

**Primary focus:**
ML outcome prediction, uncertainty estimation, and risk-aware modeling.

### Ananya Ambastha

**Primary focus:**
Network simulation, dynamic state evolution, action execution, counterfactual evaluation, and experimental evaluation.

### Joint Research

Both contributors collaborate on:

* Research design
* System integration
* Experimental methodology
* Analysis
* Ablation studies
* Paper writing
* Documentation

---

## Disclaimer

TWINSHIELD is a research prototype intended for experimentation and evaluation of intelligent network-management techniques. It is not intended for direct deployment on production network infrastructure.
