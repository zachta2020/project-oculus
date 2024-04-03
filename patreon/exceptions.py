class parseFailedException(Exception):
    """
    Exception raised when patreonScanner fails to parse target website.
    
    """
    def __init__(self, message="Website parse has failed"):
        self.message = message
        super().__init__(self.message)