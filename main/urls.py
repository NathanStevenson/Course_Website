from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views

# will all be routes appended onto the back of url/main
app_name = 'main'
urlpatterns = [

    ###########         NAV BAR MAIN ROUTES      ##############

    # the path for the /main/ route
    path('', views.index, name='index'),
    # a list of all the departments that UVA has to offer
    path('coursecatalog/', views.coursecatalog, name='coursecatalog'),
    # based on which department the user clicks on it displays that departments courses
    path('coursecatalog/<str:dept>', views.deptclasses, name='deptclasses'),
    # First step in class search -- will query for department
    path('searchclass/', views.searchclass, name='searchclass'),

    ##########         SCHEDULE ROUTES           ###############

    # shows the user their schedule
    path('myschedule/', views.myschedule, name='myschedule'),
    # allows you to view your friends schedules + leave comments on them
    path('viewschedule/<int:user_id>/', views.viewschedule, name='viewschedule'),
    # allows the owner of the schedule to delete other users comments on his page
    path('deletecomment/<int:comment_id>/', views.deletecomment, name='deletecomment'),
    # delete a comment you wrote on another users schedule
    path('deleteowncomment/<int:comment_id>/<int:friend_id>/', views.deleteowncomment, name='deleteowncomment'),

    # these routes deal with moving courses from the shopping cart into your schedule
    path('myschedule/addtoschedule', views.addToSchedule, name='addtoschedule'),
    path('myschedule/removefromschedule/<int:course_id>', views.removeFromSchedule, name='removefromschedule'),

    ##########         USER PROFILE ROUTES       ###############

    # profile route that will show the user theirs and other profiles (they can edit theirs)
    path('profile/<int:user_id>/', views.profile, name='profile'),
    # profile that takes the user to a separate form once logged in to edit or update their profile
    path('profile/edit/', views.edit, name='edit'),
    # the route users see when they first sign in for additional info
    path('editprofile/', views.editprofile, name='editprofile'),

    ##########         FRIEND SYSTEM ROUTES      ###############

    # route that allows users to see how many friends they have as well as add new ones
    path('addfriend/', views.addfriend, name='addfriend'),
    # allows users to remove friends they are currently friend with
    path('removefriend/<int:user_id>/', views.removefriend, name='removefriend'),
    # page that allows users to accept or reject friend requests
    path('friendrequests/', views.friendrequests, name='friendrequests'),
    # page that allows users to see a list of users who they are friends with
    path('friends/<int:user_id>/', views.friends, name='friends'),
    # path that triggers a view which deletes the friend request if the user declines it
    path('friendrequests/delete/<int:fromUserID>/', views.deleterequest, name='deleterequest'),
    # path for if the user accepts the incoming friend request
    path('friendrequests/accept/<int:fromUserID>/', views.acceptrequest, name='acceptrequest'),

    ###########         SHOPPING CART ROUTES      ################

    # paths for the schedule and shopping cart behavior
    path('coursecatalog/addclass/<str:dept>/<int:course_id>/<int:class_list>/', views.addclass, name='addclass'),
    path('coursecatalog/addclass/<str:dept>/<int:course_id>/<int:class_list>/<int:friend_id>', views.addclass, name='addclass'),
    path('coursecatalog/removeclass/<str:dept>/<int:course_id>/<int:class_list>/', views.removeclass, name='removeclass'),
    path('coursecatalog/removeclass/<str:dept>/<int:course_id>/<int:class_list>/<int:friend_id>', views.removeclass, name='removeclass'),

]

urlpatterns += staticfiles_urlpatterns()
