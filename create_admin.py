from django.contrib.auth import get_user_model

User = get_user_model()

username = "admin"
email = "kouakouboulv@gmail.com"
password = "Admin12345"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    print("✅ Admin créé avec succès")
else:
    print("⚠️ Admin existe déjà")