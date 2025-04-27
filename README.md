Project Description
This Django Book Tracker system is a web-based application designed to allow authenticated users to scrape book data from an external website and manage that data in a structured and organized way. The application includes role-based access control, ensuring that users can only interact with the data they are authorized to manage.

The system connects to Books to Scrape, a sample online bookstore, and retrieves book details such as Title, Price, Stock Availability, Description, UPC, and Number of Reviews. The scraping process is performed manually by users through a button available on the dashboard and is handled using Selenium in headless mode.

Each user in the system is assigned permission to scrape specific pages from the target site:

molla: Page 1 and 2  
rina: Page 3 and 4
ylli: Page 5 and 6
Admin users: Full access to all pages and data.

The application includes features to:

View a list of books in a paginated table, displaying 5 books per page.
Add, edit, and delete books.
Search for books by title using a search bar without page reload, improving user experience.
Automatically enforce permissions so that users can only manage the books they created, while admin users can access and manage all data within the system.
An optional dashboard section was also added for superusers, providing a summary of system activity, including:

The total number of books scraped.
The number of books added manually.
A list of top contributors based on activity.

The project is organized into two main components:

A Django project containing the project settings and configurations.
A Django app where the core application logic, models, views, templates, and forms are implemented.

The system makes use of Django’s built-in authentication system for secure login, logout, and user-specific permissions.

Additionally, a .gitignore file was added to exclude unnecessary files such as the virtual environment, database file, and temporary Python files from version control to keep the repository clean and organized
