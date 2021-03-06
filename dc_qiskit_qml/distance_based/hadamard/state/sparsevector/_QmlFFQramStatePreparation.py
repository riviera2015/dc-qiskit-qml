# -*- coding: utf-8 -*-

# Copyright 2018 Carsten Blank
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from qiskit import QuantumCircuit, QuantumRegister
from qiskit.circuit.measure import measure
from qiskit.extensions import standard
from scipy import sparse
import numpy as np

from dc_qiskit_algorithms.FlipFlopQuantumRam import FFQramDb, add_vector
from ._QmlSparseVectorStatePreparation import QmlSparseVectorStatePreparation


class FFQRAMStateVectorRoutine(QmlSparseVectorStatePreparation):
    def prepare_state(self, qc, state_vector):
        # type: (FFQRAMStateVectorRoutine, QuantumCircuit, sparse.dok_matrix) -> QuantumCircuit
        bus = [reg[i] for reg in qc.qregs for i in range(reg.size)]
        ffqram_reg = QuantumRegister(1, "ffqram_reg")
        branch = [reg for reg in qc.cregs if reg.name == "b"][0]
        branch.size = 2
        qc.add_register(ffqram_reg)

        # Create DB
        db = FFQramDb()
        # TODO: make it take a sparse matrix too!
        add_vector(db, list([np.real(e[0]) for e in state_vector.toarray()]))

        # State Prep
        for r in bus:
            standard.h(qc, r)
        db.add_to_circuit(qc, bus, ffqram_reg[0])

        standard.barrier(qc)
        measure(qc, ffqram_reg[0], branch[1])

        return qc

    def is_classifier_branch(self, branch_value):
        return branch_value == 2
