class ParseFailedException(Exception):
    """
    Exception raised when a scanner fails to parse target website.
    
    """
    def __init__(self, message="Website parse has failed"):
        self.message = message
        super().__init__(self.message)