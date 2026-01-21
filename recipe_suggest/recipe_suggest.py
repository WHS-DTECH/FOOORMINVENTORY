import os
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import current_user
from auth import require_role, require_login, get_db_connection

recipe_suggest_bp = Blueprint(
    'recipe_suggest',
    __name__,
    template_folder='templates/recipe_suggest'
)


# Admin view for recipe suggestions
@recipe_suggest_bp.route('/admin/recipe_suggestions')
@require_role('Admin')
def recipe_suggestions():
    return render_template('recipe_suggest/recipe_suggestions.html')

@recipe_suggest_bp.route('/suggest_recipe', methods=['POST'])
def suggest_recipe_modal():
    """Handle AJAX recipe suggestion submissions from modal and return JSON."""
    try:
        recipe_name = request.form.get('recipe_name', '').strip()
        recipe_url = request.form.get('recipe_url', '').strip()
        reason = request.form.get('reason', '').strip()
        suggested_by_name = request.form.get('suggested_by_name', '').strip()
        suggested_by_email = request.form.get('suggested_by_email', '').strip()

        if not recipe_name or not suggested_by_name or not suggested_by_email:
            return jsonify({'success': False, 'message': 'Recipe name, your name, and email are required.'})

        # Save suggestion to the database
        try:
            with get_db_connection() as conn:
                c = conn.cursor()
                sql = '''INSERT INTO recipe_suggestions (recipe_name, recipe_url, reason, suggested_by_name, suggested_by_email, created_at, status)
                       VALUES (%s, %s, %s, %s, %s, NOW(), %s)'''
                params = (recipe_name, recipe_url, reason, suggested_by_name, suggested_by_email, 'pending')
                c.execute(sql, params)
                conn.commit()
        except Exception as db_error:
            print(f"[ERROR] Failed to save suggestion to DB (modal): {db_error}")
            import traceback; traceback.print_exc()
            return jsonify({'success': False, 'message': 'There was an error saving your suggestion. Please try again or contact the Admin directly.'})

        # Send email to Admin (Vanessa Pringle)
        email_sent = False
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            smtp_username = os.getenv('SMTP_USERNAME')
            smtp_password = os.getenv('SMTP_PASSWORD')
            smtp_from_email = os.getenv('SMTP_FROM_EMAIL', smtp_username)
            Admin_email = 'vanessapringle@westlandhigh.school.nz'
            subject = f"Recipe Suggestion: {recipe_name}"
            body = f"Recipe Name: {recipe_name}\nURL: {recipe_url}\nReason: {reason}\nSuggested by: {suggested_by_name} ({suggested_by_email})"
            if smtp_username and smtp_password:
                msg = MIMEMultipart()
                msg['From'] = smtp_from_email or 'Food Room System <noreply@whsdtech.com>'
                msg['To'] = Admin_email
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain'))
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
                server.quit()
                email_sent = True
                print(f"Email sent successfully to {Admin_email}")
            else:
                print("SMTP credentials not configured - email not sent")
                print(f"RECIPE SUGGESTION EMAIL:\nTo: {Admin_email}\nSubject: {subject}\n\n{body}")
        except Exception as email_error:
            print(f"Failed to send email: {email_error}")
            print(f"RECIPE SUGGESTION EMAIL (not sent):\nTo: {Admin_email}\nSubject: {subject}\n\n{body}")
        return jsonify({'success': True, 'email_sent': email_sent})
    except Exception as e:
        print(f"Error in suggest_recipe_modal: {e}")
        import traceback; traceback.print_exc()
        return jsonify({'success': False, 'message': 'There was an error submitting your suggestion. Please try again or contact the Admin directly.'})


@recipe_suggest_bp.route('/recipes/suggest', methods=['POST'])
@require_login
def suggest_recipe():
    """Handle recipe suggestion submissions and email to Admin"""
    try:
        recipe_name = request.form.get('recipe_name', '').strip()
        recipe_url = request.form.get('recipe_url', '').strip()
        reason = request.form.get('reason', '').strip()

        if not recipe_name:
            flash('Recipe name is required.', 'error')
            return redirect(url_for('recipes_page'))

        # Set recipient email directly (Vanessa Pringle)
        Admin_email = 'vanessapringle@westlandhigh.school.nz'

        # Get current user info safely
        user_name = current_user.name if hasattr(current_user, 'name') else 'Unknown User'
        user_email = current_user.email if hasattr(current_user, 'email') else 'No email'

        # Define subject and body for the email
        subject = f"Recipe Suggestion: {recipe_name}"
        body = f"Recipe Name: {recipe_name}\nURL: {recipe_url}\nReason: {reason}\nSuggested by: {user_name} ({user_email})"

        # Save suggestion to the database (only once)
        try:
            with get_db_connection() as conn:
                c = conn.cursor()
                sql = '''INSERT INTO recipe_suggestions (recipe_name, recipe_url, reason, suggested_by_name, suggested_by_email, created_at, status)
                       VALUES (%s, %s, %s, %s, %s, NOW(), %s)'''
                params = (recipe_name, recipe_url, reason, user_name, user_email, 'pending')
                print("[DEBUG] About to execute SQL for recipe suggestion:")
                print("[DEBUG] SQL:", sql)
                print("[DEBUG] Params:", params)
                try:
                    c.execute(sql, params)
                    conn.commit()
                    print("[DEBUG] Insert committed successfully.")
                except Exception as exec_error:
                    print(f"[ERROR] Exception during SQL execute: {exec_error}")
                    import traceback; traceback.print_exc()
                    flash('There was an error saving your suggestion (SQL error). Please try again or contact the Admin directly.', 'error')
                    return redirect(url_for('recipes_page'))
        except Exception as db_error:
            print(f"[ERROR] Failed to save suggestion to DB (outer): {db_error}")
            import traceback; traceback.print_exc()
            flash('There was an error saving your suggestion (DB error). Please try again or contact the Admin directly.', 'error')
            return redirect(url_for('recipes_page'))

        # Only send email after successful DB insert
        email_sent = False
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            smtp_username = os.getenv('SMTP_USERNAME')
            smtp_password = os.getenv('SMTP_PASSWORD')
            smtp_from_email = os.getenv('SMTP_FROM_EMAIL', smtp_username)
            if smtp_username and smtp_password:
                msg = MIMEMultipart()
                msg['From'] = smtp_from_email or 'Food Room System <noreply@whsdtech.com>'
                msg['To'] = Admin_email
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain'))
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
                server.quit()
                email_sent = True
                print(f"Email sent successfully to {Admin_email}")
            else:
                print("SMTP credentials not configured - email not sent")
                print(f"RECIPE SUGGESTION EMAIL:\nTo: {Admin_email}\nSubject: {subject}\n\n{body}")
        except Exception as email_error:
            print(f"Failed to send email: {email_error}")
            print(f"RECIPE SUGGESTION EMAIL (not sent):\nTo: {Admin_email}\nSubject: {subject}\n\n{body}")

        if email_sent:
            flash(f'Thank you! Your suggestion for "{recipe_name}" has been emailed to the Admin and saved to the database.', 'success')
        else:
            flash(f'Thank you! Your suggestion for "{recipe_name}" has been saved. The Admin will review it in the Admin panel.', 'success')

    except Exception as e:
        print(f"Error in suggest_recipe: {e}")
        import traceback
        traceback.print_exc()
        flash('There was an error submitting your suggestion. Please try again or contact the Admin directly.', 'error')

    return redirect(url_for('recipes_page'))
