from typing import Any

from tools.wizards.base.option_provider_base import (
    register_option_provider,
    extract_options_from_response,
)
from env_variables import get_env
from session_auth import dib_session_client


@register_option_provider("get_avail_event_triggers_php")
def get_avail_event_triggers_php(
    *,
    container_id: str,
    context: dict[str, Any] | None = None,
) -> list:

    url = (
        f"{get_env('BASE_URL', 'https://localhost')}"
        "/peff/Crud/componentlist"
        "?containerName=dibDesignerAddEventPhp&containerItemId=3517&itemAlias=containerTrigger&page=1&limit=40&activeFilter=null"
    )

    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "RequestVerificationToken": get_env("REQUEST_VERIFICATION_TOKEN"),
    }

    payload = {
        "clientData": {
            "alias_self": {
                "dropin": None,
                "newDropin": "",
                "class": None,
                "newClass": "",
                "functionName": "",
                "trigger": "",
                "containerTrigger": None,
                "eventType": "item",
                "responseType": "",
                "confirmationMsg": "",
                "objectId": container_id,
            }
        }
    }

    response = dib_session_client.request("POST", url, headers=headers, json=payload)

    options = extract_options_from_response(response=response, topic="event triggers")

    return options


@register_option_provider("get_avail_event_triggers_js")
def get_avail_event_triggers_js(
    *,
    container_id: str,
    context: dict[str, Any] | None = None,
) -> list:

    url = (
        f"{get_env('BASE_URL', 'https://localhost')}"
        "/peff/Crud/componentlist"
        "?containerName=dibDesignerAddEventJs&containerItemId=8334&itemAlias=containerTrigger&page=1&limit=40&activeFilter=null"
    )

    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "RequestVerificationToken": get_env("REQUEST_VERIFICATION_TOKEN"),
    }

    payload = {
        "clientData": {
            "alias_self": {
                "dropin": None,
                "newDropin": "",
                "class": None,
                "newClass": "",
                "trigger": "",
                "eventType": "container",
                "objectId": container_id,
                "containerTrigger": None,
            }
        }
    }

    response = dib_session_client.request("POST", url, headers=headers, json=payload)

    options = extract_options_from_response(response=response, topic="event triggers")

    return options


@register_option_provider("get_existing_dropins_php")
def get_existing_dropins_php(
    *,
    container_id: str,
    context: dict[str, Any] | None = None,
) -> list:

    url = (
        f"{get_env('BASE_URL', 'https://localhost')}"
        "/peff/Crud/componentlist"
        "?containerName=dibDesignerAddEventPhp&containerItemId=56&itemAlias=dropin&page=1&limit=40&activeFilter=null"
    )

    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "RequestVerificationToken": get_env("REQUEST_VERIFICATION_TOKEN"),
    }

    response = dib_session_client.request("POST", url, headers=headers)

    options = extract_options_from_response(response=response, topic="existing dropins")

    return options


@register_option_provider("get_existing_dropins_js")
def get_existing_dropins_js(
    *,
    node_id: str,
    context: dict[str, Any] | None = None,
) -> list:

    url = (
        f"{get_env('BASE_URL', 'https://localhost')}"
        "/peff/Crud/componentlist"
        "?containerName=dibDesignerAddEventJs&containerItemId=3497&itemAlias=dropin&page=1&limit=40&activeFilter=null"
    )

    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "RequestVerificationToken": get_env("REQUEST_VERIFICATION_TOKEN"),
    }

    response = dib_session_client.request("POST", url, headers=headers)

    options = extract_options_from_response(response=response, topic="existing dropins")

    return options


@register_option_provider("get_class_choice_php")
def get_class_choice_php(
    *,
    dropin_choice: str,
    context: dict[str, Any] | None = None,
) -> list:
    if dropin_choice == "existing":
        return [
            {"value": "existing", "label": "Use Existing Class"},
            {"value": "new", "label": "Create New Class"},
        ]
    elif dropin_choice == "new":
        return [
            {
                "value": "new",
                "label": "Create New Class",
                "additional_info": "Since a new dropin folder is being created, a new class must also be created.",
            },
        ]
    else:
        return []


@register_option_provider("get_action_choice_js")
def get_action_choice_js(
    *,
    dropin_choice: str,
    context: dict[str, Any] | None = None,
) -> list:
    if dropin_choice == "existing":
        return [
            {"value": "existing", "label": "Use Existing Action"},
            {"value": "new", "label": "Create New Action"},
        ]
    elif dropin_choice == "new":
        return [
            {
                "value": "new",
                "label": "Create New Action",
                "additional_info": "Since a new dropin folder is being created, a new action must also be created.",
            },
        ]
    else:
        return []


@register_option_provider("get_existing_classes_php")
def get_existing_classes_php(
    *,
    dropin: str,
    node_id: str,
    event_type: str,
    container_trigger: str = "",
    context: dict[str, Any] | None = None,
) -> list:

    url = (
        f"{get_env('BASE_URL', 'https://localhost')}"
        "/peff/Crud/componentlist"
        "?containerName=dibDesignerAddEventPhp&containerItemId=60&itemAlias=class&page=1&limit=40&activeFilter=null"
    )

    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "RequestVerificationToken": get_env("REQUEST_VERIFICATION_TOKEN"),
    }

    payload = {
        "clientData": {
            "alias_self": {
                "dropin": dropin,
                "newDropin": "",
                "class": None,
                "newClass": "",
                "functionName": "",
                "trigger": "",
                "containerTrigger": container_trigger,
                "eventType": event_type,
                "responseType": "",
                "confirmationMsg": "",
                "objectId": node_id,
            }
        }
    }

    response = dib_session_client.request("POST", url, headers=headers, json=payload)

    options = extract_options_from_response(response=response, topic="existing classes")

    return options


@register_option_provider("get_existing_actions_js")
def get_existing_actions_js(
    *,
    dropin: str,
    node_id: str,
    event_type: str,
    container_trigger: str = "",
    context: dict[str, Any] | None = None,
) -> list:

    url = (
        f"{get_env('BASE_URL', 'https://localhost')}"
        "/peff/Crud/componentlist"
        "?containerName=dibDesignerAddEventJs&containerItemId=3500&itemAlias=class&page=1&limit=40&activeFilter=null"
    )

    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "RequestVerificationToken": get_env("REQUEST_VERIFICATION_TOKEN"),
    }

    payload = {
        "clientData": {
            "alias_self": {
                "dropin": dropin,
                "newDropin": "",
                "class": None,
                "newClass": "",
                "trigger": "",
                "eventType": event_type,
                "objectId": node_id,
                "containerTrigger": container_trigger,
            }
        }
    }

    response = dib_session_client.request("POST", url, headers=headers, json=payload)

    options = extract_options_from_response(response=response, topic="existing actions")

    return options


@register_option_provider("get_static_response_types")
def get_response_type(
    *,
    context: dict[str, Any] | None = None,
) -> list:

    return [
        {
            "value": "actions",
            "label": "Actions",
            "description": "Most common. Used for calling client-side actions like set-value, or server-side code that returns a JSON object that may contain messages or actions.\nIf no response is received after 60 seconds, a client exception occurs. Make use of Queues for long-running code.",
        },
        {
            "value": "integer",
            "label": "Integer",
            "description": "(integer) eg 1500. Used with Queues. Instructs the browser to 'poll' the server with requests every 1500 milliseconds for any pending actions, like updating a progress bar or displaying a progress message.\nSubmit Url must contain a call to a server-side controller function that returns actions, and eventually stops the queue.\nNote the queue will terminate itself after 10 requests that do not receive any actions. This is adjustable - see the examples for more info.\nAlso, if a list of actions is sent to the client to execute, any action that is of type 'redirect' will cause the actions following it to not be executed.",
        },
        {
            "value": "redirect",
            "label": "Redirect",
            "description": "Used for calls to the server that must replace the app in the current tab/window with HTML or another site. Can also be used for downloads, but if an error occurs and the file cannot be returned, the whole app will be replaced with an error message.",
        },
        {
            "value": "new-tab",
            "label": "New Tab",
            "description": "Often used for calls to the server that returns a file for downloading since a new tab/browser window opens briefly and then closes when the file is received. Any error message/HTML is displayed in the new tab which circumvents the problem with redirect above.\nIs also used to display HTML in a new tab/browser window.\nNote, the server-side programming should respond with the appropriate HTTP headers, which Dropinbase handles if you use eg. DibFunctions::exportFileToClient() for downloads.",
        },
        {
            "value": "window",
            "label": "Window",
            "description": "Same as new-tab, but content is displayed in popup window instead. Useful for HTML content. The following settings are applied to the window:\nscrollbars=yes, resizable=yes, status=yes, location=no, toolbar=yes, menubar=no, width=900, height=800",
        },
        {
            "value": "basic-window",
            "label": "Basic Window",
            "description": "Same as window, but content is displayed in a more basic popup window with only a close-button. The following settings are applied:\nscrollbars=no, resizable=no, status=no, location=no, toolbar=no, menubar=no, width=600, height=300, left=100, top=100",
        },
    ]
