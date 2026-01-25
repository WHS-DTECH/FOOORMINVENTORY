# Utility function to get staff code from email
def get_staff_code_from_email(email):
	"""Lookup staff code by email. Returns staff code or None if not found."""
	# Example implementation: query staff.csv or database
	# For now, return the part before @ as a placeholder
	if not email or '@' not in email:
		return None
	return email.split('@')[0]
# admin_task/utils.py

# Place any admin-specific utility functions here
