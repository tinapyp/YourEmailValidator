# Email Validator

This project provides a simple and efficient solution to validate email addresses. It can be integrated into your web applications, ensuring that users provide valid and correctly formatted email addresses before submission.

## Features

- **Valid Email Format**: Ensures the email matches standard email format rules.
- **Domain Validation**: Checks whether the email domain is valid and reachable.
- **Customizable Validation Rules**: You can configure additional rules for validation based on your application's requirements.
- **Fast and Reliable**: Built to be lightweight and optimized for quick validation.

## Installation

To install the email validator, clone the repository and install the required dependencies using `pip`.

```bash
git clone https://github.com/yourusername/email-validator.git
cd email-validator
pip install -r requirements.txt
```

## Usage

Once the package is installed, you can easily validate an email address using the following example:

```python
from app.services.email_validator import validate_email

# Example email address
email = "user@example.com"

# Validate the email
is_valid = validate_email(email)

if is_valid:
    print("The email is valid!")
else:
    print("The email is invalid!")
```

The `validate_email` function checks if the email has a proper format and ensures the domain is reachable.

## Configuration

You can customize the behavior of the email validator by adjusting the configuration in `app/services/config.py`. Add your custom rules or external services like email domain lookups for extended validation.

## API Endpoint

If you want to integrate email validation into your API, you can use the provided API endpoint. The endpoint expects a JSON payload with the email to be validated.

### Request Example

```json
{
  "email": "user@example.com"
}
```

### Response Example

```json
{
  "valid": true,
  "message": "The email is valid."
}
```

### Using the API in `app/api/routes.py`

```python
from fastapi import APIRouter
from app.services.email_validator import validate_email

router = APIRouter()

@router.post("/validate-email/")
async def validate_email_endpoint(email: str):
    is_valid = validate_email(email)
    return {"valid": is_valid, "message": "The email is valid." if is_valid else "The email is invalid."}
```

## Development

To contribute to this project, fork the repository and make changes to your fork. Once you're done, submit a pull request to the main repository.
