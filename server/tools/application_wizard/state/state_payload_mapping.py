from tools.application_wizard.state.state_model import WizardState
from tools.application_wizard.steps.option_providers_registration import (
    get_tables_for_selected_db,
)


def load_wizard_payload() -> dict:
    state = WizardState.load()

    answers = state.answers

    # Extract relevant fields from the answers
    grid_design_definition = answers.get("design_definitions_for_forms_and_grids").get(
        "grid_design_definition"
    )
    form_design_definition = answers.get("design_definitions_for_forms_and_grids").get(
        "form_design_definition"
    )

    regex_for_container_names = answers.get("regular_expression_conversions").get(
        "regex_for_container_names"
    )
    regex_for_container_captions = answers.get("regular_expression_conversions").get(
        "regex_for_container_captions"
    )
    regex_for_item_names = answers.get("regular_expression_conversions").get(
        "regex_for_item_names"
    )
    regex_for_field_captions = answers.get("regular_expression_conversions").get(
        "regex_for_field_captions"
    )

    db_id = answers.get("choose_db").get("db_name")

    table_display_on_forms = answers.get("table_display_options_on_forms").get(
        "table_display_on_forms"
    )
    grids_for_all_tables = (
        "1"
        if answers.get("grid_forms_for_all_tables").get("grids_for_all_tables")
        else "0"
    )
    forms_for_all_tables = (
        "1"
        if answers.get("grid_forms_for_all_tables").get("forms_for_all_tables")
        else "0"
    )

    base_container_template = answers.get("choose_base_container_template").get(
        "base_container_template"
    )
    base_container_name = answers.get("set_base_container_name").get(
        "base_container_name"
    )

    # Construct the payload dictionary
    payload = {
        "clientData": {
            "alias_self": {
                "pef_grid_design_id": grid_design_definition,
                "pef_form_design_id": form_design_definition,
                "container_name_replace": regex_for_container_names,
                "container_caption_replace": regex_for_container_captions,
                "field_name_replace": regex_for_item_names,
                "field_caption_replace": regex_for_field_captions,
                "exprField": None,
                "sampleText": None,
                "outputText": None,
                "id": db_id,
                "related_records": table_display_on_forms,
                "create_grid": grids_for_all_tables,
                "create_form": forms_for_all_tables,
                "filter_any_part": "0",
                "audit_create": "detail",
                "audit_update": "detail",
                "audit_delete": "detail",
                "pef_add_port_component_id": None,
                "pef_menu_id": 9979,
            },
            "alias_parent": {
                "id": db_id,
                "tmplId": base_container_template,
                "baseName": base_container_name,
                "helpIndex": "tmpl",
                "baseContainerOption": "createNew",
                "baseContainerId": None,
            },
            "query_params": {},
            "alias_wizBuildApp": {
                "id": db_id,
                "tmplId": base_container_template,
                "baseName": base_container_name,
                "helpIndex": "tmpl",
                "baseContainerOption": "createNew",
                "baseContainerId": None,
            },
            "activeFilter_self": "wizBuildApp_tabSettings",
        },
        "itemEventId": "ie327-dib",
        "itemId": "5981",
        "containerName": "wizBuildAppSettings",
        "triggerType": "click",
        "itemAlias": "btnUpdateAll",
        "activeFilter": "wizBuildApp_tabSettings",
    }

    return payload


def _to_01(v: object) -> int:
    if isinstance(v, bool):
        return 1 if v else 0
    if isinstance(v, int):
        return 1 if v != 0 else 0
    if isinstance(v, str):
        return 1 if v.strip().lower() in {"1", "true", "yes", "on"} else 0
    return 0


def load_wizard_db_table_payloads() -> list[dict]:

    state = WizardState.load()
    answers = state.answers

    # Get the previous (default) table settings
    db_id = answers.get("choose_db").get("db_name")
    old_settings = get_tables_for_selected_db(db_id=db_id)

    # Get the new table settings from the answers
    new_settings = answers.get("configure_tables_for_db").get("table_settings", [])

    # Some defaults
    grids_for_all_tables = (
        "1"
        if answers.get("grid_forms_for_all_tables").get("grids_for_all_tables")
        else "0"
    )
    forms_for_all_tables = (
        "1"
        if answers.get("grid_forms_for_all_tables").get("forms_for_all_tables")
        else "0"
    )

    # Build payloads
    table_payloads = []
    for new_setting in new_settings:
        if not isinstance(new_setting, dict):
            continue

        table_id_raw = new_setting.get("id")
        if table_id_raw is None:
            raise ValueError("Each table_setting must include 'id'")

        table_id = int(table_id_raw)
        old_setting = next((s for s in old_settings if s.get("id") == table_id), {})

        # Fall back to old values if missing in new
        name = new_setting.get("name") or old_setting.get("name")
        caption = new_setting.get("caption", old_setting.get("caption"))
        field_count = new_setting.get("field_count", old_setting.get("field_count", 0))

        create_grid = _to_01(
            new_setting.get(
                "create_grid", old_setting.get("create_grid", grids_for_all_tables)
            )
        )
        create_form = _to_01(
            new_setting.get(
                "create_form", old_setting.get("create_form", forms_for_all_tables)
            )
        )
        ignore = _to_01(new_setting.get("ignore", old_setting.get("ignore", False)))

        if not name:
            raise ValueError(f"Table name missing for table id {table_id}")

        table_payloads.append(
            {
                "recordData": {
                    "id": table_id,
                    "name": name,
                    "caption": caption,
                    "field_count": int(field_count) if field_count is not None else 0,
                    "create_grid": create_grid,
                    "create_form": create_form,
                    "ignore": ignore,
                }
            }
        )

    return table_payloads
