from django.db import models

# Create your models here.
# https://docs.djangoproject.com/en/4.1/ref/models/fields/
# refrence for different types of fields django


class myUser(models.Model):
    # we are going to ID users by this id as primary key
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.EmailField()
    summary = models.TextField(max_length=500)
    major = models.CharField(max_length=20)
    graduationYear = models.IntegerField()
    schedule = models.CharField(max_length=5, blank=True, default="")

    # followed friends tutorial at https://medium.com/analytics-vidhya/add-friends-with-689a2fa4e41d
    numFriends = models.SmallIntegerField(default=0)

    def __str__(self):
        return self.name
        

class FriendList(models.Model):
    user = models.OneToOneField(myUser, related_name='user', on_delete=models.CASCADE)
    friends = models.ManyToManyField(myUser, default='', blank=True, related_name='friends')

class Friend_Request(models.Model):
    # foreign key allows tables to be easily linked together
    # the related name field basically allows us to specify the instance of each of the models
    # django will do this by default if we do not, but in this case it is useful for us to do
    from_user = models.ForeignKey(myUser, related_name='from_user', on_delete=models.CASCADE)
    to_user = models.ForeignKey(myUser, related_name='to_user', on_delete=models.CASCADE)


class department(models.Model):
    abbreviation = models.CharField(max_length=10)
    departmentName = models.CharField(max_length=30)

    def __str__(self):
        return self.abbreviation


class course(models.Model):
    # MUST BE NAMED ID DO NOT CHANGE
    id = models.IntegerField(primary_key=True)
    # course info CS 1110 Intro to Python
    department = models.CharField(max_length=30)
    description = models.CharField(max_length=100)
    catalogNumber = models.CharField(max_length=10, default="")

    # instructor name and email of who teaches the course
    instructorName = models.CharField(max_length=100)
    instructorEmail = models.EmailField(max_length=100, blank=True)

    # class info about which semester course is taught in, credits, section, and type of class
    semesterCode = models.IntegerField(blank=True)
    courseSection = models.CharField(max_length=30)
    credits = models.CharField(max_length=30)
    lectureType = models.CharField(max_length=30)

    # all numbers related to waitlist and remaining class seats
    classCapacity = models.IntegerField(default=0)
    classEnrollment = models.IntegerField(default=0)
    classSpotsOpen = models.IntegerField(default=0)
    waitlist = models.IntegerField(default=0)
    waitlistMax = models.IntegerField(default=0)

    # meeting information
    meeting_days = models.CharField(max_length=100, default = "")
    start_time = models.CharField(max_length=100, default = "")
    end_time = models.CharField(max_length=100, default = "")
    room_location = models.CharField(max_length=100, default = "")

    # ways to check for time conflicts
    # this calculation is done by translating the time into minutes (say a course starts at 2:30pm
    # the start_time_int would equal 14*60 + 30 = 870)
    start_time_int = models.IntegerField(default=0)

    # we check to make sure the start_time_int of any new courses that are being added to the users
    # schedule do not fall within a range of any start-end_t_int of any courses already in the schedule
    end_time_int = models.IntegerField(default=0)

    def __str__(self):
        dep =  self.department
        num = self.id
        return str(dep) + " " + str(num)


class ShoppingCart(models.Model):
    activeUser = models.ForeignKey(myUser, related_name='activeUser', on_delete=models.CASCADE)
    coursesInCart = models.ManyToManyField(course, default='', blank=True, related_name='coursesInCart')
    message = models.TextField(max_length=200, default="")


class Comment(models.Model):
    author = models.ForeignKey(myUser, related_name='author', on_delete=models.CASCADE)
    toUser = models.ForeignKey(myUser, related_name='toUser', on_delete=models.CASCADE, blank=True, default='')
    commentBody = models.TextField(max_length=200)


class ClassSchedule(models.Model):
    scheduleUser = models.OneToOneField(myUser, related_name='scheduleUser', on_delete=models.CASCADE)
    coursesInSchedule = models.ManyToManyField(course, default='', blank=True, related_name='coursesInSchedule')
    comments = models.ManyToManyField(Comment, default='', blank=True, related_name='comments')