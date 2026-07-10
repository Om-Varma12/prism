"""
SQL query validator for ZCQL safety and correctness.
"""
import re
from typing import Tuple


# Valid table names from schema
VALID_TABLES = {
    'CaseMaster', 'ChargesheetDetails', 'ActSectionAssociation', 'Accused', 'Victim',
    'ComplainantDetails', 'ArrestSurrender', 'Act', 'Section', 'CrimeHead', 'CrimeSubHead',
    'CrimeHeadActSection', 'State', 'District', 'Unit', 'UnitType', 'Court', 'Employee',
    'Rank', 'Designation', 'CaseCategory', 'GravityOffence', 'CaseStatusMaster',
    'OccupationMaster', 'ReligionMaster', 'CasteMaster',
    'dashboard_stats', 'crime_alerts', 'risk_scores', 'conversations', 'audit_logs'
}

# Dangerous keywords that should not appear in queries
DANGEROUS_KEYWORDS = {
    'DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE', 'TRUNCATE',
    'GRANT', 'REVOKE', 'EXEC', 'EXECUTE', 'SCRIPT'
}

# Keywords not allowed in ZCQL
ZCQL_FORBIDDEN = {
    'CASE WHEN', 'UNION', 'INTERSECT', 'EXCEPT'
}


def validate_query(sql: str) -> Tuple[bool, str]:
    """
    Validate a ZCQL query for safety and correctness.
    
    Args:
        sql: The SQL query string to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not sql or not sql.strip():
        return False, "Query is empty"
    
    sql_upper = sql.upper()
    
    # Check for dangerous keywords
    for keyword in DANGEROUS_KEYWORDS:
        if keyword in sql_upper:
            return False, f"Dangerous keyword not allowed: {keyword}"
    
    # Check for ZCQL forbidden patterns
    for forbidden in ZCQL_FORBIDDEN:
        if forbidden in sql_upper:
            return False, f"ZCQL does not support: {forbidden}"
    
    # Must be a SELECT query
    if not sql_upper.strip().startswith('SELECT'):
        return False, "Query must start with SELECT"
    
    # Must have LIMIT clause
    if 'LIMIT' not in sql_upper:
        return False, "Query must include LIMIT clause"
    
    # Check for valid table names
    VALID_TABLES_LOWER = {t.lower() for t in VALID_TABLES}
    tables_used = re.findall(r'FROM\s+(\w+)|JOIN\s+(\w+)', sql_upper, re.IGNORECASE)
    for table_tuple in tables_used:
        table_name = table_tuple[0] or table_tuple[1]
        if table_name and table_name.lower() not in VALID_TABLES_LOWER:
            return False, f"Invalid table name: {table_name}"
    
    # Check for subqueries (parentheses after FROM/JOIN)
    if re.search(r'FROM\s+\(|JOIN\s+\(', sql_upper, re.IGNORECASE):
        return False, "Subqueries are not allowed in ZCQL"
    
    # Check for date functions
    date_functions = ['NOW()', 'DATE_TRUNC', 'CURRENT_DATE', 'CURRENT_TIME']
    for func in date_functions:
        if func in sql_upper:
            return False, f"Date function not allowed: {func} (compute in Python)"
    
    # Check for excessive JOINs (max 4)
    join_count = sql_upper.count(' JOIN')
    if join_count > 4:
        return False, f"Too many JOINs ({join_count}). Maximum allowed is 4"
    
    return True, "Query is valid"


def sanitize_query(sql: str) -> str:
    """
    Sanitize a SQL query by removing trailing semicolons and normalizing whitespace.
    
    Args:
        sql: The SQL query string to sanitize
        
    Returns:
        Sanitized SQL query
    """
    # Remove trailing semicolon
    sql = sql.rstrip(';')
    
    # Normalize whitespace (multiple spaces to single space)
    sql = re.sub(r'\s+', ' ', sql)
    
    # Trim leading/trailing whitespace
    sql = sql.strip()
    
    return sql


def extract_limit(sql: str) -> int:
    """
    Extract the LIMIT value from a SQL query.
    
    Args:
        sql: The SQL query string
        
    Returns:
        The LIMIT value, or 50 if not found
    """
    match = re.search(r'LIMIT\s+(\d+)', sql, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return 50
