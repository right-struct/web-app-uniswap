from django.db import migrations


def add_email_constraints(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    alias = schema_editor.connection.alias
    if User.objects.using(alias).filter(email='').exists() or User.objects.using(alias).filter(email__isnull=True).exists():
        raise RuntimeError('Cannot require email: existing users have blank email.')
    with schema_editor.connection.cursor() as cursor:
        cursor.execute('SELECT LOWER(email), COUNT(*) FROM auth_user GROUP BY LOWER(email) HAVING COUNT(*) > 1')
        if cursor.fetchone():
            raise RuntimeError('Cannot add email uniqueness: case-insensitive duplicates exist.')
        if schema_editor.connection.vendor == 'postgresql':
            cursor.execute('ALTER TABLE auth_user ADD CONSTRAINT auth_user_email_required CHECK (email <> \'\')')
            cursor.execute('CREATE UNIQUE INDEX auth_user_email_lower_uniq ON auth_user (LOWER(email))')
        elif schema_editor.connection.vendor == 'sqlite':
            cursor.execute("CREATE UNIQUE INDEX auth_user_email_lower_uniq ON auth_user (LOWER(email))")


def remove_email_constraints(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute('DROP INDEX IF EXISTS auth_user_email_lower_uniq')
        if schema_editor.connection.vendor == 'postgresql':
            cursor.execute('ALTER TABLE auth_user DROP CONSTRAINT IF EXISTS auth_user_email_required')


class Migration(migrations.Migration):
    dependencies = [('main', '0003_item_owner_userprofile'), ('auth', '0012_alter_user_first_name_max_length')]
    operations = [migrations.RunPython(add_email_constraints, remove_email_constraints)]
