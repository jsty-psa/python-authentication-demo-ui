# Python Authentication Demo UI

This is a sample application utilizing the PhilSys Authentication API via Python.

## Installation

**Create a virtual environment in python.**

```bash
python -m venv venv
```

**Activate the virtual environment.**

```bash
# Windows
.\venv\Scripts\activate

# Linux
source env/bin/activate
```

**Install all libraries in the requirements.txt**

```bash
pip install -r requirements.txt
```

**Create environment variable inside the auth_demo_ui folder.**

```bash
# Windows
type nul > auth_demo_ui\.env

# Linux
touch auth_demo_ui/.env
```

**Create and upload all the keys needed in this location**

```
auth_demo_ui/authentication/keys/[Partner_ID]
```

**Fill-up properties inside the environment variable.**

```properties
# PhilSys Base URL for authentication
BASE_URL=[PhilSys Base URL]

# TSP License Key provided by PDMS
TSP_LICENSE_KEY=[TSP License Key]

# Partner ID provided by PDMS
PARTNER_ID=[Partner ID]

# API Key provided by PDMS
API_KEY=[Partner Key]

# Partner P12 password (if used within the system)
P12_PASSWORD=[P12 Password]

# PhilSys Target Environment
ENV=[Environment]

# Client ID for Authorization
CLIENT_ID=[Client ID]

# Client Secret Key for Authorization
SECRET_KEY=[Secret Key]

# Client Application ID for Authorization
APP_ID=[App ID]

# Authorization URL
ID_AUTH_MANAGER=[ID Authentication manager]

# PhilSys Version
VERSION=[PhilSys Version]
```

**Run the Django Project**

```bash
python auth_demo_ui/manage.py runserver 0.0.0.0:8000
```

## Contributing

All pull requests are welcome in this environment and feel free to utilize this application.
