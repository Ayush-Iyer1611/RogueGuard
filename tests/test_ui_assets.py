import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TestRogueGuardUIAssets(unittest.TestCase):
    def test_pointer_effect_does_not_hide_native_cursor(self):
        content = (ROOT / "assets" / "rogueguard-effects.html").read_text(encoding="utf-8")
        self.assertNotIn("cursor: none", content)
        self.assertIn('id = "rg-cursor-ring"', content)
        self.assertIn('document.addEventListener("pointermove"', content)

    def test_sidebar_lime_buttons_have_dark_high_contrast_labels(self):
        content = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn('[data-testid="stSidebar"] [data-testid="stButton"] button *', content)
        self.assertIn("-webkit-text-fill-color: #17191b !important", content)

    def test_javascript_effects_are_enabled_from_trusted_local_asset(self):
        content = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn('st.html(effects_path, unsafe_allow_javascript=True)', content)
        self.assertIn('Path(__file__).with_name("assets") / "rogueguard-effects.html"', content)

    def test_sidebar_has_explicit_display_font_rules(self):
        content = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn('[data-testid="stSidebar"] h1', content)
        self.assertIn('font-family: "Barlow Condensed"', content)

    def test_sidebar_collapse_icon_keeps_material_symbols_font(self):
        content = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn('[data-testid="stSidebarCollapseButton"] span', content)
        self.assertIn('font-family: "Material Symbols Rounded" !important', content)
        self.assertIn('font-feature-settings: "liga"', content)

    def test_cursor_uses_custom_svg_and_preserves_text_cursor(self):
        content = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn('cursor: url("data:image/svg+xml,', content)
        self.assertIn('cursor: text !important', content)
        self.assertNotIn('cursor: none', content)


if __name__ == "__main__":
    unittest.main()
