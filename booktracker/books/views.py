from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage
from django.contrib import messages
from .models import Book, Profile
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from django.contrib.auth.models import User
from django.db.models import Count
from django.db import models
import re 
from .models import Book

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            Profile.objects.create(user=user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'books/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'books/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def home(request):
    search_term = request.GET.get('search', '')

    if request.user.is_superuser:
        books_list = Book.objects.filter(
            models.Q(title__icontains=search_term) | 
            models.Q(user__username__icontains=search_term)
        ).order_by('id')
    else:
        books_list = Book.objects.filter(
            user=request.user, 
            title__icontains=search_term
        ).order_by('id')

    paginator = Paginator(books_list, 5)
    page_number = request.GET.get('page', 1)
    try:
        page_number = int(page_number)
        if page_number < 1:
            page_number = 1
    except ValueError:
        page_number = 1

    if page_number > paginator.num_pages:
        page_number = paginator.num_pages

    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    if request.user.is_superuser:
        total_scraped = Book.objects.filter(created_manually=False).count()
        total_manual = Book.objects.filter(created_manually=True).count()
        top_contributors = (
            Book.objects.values('user__username')
            .annotate(total=Count('id'))
            .order_by('-total')[:5]
        )
    else:
        total_scraped = Book.objects.filter(user=request.user, created_manually=False).count()
        total_manual = Book.objects.filter(user=request.user, created_manually=True).count()
        top_contributors = []

    context = {
        'page_obj': page_obj,
        'total_scraped': total_scraped,
        'total_manual': total_manual,
        'top_contributors': top_contributors,
    }

    return render(request, 'books/home.html', context)

@login_required
def scrape_books(request):
    if request.method == 'POST':
        try:
            profile = Profile.objects.get(user=request.user)
            if not profile.scraping_pages:
                messages.error(request, "No scraping pages assigned to your profile.")
                return redirect('home')

            pages = profile.scraping_pages.split(',')
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')

            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            base_url = "https://books.toscrape.com/catalogue/page-{}.html"
            scraped_count = 0

            for page in pages:
                page = page.strip()
                driver.get(base_url.format(page))
                books = driver.find_elements(By.CLASS_NAME, 'product_pod')

                for book in books:
                    title = book.find_element(By.TAG_NAME, 'h3').text
                    book_link = book.find_element(By.TAG_NAME, 'h3').find_element(By.TAG_NAME, 'a').get_attribute('href')
                    driver.get(book_link)

                    full_title = driver.find_element(By.CSS_SELECTOR, 'h1').text
                    price = driver.find_element(By.CLASS_NAME, 'price_color').text

                    # Extract stock number safely
                    try:
                        stock_element = driver.find_element(By.CLASS_NAME, 'instock')
                        stock_text = stock_element.text
                        stock_match = re.search(r'(\d+)', stock_text)
                        if stock_match:
                            stock = f"{stock_match.group(1)} available"
                        else:
                            stock = stock_text.strip()
                    except:
                        stock = "N/A"

                    description = driver.find_element(By.CSS_SELECTOR, '#product_description ~ p').text
                    upc = driver.find_element(By.XPATH, '//th[text()="UPC"]/following-sibling::td').text
                    num_reviews = driver.find_element(By.XPATH, '//th[text()="Number of reviews"]/following-sibling::td').text

                    Book.objects.create(
                        user=request.user,
                        title=full_title,
                        price=price,
                        stock=stock,
                        description=description,
                        upc=upc,
                        num_reviews=int(num_reviews),
                        created_manually=False
                    )
                    scraped_count += 1
                    driver.back()

            driver.quit()

            if scraped_count > 0:
                messages.success(request, f"Successfully scraped {scraped_count} books!")
            else:
                messages.warning(request, "Scraping finished but no books found.")

        except Profile.DoesNotExist:
            messages.error(request, "Profile not found for this user.")
        except Exception as e:
            print("Error during scraping:", e)
            messages.error(request, f"Error during scraping: {str(e)}")
            if 'driver' in locals():
                driver.quit()

        return redirect('home')

    return redirect('home')

@login_required
def add_book(request):
    if request.method == "POST":
        title = request.POST['title']
        price = request.POST['price']
        stock = request.POST['stock']
        description = request.POST['description']
        upc = request.POST['upc']

        if request.user.is_superuser:
            user_id = request.POST['user']
            user = User.objects.get(id=user_id)
        else:
            user = request.user

        book = Book.objects.create(
            title=title,
            price=price,
            stock=stock,
            description=description,
            upc=upc,
            user=user,
            created_manually=True
        )

        messages.success(request, 'Book added successfully!')
        return redirect('home')

    users = User.objects.all()
    return render(request, 'books/add_book.html', {'users': users})


@login_required
def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if book.user != request.user and not request.user.is_superuser:
        messages.error(request, "You don't have permission to edit this book.")
        return redirect('home')

    if request.method == 'POST':
        book.title = request.POST.get('title')
        book.price = request.POST.get('price')
        book.stock = request.POST.get('stock')
        book.description = request.POST.get('description')
        book.upc = request.POST.get('upc')
        book.save()
        messages.success(request, "Book updated successfully!")
        return redirect('home')

    return render(request, 'books/edit_book.html', {'book': book})


@login_required
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if book.user != request.user and not request.user.is_superuser:
        messages.error(request, "You don't have permission to delete this book.")
        return redirect('home')

    book.delete()
    messages.success(request, "Book deleted successfully!")
    return redirect('home')
