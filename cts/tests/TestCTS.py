#__init__(self, path=None, rewriting_rules={}, strict=False):

import os
from nose import with_setup
from nose.tools import assert_is_instance
import cts.xml.inventory
import cts.xml.texts

basePath = os.path.dirname(os.path.abspath(__file__)) + "/test_files"
test_inventory_path = basePath + "/test_inventory.xml"
inv = cts.xml.inventory.Inventory(xml=test_inventory_path, rewriting_rules={}, strict=False)
inv_correct = cts.xml.inventory.Inventory(
    xml=test_inventory_path,
    rewriting_rules={
        "/db/repository/greekLit/tlg0003/tlg001/": basePath + "/"
    },
    strict=False
)

editionTest = """
<edition projid="greekLit:perseus-grc2">
    <label xml:lang="en">The Peloponnesian War (Oxford 1942 Epidoc)</label>
    <description xml:lang="eng">Thucydides. Historiae in two volumes. Oxford, Oxford University
      Press. 1942.</description>
    <online docname="/db/repository/greekLit/tlg0003/tlg001/tlg0003.tlg001.perseus-grc2.xml">
      <validate schema="tei-xl.xsd"/>
      <namespaceMapping abbreviation="tei" nsURI="http://www.tei-c.org/ns/1.0"/>
      <citationMapping>
        <citation label="book" xpath="/tei:div[@n='?']" scope="/tei:TEI/tei:text/tei:body/tei:div">
          <citation label="chapter" xpath="/tei:div[@n='?']" scope="/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n='?']">
            <citation label="section" xpath="/tei:div[@n='?']" scope="/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n='?']/tei:div[@n='?']"/>
          </citation>
        </citation>
      </citationMapping>
    </online>
</edition>
"""


def inventory_setup():
    pass


@with_setup(inventory_setup, None)
def TestInventoryAttributes():
    """ Test Inventory attributes are written """
    assert len(inv.textGroups) == 1
    assert len(inv.getTexts()) == 2


@with_setup(inventory_setup, None)
def TestTextGroupsAttributes():
    textgroup = inv.textGroups[0]
    assert textgroup.id == "greekLit:tlg0003"
    assert textgroup.name == "Thucydides"
    assert len(textgroup.works) == 1


@with_setup(inventory_setup, None)
def TestWorkAttributes():
    work = inv.textGroups[0].works[0]
    assert work.id == "greekLit:tlg001"
    assert work.getTitle() == "The Peloponnesian War"  # Default should be english
    assert work.getTitle("en") == "The Peloponnesian War"
    assert work.getTitle("fr") == "La guerre du Peloponnese"
    assert len(work.editions) == 1
    assert len(work.translations) == 1


@with_setup(inventory_setup, None)
def TestTranslationAttributes():
    trans = inv.textGroups[0].works[0].translations[0]
    assert trans.id == "greekLit:perseus-eng1"
    assert trans.getTitle() == "History of the Peloponnesian War (English translation by Thomas Hobbes)"  # Default should be english
    assert_is_instance(trans.document, cts.xml.texts.Document)


@with_setup(inventory_setup, None)
def TestTranslationDocumentNoRewriting():
    doc = inv.textGroups[0].works[0].translations[0].document
    assert doc.path == "/db/repository/greekLit/tlg0003/tlg001/tlg0003.tlg001.perseus-eng1.xml"  # Because no rewriting_rules


@with_setup(inventory_setup, None)
def TestTranslationDocumentCitation():
    doc = inv_correct.textGroups[0].works[0].translations[0].document
    assert doc.path == basePath + "/tlg0003.tlg001.perseus-eng1.xml"  # Because no rewriting_rules
    assert_is_instance(doc.citation, cts.xml.texts.Citation)
    results, errors = doc.testCitation()
    assert results == [True, True], "Results for Translations document citation test should be successful"
    assert "Citation Mapping (2) has label chapter, while refState[2] has unit error_creator" in [error.string for error in errors]


@with_setup(inventory_setup, None)
def TestEditionDocumentCitation():
    doc = inv_correct.textGroups[0].works[0].editions[0].document
    assert doc.path == basePath + "/tlg0003.tlg001.perseus-grc2.xml"  # Because no rewriting_rules
    assert_is_instance(doc.citation, cts.xml.texts.Citation)
    results, errors = doc.testCitation()
    assert results == [True, True, False], "Results for Translations document citation test should be successful except level 3"


def TestNamespaceURI():
    c = cts.xml.texts.Citation(
        xml="<citation label=\"chapter\" xpath=\"/tei:div2[@n='?']\" scope=\"/tei:TEI.2/tei:text/tei:body/\"/>",
        namespaces={
            "tei:": "{http://www.tei-c.org/ns/1.0}"
        }
    )
    warnings = c.testNamespaceURI(xml="""<?xml version="1.0" encoding="UTF-8"?>
<?xml-model href="http://www.stoa.org/epidoc/schema/latest/tei-epidoc.rng" schematypens="http://relaxng.org/ns/structure/1.0"?>
        <TEI>
        <teiHeader></teiHeader>
        <text></text>
        </TEI>
    """)
    assert "No namespace uri found in this document" in [warning.string for warning in warnings], "Absence of xml:ns should raise Error"

    warnings = c.testNamespaceURI(xml="""<?xml version="1.0" encoding="UTF-8"?>
<?xml-model href="http://www.stoa.org/epidoc/schema/latest/tei-epidoc.rng" schematypens="http://relaxng.org/ns/structure/1.0"?>
        <TEI xmlns="http://google.fr">
        <teiHeader></teiHeader>
        <text></text>
        </TEI>
    """)
    assert "Wrong namespace URI found" in [warning.string for warning in warnings], "Not in self.namespaces xml:ns should raise Error"

    warnings = c.testNamespaceURI(xml="""<?xml version="1.0" encoding="UTF-8"?>
<?xml-model href="http://www.stoa.org/epidoc/schema/latest/tei-epidoc.rng" schematypens="http://relaxng.org/ns/structure/1.0"?>
        <TEI xmlns="http://www.tei-c.org/ns/1.0">
        <teiHeader></teiHeader>
        <text></text>
        </TEI>
    """)
    assert len(warnings) == 0, "Good formated xmlns should not raise Error"


def TestNamespaceWarnings():
    #Test when there is one element with no namespace
    c = cts.xml.texts.Citation(
        xml="<citation label=\"chapter\" xpath=\"/tei:div2[@n='?']\" scope=\"/TEI.2/tei:text/tei:body/\"/>",
        namespaces={
            "tei:": "{http://www.tei-c.org/ns/1.0}"
        }
    )
    errors = [e.string for e in c.testNamespace()]
    assert len(errors) == 1, "Scope with no namespace shortcut should raise an error"
    assert "has no namespaces shortcuts like 'tei:'" in errors[0], "Scope with no namespace shortcut in xPath should have a message about it"

    #Test when there is one element with unknown namespace
    c = cts.xml.texts.Citation(
        xml="<citation label=\"chapter\" xpath=\"/tei:div2[@n='?']\" scope=\"/google:TEI.2/tei:text/tei:body/\"/>",
        namespaces={
            "tei:": "{http://www.tei-c.org/ns/1.0}"
        }
    )
    errors = [e.string for e in c.testNamespace()]
    assert len(errors) == 1, "Scope with unknown namespace shortcut in xPath"
    assert "has namespaces shortcuts with no bindings" in errors[0], "Scope with unknown namespace shortcut in xPath should have a message about it"

    #Test when there is one element with no namespace
    c = cts.xml.texts.Citation(
        xml="<citation label=\"chapter\" xpath=\"/div2[@n='?']\" scope=\"/tei:TEI.2/tei:text/tei:body/\"/>",
        namespaces={
            "tei:": "{http://www.tei-c.org/ns/1.0}"
        }
    )
    errors = [e.string for e in c.testNamespace()]
    assert len(errors) == 1, "xpath with no namespace shortcut should raise an error"
    assert "has no namespaces shortcuts like 'tei:'" in errors[0], "xpath with no namespace shortcut in xPath should have a message about it"

    #Test when there is one element with unknown namespace
    c = cts.xml.texts.Citation(
        xml="<citation label=\"chapter\" xpath=\"/google:div2[@n='?']\" scope=\"/tei:TEI.2/tei:text/tei:body/\"/>",
        namespaces={
            "tei:": "{http://www.tei-c.org/ns/1.0}"
        }
    )
    errors = [e.string for e in c.testNamespace()]
    assert len(errors) == 1, "xpath with unknown namespace shortcut in xPath"
    assert "has namespaces shortcuts with no bindings" in errors[0], "xpath with unknown namespace shortcut in xPath should have a message about it"

    #Test when there is one element with unknown namespace
    c = cts.xml.texts.Citation(
        xml="<citation label=\"chapter\" xpath=\"/tei:div2[@n='?']\" scope=\"/tei:TEI.2/tei:text/tei:body/\"/>",
        namespaces={
            "tei:": "{http://www.tei-c.org/ns/1.0}"
        }
    )
    errors = [e.string for e in c.testNamespace()]
    assert len(errors) == 0, "Correct xpath and scope should not raise error"