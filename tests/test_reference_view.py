"""Repeated relationship summaries retain navigation to each actual use."""
import copy
import os
from pathlib import Path
from unittest import TestCase
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QTreeWidget
from rcm.campaign_document import CampaignDocument
from rcm.campaign_relations import graph
from rcm.editor import i18n
from rcm.editor.deletion import DeleteDialog
from rcm.editor.reference_view import grouped_links
from rcm.editor.window import MainWindow
from rcm.paths import Workspace
from rcm.safe_edit import deletion_plan
from rcm.service import Backend
from test_release10 import blank

ROOT = Path(__file__).resolve().parents[1]
ROLE = Qt.ItemDataRole.UserRole


class ReferenceViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.backend = Backend(Workspace(ROOT))
        cls.backend.safe_mode = True

    def setUp(self):
        root = blank()
        scene = root['scenes'][0]
        scene['actors'] = [dict(id='npc', name='NPC', template='Anezka',
                               transform=dict(position=[0, 0, 384], orientation=[0, 0, 0]))]
        scene['conversations'] = [dict(id='intro', speaker='npc', entry='opening', nodes=[
            dict(id='opening', lines=[dict(speaker='npc', text='First line'),
                                     dict(speaker='npc', text='Second line')],
                 choices=[dict(text='Leave', result=1, actions=[dict(enable_ai='npc')])])])]
        self.win = MainWindow(self.backend)
        self.win.doc = CampaignDocument(self.backend.ws, root)
        self.win.refresh()
        self.before = copy.deepcopy(root)

    def tearDown(self):
        self.win.doc = None
        self.win.close()
        self.app.processEvents()

    def test_graph_keeps_all_uses_and_groups_only_matching_relationships(self):
        links = [l for l in graph(self.before) if l.target == ('scenes', 0, 'actors', 0)]
        self.assertEqual(len(links), 4)
        groups = grouped_links(links + links)
        self.assertEqual([len(g) for g in groups], [3, 1])
        self.assertEqual(len({l.detail for l in groups[0]}), 3)

    def test_search_groups_summary_and_opens_each_exact_use(self):
        self.win.find_references(('actors', 0))
        incoming = self.win.reference_tree.topLevelItem(0)
        self.assertEqual(incoming.childCount(), 2)
        summary = incoming.child(0)
        self.assertIn('(3 ', summary.text(0))
        self.assertEqual(summary.childCount(), 3)
        self.assertIn('First line', summary.toolTip(0))
        for n, destination in enumerate([('conversations', 0),
                                        ('conversations', 0, 'nodes', 0, 'lines', 0),
                                        ('conversations', 0, 'nodes', 0, 'lines', 1)]):
            child = summary.child(n)
            self.win.navigate_reference(child.data(0, ROLE))
            self.assertEqual(self.win.selection, destination)
        self.assertEqual(self.win.doc.snapshot(), self.before)

    def test_inspector_groups_in_both_directions_and_labels_actions(self):
        self.win.select(('actors', 0))
        incoming = self.win.properties.widget().findChild(QTreeWidget, 'incoming_references')
        self.assertEqual(incoming.topLevelItemCount(), 2)
        self.assertEqual(incoming.topLevelItem(0).childCount(), 3)
        self.win.select(('conversations', 0))
        outgoing = self.win.properties.widget().findChild(QTreeWidget, 'outgoing_references')
        self.assertEqual(outgoing.topLevelItemCount(), 2)
        self.assertNotIn('enable_ai', outgoing.topLevelItem(1).text(0))
        self.assertEqual(outgoing.topLevelItem(0).data(0, ROLE), ('scenes', 0, 'actors', 0))

    def test_delete_review_groups_uses_without_weakening_cascade(self):
        path = ('scenes', 0, 'actors', 0)
        plan = deletion_plan(self.win.doc, path, self.backend)
        dialog = DeleteDialog(self.win, path, plan)
        self.assertEqual(dialog.references.topLevelItemCount(), 2)
        summary = dialog.references.topLevelItem(0)
        self.assertEqual(summary.childCount(), 3)
        dialog.references.setCurrentItem(summary.child(1))
        dialog.go()
        self.assertEqual(dialog.destination, ('scenes', 0, 'conversations', 0, 'nodes', 0, 'lines', 0))
        self.assertFalse(plan.candidate['scenes'][0]['actors'])
        self.assertFalse(plan.candidate['scenes'][0]['conversations'])
        self.assertEqual(self.win.doc.snapshot(), self.before)
        dialog.deleteLater()

    def test_group_labels_switch_language_without_translating_dialogue(self):
        old = i18n._language
        try:
            for language, suffix in [('es', 'usos'), ('en', 'uses')]:
                i18n._language = language
                self.win.find_references(('actors', 0))
                item = self.win.reference_tree.topLevelItem(0).child(0)
                self.assertIn('(3 ' + suffix + ')', item.text(0))
                self.assertIn('First line', item.toolTip(0))
        finally:
            i18n._language = old
