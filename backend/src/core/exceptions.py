from fastapi import HTTPException
class AppException(Exception):
 def __init__(self,code='APP_ERROR',message='Application error',status_code=400,details=None): self.code,self.message,self.status_code,self.details=code,message,status_code,details
class UnauthorizedError(AppException):
 def __init__(self,message='Not authenticated',details=None): super().__init__('UNAUTHORIZED',message,401,details)
class NotFoundError(AppException):
 def __init__(self,message='Resource not found',details=None): super().__init__('NOT_FOUND',message,404,details)
class ForbiddenError(AppException):
 def __init__(self,message='Forbidden',details=None): super().__init__('FORBIDDEN',message,403,details)
class ConflictError(AppException):
 def __init__(self,message='Conflict',details=None): super().__init__('CONFLICT',message,409,details)

class ValidationError(AppException):
 def __init__(self,message='Validation error',details=None): super().__init__('VALIDATION_ERROR',message,422,details)
