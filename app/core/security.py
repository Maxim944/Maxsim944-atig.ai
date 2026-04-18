# JWT and Password Hashing Utilities

## Utility Functions

### 1. verify_password
This function checks if the provided plain password matches the hashed password.

```python
def verify_password(plain_password, hashed_password):
    # Implementation goes here
    pass
```

### 2. get_password_hash
This function generates a password hash from a plain password.

```python
def get_password_hash(plain_password):
    # Implementation goes here
    pass
```

### 3. create_access_token
This function creates a new access token using the provided data.

```python
def create_access_token(data, expires_delta=None):
    # Implementation goes here
    pass
```

### 4. decode_token
This function decodes a JWT and validates its signature.

```python
def decode_token(token):
    # Implementation goes here
    pass
```