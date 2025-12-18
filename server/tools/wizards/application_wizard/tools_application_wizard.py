from pathlib import Path
from typing import Any

from mcp.types import ToolAnnotations

from mcp_instance import mcp
from tools.wizards.base.steps_manager import StepManager
from tools.wizards.application_wizard.steps.answer_validation_app_wiz import (
    validate_step_answers,
)
from tools.wizards.base.state_model import WizardState, StateFile
from tools.wizards.application_wizard.state.payload_mapping_app_wiz import (
    load_wizard_payload,
    load_wizard_db_table_payloads,
)

from env_variables import get_env
from session_auth import dib_session_client

STEPS_FILE = Path(
    "server/tools/wizards/application_wizard/steps/new_base_wizard_steps.json"
)


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
    state = WizardState.reset(
        meta={"app_name": app_name}, state_file=StateFile.APPLICATION_WIZARD
    )

    first_step = steps.first()
    if not first_step:
        return {
            "status": "error",
            "message": "No wizard steps configured.",
        }

    state.current_step_id = first_step["id"]
    state.save(StateFile.APPLICATION_WIZARD)

    enriched_step = steps.enrich(first_step, wizard_state=state.__dict__)

    return {
        "status": "ok",
        "current_step": enriched_step,
        "meta": state.meta,
    }


def _set_application_values():
    """
    Sets the application-level settings via Dropinbase API. Corresponds to the first two tabs of the GUI wizard.
    """

    url = (
        f"{get_env('BASE_URL', 'https://localhost')}"
        "/peff/Sync/updateAllAppSettings"
        "?containerName=wizBuildAppSettings"
    )

    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "RequestVerificationToken": get_env("REQUEST_VERIFICATION_TOKEN"),
    }

    payload = load_wizard_payload()

    response = dib_session_client.request("POST", url, headers=headers, json=payload)

    try:
        return {"data": response.json()}
    except ValueError:
        return {
            "status_code": response.status_code,
            "response": response.text,
        }


def _set_table_settings():
    """
    Sets the table-level settings via Dropinbase API. Corresponds to the third tab containing the table list.
    """

    tables_settings = load_wizard_db_table_payloads()

    responses = []
    for table_payload in tables_settings:
        table_id = table_payload["recordData"]["id"]

        url = (
            f"{get_env('BASE_URL', 'https://localhost')}"
            "/peff/Crud/update/wizBuildAppGrid"
            f"?primaryKeyData=%7B%22id%22:{table_id}%7D"
        )

        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "RequestVerificationToken": get_env("REQUEST_VERIFICATION_TOKEN"),
        }

        response = dib_session_client.request(
            "POST", url, headers=headers, json=table_payload
        )

        try:
            responses.append({"data": response.json()})
        except ValueError:
            responses.append(
                {
                    "status_code": response.status_code,
                    "response": response.text,
                }
            )

    return responses


def _execute_create_action(db_id: str, template_id: str, base_container_name: str):
    """
    Calls the Dropinbase API to execute the application creation action.
    """
    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "RequestVerificationToken": get_env("REQUEST_VERIFICATION_TOKEN"),
    }

    # Step 1
    url = (
        f"{get_env('BASE_URL', 'https://localhost')}"
        "/peff/Sync/executeTasks"
        f"?containerName=wizBuildApp&queueUid=1765651576"
    )

    payload = {
        "clientData": {
            "alias_self": {
                "id": db_id,
                "tmplId": template_id,
                "baseName": base_container_name,
                "helpIndex": "tmpl",
                "baseContainerOption": "createNew",
                "baseContainerId": None,
            },
            "alias_parent": {},
            "query_params": {},
        },
        "itemEventId": "ie23-dib",
        "itemId": "342",
        "containerName": "wizBuildApp",
        "triggerType": "click",
        "itemAlias": "btnBuildMyApp",
    }

    response1 = dib_session_client.request("POST", url, headers=headers, json=payload)

    # Step 2
    url2 = (
        f"{get_env('BASE_URL', 'https://localhost')}"
        "/peff/Queue/get/wizBuildApp"
        "?queueItemId=1765645516918"
    )

    response2 = dib_session_client.request("POST", url2, headers=headers)

    try:
        return {"data": [response1.json(), response2.json()]}
    except ValueError:
        return {
            "data": [
                {
                    "status_code": response1.status_code,
                    "ok": response1.ok,
                    "response": response1.text,
                },
                {
                    "status_code": response2.status_code,
                    "ok": response2.ok,
                    "response": response2.text,
                },
            ]
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
    state = WizardState.load(StateFile.APPLICATION_WIZARD)

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
        # Call Dropinbase APIs to create the application
        try:
            app_settings_result = _set_application_values()
        except Exception as e:
            raise RuntimeError("Failed to set application values") from e
        try:
            table_settings_result = _set_table_settings()
        except Exception as e:
            raise RuntimeError("Failed to set table settings") from e
        try:
            db_id = state.answers.get("choose_db").get("db_name")
            template_id = state.answers.get("choose_base_container_template").get(
                "base_container_template"
            )
            base_container_name = state.answers.get("set_base_container_name").get(
                "base_container_name"
            )
            create_action_result = _execute_create_action(
                db_id, template_id, base_container_name
            )
        except Exception as e:
            raise RuntimeError("Failed to execute create action") from e

        # Wizard is complete
        state.current_step_id = None
        state.completed = True
        state.save(StateFile.APPLICATION_WIZARD)

        return {
            "summary": {
                "meta": state.meta,
                "answers": state.answers,
                "app_settings_result": app_settings_result,
                "table_settings_result": table_settings_result,
                "create_action_result": create_action_result,
            },
        }

    # Move on to the next step
    state.current_step_id = next_step_cfg["id"]
    state.save(StateFile.APPLICATION_WIZARD)

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
    state = WizardState.load(StateFile.APPLICATION_WIZARD)
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
