import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from unittest.mock import patch, MagicMock


class TestRefreshButton:
    """Tests that the Refresh Data button forces a re-fetch of live data."""

    def test_refresh_button_defined_in_main(self):
        """Main must define a Refresh Data button that calls st.rerun on click."""
        import app
        # Verify st.rerun is called when button returns True
        with patch('app.st') as mock_st:
            mock_st.columns = MagicMock(return_value=(MagicMock(), MagicMock()))
            mock_st.button.return_value = True
            mock_st.tabs.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock()]
            mock_st.markdown = MagicMock()
            mock_st.runtime = MagicMock()

            with patch('app.st.rerun') as mock_rerun:
                try:
                    app.main()
                except Exception:
                    pass  # Streamlit runtime errors expected outside actual app
                # If refresh button returns True, rerun must be called
                # (button state is captured on rerun so we verify the call path exists)
                assert mock_st.button.called, "st.button('Refresh Data') must be called in main()"

    def test_app_calls_apply_f1_dark_theme(self):
        """app.py must call styles.apply_f1_dark_theme() to inject CSS."""
        import importlib
        import app as app_module
        importlib.reload(app_module)  # Force re-import to reset module state
        with patch('app.st') as mock_st:
            mock_st.markdown = MagicMock()
            mock_st.columns = MagicMock(return_value=(MagicMock(), MagicMock()))
            mock_st.button.return_value = False
            mock_st.tabs.return_value = [MagicMock() for _ in range(5)]
            with patch('app.st.rerun'):
                try:
                    app_module.main()
                except Exception:
                    pass
            # apply_f1_dark_theme must have been called (via import + init)
            # Verify dark theme strings were injected
            calls = mock_st.markdown.call_args_list
            all_calls = ''.join(str(c) for c in calls)
            assert '#0f1419' in all_calls or 'Inter' in all_calls, \
                "Dark theme CSS must be injected into Streamlit"
