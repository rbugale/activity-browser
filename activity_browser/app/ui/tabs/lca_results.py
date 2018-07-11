# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets

from ..style import horizontal_line, header
from ..tables import LCAResultsTable
from ..graphics import (
    CorrelationPlot,
    LCAResultsPlot,
    ProcessContributionPlot,
    ElementaryFlowContributionPlot
)
from ...bwutils.multilca import MLCA
from ...bwutils import commontasks as bc
from ...signals import signals

from PyQt5.QtWidgets import QTabWidget, QVBoxLayout, QScrollArea


class ImpactAssessmentTab(QtWidgets.QWidget):
    def __init__(self, parent):
        super(ImpactAssessmentTab, self).__init__(parent)
        self.panel = parent  # e.g. right panel
        self.setVisible(False)
        self.visible = False

        # Calculate the LCA data
        self.single_lca = bool
        self.single_method = bool
        self.calculate_data()

        # Generate tabs
        self.tabs = QTabWidget()
        self.tabs.setTabShape(1)  # Triangular-shaped Tabs
        self.tabs.setTabPosition(1)  # South-facing Tabs
        self.tab1 = QScrollArea()
        self.tab2 = QScrollArea()
        self.tab3 = QScrollArea()
        self.tab4 = QScrollArea()

        # Name tabs
        self.tabs.addTab(self.tab1, "LCIA Results")
        self.tabs.addTab(self.tab2, "Process Contributions")
        self.tabs.addTab(self.tab3, "Elementary Flow Contributions")
        self.tabs.addTab(self.tab4, "Correlations")

        # Comboboxes
        self.combo_process_cont_methods = QtWidgets.QComboBox()
        self.combo_process_cont_methods.scroll = False
        self.combo_flow_cont_methods = QtWidgets.QComboBox()
        self.combo_flow_cont_methods.scroll = False

        # Plots & Table
        self.results_plot = LCAResultsPlot(self)
        self.correlation_plot = CorrelationPlot(self)
        self.process_contribution_plot = ProcessContributionPlot(self)
        self.elementary_flow_contribution_plot = ElementaryFlowContributionPlot(self)
        self.results_table = LCAResultsTable()

        # Buttons
        self.to_clipboard_button = QtWidgets.QPushButton('Copy')
        self.to_csv_button = QtWidgets.QPushButton('.csv')
        self.to_excel_button = QtWidgets.QPushButton('Excel')

        self.to_png_button = QtWidgets.QPushButton('png')
        self.to_svg_button = QtWidgets.QPushButton('svg')

        self.button_area = QtWidgets.QScrollArea()
        self.button_widget = QtWidgets.QWidget()
        self.button_widget_layout = QtWidgets.QVBoxLayout()

        self.button_widget.setLayout(self.button_widget_layout)
        self.button_area.setWidget(self.button_widget)
        self.button_area.setWidgetResizable(True)
        self.button_area.setFixedHeight(44)  # This is ugly, how do we make this automatic?
        self.layout = QtWidgets.QVBoxLayout()
        
        # Testing
        self.b_group = QtWidgets.QVBoxLayout()

        # Generate layout & Connect
        self.make_layout()
        self.connect_signals()
        self.setLayout(self.layout)

    def calculate_data(self):
        """Call remove_tab() and calculate()."""
        signals.project_selected.connect(self.remove_tab)
        signals.lca_calculation.connect(self.calculate)

    def connect_signals(self):
        """Connect all signals relevant to LCA Results tab."""
        self.combo_process_cont_methods.currentTextChanged.connect(
            lambda name: self.get_process_contribution(method=name))
        self.combo_flow_cont_methods.currentTextChanged.connect(
            lambda name: self.get_flow_contribution(method=name))
        self.to_clipboard_button.clicked.connect(self.results_table.to_clipboard)
        self.to_csv_button.clicked.connect(self.results_table.to_csv)
        self.to_excel_button.clicked.connect(self.results_table.to_excel)
        self.to_png_button.clicked.connect(self.results_plot.to_png)
        self.to_svg_button.clicked.connect(self.results_plot.to_svg)

    def create_tab(self, tab_name, Widgets):
        tab_name.layout = QVBoxLayout()
        self.tabscroll = QtWidgets.QScrollArea()
        header_height = 17
        Widgets[0].setFixedHeight(header_height)
        if len(Widgets) == 8:
            Widgets[3].setFixedHeight(header_height)
            Widgets[6].setFixedHeight(header_height)

        self.group = QVBoxLayout()
        for i in Widgets:
            self.group.addWidget(i)
        self.tabwidget = QtWidgets.QGroupBox()
        self.tabwidget.setLayout(self.group)
        self.tabscroll.setWidget(self.tabwidget)
        self.tabscroll.setWidgetResizable(True)

        tab_name.layout.addWidget(self.tabscroll)
        tab_name.setLayout(tab_name.layout)
        return ()

    def generate_tab(self, tab_name, Widgets, button_set):
        tab_name.layout = QVBoxLayout()
        self.tabscroll = QtWidgets.QVBoxLayout()

        # Add widgets
        self.w_group = QVBoxLayout()
        for i in Widgets:
            self.w_group.addWidget(i)

        # Add buttons
        self.b_group_layout = QtWidgets.QHBoxLayout()
        for i in button_set:
            self.b_group_layout.addWidget(i)
        self.b_group_layout.addStretch()
        self.b_group.addLayout(self.b_group_layout)

        if len(Widgets) > 0:
            self.tabscroll.addWidget(self.w_group)
        if len(button_set) > 0:
            self.tabscroll.addWidget(self.b_group_layout)

        self.tabscroll.setWidgetResizable(True)

        tab_name.layout.addWidget(self.tabscroll)
        tab_name.setLayout(tab_name.layout)

    def make_layout(self):
        """Make the layout for the LCA Results tab."""
        # Create export buttons
        self.buttons = QtWidgets.QHBoxLayout()
        self.buttons.addWidget(self.to_clipboard_button)
        self.buttons.addWidget(self.to_csv_button)
        self.buttons.addWidget(self.to_excel_button)
        self.buttons.addWidget(self.to_png_button)
        self.buttons.addWidget(self.to_svg_button)
        self.buttons.addStretch()

        self.button_widget_layout.addLayout(self.buttons)

        # Create first tab
        self.create_tab(self.tab1, [header("LCA Scores Plot:"), horizontal_line(), self.results_plot, \
                                    header("LCA Scores Table:"), self.results_table, horizontal_line(), \
                                    header("Export"), self.button_area])
        """

        self.generate_tab(self.tab1, [header("LCA Scores Plot:"), horizontal_line(), self.results_plot, \
                                    header("LCA Scores Table:"), self.results_table, horizontal_line(), \
                                    header("Export"), self.button_area], [self.to_clipboard_button, self.to_csv_button])"""

        # Create second tab
        self.create_tab(self.tab2, [header("Process Contributions:"), horizontal_line(), self.combo_process_cont_methods, \
                                    self.process_contribution_plot])

        # Create third tab
        self.create_tab(self.tab3, [header("Elementary Flow Contributions:"), horizontal_line(),self.combo_flow_cont_methods, \
                                   self.elementary_flow_contribution_plot])

        # Create fourth tab
        self.create_tab(self.tab4, [header("LCA Scores Correlation:"), horizontal_line(), self.correlation_plot])

        # Add tabs to widget
        self.layout.addWidget(self.tabs)

    def add_tab(self):
        """Add the LCA Results tab to the right panel of AB."""
        if not self.visible:
            self.visible = True
            self.panel.addTab(self, "LCA results")
        self.panel.select_tab(self)  # put tab to front after LCA calculation

    def remove_tab(self):
        """Remove the LCA results tab."""
        if self.visible:
            self.visible = False
            self.panel.removeTab(self.panel.indexOf(self))

    def calculate(self, name):
        """Calculate the (M)LCA."""
        # LCA Results Analysis: (ideas to implement)
        # - LCA score: Barchart (choice LCIA method)
        # - Contribution Analysis (choice process, LCIA method;
        #   THEN BY process, product, geography, ISIC sector)
        #   ALSO: Type of graph: Barchart, Treemap, Piechart, Worldmap (for geo)
        #   CUTOFF
        # - Uncertainties: Monte Carlo, Latin-Hypercube

        # Multi-LCA calculation
        self.mlca = MLCA(name)
        self.single_lca = len(self.mlca.func_units) == 1
        self.single_method = len(self.mlca.methods) == 1

        # update process and elementary flow contribution combo boxes
        self.dict_LCIA_methods_str_tuples = bc.get_LCIA_method_name_dict(self.mlca.methods)

        self.combo_process_cont_methods.clear()
        self.combo_flow_cont_methods.clear()
        self.combo_process_cont_methods.insertItems(0, self.dict_LCIA_methods_str_tuples.keys())
        self.combo_flow_cont_methods.insertItems(0, self.dict_LCIA_methods_str_tuples.keys())
        if not self.single_method:
            self.combo_process_cont_methods.setVisible(True)
            self.combo_flow_cont_methods.setVisible(True)
        else:
            self.combo_process_cont_methods.setVisible(False)
            self.combo_flow_cont_methods.setVisible(False)

        # PLOTS & TABLES

        # LCA Results Plot
        self.results_plot.plot(self.mlca)
        if not self.single_lca:
            self.results_plot.setVisible(True)
        else:
            self.results_plot.setVisible(False)

        # Contribution Analysis
        # is plotted by the combobox signal

        # Correlation Plot
        if not self.single_lca:
            labels = [str(x + 1) for x in range(len(self.mlca.func_units))]
            self.correlation_plot.plot(self.mlca, labels)
            self.correlation_plot.setVisible(True)
        else:
            self.correlation_plot.setVisible(False)

        # LCA results table
        self.results_table.sync(self.mlca)

        self.add_tab()

    def get_process_contribution(self, method=None):
        """Generate the process contribution plot."""
        if not method:
            method = next(iter(self.mlca.method_dict.keys()))
        else:
            method = self.dict_LCIA_methods_str_tuples[method]

        self.process_contribution_plot.plot(self.mlca, method=method)

    def get_flow_contribution(self, method=None):
        """Generate the Elementary flow contribution plot."""
        if not method:
            method = next(iter(self.mlca.method_dict.keys()))
        else:
            method = self.dict_LCIA_methods_str_tuples[method]

        self.elementary_flow_contribution_plot.plot(self.mlca, method=method)
