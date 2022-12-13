# Generated by Django 4.1.1 on 2022-11-13 23:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='course',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('department', models.CharField(max_length=30)),
                ('description', models.CharField(max_length=100)),
                ('catalogNumber', models.CharField(default='', max_length=10)),
                ('instructorName', models.CharField(max_length=100)),
                ('instructorEmail', models.EmailField(blank=True, max_length=100)),
                ('semesterCode', models.IntegerField(blank=True)),
                ('courseSection', models.CharField(max_length=30)),
                ('credits', models.CharField(max_length=30)),
                ('lectureType', models.CharField(max_length=30)),
                ('classCapacity', models.IntegerField(default=0)),
                ('classEnrollment', models.IntegerField(default=0)),
                ('classSpotsOpen', models.IntegerField(default=0)),
                ('waitlist', models.IntegerField(default=0)),
                ('waitlistMax', models.IntegerField(default=0)),
                ('meeting_days', models.CharField(default='', max_length=100)),
                ('start_time', models.CharField(default='', max_length=100)),
                ('end_time', models.CharField(default='', max_length=100)),
                ('room_location', models.CharField(default='', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('abbreviation', models.CharField(max_length=10)),
                ('departmentName', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='myUser',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254)),
                ('summary', models.TextField(max_length=500)),
                ('major', models.CharField(max_length=20)),
                ('graduationYear', models.IntegerField()),
                ('numFriends', models.SmallIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='ShoppingCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activeUser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activeUser', to='main.myuser')),
                ('coursesInCart', models.ManyToManyField(blank=True, default='', related_name='coursesInCart', to='main.course')),
            ],
        ),
        migrations.CreateModel(
            name='FriendList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('friends', models.ManyToManyField(blank=True, default='', related_name='friends', to='main.myuser')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user', to='main.myuser')),
            ],
        ),
        migrations.CreateModel(
            name='Friend_Request',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_user', to='main.myuser')),
                ('to_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='to_user', to='main.myuser')),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('commentBody', models.CharField(max_length=200)),
                ('date_published', models.DateTimeField(verbose_name='date published')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='author', to='main.myuser')),
            ],
        ),
        migrations.CreateModel(
            name='ClassSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comments', models.ManyToManyField(blank=True, default='', related_name='comments', to='main.comment')),
                ('coursesInSchedule', models.ManyToManyField(blank=True, default='', related_name='coursesInSchedule', to='main.course')),
                ('scheduleUser', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='scheduleUser', to='main.myuser')),
            ],
        ),
    ]