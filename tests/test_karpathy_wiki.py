import os
import pytest
from app import create_app
from app.wiki_compiler import (
    WIKI_DIR,
    get_wiki_tree,
    read_wiki_page,
    lint_wiki_vault,
    full_wiki_recompile
)

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_vault_core_files_exist():
    assert os.path.exists(os.path.join(WIKI_DIR, 'schema.md'))
    assert os.path.exists(os.path.join(WIKI_DIR, 'index.md'))
    assert os.path.exists(os.path.join(WIKI_DIR, 'log.md'))
    assert os.path.isdir(os.path.join(WIKI_DIR, 'concepts'))
    assert os.path.isdir(os.path.join(WIKI_DIR, 'programs'))
    assert os.path.isdir(os.path.join(WIKI_DIR, 'students'))
    assert os.path.isdir(os.path.join(WIKI_DIR, 'sources'))
    assert os.path.isdir(os.path.join(WIKI_DIR, 'synthesis'))
    assert os.path.isdir(os.path.join(WIKI_DIR, 'courses'))

def test_schema_constitution():
    schema_path = os.path.join(WIKI_DIR, 'schema.md')
    with open(schema_path, 'r', encoding='utf-8') as f:
        content = f.read()
    assert "Andrej Karpathy" in content or "Wiki Architecture" in content
    assert "[[Page_Name]]" in content or "wikilink" in content.lower()
    assert "YAML frontmatter" in content or "frontmatter" in content.lower()

def test_get_wiki_tree():
    tree_data = get_wiki_tree()
    assert "tree" in tree_data
    categories = [cat['id'] for cat in tree_data['tree']]
    assert 'root' in categories
    assert 'concepts' in categories
    assert 'programs' in categories
    assert 'students' in categories
    assert 'sources' in categories
    assert 'synthesis' in categories
    assert 'courses' in categories

def test_read_wiki_page_index():
    page = read_wiki_page('index.md')
    assert page['filename'] == 'index.md'
    assert page['frontmatter']['type'] == 'index'
    assert 'Dhofar University' in page['title']
    assert len(page['content_markdown']) > 50

def test_read_wiki_student_dossier():
    # Find any student file
    s_dir = os.path.join(WIKI_DIR, 'students')
    files = [f for f in os.listdir(s_dir) if f.endswith('.md')]
    assert len(files) > 0
    sample_file = files[0]
    
    page = read_wiki_page(f"students/{sample_file}")
    assert page['frontmatter']['type'] == 'student_dossier'
    assert 'student_id' in page['frontmatter']
    assert 'standing' in page['frontmatter']
    assert 'Executive Situation Assessment' in page['content_markdown']
    assert 'Recommended Next-Semester Registration Plan' in page['content_markdown']

def test_read_wiki_backlinks():
    # Academic_Probation should have backlinks from multiple student dossiers and synthesis
    page = read_wiki_page("concepts/Academic_Probation.md")
    assert len(page['backlinks']) > 0
    backlink_names = [bl['filename'] for bl in page['backlinks']]
    assert any("Students_at_Risk" in name or "_" in name for name in backlink_names)

def test_lint_wiki_vault():
    lint = lint_wiki_vault()
    assert "total_pages" in lint
    assert lint['total_pages'] > 20
    assert "broken_links_count" in lint

def test_web_routes(client):
    # Test GET /wiki
    resp = client.get('/wiki')
    assert resp.status_code == 200
    assert b'Academic Advising Wiki' in resp.data
    assert b'wiki-container' in resp.data
    
    # Test GET /api/wiki/tree
    resp_tree = client.get('/api/wiki/tree')
    assert resp_tree.status_code == 200
    data = resp_tree.get_json()
    assert 'tree' in data
    
    # Test GET /api/wiki/page?path=index.md
    resp_page = client.get('/api/wiki/page?path=index.md')
    assert resp_page.status_code == 200
    pdata = resp_page.get_json()
    assert pdata['filename'] == 'index.md'
    
    # Test GET /api/wiki/lint
    resp_lint = client.get('/api/wiki/lint')
    assert resp_lint.status_code == 200
    ldata = resp_lint.get_json()
    assert 'total_pages' in ldata

def test_recompile_endpoint(client):
    resp = client.post('/api/wiki/recompile')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'success'
    assert data['student_dossiers_compiled'] >= 20
