from tools.wizards.base.state_model import WizardState, StateFile


def load_wizard_payload() -> dict:
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
        "event_trigger", ""
    )  # Not always included - hence defaults
    event_trigger = answers.get("select_event_trigger", {}).get(
        "item_event_trigger", ""
    )  # Not always included - hence defaults

    meta = state.meta
    event_type = meta.get("event_type", "")
    node_id = str(meta.get("node_id", ""))

    # Construct the payload dictionary
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
            }
        },
        "itemEventId": "ie3-dib",
        "itemId": "63",
        "containerName": "dibDesignerAddEventPhp",
        "triggerType": "click",
        "itemAlias": "buttonCreateEvent",
    }
    return payload
