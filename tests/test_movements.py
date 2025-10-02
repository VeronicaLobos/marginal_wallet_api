"""
Focus: Movement CRUD, ensuring category ID validity and ownership, activity log creation.
Key Tests:
test_create_movement_success()
test_create_movement_invalid_category_id() (category does not exist)
test_create_movement_category_not_owned()
test_list_movements()
test_get_movement_by_id()
test_update_movement_category_change()
test_create_activity_log_success() (for a specific movement)
test_create_activity_log_duplicate_for_movement()
test_delete_movement_cascades_activity_log()
"""
