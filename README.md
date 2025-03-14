# Payroll PDF Extractor

A Streamlit application for extracting and processing certified payroll data from PDF files. This tool allows users to upload certified payroll PDFs, extract the data, and convert it to a wide-table format according to custom templates.

![Payroll PDF Extractor](https://via.placeholder.com/800x450.png?text=Payroll+PDF+Extractor)

## Features

- **PDF Extraction**: Extract data from certified payroll register PDFs
- **Template System**: Select from various output templates or create your own
- **Field Mapping**: Customize field mappings between source PDFs and output templates
- **Data Visualization**: View and verify extracted data before download
- **Export Options**: Download extracted data as CSV files

## Installation

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/payroll-pdf-extractor.git
   cd payroll-pdf-extractor
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   streamlit run main.py
   ```

### Docker Deployment

1. Build the Docker image:
   ```bash
   docker build -t payroll-pdf-extractor .
   ```

2. Run the container:
   ```bash
   docker run -p 8501:8501 payroll-pdf-extractor
   ```

3. Access the application at `http://localhost:8501`

### CoreOS / Caddy Deployment

To deploy on a CoreOS server running Caddy:

1. Create a container definition for your container orchestration system (e.g., Docker Compose, Kubernetes):
   ```yaml
   # docker-compose.yml example
   version: '3'
   services:
     payroll-extractor:
       image: ghcr.io/yourusername/payroll-pdf-extractor:latest
       restart: unless-stopped
       ports:
         - "8501:8501"
       volumes:
         - ./templates:/app/templates
         - ./mappings:/app/mappings
   ```

2. Configure Caddy to reverse proxy to the Streamlit application:
   ```
   # Caddyfile example
   payroll.yourdomain.com {
       reverse_proxy localhost:8501
   }
   ```

## Usage

1. **Upload PDF**: Click "Browse files" to upload a certified payroll PDF
2. **Select Template**: Choose a template from the sidebar
3. **View Results**: Examine the extracted data in the table
4. **Download Data**: Click the "Download CSV" button to export the data

## Creating Custom Templates

### Template Files

Templates are CSV files that define the output structure. Each column header represents a field in the output data.

1. Create a new CSV file in the `templates` directory (e.g., `custom_template.csv`)
2. Add column headers for your desired output fields
3. Save the file

### Mapping Files

Mapping files connect template fields to fields extracted from the PDF. They are JSON files stored in the `mappings` directory.

1. Create a new JSON file with the same name as your template (e.g., `custom_template.json`)
2. Define mappings between template fields and PDF fields:
   ```json
   {
     "TemplateField1": "pdf_field1",
     "TemplateField2": "pdf_field2",
     "TemplateField3": "pdf_field3"
   }
   ```
3. Save the file

## Available PDF Fields

When creating mappings, you can reference these extracted PDF fields:

- `name`: Employee name
- `ssn`: Social Security Number
- `address`: Street address
- `city`: City
- `state`: State
- `zip`: ZIP code
- `job_class`: Job classification
- `marital_status`: Marital status
- `regular_hours`: Regular hours worked
- `overtime_hours`: Overtime hours worked
- `pay_rate`: Hourly pay rate
- `gross_pay`: Gross pay
- `federal_tax`: Federal tax
- `net_pay`: Net pay
- `total_deductions`: Total deductions
- Various benefit fields: `amf_494_rate`, `amf_494_amount`, `annuity_rate`, etc.
- `dues_amount`: Union dues amount
- Job information: `job_name`, `job_number`, `week_ending`, etc.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Streamlit](https://streamlit.io/) - The web framework used
- [pdfplumber](https://github.com/jsvine/pdfplumber) - PDF text extraction library
- [pandas](https://pandas.pydata.org/) - Data manipulation library
