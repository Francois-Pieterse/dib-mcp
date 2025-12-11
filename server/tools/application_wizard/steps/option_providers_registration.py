import re

from typing import Any

from tools.application_wizard.steps.option_provider_base import register_option_provider
from env_variables import get_env
from session_auth import dib_session_client


@register_option_provider("get_avail_databases")
def get_avail_databases(
    *,
    context: dict[str, Any] | None = None,
) -> list:

    url = (
        f"{get_env('BASE_URL', 'https://localhost')}"
        "/peff/Crud/componentlist"
        "?containerName=wizBuildApp&containerItemId=339&itemAlias=id&page=1&limit=40&activeFilter=null"
    )

    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "RequestVerificationToken": get_env("REQUEST_VERIFICATION_TOKEN"),
    }

    payload = {
        "clientData": {
            "alias_self": {
                "id": None,
                "tmplId": None,
                "baseName": "",
                "helpIndex": "",
                "baseContainerOption": "createNew",
                "baseContainerId": None,
            },
            "alias_parent": {},
            "query_params": {},
        }
    }

    response = dib_session_client.request("POST", url, headers=headers, json=payload)

    try:
        data = response.json()

        # Check for success
        if not data.get("success"):
            raise ValueError("Failed to fetch databases: Unsuccessful response")

        records = data.get("records", [])

        if records is None:
            raise ValueError("Failed to fetch databases: No records field found")

    except ValueError:
        raise ValueError("Failed to parse response JSON for databases")

    options = []

    for record in records:
        db_id = record.get("id")
        db_name = record.get("id_display_value")

        if db_id is not None and db_name is not None:
            options.append({"value": str(db_id), "label": db_name})

    return options


@register_option_provider("get_avail_base_container_templates")
def get_avail_base_container_templates(
    *, context: dict[str, Any] | None = None, include_descriptions: bool
) -> list:

    def _get_base_templates() -> list:
        url = (
            f"{get_env('BASE_URL', 'https://localhost')}"
            "/peff/Crud/componentlist"
            "?containerName=wizBuildApp&containerItemId=3039&itemAlias=tmplId&page=1&limit=40&activeFilter=null"
        )

        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "RequestVerificationToken": get_env("REQUEST_VERIFICATION_TOKEN"),
        }

        response = dib_session_client.request("POST", url, headers=headers)

        try:
            data = response.json()

            # Check for success
            if not data.get("success"):
                raise ValueError(
                    "Failed to fetch container templates: Unsuccessful response"
                )

            records = data.get("records", [])

            if records is None:
                raise ValueError(
                    "Failed to fetch container templates: No records field found"
                )

        except ValueError:
            raise ValueError("Failed to parse response JSON for container templates")

        return records

    def _get_template_description(template_id: str) -> str:
        url = (
            f"{get_env('BASE_URL', 'https://localhost')}"
            "/peff/Sync/setBaseDescription?containerName=wizBuildApp"
        )

        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "RequestVerificationToken": get_env("REQUEST_VERIFICATION_TOKEN"),
        }

        payload = {
            "clientData": {
                "alias_self": {
                    "id": None,
                    "tmplId": template_id,
                    "baseName": "",
                    "helpIndex": "tmpl",
                    "baseContainerOption": "createNew",
                    "baseContainerId": None,
                },
                "alias_parent": {},
                "query_params": {},
            },
            "itemEventId": "ie89-dib",
            "itemId": "3039",
            "containerName": "wizBuildApp",
            "triggerType": "changed",
            "itemAlias": "tmplId",
        }

        response = dib_session_client.request(
            "POST", url, headers=headers, json=payload
        )

        try:
            data = response.json()

            # Check for success
            if not data.get("success"):
                raise ValueError(
                    "Failed to fetch container templates: Unsuccessful response"
                )

            actions = data.get("actions")[0]
            templateHelp = actions.get("params").get("helpTmpl")

            if templateHelp is None:
                raise ValueError(
                    "Failed to fetch container templates: No helpTmpl field found"
                )

        except ValueError:
            raise ValueError("Failed to parse response JSON for container templates")

        # Strip html tags if any
        cleanr = re.compile("<.*?>")
        cleantext = re.sub(cleanr, "", templateHelp)

        return cleantext.strip()

    base_template_records: list = _get_base_templates()

    options = []

    for record in base_template_records:
        db_id = record.get("id")
        db_name = record.get("id_display_value")

        option = {"value": str(db_id), "label": db_name}

        if include_descriptions:
            description = _get_template_description(str(db_id))
            option["description"] = description

        options.append(option)

    return options


@register_option_provider("get_avail_form_design_definitions")
def get_avail_form_design_definitions(
    *,
    context: dict[str, Any] | None = None,
    add_static_descriptions: bool = False,
) -> list:

    url = (
        f"{get_env('BASE_URL', 'https://localhost')}"
        "/peff/Crud/componentlist"
        "?containerName=wizBuildAppSettings&containerItemId=367&itemAlias=pef_form_design_id&page=1&limit=40&activeFilter=null"
    )

    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "RequestVerificationToken": get_env("REQUEST_VERIFICATION_TOKEN"),
    }

    response = dib_session_client.request("POST", url, headers=headers)

    try:
        data = response.json()

        # Check for success
        if not data.get("success"):
            raise ValueError(
                "Failed to fetch form design definitions: Unsuccessful response"
            )

        records = data.get("records", [])

        if records is None:
            raise ValueError(
                "Failed to fetch form design definitions: No records field found"
            )

    except ValueError:
        raise ValueError("Failed to parse response JSON for form design definitions")

    options = []

    for record in records:
        fd_id = record.get("id")
        fd_name = record.get("id_display_value")

        option = {"value": str(fd_id), "label": fd_name}

        if add_static_descriptions:
            # Static descriptions based on known form design IDs
            # Last updated: December 2025
            STATIC_DESCRIPTIONS = {
                "Form Equal Fieldsets": (
                    "Fields are divided evenly across a maximum of three fieldsets. "
                    "If the number of fields does not divide equally, the remainder is added to the last fieldset. "
                    "This produces a balanced multi-column layout that adapts to the number of fields. "
                    "Use this option when you want a neatly spaced form layout without manually arranging fields. "
                    "Example: 16 fields / 3 fieldsets = 4 each, remainder 2 fields added to the last fieldset."
                ),
                "Form One Fieldset": (
                    "All fields are placed together in a single fieldset, resulting in a full-width stacked form layout. "
                    "This is useful for simple forms or when you prefer to manually split and rearrange fields later in the Designer "
                    "using the dibSplit modifier."
                ),
                "Form OverFlow Fieldsets": "Description unavailable.",
            }

            option["description"] = STATIC_DESCRIPTIONS.get(
                str(fd_name), "No description available."
            )

        options.append(option)

    return options


@register_option_provider("get_avail_grid_design_definitions")
def get_avail_grid_design_definitions(
    *,
    context: dict[str, Any] | None = None,
    add_static_descriptions: bool = False,
) -> list:

    url = (
        f"{get_env('BASE_URL', 'https://localhost')}"
        "/peff/Crud/componentlist"
        "?containerName=wizBuildAppSettings&containerItemId=366&itemAlias=pef_grid_design_id&page=1&limit=40&activeFilter=wizBuildAppSettings_pef_grid_design_id"
    )

    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "RequestVerificationToken": get_env("REQUEST_VERIFICATION_TOKEN"),
    }

    response = dib_session_client.request("POST", url, headers=headers)

    try:
        data = response.json()

        # Check for success
        if not data.get("success"):
            raise ValueError(
                "Failed to fetch grid design definitions: Unsuccessful response"
            )

        records = data.get("records", [])

        if records is None:
            raise ValueError(
                "Failed to fetch grid design definitions: No records field found"
            )

    except ValueError:
        raise ValueError("Failed to parse response JSON for grid design definitions")

    options = []

    for record in records:
        gd_id = record.get("id")
        gd_name = record.get("id_display_value")

        option = {"value": str(gd_id), "label": gd_name}

        if add_static_descriptions:
            # Static descriptions based on known grid design IDs
            # Last updated: December 2025
            STATIC_DESCRIPTIONS = {
                "Grid Table Basic": (
                    "Standard read-only grid view with paging and a record filter toggle. "
                    "Rows are mainly for browsing; use this layout when users should view many records "
                    "at once and open forms or actions from the grid."
                ),
                "Grid Table Edit": (
                    "Grid rows can be edited one by one. Each row has edit controls so you can change "
                    "values inline while the rest of the grid stays in view. Use this layout when you "
                    "want controlled, row-at-a-time editing."
                ),
                "Grid Table Editable": (
                    "All rows are editable directly in the grid and changes save automatically. "
                    "There are no built-in buttons to open forms, but custom buttons can be added. "
                    "Use this layout for fast bulk updates across many records."
                ),
            }

            option["description"] = STATIC_DESCRIPTIONS.get(
                str(gd_name), "No description available."
            )

        options.append(option)

    return options


@register_option_provider("get_tables_for_selected_db")
def get_tables_for_selected_db(*, context: dict[str, Any] | None = None) -> list:
    wizard_state = (context or {}).get("wizard_state", {})
    answers = wizard_state.get("answers", {})

    db_answer = answers.get("choose_db", {})
    db_id_str = db_answer.get("db_name")
    if not db_id_str:
        raise ValueError("Database must be selected before configuring tables.")

    db_id = int(db_id_str)

    url = (
        f"{get_env('BASE_URL', 'https://localhost')}" "/peff/Crud/read/wizBuildAppGrid"
    )

    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "RequestVerificationToken": get_env("REQUEST_VERIFICATION_TOKEN"),
    }

    payload = {
        "clientData": {
            "alias_self": {},
            "alias_parent": {
                "id": db_id,
            },
            "query_params": {},
            "activeFilter_self": "wizBuildAppGrid",
        },
        "activeFilter": "wizBuildAppGrid",
    }

    response = dib_session_client.request("POST", url, headers=headers, json=payload)

    try:
        data = response.json()

        # Check for success
        if not data.get("success"):
            raise ValueError("Failed to fetch tables for DB: Unsuccessful response")

        records = data.get("records", [])

        if records is None:
            raise ValueError("Failed to fetch tables for DB: No records field found")
    except ValueError:
        raise ValueError("Failed to parse response JSON for tables for DB")

    options: list[dict[str, Any]] = []
    for record in records:
        options.append(
            {
                "id": record["id"],
                "name": record["name"],
                "caption": record.get("caption") or record["name"].title(),
                "field_count": record.get("field_count", 0),
                "create_grid": True,
                "create_form": True,
                "ignore": False,
            }
        )

    return options
