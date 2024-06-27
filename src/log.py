# module log

def log_print(*args, header='[ FILECHAT ]', end='\n', sep=' ', flush=False, file=None):
    """Custom printer

    Args:
        header (str, optional): logger name. Defaults to 'LOG:'.
        end (str, optional): ditto. Defaults to '\n'.
        sep (str, optional): ditto. Defaults to ' '.
        flush (bool, optional): ditto. Defaults to False.
        file (any, optional): redirect. Defaults to None.
    """
    print(header, *args, end=end, sep=sep, flush=flush, file=file)


