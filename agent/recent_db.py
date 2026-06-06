import shutil

shutil.copy(
    "database/company_backup.db",
    "database/company.db"
)

print("Database reset successfully.")