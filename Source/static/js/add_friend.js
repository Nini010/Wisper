// Check if the user has friends added
let userHasFriends = false; // Initially no friends

// Toggle Add Friend link visibility
function updateAddFriendLink() {
  const addFriendLink = document.getElementById('add-friend-link');

  // Ensure the element exists before trying to access its style property
  if (addFriendLink) {
    if (userHasFriends) {
      addFriendLink.style.display = 'none'; // Hide link if friends are added
    } else {
      addFriendLink.style.display = 'inline'; // Show link if no friends are added
    }
  } else {
    console.warn("Element with ID 'add-friend-link' not found.");
  }
}

// Call the function to set initial visibility
updateAddFriendLink();
