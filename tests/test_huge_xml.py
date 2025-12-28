from pathlib import Path
from smartXML.xmltree import SmartXML
import time

def test_huge_xml():
    input_file = Path('files/huge.xml')

    start_time = time.perf_counter()
    xml = SmartXML(input_file)
    elapsed_seconds = time.perf_counter() - start_time
    print(f" Loading huge XML took {elapsed_seconds:.4f} seconds")

    # Dec 26, 2025 - 2.6092 seconds
    assert elapsed_seconds < 2.7

    pass

