"""Shared visual theme for the desktop workspace."""

FONT_FAMILY = '"Noto Sans", "Microsoft YaHei UI", "Segoe UI"'

COLORS = {
    "primary": "#2563EB",
    "primary_hover": "#1D4ED8",
    "primary_pressed": "#1E40AF",
    "primary_soft": "#DBEAFE",
    "canvas": "#F4F7FB",
    "surface": "#FFFFFF",
    "surface_muted": "#EAF0F8",
    "surface_hover": "#F1F5FA",
    "text": "#172033",
    "text_secondary": "#526078",
    "text_muted": "#64748B",
    "border": "#D9E2EF",
    "border_soft": "#DDE6F2",
    "border_strong": "#CBD7E6",
    "danger": "#C93C37",
    "danger_soft": "#FFF0EF",
}


MAIN_WINDOW_STYLE = f"""
QMainWindow#mainWindow {{
    background: {COLORS['canvas']};
    color: {COLORS['text']};
    font-family: {FONT_FAMILY};
    font-size: 13px;
}}
QWidget#mainContent {{ background: {COLORS['canvas']}; }}
QFrame#toolBarCard, QFrame#tableCard, QFrame#statusCard {{
    background: {COLORS['surface']};
    border: 1px solid {COLORS['border_soft']};
    border-radius: 10px;
}}
QLabel#workspaceTitle {{
    color: {COLORS['text']};
    font-size: 16px;
    font-weight: 600;
}}
QLabel#workspaceSubtitle, QLabel#statusCaption {{ color: {COLORS['text_muted']}; }}
QLabel#itemCountBadge {{
    color: {COLORS['primary_hover']};
    background: {COLORS['primary_soft']};
    border-radius: 9px;
    padding: 3px 9px;
    font-weight: 600;
}}
QLabel#emptyState {{
    color: {COLORS['text_muted']};
    background: {COLORS['surface']};
    padding: 24px;
}}
QLabel[objectName="work dir display"] {{ color: {COLORS['text_secondary']}; }}
QPushButton {{
    min-height: 30px;
    padding: 3px 13px;
    border: 1px solid {COLORS['border_strong']};
    border-radius: 7px;
    background: {COLORS['surface']};
    color: {COLORS['text']};
}}
QPushButton:hover {{ background: {COLORS['surface_muted']}; border-color: #94A9C4; }}
QPushButton:pressed {{ background: #DCE6F3; }}
QPushButton:focus {{ border: 1px solid {COLORS['primary']}; }}
QPushButton:disabled {{ color: #9AA7B8; background: #F3F6FA; border-color: #E1E7EF; }}
QPushButton#primaryButton {{
    color: #FFFFFF;
    background: {COLORS['primary']};
    border-color: {COLORS['primary']};
    font-weight: 600;
}}
QPushButton#primaryButton:hover {{ background: {COLORS['primary_hover']}; }}
QPushButton#primaryButton:pressed {{ background: {COLORS['primary_pressed']}; }}
QPushButton#quietButton {{ color: {COLORS['text_secondary']}; background: transparent; border-color: transparent; }}
QPushButton#quietButton:hover {{ color: {COLORS['primary_hover']}; background: {COLORS['surface_muted']}; }}
QTableView#fileTable {{
    background: {COLORS['surface']};
    alternate-background-color: #F8FAFD;
    border: none;
    color: {COLORS['text']};
    gridline-color: #E8EDF4;
    selection-background-color: {COLORS['primary_soft']};
    selection-color: {COLORS['primary_hover']};
    outline: none;
}}
QTableView#fileTable::item {{ padding: 7px 9px; border-bottom: 1px solid #EDF1F6; }}
QTableView#fileTable::item:hover {{ background: #EEF5FF; }}
QTableView#fileTable::item:selected {{ background: {COLORS['primary_soft']}; color: {COLORS['primary_hover']}; }}
QHeaderView::section {{
    background: #F3F6FA;
    color: {COLORS['text_secondary']};
    border: none;
    border-right: 1px solid #E4EAF2;
    border-bottom: 1px solid {COLORS['border']};
    padding: 8px 10px;
    font-weight: 600;
}}
QTableCornerButton::section {{ background: #F3F6FA; border: none; border-bottom: 1px solid {COLORS['border']}; }}
QSplitter#workspaceSplitter::handle {{ background: {COLORS['canvas']}; width: 7px; }}
QSplitter#workspaceSplitter::handle:hover {{ background: {COLORS['primary_soft']}; }}
QMenuBar {{ background: {COLORS['surface']}; color: {COLORS['text']}; border-bottom: 1px solid {COLORS['border']}; padding: 2px 8px; }}
QMenuBar::item {{ padding: 6px 10px; border-radius: 5px; }}
QMenuBar::item:selected {{ background: {COLORS['surface_muted']}; color: {COLORS['primary_hover']}; }}
QMenu {{ background: {COLORS['surface']}; color: {COLORS['text']}; border: 1px solid {COLORS['border']}; padding: 5px; }}
QMenu::item {{ padding: 7px 28px 7px 10px; border-radius: 5px; }}
QMenu::item:selected {{ background: {COLORS['primary_soft']}; color: {COLORS['primary_hover']}; }}
QMenu::separator {{ height: 1px; background: {COLORS['border_soft']}; margin: 5px 8px; }}
"""


TAG_PANEL_STYLE = f"""
QFrame#tagPanel {{
    background: {COLORS['canvas']};
    border-left: 1px solid {COLORS['border']};
    color: {COLORS['text']};
    font-family: {FONT_FAMILY};
    font-size: 13px;
}}
QLabel#tagPanelTitle {{ font-size: 20px; font-weight: 600; color: {COLORS['text']}; }}
QLabel#tagPanelSubtitle {{ color: {COLORS['text_muted']}; font-size: 12px; }}
QFrame#tagCard {{ background: {COLORS['surface']}; border: 1px solid {COLORS['border_soft']}; border-radius: 10px; }}
QLabel#sectionTitle {{ font-size: 15px; font-weight: 600; color: {COLORS['text']}; }}
QLabel#currentFileLabel {{ color: {COLORS['text_secondary']}; background: {COLORS['surface_muted']}; border-radius: 6px; padding: 7px; }}
QLabel#countBadge {{ color: {COLORS['primary_hover']}; background: {COLORS['primary_soft']}; border-radius: 8px; padding: 2px 7px; font-weight: 600; }}
QLabel#emptyHint {{ color: {COLORS['text_muted']}; padding: 8px 2px; }}
QPushButton {{ min-height: 26px; padding: 2px 10px; border-radius: 6px; border: 1px solid {COLORS['border_strong']}; background: {COLORS['surface']}; color: {COLORS['text']}; }}
QPushButton:hover {{ background: {COLORS['surface_muted']}; border-color: #94A9C4; }}
QPushButton:pressed {{ background: #DCE6F3; }}
QPushButton:focus {{ border-color: {COLORS['primary']}; }}
QPushButton:disabled {{ color: #9AA7B8; background: #F3F6FA; border-color: #E1E7EF; }}
QPushButton#primaryButton {{ color: #FFFFFF; background: {COLORS['primary']}; border-color: {COLORS['primary']}; font-weight: 600; }}
QPushButton#primaryButton:hover {{ background: {COLORS['primary_hover']}; }}
QPushButton#primaryButton:pressed {{ background: {COLORS['primary_pressed']}; }}
QPushButton#quietButton {{ color: {COLORS['text_secondary']}; background: transparent; border-color: transparent; }}
QPushButton#quietButton:hover {{ color: {COLORS['primary_hover']}; background: {COLORS['surface_muted']}; }}
QGroupBox {{ margin-top: 10px; padding-top: 8px; border: 1px solid #E1E8F2; border-radius: 7px; font-weight: 600; color: {COLORS['text_secondary']}; }}
QGroupBox::title {{ subcontrol-origin: margin; left: 8px; padding: 0 4px; }}
QCheckBox, QRadioButton {{ spacing: 7px; color: {COLORS['text']}; font-weight: 400; }}
QCheckBox:hover, QRadioButton:hover {{ color: {COLORS['primary_hover']}; }}
QScrollArea {{ background: transparent; }}
"""


TAG_DIALOG_STYLE = f"""
QDialog {{ background: {COLORS['canvas']}; color: {COLORS['text']}; font-family: {FONT_FAMILY}; font-size: 13px; }}
QLabel#dialogTitle {{ font-size: 20px; font-weight: 600; color: {COLORS['text']}; }}
QLabel#dialogDescription {{ color: {COLORS['text_secondary']}; padding-bottom: 8px; }}
QTreeWidget {{ background: {COLORS['surface']}; border: 1px solid {COLORS['border']}; border-radius: 8px; alternate-background-color: #F7F9FC; outline: none; }}
QTreeWidget::item {{ min-height: 28px; padding: 2px 4px; }}
QTreeWidget::item:hover {{ background: #EEF5FF; }}
QTreeWidget::item:selected {{ background: {COLORS['primary_soft']}; color: {COLORS['primary_hover']}; }}
QHeaderView::section {{ background: #F3F6FA; color: {COLORS['text_secondary']}; border: none; border-bottom: 1px solid {COLORS['border']}; padding: 7px; font-weight: 600; }}
QPushButton {{ min-height: 28px; padding: 2px 12px; border: 1px solid {COLORS['border_strong']}; border-radius: 6px; background: {COLORS['surface']}; color: {COLORS['text']}; }}
QPushButton:hover {{ background: {COLORS['surface_muted']}; }}
QPushButton:pressed {{ background: #DCE6F3; }}
QPushButton:focus {{ border-color: {COLORS['primary']}; }}
QPushButton:disabled {{ color: #9AA7B8; background: #F3F6FA; border-color: #E1E7EF; }}
QPushButton#primaryButton {{ color: #FFFFFF; background: {COLORS['primary']}; border-color: {COLORS['primary']}; font-weight: 600; }}
QPushButton#primaryButton:hover {{ background: {COLORS['primary_hover']}; }}
QPushButton#dangerButton {{ color: {COLORS['danger']}; border-color: #E5B4B1; }}
QPushButton#dangerButton:hover {{ background: {COLORS['danger_soft']}; }}
"""
