import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from unittest.mock import patch, MagicMock


class TestApplyF1DarkTheme:
    """Tests that the dark theme CSS is properly defined and injected."""

    def test_apply_f1_dark_theme_injects_background_color(self):
        """CSS must set dark background (#0f1419) on .stApp."""
        import styles
        with patch('styles.st') as mock_st:
            mock_st.markdown = MagicMock()
            styles.apply_f1_dark_theme()
            # Collect all calls to st.markdown
            calls = mock_st.markdown.call_args_list
            all_css = ''.join(str(c) for c in calls)
            assert '#0f1419' in all_css, "Dark background #0f1419 must be in injected CSS"

    def test_apply_f1_dark_theme_injects_inter_font(self):
        """CSS must load Inter font for headers."""
        import styles
        with patch('styles.st') as mock_st:
            mock_st.markdown = MagicMock()
            styles.apply_f1_dark_theme()
            calls = mock_st.markdown.call_args_list
            all_css = ''.join(str(c) for c in calls)
            assert 'Inter' in all_css, "Inter font must be referenced in CSS"

    def test_apply_f1_dark_theme_injects_jetbrains_mono(self):
        """CSS must load JetBrains Mono for metric values."""
        import styles
        with patch('styles.st') as mock_st:
            mock_st.markdown = MagicMock()
            styles.apply_f1_dark_theme()
            calls = mock_st.markdown.call_args_list
            all_css = ''.join(str(c) for c in calls)
            assert 'JetBrains Mono' in all_css, "JetBrains Mono font must be referenced in CSS"

    def test_apply_f1_dark_theme_injects_team_colors(self):
        """Team colors must be defined in TEAM_COLORS dict for render-time use."""
        import styles
        with patch('styles.st') as mock_st:
            mock_st.markdown = MagicMock()
            styles.apply_f1_dark_theme()
            # TEAM_COLORS dict must exist and be non-empty
            assert len(styles.TEAM_COLORS) == 10, "TEAM_COLORS must have 10 entries"
            assert styles.TEAM_COLORS['Ferrari'] == '#DC0000', "Ferrari must be #DC0000"
            assert styles.TEAM_COLORS['McLaren'] == '#FF8700', "McLaren must be #FF8700"
            assert styles.TEAM_COLORS['Red Bull'] == '#3671C6', "Red Bull must be #3671C6"
            # CSS must have driver-card class using border-left for team color bars
            calls = mock_st.markdown.call_args_list
            all_css = ''.join(str(c) for c in calls)
            assert 'border-left' in all_css, "CSS must use border-left for team color bars"
            assert '[TEAM_COLOR]' in all_css or 'driver-card' in all_css

    def test_apply_f1_dark_theme_injects_no_emoji_in_section_headers(self):
        """CSS class names must not contain emoji characters."""
        import styles
        with patch('styles.st') as mock_st:
            mock_st.markdown = MagicMock()
            styles.apply_f1_dark_theme()
            calls = mock_st.markdown.call_args_list
            all_css = ''.join(str(c) for c in calls)
            # Emoji ranges — section headers should be text-only
            for char in all_css:
                assert not (0x1F300 <= ord(char) <= 0x1F9FF), \
                    f"CSS must not contain emoji U+{ord(char):04X}"

    def test_team_colors_all_10_teams_defined(self):
        """All 10 F1 teams must have a team color in TEAM_COLORS dict."""
        from styles import TEAM_COLORS
        expected = {
            "Mercedes", "Ferrari", "McLaren", "Red Bull", "Haas",
            "Alpine", "Williams", "Aston Martin", "Racing Bulls", "Kick Sauber"
        }
        assert set(TEAM_COLORS.keys()) == expected, \
            f"TEAM_COLORS must have exactly 10 teams, got {set(TEAM_COLORS.keys())}"
