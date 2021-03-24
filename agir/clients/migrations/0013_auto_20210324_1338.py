# Generated by Django 3.1.7 on 2021-03-24 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0012_auto_20200701_1622'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='algorithm',
            field=models.CharField(blank=True, choices=[('', 'No OIDC support'), ('RS256', 'RSA with SHA-2 256'), ('HS256', 'HMAC with SHA-2 256')], default='', max_length=5),
        ),
        migrations.AlterField(
            model_name='client',
            name='authorization_grant_type',
            field=models.CharField(choices=[('authorization-code', 'Authorization code'), ('implicit', 'Implicit'), ('password', 'Resource owner password-based'), ('client-credentials', 'Client credentials'), ('openid-hybrid', 'OpenID connect hybrid')], max_length=32),
        ),
    ]
