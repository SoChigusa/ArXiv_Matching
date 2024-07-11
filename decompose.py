from bs4 import BeautifulSoup

# Load and parse the HTML file
file_path = "Personal_arXiv_Adviser/High Energy Physics - Phenomenology.html"
with open(file_path, "r", encoding="utf-8") as file:
    soup = BeautifulSoup(file, "html.parser")

# Extract all <dt> and <dd> elements
papers = soup.find_all(['dt', 'dd'])

# Generate individual files for each paper
for i in range(0, len(papers), 2):
    paper_dt = papers[i]
    paper_dd = papers[i + 1]
    # Extracting serial number from 'name' attribute
    serial_number = paper_dt.a['name'][4:]
    file_name = f"Personal_arXiv_Adviser/output/new_paper_{serial_number}.html"

    with open(file_name, "w", encoding="utf-8") as file:
        file.write(f"<html><body>{str(paper_dt)}{str(paper_dd)}</body></html>")

print("Individual paper files created successfully.")
