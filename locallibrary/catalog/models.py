from django.db import models
from django.urls import reverse
    # Used to generate URLs by reversing the URL patterns
import uuid
    # Required for unique book instances
from django.contrib.auth.models import User
    # Required to make use of 'User' class
from datetime import date

# Create your models here.

class Genre(models.Model):
    """Model representing a book genre."""
    name = models.CharField(max_length=200, help_text='Enter a book genre (e.g. Science Fiction)')

    def __str__(self):
        """String for representing the Model object."""
        return self.name

class Book(models.Model):
    """Model representing a book (but not a specific copy of a book)."""
    title = models.CharField(max_length=200)

    # Foreign Key used because book can only have one author, but authors can have multiple books
    # Author as a string rather than object because it hasn't been declared yet in the file 
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)

    summary = models.TextField(max_length=1000, help_text='Enter a brief description of the book')
    isbn = models.CharField('ISBN', max_length=13, help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')

    # ManyToManyField used because genre can contain many books. Books can cover many genres.
    # Genre class has already been defined so we can specify the object above.
    genre = models.ManyToManyField(Genre, help_text='Select a genre for this book')

    def display_genre(self):
        """Create a string for the Genre. This is required to display genre in Admin."""
        return ', '.join(genre.name for genre in self.genre.all()[:3])
            # str.join(iterable) --> https://docs.python.org/3.7/library/stdtypes.html?highlight=join#str.join
            # 1st three '[:3]' genre items in the 'self.genre.all()' for a 'Book' object will be joined separated by a comma ', '

    display_genre.short_description = 'genre'
        # '.short_description' is a built-in Django attribute to provide human-readable descriptions for callback functions
        # https://docs.djangoproject.com/en/2.1/ref/contrib/admin/actions/

    def __str__(self):
        """String for representing the Model object."""
        return self.title

    def get_absolute_url(self):
        """Returns the url to access a detail record for this book."""
        return reverse('book-detail', args=[str(self.id)])

class BookInstance(models.Model):
    """Model representing a specific copy of a book (i.e. that can be borrowed from the library)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular book across whole library')
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
        # Foreign Key used b/c book instance can only have 1 borrower, but borrower can have many book instances
        # 'User' model class argument is declared to connect the relationship between the 'BookInstance' and 'User' classes
        # 'on_delete=models.SET_NULL' argument sets the value of the borrower to Null if the associated borrower record is deleted
        # 'null=True' argument allows the database to store a 'Null' value if no borrower is selected

    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='m',
        help_text='Book availability',
    )

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Set book as returned"),)
            # You can specify as many permissions as you need in a tuple, each permission itself being defined in a nested tuple containing the permission name and permission display value
            # Allows a user to mark that a book has been returned

    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False
    
    def __str__(self):
        """String for representing the Model object."""
        return f'{self.id} ({self.book.title})' 

class Author(models.Model):
    """Model representing an author."""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def get_absolute_url(self):
        """Returns the url to access a particular author instance."""
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.last_name}, {self.first_name}'

