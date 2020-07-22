# A Quantum Programming Language in the NISQ era

This document is a summary of the discussion among Yuan Feng, Junjie Wu, Yuxin Deng, Jintao Yu, and Xiang Fu on May 1st in PCL. It tries to clarify the scope of the quantum programming language (QPL) we are developing. Anyone in this project can update this file according to his/her understanding.

## Introduction

This file is used to specify the scope of this language. It can also serve as a center for developers involved to discuss ideas about this language.

## Motivation

The following factors drive us to develop a new quantum programming language (QPL) instead of using or upgrading from an existing one.

### Background

In the NISQ era and in the forseeable future, most of the qubit time is occupied by quantum experiments used to calibrate qubits and quantum operations. Running quantum algorithms is only possible after qubits and operations are well characterized. We have the following observations.

On the one hand, almost all high-level QPLs were born in the computer science/engineering field. They mainly target to provide an efficient description of quantum algorithms with verification support to some extent. Naturally, they abstract away most of the hardware information, which is required to control in quantum experiments. As a consequence, few high-level QPLs can be connected to quantum hardware. It is inconceivable that a QPL can get popular in the future without controlling any hardware.

On the other hand, current quantum experiments are usually controlled with a paradigm different from any existing High-level QPLs. There is ample space to optimize such a paradigm in terms of complexity. We would like to improve the efficiency of quantum experiments by using a new QPL which enables the efficient description of quantum experiments.

### Wishlist

Our QPL can be distinguished from existing QPLs by the following points:
- Our QPL targets to control nowadays quantum experiments. Hence, it requires explicit control over some low-level hardware properties. The properties currently in consideration include 1) flexible definition of quantum operations, and 2) timing of operations. This list can be extended in the future when required;
- An explicit heterogeneous classical-quantum computing architecture (see the next section);
- Individual statements, instead of a data structure representing quantum circuits, should be the basic element for the compiler to process.

## Goal

### Target Users
Target users of our QPL mainly include:
- Quantum experimentalists. They are the ones who control qubits most;
- Quantum algorithm designers;
- Others. In a discussion between Yuan and Xiang, we reached the conclusion that it seems to be difficult for us to make clear who indeed are or are not the target users of our QPL at this moment. So let's open the door.

### Target Applications

To Be Added (TBA).

## The Duty of Our QPL

### Heterogeneous Quantum-Classical Computing

**Core message: a 3-party structure (host classical CPUs, quantum control processor, qubits) is required by heterogeneous quantum-classical computing.**

It is viable to integrate quantum computing in a similar way as a GPU or an FPGA in a heterogeneous architecture. The quantum part can be seen as a coprocessor used to accelerate particular classically hard tasks.

To our understanding, a heterogeneous classical-quantum computing architecture contains three computing parts:
- a powerful classical host, which can be a classical CPU, or a cluster, or even a supercomputer;
- a quantum control processor, which can support a quantum instruction set architecture (QISA), such as eQASM;
- and a quantum core consisting of multiple qubits.

The second part and the third part together form the quantum coprocessor.

The classical host is responsible for complex classical computing as well as loading the quantum task on the quantum coprocessor. The second part is in charge of executing instructions in a QISA. It executes quantum instructions of which the execution result applies quantum operations on qubits, and auxiliary classical instructions to update classical registers and control program flow. The third part is where quantum state evolution happens.

The following figure shows an example microarchitecture (QuMA_v2 supporting eQASM) of the quantum coprocessor.

<img src="docs/figs/quma_v2.png?raw=true" width="1000">

### Heterogeneous Quantum-Classical Programming Model

To enable quantum-classical hybrid computing, we would require a heterogeneous programming and compilation model as shown in the following figure.

<img src="docs/figs/programming_model.png?raw=true" width="500">

We think that a complete quantum program should contain a classical host and a quantum kernel. Let's illustrate the essence of both parts by taking Shor's factoring as an example. Shor's algorithm is described as following by Nielsen and Chuang in _Quantum Computation and Quantum Information_:
- **Inputs**: A composite number $`N`$.
- **Outputs**: A non-trivial factor of $`N`$.
- **Runtime**: $`O((\log N)^3)`$ operations. Succeeds with probability $`O(1)`$.
- **Procedure**:
  1. If $`N`$ is even, return the factor 2.
  2. Use a classical algorithm to determine whether $`N = a^b`$ for integers $`a \ge 1`$ and $`b \ge 2`$, and if so return the factor $`a`$.
  3. Randomly choose $`x`$ in the range 1 to $`N-1`$. If $`gcd(x, N) > 1`$ then return the factor $`gcd(x, N)`$.
  4. Use the order-finding subroutine to find the order $`r`$ of $`x \mod N`$.
  5. if $`r`$ is even and $`x^{r/2}\ne -1(\mod N)`$ then compute $`gcd(x^{r/2}-1, N)`$ and $`gcd(x^{r/2}+1, N)`$, and test to see if one of these is a non-trivial factor, returning that factor if so. Otherwise, the algorithm fails.

Most of this algorithm is classical except the order-finding subroutine (step 4), which is quantum and whose quantum circuit is illustrated in the following figure:

<img src="docs/figs/order_finding.png?raw=true" width="600">

To describe this algorithm, we can describe both the classical and quantum parts using a host program `shor.py` and a quantum kernel `order_finding.qk` as following (python-like pseudo code is used)

``` python
# shor.py
# the host program for shor's factoring

from classical import *


def shor_factoring(N: int):
    if is_even(N):
        return 2

    # single_factor return a if N = a ** b; return 0 else
    if (single_factor(N) != 0):
        return single_factor(N)

    n = bit_length(N)

    while (1):
        a = random(1, N - 1)  # random number between 1 and N - 1
        if (gcd(N, a) > 1):
            return gcd(N, a)

        phi = order_finding(N, a, n)

        r = continued_fractions(phi, n)

        if (is_even(r) and mod(a ** (r/2), N) != -1):
            p = gcd(a**(r/2) + 1, N)
            q = gcd(a**(r/2) - 1, N)
            if test_non_trivial(p, q, N):
                return (p, q)
```

```python
# order_finding.qk
# quantum kernel - order finding
def order_finding(N: int, co_prime: int):
    n = bit_length(N)
    qubit top_qubits[2*n]
    qubit bot_qubits[n]

    H(top_qubits)
    H(bot_qubits[n - 1])

    ModExp(top_qubits, bot_qubits)

    inverse_QFT(top_qubits)

    return Measure(top_qubits)

def ModExp(t_qubits, b_qubits):
    for i in xrange (length(t_qubits)):
        C_Ua(t_qubits[i], b_qubits, 2**i)

def C_Ua(qubit, qubits, power):
    ...
```

The host program  (`shor.py`) is described using a classical programming
language (Python in this example), and the quantum kernel (`order_finding.qk`) is described using a quantum programming language (which we would like to design). A hybrid compilation infrastructure compiles the host program (`shor.py`) into classical code using a conventional compiler such as GCC, which is later executed by the classical
host CPU.

The quantum compiler (which we are to develop) compiles the quantum kernels
in two steps. First, quantum kernels are compiled into QASM, or a similar format mathematically equivalent to the circuit model. This format is hardware independent and can be ported across different platforms for quantum algorithms. Most of the hardware constraints are taken into account in the second step, where the compiler performs scheduling and low-level optimization. The output is the quantum code consisting of QISA instructions. The quantum code contains quantum instructions as well as auxiliary classical instructions to support comprehensive quantum program flow control including runtime feedback.  After the host CPU has loaded the quantum code into the quantum processor, the quantum code can be directly executed.

The detailed steps that we think how the heterogeneous architecture executes the hybrid program is illustrated by the [slides](docs/heterogeneous_programming.pptx).

### Summary
The QPL and compiler we are going to develop correspond to the right side of the programming model. In other words, the QPL only describes the quantum kernel, the compiler only compiles the kernel and generate instructions in a QISA.

## Discussion Points
This section lists all questions that worth a serious discussion while developing the QPL. We can add new questions whenever required.

### Low-level Properties Exposed in QPL
Based on experiments performed in Delft, we found that the QPL should support flexible quantum operation definition and explicit timing of quantum operations.

#### Timing Specification
TBA.

### Language Mode
In the future, the language should focus on the algorithm core and ignore the low-level details. It should be able to support both the experiment mode (with low-level details) and algorithm mode (without low-level details). To achieve this, we can add a compilation flag (such as `#define DESC_MODE = EXPERIMENT`) in the kernel file.
- In the `EXPERIMENT` mode, the programmer is responsible for specifying the timing of quantum operations and the quantum compiler will not further schedule the timing.
- In the `ALGORITHM` mode, the programmer only needs to focus on the logic of the quantum algorithm and can ignore all the hardware-related details. The compiler then takes care of the qubit mapping, scheduling, timing of operations, optimization, and other related low-level details.

### Boundary
What is the boundary between the classical computation performed on the classical host and the quantum control processor?
- Complex computation should be performed on the host, such as floating-point computing;
- The classical computation on the quantum control processor should mainly serve the quantum program flow control and some real-time simple computation.
- **The boundary should be made clear in the following discussion.**

## Timeline Plan

Regardless of the requirement from the quantum cloud platform project, an initial milestone of this language would be _settling down the draft of the QPL **by the end of June**_. Thereafter, the algorithm group can start describing the algorithm library using this language, and we can start the engineering work, i.e., developing the syntax tree (and the parser), IR, etc.