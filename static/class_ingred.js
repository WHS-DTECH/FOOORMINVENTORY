// class_ingred.js
// JS logic for Class Ingredients page

document.addEventListener('DOMContentLoaded', function() {
  // These variables are injected by Jinja in the HTML template
  // They must be set in a <script> block in the HTML before this file is loaded
  // Example:
  // <script>
  //   window.classIngredData = {
  //     recipes: ...,
  //     preRecipeId: ...,
  //     preServings: ...
  //   };
  // </script>
  const { recipes, preRecipeId, preServings } = window.classIngredData || {};

  function findRecipe(id) {
    if (!recipes) return null;
    return recipes.find(r => String(r.id) === String(id));
  }

  function renderOriginalIngredients(recipe) {
    const ul = document.getElementById('origList');
    if (!ul) return;
    ul.innerHTML = '';
    if (!recipe) return;
    if (!recipe.ingredients || recipe.ingredients.length === 0) {
      ul.innerHTML = '<li>No structured ingredients available.</li>';
      return;
    }
    recipe.ingredients.forEach(it => {
      const li = document.createElement('li');
      if (typeof it === 'object') {
        let q = it.quantity || '';
        let u = it.unit || '';
        let name = it.ingredient || '';
        if ((!u || u === '') && name) {
          const parsed = extractFromText(name);
          if (parsed.unit && !u) u = parsed.unit;
          if ((!q || q === '') && parsed.quantity !== null) q = parsed.quantity;
          if (parsed.name) name = parsed.name;
        }
        li.textContent = ((q || u) ? ((q !== '' ? q + ' ' : '') + (u ? u + ' ' : '')) : '') + name;
      } else {
        const parsed = extractFromText(String(it));
        const display = ((parsed.quantity !== null) ? (parsed.quantity + ' ' + (parsed.unit || '')) : '') + (parsed.name ? ' ' + parsed.name : '');
        li.textContent = display.trim();
      }
      ul.appendChild(li);
    });
  }

  function parseNumber(s) {
    if (s === null || s === undefined) return null;
    s = String(s).trim();
    if (!s) return null;
    const n = parseFloat(s.replace(',', '.'));
    if (!isNaN(n)) return n;
    const m = s.match(/(\d+[\.,]?\d*)/);
    if (m) return parseFloat(m[1].replace(',', '.'));
    return null;
  }

  function extractFromText(text) {
    if (!text) return { quantity: null, unit: '', name: text };
    const unitsList = ['kg', 'g', 'grams', 'gram', 'ml', 'l', 'tbsp', 'tablespoon', 'tablespoons', 'tsp', 'teaspoon', 'teaspoons', 'cup', 'cups', 'oz', 'lb', 'gms', 'gm'];
    const m = String(text).trim().match(/^(\d+[\.,]?\d*)\s*([a-zA-Z]+)?\s*(.*)$/);
    if (m) {
      let q = parseNumber(m[1]);
      let u = (m[2] || '').toLowerCase();
      let rest = (m[3] || '').trim();
      if (u === 'grams') u = 'g';
      if (u === 'gram') u = 'g';
      if (u === 'gms') u = 'g';
      if (u === 'gm') u = 'g';
      if (u === 'tablespoon' || u === 'tablespoons') u = 'tbsp';
      if (u === 'teaspoon' || u === 'teaspoons') u = 'tsp';
      return { quantity: q, unit: u, name: rest };
    }
    return { quantity: null, unit: '', name: text };
  }

  function calculate() {
    const sel = document.getElementById('recipeSelect');
    const rid = sel ? sel.value : null;
    const desiredEl = document.getElementById('desiredServings');
    const desired = desiredEl ? (parseFloat(desiredEl.value) || 24) : 24;
    const rec = findRecipe(parseInt(rid));
    const out = document.getElementById('calcList');
    if (!out) return;
    out.innerHTML = '';
    if (!rec) {
      out.innerHTML = '<li>Select a recipe first.</li>';
      return;
    }
    const origServ = parseInt(rec.serving_size) || 1;
    rec.ingredients.forEach(it => {
      let name = '';
      let qty = null;
      let unit = '';
      if (typeof it === 'object') {
        name = it.ingredient || '';
        qty = parseNumber(it.quantity);
        unit = it.unit || '';
        if ((qty === null || !unit) && name) {
          const parsed = extractFromText(name);
          if (qty === null && parsed.quantity !== null) qty = parsed.quantity;
          if ((!unit || unit === '') && parsed.unit) unit = parsed.unit;
          if (parsed.name) name = parsed.name;
        }
      } else {
        const parsed = extractFromText(String(it));
        name = parsed.name || String(it);
        qty = parsed.quantity;
        unit = parsed.unit || '';
      }
      let perSingle = null;
      if (qty !== null && origServ > 0) {
        perSingle = qty / origServ;
      }
      const scaled = (perSingle !== null) ? (perSingle * desired) : null;
      const li = document.createElement('li');
      if (scaled !== null) {
        let display = Math.round((scaled + Number.EPSILON) * 100) / 100;
        if (Number.isInteger(display)) display = parseInt(display);
        li.textContent = display + (unit ? (' ' + unit) : '') + ' ' + name;
      } else {
        li.textContent = name;
      }
      out.appendChild(li);
    });
  }

  // Event listeners
  const recipeSelect = document.getElementById('recipeSelect');
  if (recipeSelect) {
    recipeSelect.addEventListener('change', function () {
      const rec = findRecipe(parseInt(this.value));
      renderOriginalIngredients(rec);
    });
  }
  const calcBtn = document.getElementById('calcBtn');
  if (calcBtn) calcBtn.addEventListener('click', calculate);

  const saveBtn = document.getElementById('saveBtn');
  if (saveBtn) saveBtn.addEventListener('click', function () {
    const staff = document.getElementById('staff') ? document.getElementById('staff').value : '';
    const classcode = document.getElementById('classcode') ? document.getElementById('classcode').value : '';
    const date = document.getElementById('date') ? document.getElementById('date').value : '';
    const period = document.getElementById('period') ? document.getElementById('period').value : '';
    const rid = document.getElementById('recipeSelect') ? document.getElementById('recipeSelect').value : null;
    const desired = document.getElementById('desiredServings') ? (parseFloat(document.getElementById('desiredServings').value) || 24) : 24;
    if (!rid) { alert('Select a recipe first'); return; }
    // Check if we're editing an existing booking
    const bookingId = saveBtn.dataset.editingBookingId || null;
    fetch('/class_ingredients/save', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        booking_id: bookingId,
        staff: staff,
        classcode: classcode,
        date: date,
        period: period,
        recipe_id: rid,
        desired_servings: desired
      })
    }).then(r => r.json()).then(j => {
      if (j.success) {
        alert(bookingId ? 'Booking updated!' : 'Booking saved (id: ' + j.booking_id + ')');
        location.reload();
      } else {
        alert('Save failed');
      }
    }).catch(e => alert('Error: ' + e.message));
  });

  // set default date to today's date (unless pre-populated)
  (function () {
    const dateEl = document.getElementById('date');
    if (dateEl && !dateEl.value) {
      const d = new Date();
      const iso = d.toISOString().slice(0, 10);
      dateEl.value = iso;
    }
  })();

  // If pre-populated from booking, auto-render the recipe and calculate
  if (preRecipeId) {
    if (recipeSelect) {
      recipeSelect.value = preRecipeId;
    }
    const rec = findRecipe(preRecipeId);
    renderOriginalIngredients(rec);
    setTimeout(calculate, 100);
  }

  // Add click handlers for booking rows to load them for editing
  const bookingRows = document.querySelectorAll('.booking-row');
  bookingRows.forEach(row => {
    row.addEventListener('click', function () {
      const bookingId = this.dataset.bookingId;
      const staff = this.dataset.staff;
      const classCode = this.dataset.class;
      const date = this.dataset.date;
      const period = this.dataset.period;
      const recipeId = this.dataset.recipe;
      const servings = this.dataset.servings;
      document.getElementById('staff').value = staff;
      document.getElementById('classcode').value = classCode;
      document.getElementById('date').value = date;
      document.getElementById('period').value = period;
      document.getElementById('recipeSelect').value = recipeId;
      document.getElementById('desiredServings').value = servings;
      if (saveBtn) {
        saveBtn.dataset.editingBookingId = bookingId;
        saveBtn.textContent = 'Update booking';
        saveBtn.classList.add('btn-update');
      }
      const rec = findRecipe(parseInt(recipeId));
      renderOriginalIngredients(rec);
      calculate();
      window.scrollTo({ top: 0, behavior: 'smooth' });
      bookingRows.forEach(r => r.classList.remove('selected'));
      this.classList.add('selected');
    });
  });

  // Delete booking function
  window.deleteBooking = function (bookingId) {
    if (!confirm('Are you sure you want to delete this booking?')) return;
    fetch('/class_ingredients/delete/' + bookingId, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    }).then(r => r.json()).then(j => {
      if (j.success) {
        alert('Booking deleted');
        location.reload();
      } else {
        alert('Delete failed');
      }
    }).catch(e => alert('Error: ' + e.message));
  };
});
