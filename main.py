import streamlit as st
import pandas as pd
import os
import json
import tempfile
import base64
from pathlib import Path
from typing import Dict, List, Any

# Import the PDF parser
from pdf_parser import PayrollPDFParser

# Set up page configuration
st.set_page_config(
    page_title="Payroll PDF Extractor",
    page_icon="📊",
    layout="wide"
)

# Application styling
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .header {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 2rem;
    }
    .title {
        color: #0066cc;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        color: #666;
        font-size: 1.2rem;
        font-weight: 400;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #ddd;
    }
    .info-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .stButton > button {
        width: 100%;
    }
    .download-btn {
        margin-top: 1rem;
        padding: 0.5rem 1rem;
        background-color: #4CAF50;
        color: white;
        text-decoration: none;
        border-radius: 0.25rem;
        font-weight: 600;
        display: inline-block;
    }
    .download-btn:hover {
        background-color: #45a049;
    }
</style>
""", unsafe_allow_html=True)

# Directory paths
TEMPLATES_DIR = Path("templates")
MAPPINGS_DIR = Path("mappings")

# Ensure directories exist
TEMPLATES_DIR.mkdir(exist_ok=True)
MAPPINGS_DIR.mkdir(exist_ok=True)


def load_templates() -> Dict[str, Path]:
    """Load available templates from templates directory"""
    templates = {}
    for filename in TEMPLATES_DIR.glob("*.csv"):
        template_name = filename.stem
        templates[template_name] = filename
    return templates


def load_mappings() -> Dict[str, Dict[str, str]]:
    """Load field mappings from mappings directory"""
    mappings = {}
    for filename in MAPPINGS_DIR.glob("*.json"):
        mapping_name = filename.stem
        with open(filename, 'r') as f:
            mappings[mapping_name] = json.load(f)
    return mappings


def create_default_templates():
    """Create default templates and mappings if none exist"""
    # Default template
    if not (TEMPLATES_DIR / "default.csv").exists():
        default_columns = [
            "EmployeeName", "SSN", "Address", "City", "State", "PayRate", 
            "RegularHours", "OvertimeHours", "GrossPay", "NetPay"
        ]
        pd.DataFrame(columns=default_columns).to_csv(
            TEMPLATES_DIR / "default.csv", index=False
        )
        
        # Default mapping
        default_mapping = {
            "EmployeeName": "name",
            "SSN": "ssn",
            "Address": "address",
            "City": "city",
            "State": "state",
            "PayRate": "pay_rate",
            "RegularHours": "regular_hours",
            "OvertimeHours": "overtime_hours",
            "GrossPay": "gross_pay",
            "NetPay": "net_pay"
        }
        
        with open(MAPPINGS_DIR / "default.json", "w") as f:
            json.dump(default_mapping, f, indent=2)
    
    # WISDOT template
    if not (TEMPLATES_DIR / "wisdot.csv").exists():
        wisdot_columns = [
            "EmployeeName", "SSN", "Address", "City", "State", "MaritalStatus",
            "JobClass", "PayRate", "RegularHours", "OvertimeHours", "GrossPay",
            "NetPay", "TotalDeductions", "AMF494Rate", "AMF494Amount", 
            "AnnuityRate", "AnnuityAmount", "HWRate", "HWAmount", "PensionRate",
            "PensionAmount", "DuesAmount", "JobName", "JobNumber", "WeekEnding"
        ]
        pd.DataFrame(columns=wisdot_columns).to_csv(
            TEMPLATES_DIR / "wisdot.csv", index=False
        )
        
        # WISDOT mapping
        wisdot_mapping = {
            "EmployeeName": "name",
            "SSN": "ssn",
            "Address": "address",
            "City": "city",
            "State": "state",
            "MaritalStatus": "marital_status",
            "JobClass": "job_class",
            "PayRate": "pay_rate",
            "RegularHours": "regular_hours",
            "OvertimeHours": "overtime_hours",
            "GrossPay": "gross_pay",
            "NetPay": "net_pay",
            "TotalDeductions": "total_deductions",
            "AMF494Rate": "amf_494_rate",
            "AMF494Amount": "amf_494_amount",
            "AnnuityRate": "annuity_rate",
            "AnnuityAmount": "annuity_amount",
            "HWRate": "h_and_w_rate",
            "HWAmount": "h_and_w_amount",
            "PensionRate": "pension_rate",
            "PensionAmount": "pension_amount",
            "DuesAmount": "dues_amount",
            "JobName": "job_name",
            "JobNumber": "job_number",
            "WeekEnding": "week_ending"
        }
        
        with open(MAPPINGS_DIR / "wisdot.json", "w") as f:
            json.dump(wisdot_mapping, f, indent=2)


def map_fields(employees: List[Dict[str, Any]], mapping: Dict[str, str]) -> List[Dict[str, Any]]:
    """Map extracted fields to template fields according to mapping"""
    mapped_data = []
    
    for employee in employees:
        mapped_employee = {}
        for template_field, pdf_field in mapping.items():
            if pdf_field in employee:
                mapped_employee[template_field] = employee[pdf_field]
            else:
                # Field not found, set to empty string or value
                mapped_employee[template_field] = ""
        
        mapped_data.append(mapped_employee)
    
    return mapped_data


def get_download_link(df: pd.DataFrame, filename: str = "extracted_payroll_data.csv") -> str:
    """Generate a download link for a DataFrame"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}" class="download-btn">Download CSV</a>'
    return href


def main():
    """Main application function"""
    # App header
    st.markdown('<div class="header">', unsafe_allow_html=True)
    st.markdown('<div class="title">Payroll PDF Extractor</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Extract and process certified payroll data from PDF files</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Create default templates if needed
    create_default_templates()
    
    # Load templates and mappings
    templates = load_templates()
    mappings = load_mappings()
    
    # Sidebar for template selection
    st.sidebar.markdown('<div class="section-header">Template Selection</div>', unsafe_allow_html=True)
    
    template_names = list(templates.keys())
    selected_template = st.sidebar.selectbox(
        "Select an output template:",
        template_names,
        index=template_names.index("wisdot") if "wisdot" in template_names else 0
    )
    
    # Display template information
    if selected_template:
        st.sidebar.markdown('<div class="section-header">Template Fields</div>', unsafe_allow_html=True)
        template_df = pd.read_csv(templates[selected_template])
        for column in template_df.columns:
            pdf_field = mappings[selected_template].get(column, "Not mapped")
            st.sidebar.markdown(f"- **{column}** → *{pdf_field}*")
    
    # File upload section
    st.markdown('<div class="section-header">Upload Payroll PDF</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="info-box">Upload a certified payroll PDF file to extract the data. '
        'The file will be processed according to the selected template.</div>',
        unsafe_allow_html=True
    )
    
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
    
    if uploaded_file is not None:
        # Save the uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(uploaded_file.getvalue())
            temp_path = temp_file.name
        
        try:
            # Process the PDF file
            with st.spinner("Extracting data from PDF..."):
                # Parse the PDF
                parser = PayrollPDFParser(temp_path)
                parsed_data = parser.parse()
                
                if parsed_data["employees"]:
                    # Map fields according to selected template
                    if selected_template in mappings:
                        mapped_data = map_fields(
                            parsed_data["employees"], 
                            mappings[selected_template]
                        )
                        
                        # Create DataFrame from mapped data
                        df = pd.DataFrame(mapped_data)
                        
                        # Display extraction summary
                        st.markdown('<div class="section-header">Extraction Summary</div>', unsafe_allow_html=True)
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Employees Extracted", len(parsed_data["employees"]))
                        with col2:
                            st.metric("Job Number", parsed_data["job_info"].get("job_number", "N/A"))
                        with col3:
                            st.metric("Week Ending", parsed_data["job_info"].get("week_ending", "N/A"))
                        
                        # Display extracted data
                        st.markdown('<div class="section-header">Extracted Data</div>', unsafe_allow_html=True)
                        st.dataframe(df)
                        
                        # Provide download link
                        st.markdown(get_download_link(df), unsafe_allow_html=True)
                    else:
                        st.error(f"Mapping for template '{selected_template}' not found.")
                else:
                    st.warning("No employee data could be extracted from the PDF. Please check if the file format is supported.")
            
        except Exception as e:
            st.error(f"An error occurred during processing: {str(e)}")
        finally:
            # Clean up the temporary file
            os.unlink(temp_path)
    
    # Information about creating custom templates
    st.sidebar.markdown('<div class="section-header">Custom Templates</div>', unsafe_allow_html=True)
    st.sidebar.markdown(
        'To create a custom template:\n\n'
        '1. Create a CSV file with your desired column headers\n'
        '2. Place it in the `/templates` directory\n'
        '3. Create a matching JSON mapping file in `/mappings`\n\n'
        'The mapping file should map template fields to PDF fields.'
    )


if __name__ == "__main__":
    main()
