import io
try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    requests = None
    BeautifulSoup = None
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

def extract_raw_text_from_url(url):
    global requests, BeautifulSoup, PyPDF2
    if requests is None:
        return None, 'Requests library not installed.'
    try:
        resp = requests.get(url, timeout=10)
    except Exception as e:
        return None, f'Failed to fetch URL: {e}'
    if resp.status_code != 200:
        return None, f'URL returned status code {resp.status_code}'
    content_type = resp.headers.get('Content-Type', '')
    if 'pdf' in content_type or url.lower().endswith('.pdf'):
        if not PyPDF2:
            return None, 'PyPDF2 not installed.'
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(resp.content))
            full_text = "\n".join([page.extract_text() or '' for page in pdf_reader.pages])
            return full_text, None
        except Exception as e:
            return None, f'PDF extraction failed: {e}'
    else:
        html = resp.text
        if BeautifulSoup is None:
            return html, None
        soup = BeautifulSoup(html, 'html.parser')
        texts = soup.stripped_strings
        visible_text = "\n".join(texts)
        return visible_text, None