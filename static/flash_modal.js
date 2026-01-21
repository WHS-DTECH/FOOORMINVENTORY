// flash_modal.js
// Makes Flask flash messages stay until dismissed by the user (modal style)
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.alert-dismissible').forEach(function(alert) {
    alert.querySelector('.btn-close').addEventListener('click', function() {
      alert.style.display = 'none';
    });
  });
});
