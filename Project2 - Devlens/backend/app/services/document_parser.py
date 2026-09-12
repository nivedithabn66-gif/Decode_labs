import io
import re
import zipfile
from typing import Dict, Any, List
import pypdf

def parse_uploaded_file(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """
    Parses PDF, ZIP, TXT, LOG, or JSON file content to extract issue report details,
    stack traces, error logs, and environmental context.
    """
    ext = filename.lower().split('.')[-1]
    
    extracted_text = ""
    extracted_logs = ""
    file_list = []
    
    if ext == "pdf":
        try:
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            file_list.append(f"{filename} ({len(reader.pages)} pages)")
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
        except Exception as e:
            extracted_text = f"Failed to extract PDF content: {str(e)}"
            
    elif ext == "zip":
        try:
            with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
                all_names = z.namelist()
                file_list = all_names[:15] # Limit file list
                
                # Prioritize log, txt, md, json files
                for item in all_names:
                    if item.endswith('/') or '__MACOSX' in item:
                        continue
                    item_ext = item.lower().split('.')[-1]
                    if item_ext in ['txt', 'log', 'md', 'json', 'py', 'java', 'js', 'ts', 'cpp', 'yml', 'yaml']:
                        try:
                            content = z.read(item).decode('utf-8', errors='ignore')
                            if item_ext in ['log', 'txt'] and 'error' in item.lower():
                                extracted_logs += f"--- Content from {item} ---\n{content[:2000]}\n\n"
                            else:
                                extracted_text += f"--- Content from {item} ---\n{content[:2000]}\n\n"
                        except Exception:
                            pass
        except Exception as e:
            extracted_text = f"Failed to extract ZIP content: {str(e)}"
            
    else:
        # Raw text, log, or json file
        try:
            extracted_text = file_bytes.decode('utf-8', errors='ignore')
            file_list.append(filename)
        except Exception as e:
            extracted_text = f"Failed to read file: {str(e)}"

    # Process and structure extracted content
    lines = [line.strip() for line in extracted_text.split('\n') if line.strip()]
    
    # Extract Title (first non-empty line or filename)
    title = ""
    if lines:
        first_line = lines[0]
        # Clean title markdown
        first_line = re.sub(r'^[#*\-\s]+', '', first_line).strip()
        if len(first_line) > 5 and len(first_line) < 120:
            title = first_line
            
    if not title:
        title = f"Issue report extracted from {filename}"

    # Separate stacktraces / logs from general description
    logs = extracted_logs
    description_lines = []
    
    log_patterns = [
        r'Exception in thread', r'Traceback \(most recent call last\):',
        r'NullPointerException', r'Segmentation fault', r'OperationalError',
        r'ERROR:', r'FATAL:', r'STACKTRACE', r'at [a-zA-Z0-9_.]+\([a-zA-Z0-9_.]+:\d+\)'
    ]
    
    for line in lines:
        is_log = any(re.search(pat, line, re.IGNORECASE) for pat in log_patterns)
        if is_log:
            logs += line + "\n"
        else:
            description_lines.append(line)
            
    description = "\n".join(description_lines[:25]) # Cap description length
    if not description and logs:
        description = f"Automated log extract from attached file {filename}."

    # Extract reproduction steps or environment if present
    steps = ""
    environment = ""
    
    for i, line in enumerate(lines):
        if "reproduce" in line.lower() or "steps" in line.lower():
            steps = "\n".join(lines[i:i+6])
        if "environment" in line.lower() or "os:" in line.lower() or "version:" in line.lower():
            environment = "\n".join(lines[i:i+4])

    return {
        "filename": filename,
        "file_type": ext.upper(),
        "extracted_files": file_list,
        "title": title,
        "description": description,
        "steps_to_reproduce": steps or "Extracted from uploaded attachment.",
        "environment": environment or f"File Format: {ext.upper()}",
        "logs": logs.strip()
    }


def generate_error_rectification(title: str, description: str, logs: str, category: str) -> Dict[str, Any]:
    """
    Generates intelligent error diagnosis, root cause explanation, and step-by-step
    rectification recommendations for bugs, features, and questions.
    """
    full_text = f"{title}\n{description}\n{logs}".lower()
    
    rectifications = []
    root_cause = "General software issue detected."
    code_fix = None
    
    if "nullpointerexception" in full_text or "none-type" in full_text or "nonetype" in full_text or "pointer is null" in full_text:
        root_cause = "Null Reference / Unhandled Nonetype Access."
        rectifications = [
            "Add defensive null-checks prior to calling methods on object references.",
            "Utilize optional chaining or Python `getattr(obj, 'attr', default)` patterns.",
            "Verify that input parameters and payload parameters are correctly validated before processing."
        ]
        code_fix = """// Defensive Check Example (Java / C#)
if (fileHandler != null && fileHandler.getFile() != null) {
    fileHandler.processUpload();
} else {
    logger.warn("FileHandler payload reference is null");
}"""

    elif "memory" in full_text or "oom" in full_text or "heap" in full_text or "segmentation fault" in full_text or "sigsegv" in full_text:
        root_cause = "Memory Leak / Buffer Overflow / Heap Exhaustion."
        rectifications = [
            "Inspect long-running loops or unclosed file handles/sockets causing memory leak.",
            "Implement stream buffering (e.g., chunked file reading) instead of loading entire files into memory.",
            "Configure process memory limits and enable garbage collection logging (`--max-old-space-size` or `-Xmx`)."
        ]
        code_fix = """# Python Chunked Stream Processing Example
with open('large_file.bin', 'rb') as f:
    while chunk := f.read(8192): # Process 8KB chunks
        process_chunk(chunk)"""

    elif "deadlock" in full_text or "connection pool" in full_text or "operationalerror" in full_text or "too many connections" in full_text:
        root_cause = "Database Connection Pool Exhaustion or Transaction Lock Contention."
        rectifications = [
            "Increase max database pool size and statement timeout settings in connection pool config.",
            "Ensure all database transactions execute within short `with db.session()` context blocks.",
            "Add exponential backoff retries on transient database deadlock errors."
        ]
        code_fix = """# SQLAlchemy Connection Pool Configuration
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800
)"""

    elif "cors" in full_text or "access-control-allow-origin" in full_text:
        root_cause = "Cross-Origin Resource Sharing (CORS) Policy Misconfiguration."
        rectifications = [
            "Add explicit client domain URLs to backend CORS middleware configuration.",
            "Allow required HTTP methods (`GET`, `POST`, `PUT`, `DELETE`, `OPTIONS`) and headers (`Content-Type`, `Authorization`)."
        ]
        code_fix = """# FastAPI CORS Setup
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)"""

    elif "jwt" in full_text or "401" in full_text or "unauthorized" in full_text or "token" in full_text:
        root_cause = "Authentication / Token Validation Failure."
        rectifications = [
            "Verify token expiration claims (`exp`) and secret key alignment between Auth Server and API Server.",
            "Implement token refresh interceptors on client side to handle token rotation seamlessly."
        ]
        code_fix = """# PyJWT Token Verification
try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
except jwt.ExpiredSignatureError:
    raise HTTPException(status_code=401, detail="Token expired. Please re-authenticate.")"""

    elif category == "Feature":
        root_cause = "New Feature Enhancement Requirement."
        rectifications = [
            "Outline functional specifications and API interface contracts.",
            "Create modular component mockups or schema migrations.",
            "Write comprehensive unit test cases covering edge cases for the new feature."
        ]
        code_fix = None

    elif category == "Question":
        root_cause = "Configuration or Usage Inquiry."
        rectifications = [
            "Review official project documentation and configuration guidelines.",
            "Check environment variable definitions in `.env.example` file.",
            "Verify setup steps in project README.md."
        ]
        code_fix = None

    else:
        root_cause = "General Software Bug / Issue."
        rectifications = [
            "Inspect error log timestamps and match against recent deployment releases.",
            "Add extra debug logging around failing function calls.",
            "Write reproducible integration tests isolating the error signal."
        ]
        code_fix = None

    return {
        "root_cause": root_cause,
        "rectification_steps": rectifications,
        "recommended_code_fix": code_fix
    }
