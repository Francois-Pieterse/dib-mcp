from pathlib import Path
from typing import Any, Literal

from mcp.types import ToolAnnotations

from mcp_instance import mcp
from tools.wizards.base.steps_manager import StepManager
from tools.wizards.event_wizard.steps.answer_validation_event_wiz import (
    validate_step_answers,
)
from tools.wizards.base.state_model import WizardState, StateFile
from tools.wizards.event_wizard.state.payload_mapping_event_wiz import (
    load_wizard_payload,
)

from tools.designer.tools_designer import get_node_info_from_id_and_type

from env_variables import get_env
from session_auth import dib_session_client


def _get_steps_file(
    event_type: Literal["item", "container"], event_side: Literal["php", "javascript"]
) -> Path:
    """
    Determine the steps file based on event type and side.
    """
    CONTAINER_PHP_STEPS_FILE = Path(
        "server/tools/wizards/event_wizard/steps/container_php_events_wizard_steps.json"
    )
    ITEM_PHP_STEPS_FILE = Path(
        "server/tools/wizards/event_wizard/steps/item_php_events_wizard_steps.json"
    )
    CONTAINER_JS_STEPS_FILE = Path(
        "server/tools/wizards/event_wizard/steps/container_js_events_wizard_steps.json"
    )
    ITEM_JS_STEPS_FILE = Path(
        "server/tools/wizards/event_wizard/steps/item_js_events_wizard_steps.json"
    )

    if event_type == "container" and event_side == "php":
        return CONTAINER_PHP_STEPS_FILE
    elif event_type == "item" and event_side == "php":
        return ITEM_PHP_STEPS_FILE
    elif event_type == "container" and event_side == "javascript":
        return CONTAINER_JS_STEPS_FILE
    elif event_type == "item" and event_side == "javascript":
        return ITEM_JS_STEPS_FILE
    else:
        raise ValueError("Invalid event_type or event_side")


def _check_node_existance(
    node_id: str, event_type: Literal["item", "container"]
) -> bool:
    """
    Check if a node with the given ID exists in Dropinbase.
    """

    node_info = get_node_info_from_id_and_type(node_id, node_type=event_type)

    # Extract relevant information
    try:
        pef_item = node_info.get("data").get("records").get("data").get(f"pef_{event_type}")

        if pef_item is None or pef_item == {} or pef_item == []:
            return False
    except Exception as e:
        return False

    return True


@mcp.tool(
    name="start_event_wizard",
    title="Start Event Creation Wizard",
    description=(
        "Start a guided wizard for creating a new event in Dropinbase. "
        "Always call this first when the user wants to set up a new event for an item or container."
        "An event can be of type 'item' or 'container', which determines the steps presented in the wizard."
        "Furthermore, the event can either be added as a PHP (server-side) or JavaScript (client-side) event."
    ),
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=False,
    ),
)
def start_event_wizard(
    event_type: Literal["item", "container"],
    event_side: Literal["php", "javascript"],
    node_id: str,
) -> dict[str, Any]:
    """
    Initialise the wizard state and return the first step definition,
    including dynamic options.
    """
    # Validate node existence
    if not _check_node_existance(node_id, event_type):
        return {
            "status": "error",
            "message": f"Node with ID '{node_id}' does not exist. Use tool 'get_node_info' to verify or get_project_tree to list available nodes.",
        }

    # TODO: Further validation if node type (item/container) corresponds to node_id if possible?

    steps_file = _get_steps_file(event_type, event_side)
    steps = StepManager.load(steps_file)
    state = WizardState.reset(
        meta={"event_type": event_type, "event_side": event_side, "node_id": node_id},
        state_file=StateFile.EVENT_WIZARD,
    )

    first_step = steps.first()
    if not first_step:
        return {
            "status": "error",
            "message": "No wizard steps configured.",
        }

    state.current_step_id = first_step["id"]
    state.save(StateFile.EVENT_WIZARD)

    enriched_step = steps.enrich(first_step, wizard_state=state.__dict__)

    return {
        "status": "ok",
        "current_step": enriched_step,
        "meta": state.meta,
    }


def _execute_event_creation(wizard_payload: dict[str, Any]) -> str:
    """
    Call Dropinbase APIs to create the event based on the wizard payload.
    """

    url = (
        f"{get_env('BASE_URL', 'https://localhost')}"
        "/dropins/dibAdmin/DDesignerAddOn/createEvent"
        "?containerName=dibDesignerAddEventPhp"
    )

    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "RequestVerificationToken": get_env("REQUEST_VERIFICATION_TOKEN"),
    }

    response = dib_session_client.request(
        "POST", url, headers=headers, json=wizard_payload
    )

    try:
        data = response.json()

        # Check for success
        if not data.get("success"):
            return {
                "success": False,
                "message": data.get("message", "Event creation failed without message"),
            }

        return {
            "success": True,
            "message": data.get("message", "No message provided"),
        }
    except ValueError as e:
        raise RuntimeError("Event creation failed") from e


@mcp.tool(
    name="step_event_wizard",
    title="Step Event Creation Wizard",
    description=(
        "Submit answers for the current event wizard step and receive the next step. "
        "Use this repeatedly until the wizard reports completion."
    ),
    annotations=ToolAnnotations(
        readOnlyHint=False,
        destructiveHint=False,
        idempotentHint=False,
        openWorldHint=False,
    ),
)
def step_event_wizard(
    step_id: str,
    answers: dict[str, Any],
) -> dict[str, Any]:
    """
    Validate the user's answers for the current step, persist them,
    and return the next step (or a completion summary).
    """

    state = WizardState.load(StateFile.EVENT_WIZARD)
    steps_file = _get_steps_file(
        state.meta.get("event_type"), state.meta.get("event_side")
    )
    steps = StepManager.load(steps_file)

    current_step_id = state.current_step_id
    if not current_step_id:
        return {
            "status": "error",
            "message": "Wizard has not been started. Call start_event_wizard first.",
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

    next_step_cfg = steps.next_after(step_id, previous_answers=state.answers)

    if not next_step_cfg:
        # Call Dropinbase APIs to create the event
        try:
            wizard_payload = load_wizard_payload()
        except Exception as e:
            raise RuntimeError(f"Failed to load wizard payload: {e}")
        try:
            creation_results = _execute_event_creation(wizard_payload)
        except Exception as e:
            raise RuntimeError(f"Failed to execute create action: {e}")

        if not creation_results.get("success"):
            return {
                "status": "error",
                "message": f"Event creation failed: {creation_results.get('message')}",
            }

        # Wizard is complete
        state.current_step_id = None
        state.completed = True
        state.save(StateFile.EVENT_WIZARD)

        return {
            "summary": {
                "success" "meta": state.meta,
                "answers": state.answers,
                "message": creation_results.get("message"),
            },
        }

    # Move on to the next step
    state.current_step_id = next_step_cfg["id"]
    state.save(StateFile.EVENT_WIZARD)

    next_step_enriched = steps.enrich(next_step_cfg, wizard_state=state.__dict__)

    return {
        "status": "ok",
        "current_step": next_step_enriched,
        "meta": state.meta,
    }


@mcp.tool(
    name="get_event_wizard_state",
    title="Get Event Wizard State",
    description=(
        "Retrieve the current state of the event creation wizard, "
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
def get_event_wizard_state() -> dict[str, Any]:
    """
    Return the raw wizard state and, if there is an active step,
    the enriched definition of that step.
    """
    state = WizardState.load(StateFile.EVENT_WIZARD)
    steps_file = _get_steps_file(
        state.meta.get("event_type"), state.meta.get("event_side")
    )
    steps = StepManager.load(steps_file)
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
