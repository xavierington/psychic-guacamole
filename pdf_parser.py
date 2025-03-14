import re
import pdfplumber
from typing import List, Dict, Any, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PayrollPDFParser:
    """Parser for Certified Payroll Register PDFs"""
    
    def __init__(self, pdf_path: str):
        """Initialize the parser with the path to the PDF file"""
        self.pdf_path = pdf_path
        self.text_pages = []
        self.job_info = {}
        self.employees = []
    
    def extract_text(self) -> List[str]:
        """Extract text from all pages of the PDF"""
        logger.info(f"Extracting text from {self.pdf_path}")
        
        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    self.text_pages.append(text)
        
        logger.info(f"Extracted {len(self.text_pages)} pages of text")
        return self.text_pages
    
    def extract_job_info(self) -> Dict[str, str]:
        """Extract job information from the header of the PDF"""
        if not self.text_pages:
            self.extract_text()
        
        # Patterns for job information
        job_patterns = {
            "job_name": r"Job\s*\n([^\n]+)",
            "job_number": r"Job Number:\s*([^\n]+)",
            "week_ending": r"Week Ending:\s*([^\n]+)",
            "payroll_number": r"Payroll #\s*([^\n]+)",
            "contractor_name": r"Contractor\s*\n([^\n]+)",
            "contractor_address": r"BUTLER, WI 53007",  # This is specific to the example
            "customer_name": r"Customer\s*\n([^\n]+)",
            "customer_address": r"BROOKFIELD, WI 53005"  # This is specific to the example
        }
        
        job_info = {}
        
        # Try to extract job information from the first page
        first_page = self.text_pages[0] if self.text_pages else ""
        
        for key, pattern in job_patterns.items():
            match = re.search(pattern, first_page)
            if match:
                job_info[key] = match.group(1).strip()
            else:
                job_info[key] = ""
        
        self.job_info = job_info
        return job_info
    
    def extract_employee_records(self) -> List[Dict[str, Any]]:
        """Extract employee records from the PDF"""
        if not self.text_pages:
            self.extract_text()
        
        employees = []
        
        # Process each page
        for page_text in self.text_pages:
            # Skip pages without employee data
            if "Name / Address" not in page_text or "Hours Worked This Job" not in page_text:
                continue
            
            # Extract employee information
            employee = self._extract_employee_info(page_text)
            if employee:
                # Add job information to the employee record
                employee.update(self.job_info)
                employees.append(employee)
        
        self.employees = employees
        logger.info(f"Extracted {len(employees)} employee records")
        return employees
    
    def _extract_employee_info(self, page_text: str) -> Optional[Dict[str, Any]]:
        """Extract employee information from a page of text"""
        employee = {}
        
        # Extract basic employee info
        name_match = re.search(r"([A-Z\s]+[A-Z])\s+(\*\*\*-\*\*-\d{4})", page_text)
        if name_match:
            employee["name"] = name_match.group(1).strip()
            employee["ssn"] = name_match.group(2)
        else:
            return None  # No employee data on this page
        
        # Extract address
        address_match = re.search(r"([A-Z0-9\s]+)\s+([A-Z]+)\s+(\w+)\s+(\d+)", page_text)
        if address_match:
            employee["address"] = address_match.group(1).strip()
            employee["city"] = address_match.group(2).strip()
            employee["state"] = address_match.group(3).strip()
            employee["zip"] = address_match.group(4).strip()
        
        # Extract job classification
        class_match = re.search(r"Class\s+.+\s+([A-Z]+)\s+Male", page_text)
        if class_match:
            employee["job_class"] = class_match.group(1).strip()
        
        # Extract marital status
        marital_match = re.search(r"(Single|Married)\s+\d+", page_text)
        if marital_match:
            employee["marital_status"] = marital_match.group(1).strip()
        
        # Extract hours
        hours_pattern = r"R:\s+(\d+\.\d+).*O:\s+(\d+\.\d+)"
        hours_match = re.search(hours_pattern, page_text)
        if hours_match:
            employee["regular_hours"] = float(hours_match.group(1))
            employee["overtime_hours"] = float(hours_match.group(2))
        
        # Extract pay rate and gross pay
        pay_pattern = r"(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)"
        pay_match = re.search(pay_pattern, page_text)
        if pay_match:
            employee["pay_rate"] = float(pay_match.group(1))
            employee["gross_pay"] = float(pay_match.group(2))
            employee["federal_tax"] = float(pay_match.group(3))
            employee["net_pay"] = float(pay_match.group(4))
        
        # Extract fringe benefits
        fringe_matches = re.finditer(r"(AMF 494|ANNUITY|H&W|JATC 494|LMCC 494|NEBF 494|NECA-494|NEIF-494|PENSION|VAC/HOL)\s+(\d+\.\d+)\s+(\d+\.\d+)", page_text)
        for match in fringe_matches:
            benefit_name = match.group(1).replace(" ", "_").replace("&", "and").replace("-", "_").lower()
            rate = float(match.group(2))
            amount = float(match.group(3))
            employee[f"{benefit_name}_rate"] = rate
            employee[f"{benefit_name}_amount"] = amount
        
        # Extract DUES amount
        dues_match = re.search(r"DUES\s+(\d+\.\d+)", page_text)
        if dues_match:
            employee["dues_amount"] = float(dues_match.group(1))
        
        # Extract totals
        total_match = re.search(r"Total\s+(\d+\.\d+)", page_text)
        if total_match:
            employee["total_deductions"] = float(total_match.group(1))
        
        return employee
    
    def parse(self) -> Dict[str, Any]:
        """Parse the PDF and return all extracted information"""
        self.extract_text()
        self.extract_job_info()
        self.extract_employee_records()
        
        return {
            "job_info": self.job_info,
            "employees": self.employees
        }


# Example usage:
# parser = PayrollPDFParser("path/to/payroll.pdf")
# data = parser.parse()
# print(f"Job info: {data['job_info']}")
# print(f"Number of employees: {len(data['employees'])}")
