class Error(Exception):
    """A Basic Error"""
    pass

class InvalidData(Exception):
    """Data is invallid"""
    pass

class CharacterNotFound(InvalidData):
    """When A user cannot be found, raise this"""
    pass

class FailedToParse(Error):
    """When Parsing Fails"""
    pass

class ServiceUnavialable(Error):
    """When BNS is down"""
    pass
