document.addEventListener('DOMContentLoaded', () => {
  const highlightBar = document.querySelector('.highlight-bar');
  const navItems = document.querySelectorAll('.icon-container');

  // Function to update the highlight bar and active state
  const updateHighlightBar = (index) => {
    const target = navItems[index];
    const { offsetLeft, offsetWidth } = target;

    // Move and resize the bottom highlight bar
    highlightBar.style.left = `${offsetLeft}px`;
    highlightBar.style.width = `${offsetWidth}px`;

    // Add 'active' class to the clicked item and remove from others
    navItems.forEach(item => item.classList.remove('active'));
    target.classList.add('active');

    // Save the active index to local storage
    localStorage.setItem('activeIconIndex', index);
  };

  // Update on click
  navItems.forEach((item, index) => {
    item.addEventListener("click", () => updateHighlightBar(index));
  });

  // Restore the highlight on page reload
  const savedIndex = localStorage.getItem('activeIconIndex');
  const activeIndex = savedIndex !== null ? parseInt(savedIndex) : [...navItems].findIndex(item =>
    item.classList.contains("active")
  );

  if (activeIndex >= 0) {
    updateHighlightBar(activeIndex);
  }
});
