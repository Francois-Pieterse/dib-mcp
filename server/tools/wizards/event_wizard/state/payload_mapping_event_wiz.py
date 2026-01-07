from tools.wizards.base.state_model import WizardState, StateFile
from tools.designer.tools_designer import get_node_info_from_id_and_type


def _get_container_id_for_item(item_id: str) -> str:

    node_info = get_node_info_from_id_and_type(item_id, "item")
    if not node_info:
        return ""

    # Container ID path: data -> records -> data -> pef_item -> pef_container_id
    container_id = (
        node_info.get("data", {})
        .get("records", {})
        .get("data", {})
        .get("pef_item", {})
        .get("pef_container_id", "")
    )

    return str(container_id)


def load_php_wizard_payload() -> dict:
    state = WizardState.load(StateFile.EVENT_WIZARD)

    answers = state.answers

    # Extract relevant fields from the answers
    dropin_type = answers.get("select_dropin_or_new_dropin").get("dropin_choice")

    if dropin_type == "existing":
        dropin_choice = answers.get("choose_existing_dropin").get("existing_dropin")
        new_dropin_name = ""
    elif dropin_type == "new":
        dropin_choice = ""
        new_dropin_name = answers.get("create_new_dropin").get("new_dropin_name")
    else:
        dropin_choice = ""
        new_dropin_name = ""

    class_type = answers.get("select_class_or_new_class").get("class_choice")
    if class_type == "existing":
        class_choice = answers.get("choose_existing_class").get("existing_class")
        new_class_name = ""
    elif class_type == "new":
        class_choice = ""
        new_class_name = answers.get("create_new_class").get("new_class_name")
    else:
        class_choice = ""
        new_class_name = ""

    function_name = answers.get("function_name").get("function_name")

    response_type = answers.get("response_type", {}).get("response_type", "actions")
    confirmation_message = answers.get("add_confirmation_message", {}).get(
        "confirmation_message", ""
    )

    container_trigger = answers.get("select_event_trigger", {}).get(
        "event_trigger", None
    )  # Not always included - hence defaults
    event_trigger = answers.get("select_event_trigger", {}).get(
        "item_event_trigger", ""
    )  # Not always included - hence defaults

    meta = state.meta
    event_type = meta.get("event_type", "")
    node_id = str(meta.get("node_id", ""))
    event_side = meta.get("event_side", "")

    # Construct the payload dictionary
    query_params = (
        {
            "dibDesignerAddEventPhp.eventType": event_type,
            "dibDesignerAddEventPhp.objectId": node_id,
        }
        if event_side == "php"
        else {}
    )

    alias_dibDesigner = (
        {
            "containerId": _get_container_id_for_item(node_id),
        }
        if event_type == "item"
        else {}
    )

    payload = {
        "clientData": {
            "alias_self": {
                "dropin": dropin_choice,
                "newDropin": new_dropin_name,
                "class": class_choice,
                "newClass": new_class_name,
                "functionName": function_name,
                "trigger": event_trigger,
                "containerTrigger": container_trigger,
                "eventType": event_type,
                "responseType": response_type,
                "confirmationMsg": confirmation_message,
                "objectId": node_id,
            },
            "query_params": query_params,
            "alias_dibDesigner": alias_dibDesigner,
        },
        "itemEventId": "ie3-dib",
        "itemId": "63",
        "containerName": "dibDesignerAddEventPhp",
        "triggerType": "click",
        "itemAlias": "buttonCreateEvent",
    }
    return payload


def load_js_wizard_payload() -> dict:

    state = WizardState.load(StateFile.EVENT_WIZARD)

    answers = state.answers

    # Extract relevant fields from the answers
    dropin_type = answers.get("select_dropin_or_new_dropin").get("dropin_choice")

    if dropin_type == "existing":
        dropin_choice = answers.get("choose_existing_dropin").get("existing_dropin")
        new_dropin_name = ""
    elif dropin_type == "new":
        dropin_choice = ""
        new_dropin_name = answers.get("create_new_dropin").get("new_dropin_name")
    else:
        dropin_choice = ""
        new_dropin_name = ""

    action_type = answers.get("select_action_or_new_action").get("action_choice")
    if action_type == "existing":
        action_choice = answers.get("choose_existing_action").get("existing_action")
        new_action_name = ""
    elif action_type == "new":
        action_choice = ""
        new_action_name = answers.get("create_new_action").get("new_action_name")
    else:
        action_choice = ""
        new_action_name = ""

    meta = state.meta
    event_type = meta.get("event_type", "")
    node_id = str(meta.get("node_id", ""))
    event_side = meta.get("event_side", "")

    # Construct the payload dictionary
    query_params = (
        {
            "dibDesignerAddEventJs.eventType": event_type,
            "dibDesignerAddEventJs.objectId": node_id,
        }
        if event_side == "javascript"
        else {}
    )

    alias_dibDesigner = (
        {
            "containerId": _get_container_id_for_item(node_id),
        }
        if event_type == "item"
        else {}
    )

    payload = {
        "clientData": {
            "alias_self": {
                "dropin": dropin_choice,
                "newDropin": new_dropin_name,
                "class": action_choice,
                "newClass": new_action_name,
                "trigger": "click",
                "eventType": event_type,
                "objectId": node_id,
                "containerTrigger": None,
            },
            "query_params": query_params,
            "alias_dibDesigner": alias_dibDesigner,
        },
        "itemEventId": "ie120-dib",
        "itemId": "3503",
        "containerName": "dibDesignerAddEventJs",
        "triggerType": "click",
        "itemAlias": "buttonCreateEvent",
    }

    return payload
