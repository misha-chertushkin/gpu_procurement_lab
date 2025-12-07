import xml.etree.ElementTree as ET
import sys
import os

def parse_test_results(file_path):
    """Parses a single JUnit XML file and extracts test suite summary."""
    tree = ET.parse(file_path)
    root = tree.getroot()
    testsuite = root.find('testsuite')
    if testsuite is not None:
        phase_name = os.path.basename(os.path.dirname(os.path.dirname(file_path)))
        return {
            'name': phase_name,
            'tests': int(testsuite.attrib.get('tests', 0)),
            'failures': int(testsuite.attrib.get('failures', 0)),
            'errors': int(testsuite.attrib.get('errors', 0)),
            'skipped': int(testsuite.attrib.get('skipped', 0)),
            'time': float(testsuite.attrib.get('time', 0.0)),
        }
    return None

def generate_summary_markdown(results):
    """Generates a Markdown summary from a list of test results."""
    # Sort results by phase name for consistent ordering
    results.sort(key=lambda x: x['name'])

    summary = ["# Test Summary\n\n"]
    summary.append("| Phase | Tests | Failures | Errors | Skipped | Time (s) |\n")
    summary.append("|-------|-------|----------|--------|---------|----------|\n")

    totals = {'tests': 0, 'failures': 0, 'errors': 0, 'skipped': 0, 'time': 0.0}

    for res in results:
        summary.append(
            f"| {res['name']} | {res['tests']} | {res['failures']} | "
            f"{res['errors']} | {res['skipped']} | {res['time']:.2f} |\n"
        )
        for key in totals:
            if key != 'time':
                totals[key] += res[key]
        totals['time'] += res['time']

    summary.append("\n**Totals**\n\n")
    summary.append("| Total Tests | Total Failures | Total Errors | Total Skipped | Total Time (s) |\n")
    summary.append("|-------------|----------------|--------------|---------------|----------------|\n")
    summary.append(
        f"| {totals['tests']} | {totals['failures']} | {totals['errors']} | "
        f"{totals['skipped']} | {totals['time']:.2f} |\n"
    )
    return "".join(summary)

def main(files):
    """Main function to parse files and generate summary."""
    results = []
    for f in files:
        if os.path.exists(f):
            result = parse_test_results(f)
            if result:
                results.append(result)

    if not results:
        print("No test result files found or processed.")
        return

    markdown_content = generate_summary_markdown(results)

    with open('TEST_RESULTS.md', 'w') as f:
        f.write(markdown_content)

    print("Test summary generated at TEST_RESULTS.md")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_test_summary.py <path/to/test-results.xml> ...")
        sys.exit(1)
    main(sys.argv[1:])
