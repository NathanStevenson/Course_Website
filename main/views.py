from tracemalloc import start
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound
from django.views import generic
import datetime
from django.urls import reverse
from .forms import UserForm
from .models import Friend_Request, FriendList, myUser, department, course, ShoppingCart, ClassSchedule, Comment
# this is used for making HTTP requests from an external API with django
import requests


#######################          UTILITY FUNCTIONS       ################


def getFriendRequest(request):
    numFriendRequests = 0
    theUser = ''
    if request.user.id:
        theUser = request.user.id
        activeUser = myUser.objects.get(id=request.user.id)
        friendRequestList = Friend_Request.objects.filter(to_user=activeUser)
        numFriendRequests = len(friendRequestList)
    return numFriendRequests

# turns a list of user courses and parses them into the appropriate day in the schedule
def scheduleFormatter(courses):
    courses = courses.order_by('start_time_int')
    courses = format_times_user(courses)
    meetings = {"Monday":[], "Tuesday":[], "Wednesday":[], "Thursday":[], "Friday":[], "Misc.":[]}
    for course in courses:
        
        days = course['meeting_days']
        if "Mo" in days:
            meetings['Monday'].append(course)
        if "Tu" in days:
            meetings['Tuesday'].append(course)
        if "We" in days:
            meetings['Wednesday'].append(course)
        if "Th" in days:
            meetings['Thursday'].append(course)
        if "Fr" in days:
            meetings['Friday'].append(course)
        if "-" in days:
            meetings["Misc."].append(course)

    return meetings

# turns the list of departments into 8 diff lists organized in an alphabetical manner
def deptFormatter(depts):
    categories = {"A-B":[], "C-D":[], "E-F":[], "G-H":[], "I-L":[], "M-O":[], "P-Q":[], "R-Z":[]}
    for dept in depts:
        if dept.abbreviation[0] in ["A", "B"]:
            categories['A-B'].append(dept)
        if dept.abbreviation[0] in ["C", "D"]:
            categories['C-D'].append(dept)
        if dept.abbreviation[0] in ["E", "F"]:
            categories['E-F'].append(dept)
        if dept.abbreviation[0] in ["G", "H"]:
            categories['G-H'].append(dept)
        if dept.abbreviation[0] in ["I", "J", "K", "L"]:
            categories['I-L'].append(dept)
        if dept.abbreviation[0] in ["M", "N", "O"]:
            categories['M-O'].append(dept)
        if dept.abbreviation[0] in ["P", "Q"]:
            categories['P-Q'].append(dept)
        if dept.abbreviation[0] in ["R", "S", "T", "U", "V", "W", "X", "Y", "Z"]:
            categories['R-Z'].append(dept)
    return categories


#######################        NAVBAR VIEWS           #################


def index(request):
    numFriendRequests = getFriendRequest(request)
    context = {
        'numFriendRequests': numFriendRequests,
    }
    return render(request, 'main/index.html', context)

# view for the course catalog tab has a list of departments that user can click on to choose
def coursecatalog(request):
    numFriendRequests = getFriendRequest(request)
    rawDepartments = department.objects.all() # data is a list of departments {"subject": abbrev}
    departments = deptFormatter(rawDepartments)
    context = {
        'department_results' : departments,
        'numFriendRequests': numFriendRequests,
        # tab tells the HTML what the depict as the active tab
        'tab' : 'coursecatalog',
    }
    return render(request,'main/coursecatalog.html', context)


def format_times(courses):
    startTime = '0000000'
    endTime = '00000000'
    for i in range(len(courses)):
        if courses[i]['meetings'][0]['start_time']:
            raw_startTime = courses[i]['meetings'][0]['start_time']
            if int(raw_startTime[:2].replace(':','')) > 12: 
                raw_startTime = str(int(raw_startTime[:2]) - 12) + raw_startTime[2:5] + " PM"
            elif int(raw_startTime[:2].replace(':','')) == 12: 
                raw_startTime = raw_startTime[:2] + raw_startTime[2:5] + " PM"
            else: 
                raw_startTime = raw_startTime[:2] + raw_startTime[2:5] + " AM"
            startTime = raw_startTime.replace('.',':')
            courses[i]['meetings'][0]['start_time'] = startTime
        else:
            courses[i]['meetings'][0]['start_time'] = ""


        if courses[i]['meetings'][0]['end_time']:
            raw_endTime = courses[i]['meetings'][0]['end_time']
            if int(raw_endTime[:2].replace(':','')) > 12: 
                raw_endTime = str(int(raw_endTime[:2]) - 12) + raw_endTime[2:5] + " PM"
            elif int(raw_endTime[:2].replace(':','')) == 12: 
                raw_endTime = raw_endTime[:2] + raw_endTime[2:5] + " PM"
            else: 
                raw_endTime = raw_endTime[:2] + raw_endTime[2:5] + " AM"
            endTime = raw_endTime.replace('.',':')
            courses[i]['meetings'][0]['end_time'] = endTime
        else:
            courses[i]['meetings'][0]['end_time'] = ""
        if courses[i]['meetings'][0]['facility_description'] == '-':
            courses[i]['meetings'][0]['facility_description'] = "No Set Location"

        if courses[i]['meetings'][0]['days'] == '-':
            courses[i]['meetings'][0]['days'] = "No Set Meeting Days -  "

    return courses

# dynamic routing based on which department the user clicked a list of all classes that belong to that department appear
def deptclasses(request, dept):
    numFriendRequests = getFriendRequest(request)
    credits_amount = 0
    url = 'http://luthers-list.herokuapp.com/api/dept/' + dept + '/'
    response = requests.get(url)
    courses = response.json()
    coursesNoDup = { each['catalog_number'] : each for each in courses }.values()

    courses = format_times(courses)


    # displaying to the user what items are in their shopping cart
    has_class = ShoppingCart.objects.filter(activeUser=request.user.id).first()
    classesInCart = []
    if has_class:
        classesInCart = has_class.coursesInCart.all()

    shoppingCartMessage = ""
    if request.user.id:
        cartActiveUser, created = ShoppingCart.objects.get_or_create(activeUser=request.user.id)
        shoppingCartMessage = ShoppingCart.objects.get(activeUser=request.user.id).message
        has_class.message = ""
        has_class.save()
        # Credit System
    for classes in classesInCart:
        credits_amount = credits_amount + float(classes.credits)
    
    classesInCart = format_times_user(classesInCart)
    context = {
        'course_list': courses,
        'course_list_nodup':coursesNoDup,
        'classesInCart':classesInCart,
        'creditAmount': credits_amount,
        'shoppingCartMessage':shoppingCartMessage,
        'numFriendRequests': numFriendRequests,

    }
    return render(request, 'main/classesList.html', context)

# class search dummy implementation for now
def searchclass(request):
    numFriendRequests = getFriendRequest(request)

    departments = department.objects.all() # data is a list of departments {"subject": abbrev}
    noDep = True
    Instructors = []
    courses = []
    filteredClass = []
    filteredNoDup = []
    credits_amount = 0
    # These will check for what the user inputed
    fi = False
    fct = False
    fc = False
    # sending important data to the front end for select boxes and to filter out stuff
    instructorChosen = ''
    classTypeChosen = ''
    creditsChosen = ''
    input = request.GET.get('depSelect', None)
    # displaying to the user what items are in their shopping cart
    has_class = ShoppingCart.objects.filter(activeUser=request.user.id).first()
    classesInCart = []
    if has_class:
        classesInCart = has_class.coursesInCart.all()

    # message after adding the course to the shopping cart or removing one
    shoppingCartMessage = ""
    if request.user.id and has_class:
        shoppingCartMessage = ShoppingCart.objects.get(activeUser=request.user.id).message
        has_class.message = ""
        has_class.save()

    if input:
        noDep = False
        # update the shoppingCartMessage to clear it
        shoppingCartMessage = ""
        url = 'http://luthers-list.herokuapp.com/api/dept/' + input + '/'
        response = requests.get(url)
        courses = response.json()
        filteredInstructor = request.GET.get('instructor', "none")
        if (filteredInstructor != "none"):
            fi = True
            instructorChosen = filteredInstructor

        filteredClassType = request.GET.get('classType', "none")
        if (filteredClassType != "none"):
            fct = True
            classTypeChosen = filteredClassType

        filteredCredits = request.GET.get('credits', "none")
        if (filteredCredits != "none"):
            fc = True
            creditsChosen = filteredCredits

        for course in courses:
            # preventing duplicate professors
            if (course['instructor']['name'] not in Instructors):
                Instructors.append(course['instructor']['name'])
            # Checking for various combination of input that the user can enter -- some are less practical such as searching by credits but it is included nonetheless
            if (fi and fct and fc):
                if ((course['instructor']['name'] == filteredInstructor) and (course['component'] == filteredClassType)
                and (course['units'] == filteredCredits)) :
                    filteredClass.append(course)
            elif (fi and fct):
                if ((course['instructor']['name'] == filteredInstructor) and (course['component'] == filteredClassType)) :
                    filteredClass.append(course)

            elif (fi and fc):
                if ((course['instructor']['name'] == filteredInstructor) and (course['units'] == filteredCredits)) :
                    filteredClass.append(course)


            elif (fct and fc):
                if ((course['component'] == filteredClassType) and (course['units'] == filteredCredits)) :
                    filteredClass.append(course)


            elif (fi):
                if ((course['instructor']['name'] == filteredInstructor)):
                    filteredClass.append(course)

            elif (fct):
                if ((course['component'] == filteredClassType)):
                    filteredClass.append(course)


            elif (fc):
                if ((course['units'] == filteredCredits)):
                    filteredClass.append(course)
            else:
                filteredClass.append(course)
        # sort all the instructors alphabetically so it is easier to find them
        Instructors.sort()
        # ensure no duplicate filtered classes
        filteredNoDup = { each['catalog_number'] : each for each in filteredClass }.values()
        # Credit System

    for classes in classesInCart:
        credits_amount = credits_amount + float(classes.credits)

    filteredClass = format_times(filteredClass)
    classesInCart = format_times_user(classesInCart)
    context = {
        'department_results' : departments,
        'instructors': Instructors,
        'noDepartment': noDep,
        'course_list': filteredClass,
        'course_list_nodup': filteredNoDup,
        'department': input,
        # passing extra data to help us filter stuff
        'instructorChosen': instructorChosen,
        'classTypeChosen':classTypeChosen,
        'creditAmount': credits_amount,
        'creditsChosen': creditsChosen,
        'classesInCart':classesInCart,
        'shoppingCartMessage':shoppingCartMessage,
        'numFriendRequests': numFriendRequests,

        # tab tells the HTML what the depict as the active tab
        'tab' : 'coursecatalog',
    }
    return render(request,'main/searchclass.html', context)


#######################         SCHEDULE VIEWS           ##################

def format_times_user(courses):
    startTime = '0000000'
    endTime = '00000000'
    courses = list(courses)
    retList = []
    for course in courses:
        course = course.__dict__
        if course['start_time']:
            raw_startTime = course['start_time']
            if int(raw_startTime[:2].replace(':','')) > 12: 
                raw_startTime = str(int(raw_startTime[:2]) - 12) + raw_startTime[2:5] + " PM"
            elif int(raw_startTime[:2].replace(':','')) == 12: 
                raw_startTime = raw_startTime[:2] + raw_startTime[2:5] + " PM"
            else: 
                raw_startTime = raw_startTime[:2] + raw_startTime[2:5] + " AM"
            startTime = raw_startTime.replace('.',':')
            course['start_time'] = startTime
        else:
            course['start_time'] = ""


        if course['end_time'] :
            raw_endTime = course['end_time']
            if int(raw_endTime[:2].replace(':','')) > 12: 
                raw_endTime = str(int(raw_endTime[:2]) - 12) + raw_endTime[2:5] + " PM"
            elif int(raw_endTime[:2].replace(':','')) == 12: 
                raw_endTime = raw_endTime[:2] + raw_endTime[2:5] + " PM"
            else: 
                raw_endTime = raw_endTime[:2] + raw_endTime[2:5] + " AM"
            endTime = raw_endTime.replace('.',':')
            course['end_time'] = endTime
        else:
            course['end_time'] = ""
        if course['room_location'] == '-':
            course['room_location'] = "No Set Location"

        if course['meeting_days'] == '-':
            course['meeting_days'] = "No Set Meeting Days -  "
        retList.append(course)
    return retList

# View for seeing your personal schedule and adding and subtracting course from it
def myschedule(request):
    numFriendRequests = getFriendRequest(request)
    credits_amount = 0
    schedule_credits = 0
    has_comment = False
    all_comments = []
    # generating the comments for each user's schedule
    if request.user.id:
        has_comment = Comment.objects.filter(toUser=request.user.id).first()
        all_comments = []
        if has_comment:
            all_comments = Comment.objects.filter(toUser=request.user.id)

    # begin by assuming user is logged in, if not, variable is used in html to print appropriate message
    no_user = False
    courses = []
    classesInCart= []
    coursesScheduled = []
    shoppingCartMessage = ""
    try:
        activeUser = myUser.objects.get(id=request.user.id)

        scheduleActiveUser, created = ClassSchedule.objects.get_or_create(scheduleUser=activeUser)
        cartActiveUser, created = ShoppingCart.objects.get_or_create(activeUser=activeUser)

        courses = scheduleFormatter(scheduleActiveUser.coursesInSchedule.all())

        classesInCart = cartActiveUser.coursesInCart.all()
        
        coursesScheduled = scheduleActiveUser.coursesInSchedule.all()

        if request.user.id:
            shoppingCartMessage = ShoppingCart.objects.get(activeUser=request.user.id).message
    except:
        no_user = True
    f_classesInCart = format_times_user(classesInCart)

    # Credit System -- cart
    for classes in classesInCart:
        if len(classes.credits) == 1:
            credits_amount = credits_amount + int(classes.credits)
    # Credit System -- in schedule
    for scheduledClasses in coursesScheduled:
        if len(scheduledClasses.credits) == 1:
            schedule_credits = schedule_credits + int(scheduledClasses.credits)

    context = {
        'schedule_courses' : courses,
        'classesInCart' : f_classesInCart,
        'creditAmount': credits_amount,
        'scheduledCredits': schedule_credits,
        'logged_in' : no_user,
        'shoppingCartMessage': shoppingCartMessage,
        'hasComment': has_comment,
        'allComments': all_comments,
        'numFriendRequests': numFriendRequests,
    }
    return render(request,'main/myschedule.html', context)


# view for viewing and commenting on other users schedules
def viewschedule(request, user_id):
    numFriendRequests = getFriendRequest(request)
    activeUser_comments = []
    shoppingCartMessage = ""

    if request.user.id:
        shoppingCartMessage = ShoppingCart.objects.get(activeUser=request.user.id).message

    # profile of the individual the user is looking at
    friend = myUser.objects.get(id=user_id)
    activeUser = myUser.objects.get(id=request.user.id)
    friendSchedule, created = ClassSchedule.objects.get_or_create(scheduleUser=friend)
    friendCourses = scheduleFormatter(friendSchedule.coursesInSchedule.all())

    try:
        currentUser = myUser.objects.get(id = request.user.id)
        userCart, cartCreated = ShoppingCart.objects.get_or_create(activeUser=currentUser)
        classesInCart = userCart.coursesInCart.all()
    except:
        classesInCart = []

    # Code for seeing other users comments / allowing users to leave their own comments on their friends schedule
    # grabbing the new comment that the current user has posted
    input = request.GET.get('commentbody', None)
    if input:
        newComment, commentCreated = Comment.objects.get_or_create(author=activeUser, toUser=friend, commentBody=input)
        # do not allow duplicate comments to be posted by the same user
        if commentCreated:
            newComment.save()

    # seeing if the user has any comments on their schedule yet
    has_comment = Comment.objects.filter(toUser=user_id).first()
    all_comments = []
    if has_comment:
        all_comments = Comment.objects.filter(toUser=user_id)
        activeUser_comments = Comment.objects.filter(author=activeUser)
    context = {
        'schedule_courses' : friendCourses,
        # profile of the individual you are looking at
        'theUser': friend,
        'classesInCart' : classesInCart,
        'hasComment': has_comment,
        'allComments': all_comments,
        'numFriendRequests': numFriendRequests,
        'activeUser_comments': activeUser_comments,
        'shoppingCartMessage': shoppingCartMessage,
    }

    return render(request, 'main/friendsschedule.html', context)

# view for allowing owner of the schedule to delete other users comments from it
def deletecomment(request, comment_id):
    theComment = Comment.objects.get(id=comment_id)
    theComment.delete()
    return HttpResponseRedirect(reverse('main:myschedule'))

def deleteowncomment(request, comment_id, friend_id):
    theComment = Comment.objects.get(id=comment_id)
    theComment.delete()
    return HttpResponseRedirect(reverse('main:viewschedule', args=(friend_id,)))

#######################          PROFILE VIEWS               ################


# profile view which allows the user to see their profile info they entered at login as well as edit it
# only time they can hit this link is when they have already logged in WILL HAVE AN ID
def profile(request, user_id):
    numFriendRequests = getFriendRequest(request)

    # profile of the individual the user is looking at
    theUser = myUser.objects.get(id=user_id)

    # boolean value that determines whether or not the users are friends by default is False
    isFriend = False
    # get a list of all the friends of the user currently using the website
    has_friend = FriendList.objects.filter(user=request.user.id).first()
    allFriends = []
    if has_friend:
        allFriends = has_friend.friends.all()
        if theUser in allFriends:
            isFriend = True

    # only able to send a Friend Request to people who you are not already friends with therefore
    # a friendRequest can either be already sent and you will get a message telling you that
    # or it will be created and sent for the first time and the message will alert you of that
    messageSent = ''
    if request.method == 'POST':
        from_user = myUser.objects.get(id=request.user.id)
        to_user = theUser
        friend_request, created = Friend_Request.objects.get_or_create(from_user=from_user, to_user=to_user)

        # if the friend request was created for the first time alerts the user that it was sent
        if created:
            messageSent = 'Friend Request was sent!'
        else:
            messageSent = 'Friend Request has already been sent!'

    # theUser passes along ifno about the user profile we are looking at, message sent is just
    # alerting the user to assure them their request was sent
    # isFriend is a boolean value (can only see a user's email and schedule if you are friends with
    # them and you cannot send someone a FriendRequest if you are already friend with them)
    context = {
        'theUser' : theUser,
        'messageSent' : messageSent,
        'isFriend': isFriend,
        'numFriendRequests': numFriendRequests,
    }
    return render(request, 'main/profile.html', context)


# allows the user to edit his profile (the button to get here can only be viewed on the HTML
# profile where the user is looking at his own profile)
def edit(request):
    activeUser = myUser.objects.get(id=request.user.id)
    form = UserForm(instance=activeUser)
    context={'form':form}
    if request.POST:
        # form but we have some of the info filled out
        form = UserForm(request.POST, instance=activeUser)
        if form.is_valid():
            form.save()
            # reverse looks through all URLs defined in project and returns the one specified
            # this is what we want so we have no hardcoded URLS
            # comma is needed in order for it not to be an iterable very weird
            return HttpResponseRedirect(reverse('main:profile', args=(request.user.id,)))
    return render(request, 'main/editprofileloggedin.html', context)

# when the user signs in for the first time they will fill out our custom form
def editprofile(request):
    if(request.user.is_authenticated):
        try:
            newUser = myUser.objects.get(id=request.user.id)
            return HttpResponseRedirect(reverse('main:index'))
        # if the user has not logged in yet then create a new user
        except:
            # users have id, name, email, summary, major, graduationYear
                newUser = myUser(id=request.user.id, name=str(request.user.first_name + " " + request.user.last_name), summary='', major='', graduationYear="")

                # beauty of this is our users will have the same ID as the socialaccount -> request.user
                form = UserForm()
                context = {
                    'form': form,
                }
                if request.POST:
                    # form but we have some of the info filled out
                    form = UserForm(request.POST, instance=newUser)
                    if form.is_valid():
                        form.save()
                        cartActiveUser, created = ShoppingCart.objects.get_or_create(activeUser=newUser)
                        # reverse looks through all URLs defined in project and returns the one specified
                        # this is what we want so we have no hardcoded URLS
                        return HttpResponseRedirect(reverse('main:index'))
                return render(request, 'main/editprofile.html', context)
    else:
        return HttpResponseNotFound('<h1>Page not found</h1>')



#######################   FRIENDS VIEWS AND LOGIC     ######################



# this displays all of the active friend requests and allows users to accept or delete them
def friendrequests(request):
    numFriendRequests = getFriendRequest(request)

    friend_requests = Friend_Request.objects.filter(to_user_id=request.user.id)
    context = {
        'friend_requests': friend_requests,
        'numFriendRequests': numFriendRequests,
    }
    return render(request, 'main/friendrequests.html', context)

# this is the link that is hit if the user decides to delete the friend request
def deleterequest(request, fromUserID):
    # activeUser is the person who is checking their friend requests
    activeUser = myUser.objects.get(id=request.user.id)
    # from user is the person who sent the friend request
    fromUser = myUser.objects.get(id=fromUserID)
    # go and get the specific friend request since we know it exists and then delete it
    friendRequest = Friend_Request.objects.get(from_user=fromUser, to_user=activeUser)
    friendRequest.delete()
    # return to the same page where hopefully that friend request has been deleted
    return HttpResponseRedirect(reverse('main:friendrequests'))


def acceptrequest(request, fromUserID):
    # activeUser is the person who is checking their friend requests
    activeUser = myUser.objects.get(id=request.user.id)
    # from user is the person who sent the friend request
    fromUser = myUser.objects.get(id=fromUserID)
    # go and get the specific friend request since we know it exists and then delete it
    friendRequest = Friend_Request.objects.get(from_user=fromUser, to_user=activeUser)

    # see whether or not each user has an exisiting friends list or if one needs to be made
    friendListActiveUser, createdActive = FriendList.objects.get_or_create(user=activeUser)
    friendListFromUser, createdFrom = FriendList.objects.get_or_create(user=fromUser)

    # add the fromUser to the activeUsers friends list AND VICE VERSA
    friendListActiveUser.friends.add(fromUser)
    friendListFromUser.friends.add(activeUser)
    # increment the number of friends each user has
    fromUser.numFriends = fromUser.numFriends + 1
    activeUser.numFriends = activeUser.numFriends + 1
    fromUser.save()
    activeUser.save()

    # delete the friend request since it has been processed
    friendRequest.delete()
    return HttpResponseRedirect(reverse('main:friendrequests'))

def removefriend(request, user_id):
     # activeUser is the person who is checking their friend requests
    activeUser = myUser.objects.get(id=request.user.id)
    # friend is the person who you are removing from your friends list
    friend = myUser.objects.get(id=user_id)

    # see whether or not each user has an exisiting friends list or if one needs to be made
    friendListActiveUser, createdActive = FriendList.objects.get_or_create(user=activeUser)
    friendListFromUser, createdFrom = FriendList.objects.get_or_create(user=friend)

    # add the fromUser to the activeUsers friends list AND VICE VERSA
    friendListActiveUser.friends.remove(friend)
    friendListFromUser.friends.remove(activeUser)
    # increment the number of friends each user has
    friend.numFriends = friend.numFriends - 1
    activeUser.numFriends = activeUser.numFriends - 1
    friend.save()
    activeUser.save()
    return HttpResponseRedirect(reverse('main:friends', args=(request.user.id,)))


def friends(request, user_id):
    numFriendRequests = getFriendRequest(request)

    theUser = myUser.objects.get(id=user_id)
    # we are basically checking whether or not the user has friends since you cannot call .all()
    # on a "None". Essentially trying to find all on a null object does not work
    has_friend = FriendList.objects.filter(user=theUser).first()
    allFriends = []
    if has_friend:
        allFriends = has_friend.friends.all()
    # passing all the friends that a user has into context so they can go to the front end
    context = {
        'allFriends': allFriends,
        'theUser' : theUser,
        'numFriendRequests': numFriendRequests,
    }

    return render(request, 'main/friends.html', context)


# allows the user to search for other users on the app by name (corresponds to addfriend/ path)
def addfriend(request):
    numFriendRequests = getFriendRequest(request)

    # do not allow users to find ppl they are already friends with on this page
    has_friend = FriendList.objects.filter(user=request.user.id).first()
    allFriends = []
    if has_friend:
        allFriends = has_friend.friends.all()

    # list of all the Users on the site so far (only show the top ten results on front end)
    # exlcudes the user himself as well as all people he is already friends with
    shownUsers = myUser.objects.all().exclude(id=request.user.id).exclude(id__in=allFriends)
    # the user input provided to search for their friends
    input = request.GET.get('friendsearch', None)
    if input:
        # filter on a specific item inside the model then __ some form of filtering in python
        shownUsers = myUser.objects.filter(name__icontains=input).exclude(id=request.user.id).exclude(id__in=allFriends)
    context = {
        'shownUsers' : shownUsers,
        'numFriendRequests': numFriendRequests,
    }
    return render(request, 'main/addfriend.html', context)




#######################   VIEWS DEALING WITH SHOPPING CART / SCHEDULE   ######################



# If the last parameter is 1 it is coming from the classList page, if it is 0 it is coming from the searchClass page
# changes where the redirect goes to. If 1 send it back to the department page, however if it is 0, send it back to the default
# classSearch page

def addclass(request, dept, course_id, class_list, friend_id = 0):
    # get all courses from that department since we cannot store them in model due to heroku max
    # number of rows with free version
    url = 'http://luthers-list.herokuapp.com/api/dept/' + dept + '/'
    response = requests.get(url)
    courses = response.json()

    # only add classes to model when people need them for their schedule bc Heroku cant support all classes
    addedClass = list(filter(lambda course: course['course_number'] == course_id, courses))

    startTime = '0000000'
    endTime = '00000000'
    if addedClass[0]['meetings'][0]['start_time']:
        startTime = addedClass[0]['meetings'][0]['start_time']

    if addedClass[0]['meetings'][0]['end_time']:
        endTime = addedClass[0]['meetings'][0]['end_time']    
    newCourse, courseCreated = course.objects.get_or_create(
        id=addedClass[0]['course_number'],
        department=addedClass[0]['subject'],
        instructorName=addedClass[0]['instructor']['name'], instructorEmail=addedClass[0]['instructor']['email'],
        courseSection=addedClass[0]['course_section'], semesterCode=addedClass[0]['semester_code'],
        description=addedClass[0]['description'],
        credits=addedClass[0]['units'], catalogNumber=addedClass[0]['catalog_number'],
        lectureType=addedClass[0]['component'],
        meeting_days=addedClass[0]['meetings'][0]['days'],
        # start_time=addedClass[0]['meetings'][0]['start_time'],
        # end_time=addedClass[0]['meetings'][0]['end_time'],
        start_time = startTime,
        end_time = endTime,
        room_location=addedClass[0]['meetings'][0]['facility_description'],
        classCapacity=addedClass[0]['class_capacity'],classEnrollment=addedClass[0]['enrollment_total'],
        classSpotsOpen=addedClass[0]['enrollment_available'],waitlist=addedClass[0]['wait_list'],
        waitlistMax=addedClass[0]['wait_cap'],

        start_time_int = (int(startTime[0:2])*60) + (int(startTime[3:5])),
        end_time_int = (int(endTime[0:2])*60) + (int(endTime[3:5])),
    )

    # activeUser is the person who is adding courses to their cart
    activeUser = myUser.objects.get(id=request.user.id)

    # seeing if they have a shopping cart already
    shoppingCartActiveUser, created = ShoppingCart.objects.get_or_create(activeUser=activeUser)
    isInCart = shoppingCartActiveUser.coursesInCart.filter(department=newCourse.department, catalogNumber=newCourse.catalogNumber, lectureType = newCourse.lectureType ).first()

    # if there is no objects of the isInCart list then you can add it however otherwise you cannot add duplicate classes
    if not isInCart:
        shoppingCartActiveUser.coursesInCart.add(newCourse)
        shoppingCartActiveUser.message = ""
    # if the course is already in your shoppingCart then it will not be added and it will show the user that you cannot do that
    elif isInCart:
        shoppingCartActiveUser.message = "Another section of the same course was already in your cart!"

    shoppingCartActiveUser.save()
    if (class_list == 2): #response for when user is adding class when viewing friends profile
        # let the user know from friends page if the course was added to their cart
        if not isInCart:
            shoppingCartActiveUser.message = "Course added to your cart!"
        shoppingCartActiveUser.save()

        return HttpResponseRedirect(reverse('main:viewschedule', args=(friend_id,)))

    elif(class_list == 1):
        return HttpResponseRedirect(reverse('main:deptclasses', args=(dept,)))

    else:
        return HttpResponseRedirect(reverse('main:searchclass'))

def removeclass(request, dept, course_id, class_list, friend_id = 0):
    # activeUser is the person who is adding courses to their cart
    activeUser = myUser.objects.get(id=request.user.id)
    # seeing if they have a shopping cart already
    shoppingCartActiveUser, created = ShoppingCart.objects.get_or_create(activeUser=activeUser)
    courseDeleted = course.objects.get(department=dept, id=course_id)
    shoppingCartActiveUser.coursesInCart.remove(courseDeleted)
    shoppingCartActiveUser.message = ""
    shoppingCartActiveUser.save()
    if(class_list == 3):
        return HttpResponseRedirect(reverse('main:viewschedule', args=(friend_id,)))
    elif(class_list == 2):
        return HttpResponseRedirect(reverse('main:myschedule'))
    elif(class_list == 1):
        return HttpResponseRedirect(reverse('main:deptclasses', args=(dept,)))
    elif(class_list == 0):
        return HttpResponseRedirect(reverse('main:searchclass'))

def addToSchedule(request):
    # adds a class to the schedule and removes it from users cart
    activeUser = myUser.objects.get(id=request.user.id)

    shoppingCartActiveUser, created = ShoppingCart.objects.get_or_create(activeUser=activeUser)
    scheduleActiveUser, created = ClassSchedule.objects.get_or_create(scheduleUser=activeUser)

    currentCart = shoppingCartActiveUser.coursesInCart.all()
    currentSchedule = scheduleActiveUser.coursesInSchedule.all()
    # combining all the courses the user currently has in their cart and their schedule
    allCourses = currentCart | currentSchedule
    for cartCourse in currentCart:
        # not allowing time conflicts or duplicate classes in the same schedule
        # seeing if there any courses currently in the schedule that have the same dep, catalogNumber, and department if
        # so then prevent this course from being add to schedule
        isInSchedule = scheduleActiveUser.coursesInSchedule.filter(department=cartCourse.department, catalogNumber=cartCourse.catalogNumber, lectureType = cartCourse.lectureType ).first()

        course_start_time = cartCourse.start_time_int
        course_end_time = cartCourse.end_time_int
        time_conflict = False
        days1 = cartCourse.meeting_days
        # checking to see if any time conflicts (for conflict to occur the start time of another class
        # must fall within the range of a current class time)
        for cartCourse2 in allCourses:
            days2 = cartCourse2.meeting_days
            # do not want to compare two of the same courses
            if cartCourse2 == cartCourse:
                continue
            else:
                # ensuring that the courses both meet on the same days (cant have time conflicts across diff days)
                if ("Mo" in days1 and "Mo" in days2) or ("Tu" in days1 and "Tu" in days2) or ("We" in days1 and "We" in days2) or ("Th" in days1 and "Th" in days2) or ("Fr" in days1 and "Fr" in days2):
                    # C1 is cartCourse, and C2 is cartCourse2 in the example below
                    # comparing two courses (time conflict if C1.start <= C2.start <= C1.end --> C2 starts during C1
                    # or if C2.start <= C1.start <= C2.end C1 starts during C2)
                    if (course_start_time <= cartCourse2.start_time_int and cartCourse2.start_time_int <= course_end_time) or (cartCourse2.start_time_int <= course_start_time and course_start_time <= cartCourse2.end_time_int):
                        time_conflict = True

                    if time_conflict:
                        shoppingCartActiveUser.message = "Time conflict between: " + cartCourse.department + " " + cartCourse.catalogNumber + " (" + cartCourse.lectureType +  ") and " + cartCourse2.department + " " + cartCourse2.catalogNumber + " (" + cartCourse2.lectureType +  ")!"
                        shoppingCartActiveUser.save()

        if isInSchedule:
            shoppingCartActiveUser.message = "Another section of " + cartCourse.department + " " + cartCourse.catalogNumber + " (" + cartCourse.lectureType + ") is in your schedule (no duplicates allowed)!"
            shoppingCartActiveUser.save()
        elif time_conflict:
            print('do nothing')
        else:
            scheduleActiveUser.coursesInSchedule.add(cartCourse)
            shoppingCartActiveUser.coursesInCart.remove(cartCourse)

    return HttpResponseRedirect(reverse('main:myschedule'))


def removeFromSchedule(request, course_id):
    # removes the class from the schedule and adds it back to the shopping cart
    activeUser = myUser.objects.get(id=request.user.id)

    courseToRemove = course.objects.get(id=course_id)

    shoppingCartActiveUser, created = ShoppingCart.objects.get_or_create(activeUser=activeUser)
    scheduleActiveUser, created = ClassSchedule.objects.get_or_create(scheduleUser=activeUser)

    shoppingCartActiveUser.coursesInCart.add(courseToRemove)
    scheduleActiveUser.coursesInSchedule.remove(courseToRemove)

    shoppingCartActiveUser.message = ""
    shoppingCartActiveUser.save()

    return HttpResponseRedirect(reverse('main:myschedule'))


    '''
    CODE TO LOAD IN DEPARTMENT DATA
    '''
    # fetching the data and storing it once in DB for users when they are filling out intro form
    # url = 'http://luthers-list.herokuapp.com/api/deptlist/'
    # response = requests.get(url)
    # data = response.json()
    # for i in data:
    #     try:
    #         deps = department.objects.get(abbreviation=i['subject'])
    #     except:
    #         deps = department(abbreviation = i['subject'])
    #         deps.save()

    # request.user.id gives and id to each user, request.user will be the name of the user
    # https://docs.djangoproject.com/en/4.1/ref/contrib/auth/ info about user fields