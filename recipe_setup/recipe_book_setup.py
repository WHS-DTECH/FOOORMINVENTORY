# --- Load Recipe from URL: Insert into parser_test_recipes and redirect to parser_debug ---
from flask import current_app
from datetime import datetime

@app.route('/load_recipe_url', methods=['POST'])
@require_role('Admin')
def load_recipe_url():
    url = request.form.get('url') or request.args.get('url')
    if not url:
        flash('No URL provided', 'error')
        return redirect(url_for('recipe_book_setup'))
    user = getattr(current_user, 'email', 'unknown')
    now = datetime.utcnow()
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO parser_test_recipes (upload_source_detail, upload_source_type, uploaded_by, upload_date)
            VALUES (%s, %s, %s, %s) RETURNING id
        ''', (url, 'url', user, now))
        new_id = c.fetchone()[0]
        conn.commit()
    flash('Recipe URL loaded for debugging.', 'success')
    return redirect(url_for('debug_parser.parser_debug', test_recipe_id=new_id))
# Recipe Book Setup Page Logic
# Transferred from previous location (if applicable)
# ...existing code from recipe_book_setup.py... 

@app.route('/uploadclass', methods=['POST'])
@require_role('Admin')
def uploadclass():
    uploaded = request.files.get('csvfile')
    if not uploaded:
        flash('No class file uploaded')
        return redirect(url_for('admin'))

    # Normalize line endings
    file_content = uploaded.stream.read().decode('utf-8', errors='ignore')
    file_content = file_content.replace('\r\n', '\n').replace('\r', '\n')
    stream = io.StringIO(file_content)
    reader = csv.DictReader(stream)
    rows = []
    with get_db_connection() as conn:
        c = conn.cursor()
        for row in reader:
            # Map expected fields, allow flexible header names
            classcode = row.get('ClassCode') or row.get('classcode') or row.get('Class') or row.get('class')
            lineno = row.get('LineNo') or row.get('lineno') or row.get('Line')
            try:
                ln = int(lineno) if lineno not in (None, '') else None
            except ValueError:
                ln = None
            # Upsert for PostgreSQL: ON CONFLICT (ClassCode) DO UPDATE
            if not classcode or ln is None:
                skipped_rows = skipped_rows + 1 if 'skipped_rows' in locals() else 1
                continue
            c.execute('''
                INSERT INTO classes (ClassCode, LineNo, Misc1, RoomNo, CourseName, Misc2, Year, Dept, StaffCode, ClassSize, TotalSize, TimetableYear, Misc3)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (ClassCode, LineNo) DO UPDATE SET
                  Misc1=EXCLUDED.Misc1,
                  RoomNo=EXCLUDED.RoomNo,
                  CourseName=EXCLUDED.CourseName,
                  Misc2=EXCLUDED.Misc2,
                  Year=EXCLUDED.Year,
                  Dept=EXCLUDED.Dept,
                  StaffCode=EXCLUDED.StaffCode,
                  ClassSize=EXCLUDED.ClassSize,
                  TotalSize=EXCLUDED.TotalSize,
                  TimetableYear=EXCLUDED.TimetableYear,
                  Misc3=EXCLUDED.Misc3
            ''',
                (
                    classcode,
                    ln,
                    row.get('Misc1'),
                    row.get('RoomNo'),
                    row.get('CourseName'),
                    row.get('Misc2'),
                    row.get('Year'),
                    row.get('Dept'),
                    row.get('StaffCode'),
                    row.get('ClassSize'),
                    row.get('TotalSize'),
                    row.get('TimetableYear'),
                    row.get('Misc3'),
                ))
            rows.append(row)

    flash('Classes CSV processed')
    if 'skipped_rows' in locals():
        flash(f'Skipped {skipped_rows} row(s) with missing ClassCode or LineNo.')
    
    # Fetch suggestions for admin page
    suggestions = []
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT id, name, source, source_url, upload_method, uploaded_by, upload_date FROM recipes ORDER BY name')
            recipe_list = [dict(row) for row in c.fetchall()]
        return render_template('recipe_book_setup.html', recipe_list=recipe_list)
    except Exception:
        suggestions = []
    return render_template('admin.html', preview_data=rows, suggestions=suggestions)


@app.route('/upload', methods=['GET', 'POST'], endpoint='main_upload')
@require_role('Admin')
def upload():
    # GET request - show the upload form
    if request.method == 'GET':
        return render_template('upload_recipe.html')
    
    # POST request - handle form submission
    # Step 1: PDF upload, extract and show titles
    if 'pdfFile' in request.files:
        try:
            if not PyPDF2:
                return render_template('upload_result.html', recipes=[], pdf_filename=None, error='PyPDF2 not installed - cannot parse PDF files')
            pdf_file = request.files.get('pdfFile')
            if not pdf_file or pdf_file.filename == '':
                return render_template('upload_result.html', recipes=[], pdf_filename=None, error='No PDF file selected')
            # Save PDF to a temp file, store temp filename in session
            import uuid
            tmp_dir = os.path.join(os.path.dirname(__file__), 'tmp')
            if not os.path.exists(tmp_dir):
                os.makedirs(tmp_dir)
            tmp_filename = f"pdf_{uuid.uuid4().hex}.pdf"
            tmp_path = os.path.join(tmp_dir, tmp_filename)
            pdf_bytes = pdf_file.read()
            with open(tmp_path, 'wb') as f:
                f.write(pdf_bytes)
            session['pdf_tmpfile'] = tmp_filename
            session['pdf_filename'] = pdf_file.filename
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            full_text = "\n".join([page.extract_text() or '' for page in pdf_reader.pages])
            # Extract titles only
            recipes_found = parse_recipes_from_text(full_text)
            titles = [r.get('name', '').strip() for r in recipes_found if isinstance(r, dict) and r.get('name')]
            session['detected_titles'] = titles
            return render_template('upload_result.html', recipes=[{'name': t} for t in titles], pdf_filename=pdf_file.filename, step='titles')
        except Exception as e:
            print(f"[ERROR] PDF upload failed: {e}")
            return render_template('upload_result.html', recipes=[], pdf_filename=None, error=f'PDF upload failed: {str(e)}')

    # Step 2: Confirmed titles, extract full details
    if request.form.get('step') == 'titles_confirmed':
        try:
            tmp_dir = os.path.join(os.path.dirname(__file__), 'tmp')
            tmp_filename = session.get('pdf_tmpfile')
            pdf_filename = session.get('pdf_filename')
            selected_titles = request.form.getlist('selected_titles')
            if not tmp_filename or not selected_titles:
                return render_template('upload_result.html', recipes=[], pdf_filename=None, error='Session expired or no titles selected.')
            tmp_path = os.path.join(tmp_dir, tmp_filename)
            with open(tmp_path, 'rb') as f:
                pdf_bytes = f.read()
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            full_text = "\n".join([page.extract_text() or '' for page in pdf_reader.pages])
            # Extract all recipes, then filter for selected titles
            all_recipes = parse_recipes_from_text(full_text)
            recipes_to_show = []
            for r in all_recipes:
                if r.get('name') in selected_titles:
                    # Ensure all required keys exist for template safety
                    recipe = dict(r)
                    if 'method' not in recipe:
                        recipe['method'] = ''
                    if 'ingredients' not in recipe:
                        recipe['ingredients'] = []
                    if 'equipment' not in recipe:
                        recipe['equipment'] = []
                    if 'serving_size' not in recipe:
                        recipe['serving_size'] = ''
                    recipes_to_show.append(recipe)
            # Store recipes_to_show in a temp file instead of session
            import uuid, json
            tmp_dir = os.path.join(os.path.dirname(__file__), 'tmp')
            if not os.path.exists(tmp_dir):
                os.makedirs(tmp_dir)
            recipes_to_save_filename = f"recipes_to_save_{uuid.uuid4().hex}.json"
            recipes_to_save_path = os.path.join(tmp_dir, recipes_to_save_filename)
            with open(recipes_to_save_path, 'w', encoding='utf-8') as f:
                json.dump(recipes_to_show, f)
            session['recipes_to_save_file'] = recipes_to_save_filename
            return render_template('upload_result.html', recipes=recipes_to_show, pdf_filename=pdf_filename, step='details')
        except Exception as e:
            print(f"[ERROR] Full details extraction failed: {e}")
            return render_template('upload_result.html', recipes=[], pdf_filename=None, error=f'Full details extraction failed: {str(e)}')

    # Step 3: Confirmed full details, save to DB
    if request.form.get('step') == 'details_confirmed':
        # Load recipes_to_save from temp file instead of session
        import json
        recipes_to_save = []
        recipes_to_save_filename = session.get('recipes_to_save_file')
        if recipes_to_save_filename:
            tmp_dir = os.path.join(os.path.dirname(__file__), 'tmp')
            recipes_to_save_path = os.path.join(tmp_dir, recipes_to_save_filename)
            try:
                with open(recipes_to_save_path, 'r', encoding='utf-8') as f:
                    recipes_to_save = json.load(f)
            except Exception as e:
                print(f"[ERROR] Could not load recipes_to_save file: {e}")
        pdf_filename = session.get('pdf_filename', 'manual_upload')
        tmp_filename = session.get('pdf_tmpfile')
        tmp_dir = os.path.join(os.path.dirname(__file__), 'tmp')
        saved_count = 0
        skipped_count = 0
        error_details = []
        with get_db_connection() as conn:
            c = conn.cursor()
            try:
                c.execute("SELECT name FROM recipes")
                all_existing_names = [row['name'] for row in c.fetchall()]
                for recipe in recipes_to_save:
                    c.execute("SELECT id FROM recipes WHERE LOWER(name) = LOWER(%s)", (recipe['name'],))
                    existing = c.fetchone()
                    if existing:
                        skipped_count += 1
                        error_details.append(f'Duplicate: "{recipe["name"]}" already exists.')
                        continue
                    similar = []
                    for existing_name in all_existing_names:
                        if simple_similarity(recipe['name'], existing_name) >= 0.7:
                            similar.append(existing_name)
                    if similar:
                        error_details.append(f'Warning: "{recipe["name"]}" is similar to existing recipe(s): {", ".join(similar)}.')
                    try:
                        c.execute(
                            "INSERT INTO recipes (name, ingredients, instructions, serving_size, equipment) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                            (
                                recipe['name'],
                                json.dumps(recipe.get('ingredients', [])),
                                recipe.get('method', ''),
                                recipe.get('serving_size'),
                                json.dumps(recipe.get('equipment', []))
                            ),
                        )
                        recipe_id = c.fetchone()[0]
                        # Save raw extracted text to recipe_upload
                        c.execute(
                            "INSERT INTO recipe_upload (recipe_id, upload_source_type, upload_source_detail, uploaded_by, raw_text) VALUES (%s, %s, %s, %s)",
                            (recipe_id, 'pdf', pdf_filename, getattr(current_user, 'email', None), full_text)
                        )
                        saved_count += 1
                    except psycopg2.IntegrityError as e:
                        conn.rollback()
                        skipped_count += 1
                        error_details.append(f'DB IntegrityError for "{recipe["name"]}": {str(e)}')
            except Exception as e:
                conn.rollback()
                error_details.append(f'Bulk upload failed: {str(e)}')
                saved_count = 0
                skipped_count = len(recipes_to_save)
        # Clean up temp file and session
        if tmp_filename:
            tmp_path = os.path.join(tmp_dir, tmp_filename)
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception as e:
                print(f"[WARN] Could not remove temp PDF: {e}")
        session.pop('pdf_tmpfile', None)
        session.pop('pdf_filename', None)
        session.pop('detected_titles', None)
        # Remove temp file and session key
        recipes_to_save_filename = session.pop('recipes_to_save_file', None)
        if recipes_to_save_filename:
            tmp_dir = os.path.join(os.path.dirname(__file__), 'tmp')
            recipes_to_save_path = os.path.join(tmp_dir, recipes_to_save_filename)
            try:
                if os.path.exists(recipes_to_save_path):
                    os.remove(recipes_to_save_path)
            except Exception as e:
                print(f"[WARN] Could not remove temp recipes_to_save file: {e}")
        return render_template('upload_result.html', recipes=recipes_to_save, pdf_filename=pdf_filename, step='done', saved_count=saved_count, skipped_count=skipped_count, errors=error_details)

    # Step 1: If PDF file, parse and return detected recipes for preview/correction
    if 'pdfFile' in request.files:
        try:
            if not PyPDF2:
                return render_template('upload_result.html', recipes=[], pdf_filename=None, error='PyPDF2 not installed - cannot parse PDF files')
            pdf_file = request.files.get('pdfFile')
            if not pdf_file or pdf_file.filename == '':
                return render_template('upload_result.html', recipes=[], pdf_filename=None, error='No PDF file selected')
            # --- Page Range Support ---
            page_range_str = request.form.get('pageRange', '').strip()
            titles_only = request.form.get('titlesOnly', '').lower() == 'true'
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            total_pages = len(pdf_reader.pages)
            def parse_page_range(page_range, max_page):
                if not page_range:
                    return list(range(max_page))
                pages = set()
                for part in page_range.split(','):
                    part = part.strip()
                    if '-' in part:
                        start, end = part.split('-')
                        try:
                            start = int(start) - 1
                            end = int(end) - 1
                        except ValueError:
                            continue
                        if start < 0 or end >= max_page or start > end:
                            continue
                        pages.update(range(start, end + 1))
                    else:
                        try:
                            idx = int(part) - 1
                        except ValueError:
                            continue
                        if 0 <= idx < max_page:
                            pages.add(idx)
                return sorted(pages)
            selected_pages = parse_page_range(page_range_str, total_pages)
            if not selected_pages:
                return render_template('upload_result.html', recipes=[], pdf_filename=pdf_file.filename, error='No valid pages selected. Please check your page range.')
            full_text = ""
            for i in selected_pages:
                page = pdf_reader.pages[i]
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    full_text += page_text + "\n"
                elif pytesseract and Image:
                    try:
                        xobj = page.get("/Resources", {}).get("/XObject")
                        if xobj:
                            for obj in xobj:
                                img_obj = xobj[obj]
                                if img_obj.get("/Subtype") == "/Image":
                                    data = img_obj.get_data()
                                    mode = "RGB" if img_obj.get("/ColorSpace") == "/DeviceRGB" else "L"
                                    img = Image.frombytes(mode, (img_obj["/Width"], img_obj["/Height"]), data)
                                    ocr_text = pytesseract.image_to_string(img)
                                    if ocr_text.strip():
                                        full_text += ocr_text + "\n"
                    except Exception as ocr_e:
                        print(f"[OCR ERROR] {ocr_e}")
            # --- Titles Only Mode ---
            if titles_only:
                try:
                    recipes_found = parse_recipes_from_text(full_text)
                    titles = [r.get('name', '').strip() for r in recipes_found if isinstance(r, dict) and r.get('name')]
                    return render_template('upload_result.html', recipes=[{'name': t} for t in titles], pdf_filename=pdf_file.filename, titles_only=True)
                except Exception as e:
                    print(f"[ERROR] Titles only extraction failed: {e}")
                    return render_template('upload_result.html', recipes=[], pdf_filename=pdf_file.filename, error=f'Titles only extraction failed: {str(e)}')
            # --- Full Extraction (default) ---
            try:
                recipes_found = parse_recipes_from_text(full_text)
                if not recipes_found:
                    # Log extraction failure
                    try:
                        analytics_path = os.path.join(os.path.dirname(__file__), 'extraction_analytics.log')
                        with open(analytics_path, 'a', encoding='utf-8') as f:
                            f.write(json.dumps({
                                'event': 'no_recipes_found',
                                'pdf_filename': pdf_file.filename,
                                'selected_pages': selected_pages,
                                'timestamp': datetime.datetime.utcnow().isoformat()
                            }) + '\n')
                    except Exception as log_e:
                        print(f'[ANALYTICS LOG ERROR] {log_e}')
                    return render_template('upload_result.html', recipes=[], pdf_filename=pdf_file.filename, error=f'No recipes found with Ingredients, Equipment, and Method sections in the selected PDF pages ({len(selected_pages)} pages scanned). Try using manual recipe upload instead.')
                # Log flagged recipes (e.g., those with warnings or similarity issues)
                try:
                    analytics_path = os.path.join(os.path.dirname(__file__), 'extraction_analytics.log')
                    for recipe in recipes_found:
                        if isinstance(recipe, dict) and (recipe.get('flagged', False) or recipe.get('warnings')):
                            with open(analytics_path, 'a', encoding='utf-8') as f:
                                f.write(json.dumps({
                                    'event': 'flagged_recipe',
                                    'pdf_filename': pdf_file.filename,
                                    'recipe': recipe,
                                    'timestamp': datetime.datetime.utcnow().isoformat()
                                }) + '\n')
                except Exception as log_e:
                    print(f'[ANALYTICS LOG ERROR] {log_e}')
                # Render confirmation page for preview/correction (do not save yet)
                return render_template('upload_result.html', recipes=recipes_found, pdf_filename=pdf_file.filename)
            except Exception as e:
                print(f"[ERROR] Full extraction failed: {e}")
                return render_template('upload_result.html', recipes=[], pdf_filename=pdf_file.filename, error=f'Full extraction failed: {str(e)}')
        except Exception as e:
            print(f"[ERROR] PDF upload failed: {e}")
            return render_template('upload_result.html', recipes=[], pdf_filename=None, error=f'PDF upload failed: {str(e)}')
    
    # Handle form data upload
    name = request.form.get('name', '').strip()
    instructions = request.form.get('instructions', '').strip()
    
    if not name or not instructions:
        flash('Recipe name and instructions required', 'error')
        return redirect(url_for('recipes_page'))

    # Validate serving_size
    serving_size_raw = request.form.get('serving_size', '').strip()
    try:
        serving_size = int(serving_size_raw) if serving_size_raw != '' else None
    except ValueError:
        flash('Invalid serving size', 'error')
        return redirect(url_for('recipes_page'))

    equipment_text = request.form.get('equipment', '')

    # Collect structured ingredients

    quantities = request.form.getlist('quantity[]')
    units = request.form.getlist('unit[]')
    ingredients_names = request.form.getlist('ingredient[]')

    # Check if ingredients were parsed
    if not quantities or len(quantities) == 0:
        flash('No ingredients found. Please click "Format Ingredients" button before saving.', 'error')
        return redirect(url_for('admin'))

    ingredients = []
    for q, u, ing in zip(quantities, units, ingredients_names):
        ingredients.append({"quantity": q, "unit": u, "ingredient": ing})

    # Convert equipment text into a list
    equipment_list = [item.strip() for item in equipment_text.split('\n') if item.strip()]

    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            
            # Check if recipe name already exists
            c.execute("SELECT id, name FROM recipes WHERE name = %s", (name,))
            existing = c.fetchone()
            if existing:
                flash(f'Recipe "{name}" already exists in the database. Please use a different name or edit the existing recipe.', 'warning')
                return redirect(url_for('admin'))
            
            c.execute(
                "INSERT INTO recipes (name, ingredients, instructions, serving_size, equipment) VALUES (%s, %s, %s, %s, %s)",
                (name, json.dumps(ingredients), instructions, serving_size, json.dumps(equipment_list)),
            )
            conn.commit()
            
        # Run cleaners after form insert
        flash(f'Recipe "{name}" saved successfully!', 'success')
    except psycopg2.IntegrityError as e:
        flash(f'Recipe "{name}" already exists in the database. Please use a different name.', 'error')
        return redirect(url_for('admin'))
    except Exception as e:
        flash(f'Error saving recipe: {str(e)}', 'error')
        return redirect(url_for('admin'))
        
    return redirect(url_for('recipes_page'))


# --- Title Extraction Strategies ---
def extract_title_candidates(raw_html):
    candidates = []
    best_guess = None
    import re
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        BeautifulSoup = None
    # 1. <title> tag
    title_tag = None
    if BeautifulSoup:
        soup = BeautifulSoup(raw_html, 'html.parser')
        title_tag = soup.title.string.strip() if soup.title and soup.title.string else None
    else:
        m = re.search(r'<title>(.*?)</title>', raw_html, re.I|re.S)
        title_tag = m.group(1).strip() if m else None
    candidates.append({'name': '<title> tag', 'value': title_tag or '', 'best': False})
    # 2. og:title meta
    og_title = None
    if BeautifulSoup and soup:
        og = soup.find('meta', property='og:title')
        og_title = og['content'].strip() if og and og.get('content') else None
    else:
        m = re.search(r'<meta[^>]+property=["\"]og:title["\"][^>]+content=["\"](.*?)["\"]', raw_html, re.I|re.S)
        og_title = m.group(1).strip() if m else None
    candidates.append({'name': 'og:title meta', 'value': og_title or '', 'best': False})
    # 3. First <h1>
    h1 = None
    if BeautifulSoup and soup:
        h1tag = soup.find('h1')
        h1 = h1tag.get_text(strip=True) if h1tag else None
    else:
        m = re.search(r'<h1[^>]*>(.*?)</h1>', raw_html, re.I|re.S)
        h1 = m.group(1).strip() if m else None
    candidates.append({'name': 'First <h1>', 'value': h1 or '', 'best': False})
    # 4. JSON-LD schema.org name
    jsonld_title = None
    if BeautifulSoup and soup:
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                import json
                data = json.loads(script.string)
                if isinstance(data, dict) and 'name' in data:
                    jsonld_title = data['name']
                    break
                elif isinstance(data, list):
                    for entry in data:
                        if isinstance(entry, dict) and 'name' in entry:
                            jsonld_title = entry['name']
                            break
            except Exception:
                continue
    candidates.append({'name': 'schema.org/JSON-LD name', 'value': jsonld_title or '', 'best': False})
    # 5. Heuristic: First large/bold text (e.g., <b>, <strong>, <h2>)
    heuristic = None
    if BeautifulSoup and soup:
        for tag in soup.find_all(['h2', 'b', 'strong']):
            txt = tag.get_text(strip=True)
            if txt and len(txt) > 5:
                heuristic = txt
                break
    candidates.append({'name': 'Heuristic: first large/bold text', 'value': heuristic or '', 'best': False})
    # Pick best guess (first non-empty in priority order)
    for cand in candidates:
        if cand['value']:
            cand['best'] = True
            best_guess = cand['value']
            break
    return candidates, best_guess or ''


