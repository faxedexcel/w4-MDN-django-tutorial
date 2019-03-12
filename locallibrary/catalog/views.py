import datetime
from django.shortcuts import render, get_object_or_404
    # 'get_object_or_404()' returns a specified object from a model based on its primary key value and raises an 'Http404' exception (not found), if the record does not exist
from catalog.models import Book, Author, BookInstance, Genre
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseRedirect
    # 'HttpResponseRedirect' creates a redirect to a specified URL (HTTP status code 302)
from django.urls import reverse, reverse_lazy
    # 'reverse()' generates a URL from a URL configuration name and a set of arguments...it is the Python equivalent of the 'url' tag used in templates
from catalog.forms import RenewBookForm
    # imports the 'RenewBookForm' class from forms.py
from django.views.generic.edit import CreateView, UpdateView, DeleteView
    # Django generic editing views

# Create your views here.

def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
        # sets the value of the 'num_visits' session key to 0 if it has not previously been set
    request.session['num_visits'] = num_visits + 1
        # each time a request is received, the value is incremented and store it back in the session

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits,
            # passed to the template in the context variable
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

class BookListView(generic.ListView):
    model = Book
    paginate_by = 10
    # context_object_name = 'my_book_list' # your own name for the list as a template variable
    # queryset = Book.objects.filter(title__icontains='war')[:5] # Get 5 books containing the title war
    # template_name = 'books/my_arbitrary_template_name_list.html' # Specify your own template name/location
    # def get_queryset(self):
    #     return Book.objects.filter(title__icontains='war')[:5]
            # Get 5 books containing the title war
    # def get_context_data(self, **kwargs):
    #     # Call the base implementation first to get the context
    #     context = super(BookListView, self).get_context_data(**kwargs)
    #     # Create any data and add it to the context
    #     context['some_data'] = 'This is just some data'
    #     return context


class BookDetailView(generic.DetailView):
    model = Book

class AuthorListView(generic.ListView):
    model = Author
    parginate_by = 10

class AuthorDetailView(generic.DetailView):
    model = Author
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

class AuthorCreate(PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.can_mark_returned'
        # permission-required mixin required for class-based views instead of function view decorator
        # restricts access to the view to librarian
    model = Author
    fields = '__all__'
        # specify the fields to display in the form, in this case: all fields
    # initial = {'date_of_death': '05/01/2018'}
        # specify initial values for each of the fields using a dictionary of {field_name/value} pairs
    # 'CreateView' and 'UpdateView' use the same template by default and expects it to be named '<model name>_form.html'...in this case: 'author_form.html'

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.can_mark_returned'
        # permission-required mixin required for class-based views instead of function view decorator
        # restricts access to the view to librarian
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
        # specify the fields to display in the form, in this case: listed individually  
    # expects a template to be named: 'author_form.html'   

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'catalog.can_mark_returned'
        # permission-required mixin required for class-based views instead of function view decorator
        # restricts access to the view to librarian
    model = Author
    success_url = reverse_lazy('authors')
        # 'reverse_lazy()' function redirects to the author list after an author has been deleted
        # ...is a lazily executed version of 'reverse()', b/c we're providing a URL to a class-based view attribute
    # 'DeleteView' expects a template to be named '<model name>_confirm_delete.html'...in this case: 'author_confirm_delete.html'

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
        # 'template_name' declared, rather than useing the default, b/c we may end up having a few different lists of BookInstance records, with different views and templates
    paginate_by = 10
    
    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')
        # 'get_queryset()' re-implemented to restrict our query to just the 'BookInstance' objects for the current user
        # Note: that 'o' is the stored code for "on loan" and we order by the 'due_back' date so that the oldest items are displayed first

class AllLoanedBooksListView(PermissionRequiredMixin,generic.ListView):
    """Generic class-based view listing all books on loan to librarian user."""
    permission_required = 'catalog.can_mark_returned'
        # permission-required mixin required for class-based views instead of function view decorator
        # restricts access to the view to librarian
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_librarian.html'
        # 'template_name' declared, rather than useing the default, b/c we may end up having a few different lists of BookInstance records, with different views and templates
    paginate_by = 10
    
    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')
        # Note: that 'o' is the stored code for "on loan" and we order by the 'due_back' date so that the oldest items are displayed first

@permission_required('catalog.can_mark_returned') # restricts access to the view to librarians
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)
            # 'binding' is the process of creating a 'form' object and populating it with data from the request

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('/'))
                # 'all-borrowed' view was not created, so we'll redirect to the home page at URL '/'

    # if this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)