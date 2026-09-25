from scripts.provision_local_database import replace_environment_setting


def test_password_rotation_preserves_other_local_settings_and_line_endings():
    original = "APP_ENV=test\r\nPOSTGRES_PASSWORD=old\r\nDB_POOL_SIZE=9\r\n"

    updated = replace_environment_setting(original, "POSTGRES_PASSWORD", "new-secret")

    assert updated == "APP_ENV=test\r\nPOSTGRES_PASSWORD=new-secret\r\nDB_POOL_SIZE=9\r\n"
