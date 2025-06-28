"""
Focus: Category creation, listing, retrieval by ID, updating, and deletion, ensuring user ownership.
Key Tests:
test_create_category_success(): Valid data, HTTP 201.
test_create_category_unauthenticated(): HTTP 401.
test_list_categories_empty(): No categories created yet, returns empty list.
test_list_categories_with_data(): Categories exist, returns list.
test_get_category_by_id_success(): Existing category, HTTP 200.
test_get_category_by_id_not_found(): Non-existent ID, HTTP 404.
test_get_category_by_id_not_owned(): Category exists but belongs to another user, HTTP 404/403.
test_update_category_success(): Valid update, HTTP 200.
test_update_category_not_found_or_not_owned(): HTTP 404.
test_delete_category_success(): HTTP 204.
test_delete_category_not_found_or_not_owned(): HTTP 404.
"""