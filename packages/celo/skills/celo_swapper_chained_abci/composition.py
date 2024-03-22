# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2024 Valory AG
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------

"""This package contains round behaviours of CeloSwapperChainedSkillAbciApp."""

import packages.celo.skills.celo_swapper_abci.rounds as CeloSwapperAbci
import packages.valory.skills.mech_interact_abci.rounds as MechInteractAbci
import packages.valory.skills.mech_interact_abci.states.final_states as MechFinalStates
import packages.valory.skills.mech_interact_abci.states.request as MechRequestStates
import packages.valory.skills.mech_interact_abci.states.response as MechResponseStates
import packages.valory.skills.registration_abci.rounds as RegistrationAbci
import packages.valory.skills.reset_pause_abci.rounds as ResetAndPauseAbci
import packages.valory.skills.transaction_settlement_abci.rounds as TxSettlementAbci
from packages.valory.skills.abstract_round_abci.abci_app_chain import (
    AbciAppTransitionMapping,
    chain,
)
from packages.valory.skills.abstract_round_abci.base import BackgroundAppConfig
from packages.valory.skills.termination_abci.rounds import (
    BackgroundRound,
    Event,
    TerminationAbciApp,
)


# Here we define how the transition between the FSMs should happen
# more information here: https://docs.autonolas.network/fsm_app_introduction/#composition-of-fsm-apps
abci_app_transition_mapping: AbciAppTransitionMapping = {
    RegistrationAbci.FinishedRegistrationRound: CeloSwapperAbci.DecisionMakingRound,
    CeloSwapperAbci.FinishedMechRequestPreparationRound: MechRequestStates.MechRequestRound,
    CeloSwapperAbci.FinishedSwapPreparationRound: TxSettlementAbci.RandomnessTransactionSubmissionRound,
    MechFinalStates.FinishedMechRequestRound: TxSettlementAbci.RandomnessTransactionSubmissionRound,
    CeloSwapperAbci.FinishedDecisionMakingRound: ResetAndPauseAbci.ResetAndPauseRound,
    TxSettlementAbci.FinishedTransactionSubmissionRound: CeloSwapperAbci.PostTxDecisionMakingRound,
    TxSettlementAbci.FailedRound: TxSettlementAbci.RandomnessTransactionSubmissionRound,
    MechFinalStates.FinishedMechResponseRound: CeloSwapperAbci.DecisionMakingRound,
    MechFinalStates.FinishedMechRequestSkipRound: CeloSwapperAbci.DecisionMakingRound,
    MechFinalStates.FinishedMechResponseTimeoutRound: MechResponseStates.MechResponseRound,
    CeloSwapperAbci.FinishedPostTxDecisionMakingRound: MechResponseStates.MechResponseRound,
    ResetAndPauseAbci.FinishedResetAndPauseRound: CeloSwapperAbci.DecisionMakingRound,
    ResetAndPauseAbci.FinishedResetAndPauseErrorRound: ResetAndPauseAbci.ResetAndPauseRound,
}

termination_config = BackgroundAppConfig(
    round_cls=BackgroundRound,
    start_event=Event.TERMINATE,
    abci_app=TerminationAbciApp,
)

CeloSwapperChainedSkillAbciApp = chain(
    (
        RegistrationAbci.AgentRegistrationAbciApp,
        CeloSwapperAbci.CeloSwapperAbciApp,
        TxSettlementAbci.TransactionSubmissionAbciApp,
        MechInteractAbci.MechInteractAbciApp,
        ResetAndPauseAbci.ResetPauseAbciApp,
    ),
    abci_app_transition_mapping,
).add_background_app(termination_config)
