def extract_variables(query):
    import re
    return re.findall(r'\*(.*?)\*', query)

def enhance_prompt(query, patterns):
    variables = extract_variables(query)
    for pattern, extended_prompt in patterns.items():
        if pattern.lower() in query.lower():
            if variables:
                vars_str = ", ".join(variables)
                return extended_prompt.format(vars=vars_str)
            return extended_prompt.format(vars="specified variables")
    return query
