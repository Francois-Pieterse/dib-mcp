from pathlib import Path
from typing import Any

from mcp.types import ToolAnnotations

from mcp_instance import mcp
from tools.application_wizard.steps.steps_manager import StepManager
from tools.application_wizard.steps.answer_validation import validate_step_answers
from tools.application_wizard.state.state_model import WizardState

STEPS_FILE = Path("server/tools/application_wizard/steps/new_base_wizard_steps.json")


@mcp.tool(
    name="start_application_wizard",
    title="Start Application Creation Wizard",
    description=(
        "Start a guided wizard for creating a new application in Dropinbase. "
        "Always call this first when the user wants to set up a new application from database tables."
    ),
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=False,
    ),
)
def start_application_wizard(app_name: str | None = None) -> dict[str, Any]:
    """
    Initialise the wizard state and return the first step definition,
    including dynamic options.
    """
    steps = StepManager.load(STEPS_FILE)
    state = WizardState.reset(meta={"app_name": app_name})

    first_step = steps.first()
    if not first_step:
        return {
            "status": "error",
            "message": "No wizard steps configured.",
        }

    state.current_step_id = first_step["id"]
    state.save()

    enriched_step = steps.enrich(first_step, wizard_state=state.__dict__)

    return {
        "status": "ok",
        "current_step": enriched_step,
        "meta": state.meta,
    }


@mcp.tool(
    name="step_application_wizard",
    title="Step Application Creation Wizard",
    description=(
        "Submit answers for the current application wizard step and receive the next step. "
        "Use this repeatedly until the wizard reports completion."
    ),
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=False,
    ),
)
def step_application_wizard(
    step_id: str,
    answers: dict[str, Any],
) -> dict[str, Any]:
    """
    Validate the user's answers for the current step, persist them,
    and return the next step (or a completion summary).
    """
    steps = StepManager.load(STEPS_FILE)
    state = WizardState.load()

    current_step_id = state.current_step_id
    if not current_step_id:
        return {
            "status": "error",
            "message": "Wizard has not been started. Call start_application_wizard first.",
        }

    if step_id != current_step_id:
        return {
            "status": "error",
            "message": f"Expected step '{current_step_id}', but got '{step_id}'.",
        }

    step_cfg = steps.get(step_id)
    if not step_cfg:
        return {
            "status": "error",
            "message": f"Unknown step id '{step_id}'.",
        }

    # Enrich with options before validation (for enum validation)
    enriched_step = steps.enrich(step_cfg, wizard_state=state.__dict__)
    errors = validate_step_answers(enriched_step, answers)

    if errors:
        return {
            "status": "validation_error",
            "step": enriched_step,
            "errors": errors,
        }

    # Persist answers
    state.answers[step_id] = answers
    if step_id not in state.completed_step_ids:
        state.completed_step_ids.append(step_id)

    next_step_cfg = steps.next_after(step_id)

    if not next_step_cfg:
        # Wizard is complete – perform final backend call here if needed.
        state.current_step_id = None
        state.completed = True
        state.save()

        # TODO: call your Dropinbase application creation endpoint here,
        # using aggregated answers in state.answers.

        return {
            "status": "completed",
            "summary": {
                "meta": state.meta,
                "answers": state.answers,
            },
        }

    # Move on to the next step
    state.current_step_id = next_step_cfg["id"]
    state.save()

    next_step_enriched = steps.enrich(next_step_cfg, wizard_state=state.__dict__)

    return {
        "status": "ok",
        "current_step": next_step_enriched,
        "meta": state.meta,
    }


@mcp.tool(
    name="get_application_wizard_state",
    title="Get Application Wizard State",
    description=(
        "Retrieve the current state of the application creation wizard, "
        "including the current step and all collected answers so far. "
        "Use this when the user asks about progress or wants to review their inputs."
    ),
    annotations=ToolAnnotations(
        readOnlyHint=True,
        destructiveHint=False,
        idempotentHint=True,
        openWorldHint=False,
    ),
)
def get_application_wizard_state() -> dict[str, Any]:
    """
    Return the raw wizard state and, if there is an active step,
    the enriched definition of that step.
    """
    steps = StepManager.load(STEPS_FILE)
    state = WizardState.load()
    current_step_id = state.current_step_id

    current_step = None
    if current_step_id:
        step_cfg = steps.get(current_step_id)
        if step_cfg:
            current_step = steps.enrich(step_cfg, wizard_state=state.__dict__)

    return {
        "status": "ok",
        "state": {
            "current_step_id": state.current_step_id,
            "completed_step_ids": state.completed_step_ids,
            "answers": state.answers,
            "meta": state.meta,
            "completed": state.completed,
        },
        "current_step": current_step,
    }
