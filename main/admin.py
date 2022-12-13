from django.contrib import admin
from .models import myUser, course, department, Friend_Request, FriendList, ShoppingCart, ClassSchedule, Comment
# Register your models here.

class FriendListInline(admin.TabularInline):
    model = FriendList
    extra = 5

class UserAdmin(admin.ModelAdmin):
    inlines = [FriendListInline]


admin.site.register(myUser, UserAdmin)
admin.site.register(course)
admin.site.register(department)
admin.site.register(Friend_Request)
admin.site.register(FriendList)
admin.site.register(ShoppingCart)
admin.site.register(ClassSchedule)
admin.site.register(Comment)
