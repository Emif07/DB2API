from core.project_manager import ProjectManager

def main():
    manager = ProjectManager()
    manager.run()

    """project_details = get_project_details()
    
    project_name = project_details["project_name"]
    is_new_project = project_details["is_new_project"]

    project_name, is_new_project = prompt_for_project_name()
    project_path = os.path.join("projects", project_name)
    config_path = os.path.join(project_path, "db_config.json")

    if is_new_project:
        logging.info(f"Creating project '{project_name}'...")
        create_project_folder(project_name)
        db_info = get_db_info_from_user()
        if validate_db_connection(db_info):
            save_db_info(project_name, db_info)
        else:
            logging.warning(
                "Failed to connect with the provided database configuration."
            )
    else:
        logging.info(f"Using existing project '{project_name}'...")
        if os.path.exists(config_path):
            logging.info("Loading existing database configuration...")
            db_info = load_db_info(project_name)
            if not validate_db_connection(db_info):
                logging.warning(
                    "Failed to connect with existing database configuration."
                )
                db_info = get_db_info_from_user()
                if validate_db_connection(db_info):
                    save_db_info(project_name, db_info)
        else:
            db_info = get_db_info_from_user()
            if validate_db_connection(db_info):
                save_db_info(project_name, db_info)
            else:
                logging.warning(
                    "Failed to connect with the provided database configuration."
                )

    logging.info("Database configuration is set!")

    # 1 Create database/extensions.py
    create_database_extensions(project_name)

    # 2. Generate model for the table
    generate_model_for_database(db_info,  project_name)

    # 3. Generate controllers, services, repositories
    # Prompt user for table name or if they want to generate for all tables
    user_choice = input(
        "Do you want to generate structure for all tables? (yes/no): "
    ).strip().lower()

    connector = DatabaseConnector(db_info)

    tables_query = (
        "SELECT table_name FROM information_schema.tables WHERE table_schema='public';"
    )
    available_tables = [row[0] for row in connector.execute_query(tables_query)]

    if user_choice in ['y', 'yes']:
        for table_name in available_tables:
            generate_api_structure_for_table(db_info, table_name, project_name)
            logging.info(f"API structure for table '{table_name}' has been successfully generated!")
    else:
        table_name = input(
            "Please enter the name of the table for which you want to generate a structure: "
        ).strip()

        if table_name not in available_tables:
            logging.warning(f"The table '{table_name}' does not exist in the specified database.")
        else:
            # Generate structure for the table
            generate_api_structure_for_table(db_info, table_name, project_name)
            logging.info(f"Structure for table '{table_name}' has been successfully generated!")

    # 4. Create run.py file
    create_run_py(project_name) """

if __name__ == "__main__":
    main()
