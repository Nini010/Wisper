# Wisper

Wisper is a feature-rich Python web application for social networking, enabling users to interact through chats, direct messages, profile management, and notifications. The backend is built with Flask, while the frontend leverages Bootstrap for responsive design and custom JavaScript for interactivity. The app supports secure authentication via Google and Facebook, and stores user data in a local SQLite database.

---

## How It Works

1. **User Authentication**: Users can sign in using Google or Facebook OAuth. The app uses the credentials in `FB_client_secret.json` and `google_client_secret.json` to securely authenticate users and manage sessions.
2. **Profile Management**: After authentication, users can view and edit their profiles, including uploading profile pictures and updating personal information. Profile data is stored in `profile.db`.
3. **Chat & Direct Messaging**: Users can participate in group chats or send direct messages (DMs) to other users. The chat interface is dynamic, powered by JavaScript and styled with Bootstrap.
4. **Notifications**: The app provides real-time or near-real-time notifications for new messages, friend requests, and other events.
5. **Settings & Customization**: Users can adjust their settings, such as notification preferences and account details, through a dedicated settings page.
6. **Static & Media Files**: All static assets (CSS, JS, images, fonts) are served from the `static/` directory. User-uploaded images are stored in `static/images/uploads/`.
7. **Security**: The app supports HTTPS using the provided SSL certificate files (`ssl.crt`, `ssl.key`).

---

## Getting Started

1. **Clone the repository**:
   ```sh
   git clone https://github.com/Nini010/Wisper.git
   ```
2. **Install dependencies**:
   - Ensure Python 3.x is installed.
   - Install required packages:
     ```sh
     pip install -r requirements.txt
     ```
3. **Set up OAuth credentials**:
   - Place your Google and Facebook OAuth credentials in `google_client_secret.json` and `FB_client_secret.json` respectively.
4. **Run the application**:
   ```sh
   python Source/Main.py
   ```
5. **Access the app**:
   - Open your browser and go to `https://localhost:5000`.

--- 

## Project Structure

All main application code and resources are located in the `Source/` directory. Below is an in-depth overview of its contents:

### Main Files
- **Main.py**: The application's entry point. Initializes the Flask app, configures routes, handles requests, and manages the app lifecycle. Responsible for starting the server and integrating all modules.
- **functions.py**: Contains backend logic, utility functions, and possibly database interaction code. Handles operations such as user authentication, message handling, profile updates, and more.
- **profile.db**: SQLite database file. Stores persistent data such as user profiles, chat history, friend lists, and settings.
- **FB_client_secret.json** / **google_client_secret.json**: Store OAuth credentials for Facebook and Google. Required for enabling social login features.
- **ssl.crt**, **ssl.csr**, **ssl.key**: SSL certificate, certificate signing request, and private key. Used to enable HTTPS for secure communication between the client and server.

### Templates (`Source/templates/`)
HTML templates rendered by Flask. These use Jinja2 templating to dynamically inject user data and content. Key templates include:
- `base.html`: The base layout, includes common elements like navigation bars, footers, and links to static assets. All other templates extend this file.
- `SignIn.html`: Login page for user authentication via Google or Facebook.
- `Profilepage.html`: Displays a user's profile, including posts, friends, and activity.
- `ProfileInfo.html`: Shows detailed user information.
- `EditProfile.html`: Allows users to update their profile details and upload a new profile picture.
- `my-pfp.html`, `pfp.html`: Dedicated pages for managing and displaying profile pictures.
- `chats.html`: Main chat interface for group conversations.
- `DMs.html`: Direct messaging interface for private conversations between users.
- `notifications.html`: Displays user notifications.
- `settings.html`: User settings page for account and notification preferences.
- `404.html`: Custom error page for handling not found errors.

### Static Assets (`Source/static/`)
Organized into subfolders for modularity and maintainability:
- **bootstrap/**: Contains Bootstrap CSS and JS files for responsive, mobile-first UI design. Ensures consistent styling and layout across all pages.
- **css/**: Custom stylesheets for different parts of the app:
  - `chats.css`: Styles for the chat interface.
  - `DMs.css`: Styles for direct messaging.
  - `settings.css`: Styles for the settings page.
- **js/**: Custom JavaScript files to enhance interactivity:
  - `add_friend.js`: Handles friend request logic.
  - `emoji.js`: Adds emoji support to chat and messages.
  - `pfp_upload.js`: Manages profile picture uploads.
  - `posts_upload.js`: Handles post creation and uploads.
  - `profileInfoError.js`: Displays errors on the profile info page.
  - `requests.js`: Manages friend requests and notifications.
  - `updateProfile.js`: Handles profile updates from the frontend.
- **fonts/**: Custom fonts, such as `josephsophia.otf`, for unique branding and improved UI aesthetics.
- **images/**: Contains all static images and icons used in the UI, such as profile pictures (`pfp.jpg`), navigation icons (`home.svg`, `chat.svg`), and action icons (`addPost.png`).
- **images/uploads/**: Stores user-uploaded images, such as new profile pictures or post images. Ensures user content is separated from static assets.

---

## Features
- **User Authentication**: Secure login via Google and Facebook OAuth.
- **Profile Management**: View, edit, and customize user profiles, including profile pictures.
- **Chat & Direct Messaging**: Participate in group chats or private conversations.
- **Notifications**: Stay updated with real-time notifications for important events.
- **Settings**: Customize account and notification preferences.
- **Responsive UI**: Modern, mobile-friendly design using Bootstrap.
- **Security**: HTTPS support for secure data transmission.

---