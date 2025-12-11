from tools.application_wizard.state.state_model import WizardState


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
