from flask import Flask, render_template, request, redirect, url_for
import xml.etree.ElementTree as ET
import os
import datetime
import requests

app = Flask(__name__)

# XML dosyasının yolu
XML_FILE = "web_sources.xml"
TXT_REPORT_DIR = "reports"

# Rapor klasörü yoksa oluştur
os.makedirs(TXT_REPORT_DIR, exist_ok=True)

# URL erişilebilirlik kontrolü fonksiyonu
def check_url_accessibility(url):
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except Exception:
        return False

# Ana sayfa
@app.route('/')
def index():
    return render_template('index.html')

# Yeni kaynak ekleme
@app.route('/add_source', methods=['GET', 'POST'])
def add_source():
    if request.method == 'POST':
        # Form verilerini al
        source_id = request.form['source_id']
        source_name = request.form['source_name']
        source_details = request.form['source_details']
        source_url = request.form['source_url']
        timestamp = datetime.datetime.now().isoformat()

        # XML dosyası yoksa oluştur
        if not os.path.exists(XML_FILE):
            root = ET.Element('WebSources')
            tree = ET.ElementTree(root)
            tree.write(XML_FILE)

        # Yeni kaynak ekle
        tree = ET.parse(XML_FILE)
        root = tree.getroot()
        source = ET.SubElement(root, 'Source')
        ET.SubElement(source, 'ID').text = source_id
        ET.SubElement(source, 'Name').text = source_name
        ET.SubElement(source, 'Details').text = source_details
        ET.SubElement(source, 'URL').text = source_url
        ET.SubElement(source, 'Timestamp').text = timestamp
        tree.write(XML_FILE)

        return redirect(url_for('index'))
    return render_template('add_source.html')

# Rapor oluşturma
@app.route('/generate_report')
def generate_report():
    if not os.path.exists(XML_FILE):
        return "XML dosyası bulunamadı. Lütfen önce kaynak ekleyin."

    tree = ET.parse(XML_FILE)
    root = tree.getroot()

    report_lines = []
    for source in root.findall('Source'):
        source_id = source.find('ID').text
        source_name = source.find('Name').text
        source_url = source.find('URL').text
        is_accessible = check_url_accessibility(source_url)
        status = "kaynak erişilebilir durumda" if is_accessible else "Aradığınız kaynak erişilemez"
        report_lines.append(f"ID: {source_id}, Name: {source_name}, URL: {source_url}, Status: {status}")

    # Raporu TXT dosyasına kaydet
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = os.path.join(TXT_REPORT_DIR, f"report_{timestamp}.txt")
    with open(report_path, 'w') as report_file:
        report_file.write("\n".join(report_lines))

    return render_template('report.html', report_lines=report_lines, report_path=report_path)

if __name__ == '__main__':
    app.run(debug=True)
