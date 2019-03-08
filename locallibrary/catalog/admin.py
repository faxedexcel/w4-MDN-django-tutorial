from django.contrib import admin
from catalog.models import Author, Genre, Book, BookInstance

# Register your models here.

# admin.site.register(Book)
# admin.site.register(Author)
admin.site.register(Genre)
# admin.site.register(BookInstance)

# Define the admin class
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
        # 'fields' is a built-in Django attribute

# Register the admin class with the associated model
admin.site.register(Author, AuthorAdmin)

class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
    # declare 'TabularInline' class to add all fields from the 'inlines' model
    # 'model' is a built-in Django attribute? set to the 'BookInstance' model
    extra = 0
        # 'extra' is built-in Django attribute that removes the extra placeholders

# Register the Admin classes for Book using the decorator
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_genre')
        # 'list_display' is a built-in Django attribute
    inlines = [BooksInstanceInline]
        # 'inlines' is a built-in Djanto attribute? set to the 'BooksInstanceInline' class defined above

# Register the Admin classes for BookInstance using the decorator
@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'status', 'due_back', 'id')
    list_filter = ('status', 'due_back')
        # 'list_filter' is a built-in Django attribute
    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back')
        }),
    )