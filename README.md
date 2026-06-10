# Lost & Found Desktop App

A modern Lost & Found management system built with Python Tkinter. This application provides an intuitive interface for managing lost and found items with advanced search functionality, dark/light mode support, animated effects, and comprehensive database integration.

## Features

### User Interface

- **Dark/Light Mode Toggle**: Switch between dark and light themes for better user experience across all interfaces
- **Modern Dashboard**: Clean, professional interface with customizable color schemes and gradient backgrounds
- **Animated Effects**: Typewriter text effects, blinking text animations, and smooth color transitions
- **Responsive Design**: Modern GUI that adapts to different themes with consistent styling

### Authentication & User Management

- **Secure Login System**: Role-based authentication distinguishing between users and administrators
- **User Registration**: Complete registration form with validation for new user accounts
- **Admin Panel Access**: Separate administrative interface for system management
- **Database Integration**: SQLite database for secure user credential storage

### Item Management

- **Lost Item Reporting**: Comprehensive forms for reporting lost items with detailed information
- **Found Item Submission**: Easy-to-use interface for submitting found items
- **Advanced Search**: Multi-criteria search functionality (item type, category, keywords, location)
- **Quick Search**: Fast search from main interface with instant results
- **Category Support**: Multiple predefined categories including Electronics, Bags, Books, Personal Items, and more

### Search and Navigation

- **Advanced Search Window**: Detailed search functionality with filters for item type and category
- **Quick Search Bar**: Fast search from main interface with real-time results
- **Modal Windows**: Professional popup windows for forms and searches
- **Intuitive Navigation**: Easy-to-use interface with clear button layouts and color coding

### Administrative Features

- **Admin Control Panel**: Complete administrative interface with tabbed navigation
- **User Management**: Edit user accounts, delete users, manage permissions, and view user data
- **Item Management**: Add lost/found items directly through admin interface
- **Reports & Statistics**: View comprehensive statistics including total items, active items, and claimed items
- **Dark Mode Support**: Theme switching available in admin panel
- **User Type Management**: Distinguish between admin and regular users
- **Database Oversight**: Complete CRUD operations for all data tables

### Database Features

- **SQLite Database**: Lightweight and efficient database for storing all application data
- **Multiple Tables**: Separate tables for users, lost items, found items, and claimed items
- **Data Validation**: Form validation and error handling throughout the application
- **CRUD Operations**: Complete Create, Read, Update, Delete functionality
- **Automatic Table Creation**: Database initialization with proper schema setup
- **User Authentication**: Secure credential storage with role-based access (admin/user)
- **Phone Number Support**: Complete user profile management including contact information

### Application Components

1. **Login System** (`main.py`):
   - User authentication interface with gradient background
   - Animated typewriter effects and blinking text
   - User registration functionality with validation
   - Admin panel access for authorized users
   - Secure database integration

2. **User Interface** (`user_page.py`):
   - Report lost/found items with detailed forms
   - Advanced search functionality with multiple filters
   - Dark/light mode toggle with theme persistence
   - Clean table display with sortable columns
   - Modal windows for enhanced user experience

3. **Admin Panel** (`admin_page.py`):
   - Administrative controls with tabbed interface
   - Item management (add lost/found items)
   - User management (edit accounts, view details)
   - Reports and statistics dashboard
   - Dark mode support with consistent theming

4. **Database Connection** (`db_connection.py`):
   - Centralized database connection management
   - Automatic table creation and schema management
   - Error handling and connection security

### User Experience

- **Theme Switching**: Dark and light mode support across all interfaces
- **Color-coded Interface**:
  - Red for "Report Lost Item"
  - Green for "Report Found Item"
  - Blue for "Search Items"
  - Orange for administrative functions
- **Animated Effects**: Typewriter animations, text blinking, and color transitions
- **Modal Dialogs**: Professional popup windows for forms and data entry
- **Form Validation**: Comprehensive input validation with user-friendly error messages
- **Responsive Design**: Consistent layout across different window sizes
- **Modal Window Management**: Prevents multiple instances of the same window
- **Error Handling**: Robust database error handling throughout the application
- **Responsive Tables**: Automatic table refresh and data synchronization
- **Sequential ID Display**: User-friendly ID numbering in table displays
- **Window Centering**: All windows automatically center on screen
- **Gradient Backgrounds**: Beautiful gradient effects in login and registration windows

## Getting Started

### Prerequisites

- Python 3.7 or higher
- Tkinter (usually included with Python installation)
- SQLite3 (included with Python)

### Installation

1. Clone or download the repository
2. Navigate to the project directory
3. Ensure all Python files are in the same directory
4. Run the application

### Running the Application

**Main Entry Point (Recommended):**

```bash
python main.py
```

**Direct Access Options:**

```bash
# Access user interface directly
python user_page.py

# Access admin panel directly (requires authentication)
python admin_page.py
```

### Application Flow

1. **Start with Login** (`main.py`) - Main entry point with authentication and registration
2. **User Authentication** - Login with username/password or register new account
3. **User Interface** - Report lost/found items, search database, and view results
4. **Admin Panel** - Administrative controls, user management, and system reports

### Database Structure

- **Users Table**: Stores user accounts with authentication and profile information (username, password, full_name, email, phone, user_type)
- **Lost Items Table**: Records of reported lost items with detailed descriptions
- **Found Items Table**: Records of submitted found items with location data
- **Claimed Items Table**: Tracking of successfully reunited items

## Features in Detail

### Search Functionality

- Multi-field search across item names, categories, locations, and descriptions
- Filter by item type (Lost, Found, or All)
- Category-based filtering with predefined options
- Real-time results display with sequential ID numbering

### Theme Support

- Consistent dark/light mode across all application windows
- Automatic theme application to modal windows and forms
- Professional color schemes optimized for readability

### Data Management

- Automatic database initialization on first run
- Comprehensive error handling and user feedback
- Data validation for all form inputs
- Secure database operations with proper connection management

