def sanitize_query(query):
    dangerous_keywords = [" os", " io", ".os", ".io", "'os'", "'io'", '"os"', '"io"', "chr(", "chr)", "chr ", "(chr", "b64decode"]
    for keyword in dangerous_keywords:
        query = query.replace(keyword, "")
    return query
