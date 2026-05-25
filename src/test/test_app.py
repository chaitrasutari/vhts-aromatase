# src/test/test_app.py

import pytest
from streamlit.testing.v1 import AppTest
import os

# ---------------------------------------------------------
# SETUP FIXTURE
# ---------------------------------------------------------
@pytest.fixture
def app():
    """
    Initializes a simulated Streamlit environment for app.py.
    The default timeout is set to 10 seconds to allow the engine to load.
    """
    # Point AppTest to your main app file
    at = AppTest.from_file("src/app/app.py", default_timeout=10)
    return at.run()

# ---------------------------------------------------------
# THE UI TESTS
# ---------------------------------------------------------
def test_app_loads_correctly(app):
    """Test 1: Does the UI render without crashing?"""
    # Check that no Python exceptions were thrown during render
    assert not app.exception
    
    # Check that the main title loaded correctly
    assert app.title[0].value == "🧬 AI-Driven Virtual High-Throughput Screening"
    
    # Verify both subheaders rendered
    subheaders = [sh.value for sh in app.subheader]
    assert "⚡ Quick Predict (Single Molecule)" in subheaders
    assert "📂 Batch Screening (CSV Upload)" in subheaders

def test_single_molecule_success(app):
    """Test 2: Can a user run a valid Quick Predict?"""
    # Find the text input box (index 0) and type a known active SMILES (Letrozole)
    app.text_input[0].input("N#Cc1ccc(C(c2ccc(C#N)cc2)n2cncn2)cc1").run()
    
    # Click the "Predict Single Molecule" button (index 0)
    app.button[0].click().run()
    
    assert not app.exception
    
    # Search all the 'success' alert boxes in the UI for the expected string
    success_messages = [msg.value for msg in app.success]
    assert any("Predicted Active" in msg for msg in success_messages)

def test_single_molecule_invalid(app):
    """Test 3: Does the UI gracefully handle syntax errors?"""
    # Type a malformed SMILES string
    app.text_input[0].input("C(C(=O)O").run()
    app.button[0].click().run()
    
    assert not app.exception
    
    # Verify the specific error message rendered to the user
    error_messages = [msg.value for msg in app.error]
    assert any("Invalid SMILES string" in msg for msg in error_messages)

def test_backend_file_extension_lock(app):
    """Test 4: Does the backend reject non-CSV files?"""
    mock_file_content = b"This is a fake text file."
    
    app.file_uploader[0].set_value(
        [("malicious_script.txt", mock_file_content, "text/plain")]
    ).run()
    
    # 3. Verify Streamlit's native security caught the bad extension and threw an exception
    assert app.exception
    assert "Invalid file extension" in app.exception[0].message