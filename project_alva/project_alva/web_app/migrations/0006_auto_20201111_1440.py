# Generated by Django 3.1.2 on 2020-11-11 13:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web_app', '0005_auto_20201107_2350'),
    ]

    operations = [
        migrations.CreateModel(
            name='District',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
            ],
        ),
        migrations.AlterField(
            model_name='history',
            name='district',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='web_app.district'),
        ),
    ]